import os
import shutil
import uuid
from kivy.clock import Clock
from kivy.properties import StringProperty, NumericProperty
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.logger import Logger
from datetime import datetime

Builder.load_string("""
<ParkScreen>:
    MDBoxLayout:
        orientation: "vertical"
        md_bg_color: 0.05, 0.07, 0.09, 1
        spacing: "24dp"
        padding: ["24dp", "48dp", "24dp", "24dp"]

        MDTopAppBar:
            title: "Parcheggia"
            md_bg_color: 0.05, 0.07, 0.09, 1
            specific_text_color: 1, 1, 1, 1
            left_action_items: [["arrow-left", lambda x: root.go_back(), "Indietro"]]

        MDRelativeLayout:
            size_hint_y: 0.6

            MDCard:
                orientation: "vertical"
                size_hint: 0.9, 0.8
                pos_hint: {"center_x": 0.5, "center_y": 0.5}
                md_bg_color: 0.09, 0.1, 0.13, 1
                radius: [24, 24, 24, 24]
                padding: "24dp"
                spacing: "16dp"
                elevation: 4

                MDIcon:
                    icon: "map-marker-radius"
                    font_size: "64sp"
                    theme_text_color: "Custom"
                    text_color: 0.0, 0.898, 1.0, 1
                    halign: "center"
                    size_hint_y: 0.3

                MDLabel:
                    text: "Salva posizione"
                    font_size: "22sp"
                    theme_text_color: "Custom"
                    text_color: 1, 1, 1, 1
                    halign: "center"
                    bold: True

                MDLabel:
                    text: root.address_text
                    font_size: "13sp"
                    theme_text_color: "Custom"
                    text_color: 0.6, 0.62, 0.65, 1
                    halign: "center"
                    shorten: True
                    shorten_from: "right"

                MDLabel:
                    text: root.coords_text
                    font_size: "11sp"
                    theme_text_color: "Custom"
                    text_color: 0.4, 0.42, 0.45, 1
                    halign: "center"

                Widget:
                    size_hint_y: None
                    height: "1dp"
                    canvas:
                        Color:
                            rgba: 0.2, 0.22, 0.25, 1
                        Rectangle:
                            pos: self.pos
                            size: self.size

                MDTextField:
                    id: notes_input
                    hint_text: "Aggiungi note (piano, zona...)"
                    multiline: False
                    md_bg_color: 0.12, 0.14, 0.17, 1
                    mode: "fill"
                    size_hint_x: 1
                    font_size: "14sp"
                    hint_text_color_normal: 0.4, 0.42, 0.45, 1
                    text_color_normal: 1, 1, 1, 1
                    line_color_normal: 0, 0, 0, 0
                    line_color_focus: 0.0, 0.898, 1.0, 1

            MDRoundFlatIconButton:
                id: park_btn
                text: "Parcheggia Qui"
                icon: "check-circle"
                font_size: "18sp"
                size_hint_x: 0.9
                pos_hint: {"center_x": 0.5}
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1
                md_bg_color: 0.0, 0.6, 0.8, 1
                line_color: 0, 0, 0, 0
                radius: [28, 28, 28, 28]
                on_release: root.save_parking()

        MDBoxLayout:
            orientation: "horizontal"
            size_hint_y: 0.1
            pos_hint: {"center_x": 0.5}

            MDIconButton:
                icon: "camera-outline"
                theme_text_color: "Custom"
                text_color: 0.6, 0.62, 0.65, 1
                on_release: root.take_photo()

            MDLabel:
                text: root.photo_text
                font_size: "12sp"
                theme_text_color: "Custom"
                text_color: 0.4, 0.42, 0.45, 1
                valign: "middle"
""")


class ParkScreen(Screen):
    address_text = StringProperty("Rilevamento posizione...")
    coords_text = StringProperty("")
    photo_text = StringProperty("Aggiungi foto")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.gps_service = None
        self.storage_service = None
        self._photo_path = ""

    def on_enter(self):
        Clock.schedule_once(self._setup, 0.1)

    def _setup(self, dt):
        app = self._get_app()
        if not app:
            return
        self.gps_service = app.gps_service
        self.storage_service = app.storage_service
        self.gps_service.add_listener(self._on_gps_update)

        if self.gps_service.has_fix():
            pos = self.gps_service.get_position()
            if pos:
                self._update_coords(pos[0], pos[1])

    def _get_app(self):
        try:
            from kivy.app import App
            return App.get_running_app()
        except:
            return None

    def _on_gps_update(self, gps_svc):
        pos = gps_svc.get_position()
        if pos:
            self._update_coords(pos[0], pos[1])

    def _update_coords(self, lat, lon):
        self.coords_text = f"{lat:.6f}, {lon:.6f}"
        self.address_text = f"Lat: {lat:.4f}° · Lon: {lon:.4f}°"

    def save_parking(self):
        if not self.gps_service or not self.gps_service.has_fix():
            self._show_error("GPS non attivo")
            return

        pos = self.gps_service.get_position()
        if not pos:
            return

        notes = self.ids.notes_input.text
        record = self.storage_service.save_parking(
            pos[0], pos[1],
            address=self.address_text,
            notes=notes,
        )

        if hasattr(record, "photo_path") and self._photo_path:
            record.photo_path = self._photo_path
            self.storage_service._save()

        self._show_success("Posizione salvata!")
        Clock.schedule_once(lambda dt: self._go_home(), 1.0)

    def take_photo(self):
        try:
            from android.permissions import request_permissions, Permission, check_permission
            if not check_permission("android.permission.CAMERA"):
                results = request_permissions([Permission.CAMERA])
                if not results or not all(results):
                    self.photo_text = "Permesso fotocamera negato"
                    return
            from plyer import camera
            camera.take_picture(callback=self._on_photo_captured)
        except Exception as e:
            Logger.warning(f"ParkScreen: Camera error - {e}")
            self.photo_text = "Fotocamera non disponibile"

    def _on_photo_captured(self, path):
        if path:
            self._photo_path = path
            self.photo_text = "Foto aggiunta ✓"

    def _show_error(self, msg):
        from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
        from kivy.metrics import dp
        MDSnackbar(
            MDSnackbarText(text=msg),
            y=dp(24),
            pos_hint={"center_x": 0.5},
            size_hint_x=0.5,
            background_color=(0.8, 0.1, 0.1, 1),
        ).open()

    def _show_success(self, msg):
        from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
        from kivy.metrics import dp
        MDSnackbar(
            MDSnackbarText(text=msg),
            y=dp(24),
            pos_hint={"center_x": 0.5},
            size_hint_x=0.5,
            background_color=(0.0, 0.6, 0.3, 1),
        ).open()

    def _go_home(self):
        self.manager.current = "home"

    def go_back(self):
        self.manager.current = "home"