from kivy.clock import Clock
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.logger import Logger
import os

Builder.load_string("""
<DetailsScreen>:
    canvas.before:
        Color:
            rgba: 0.075, 0.075, 0.082, 1
        Rectangle:
            pos: self.pos
            size: self.size

    BoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "Dettagli Parcheggio"
            md_bg_color: 0.075, 0.075, 0.082, 1
            specific_text_color: 0.678, 0.776, 1.0, 1
            elevation: 0
            left_action_items: [["arrow-left", lambda x: root.go_back()]]
            right_action_items: [["camera", lambda x: root.take_photo()]]

        ScrollView:
            MDBoxLayout:
                orientation: "vertical"
                size_hint_y: None
                height: self.minimum_height
                padding: "20dp", "16dp", "20dp", "16dp"
                spacing: "16dp"

                RelativeLayout:
                    size_hint_y: None
                    height: "200dp"
                    canvas.before:
                        Color:
                            rgba: 0.11, 0.11, 0.118, 0.8
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [16, 16, 16, 16]
                        Color:
                            rgba: 1, 1, 1, 0.05
                        Line:
                            rounded_rectangle: [self.x, self.y, self.width, self.height, 16, 16, 16, 16]
                            width: 0.5

                    MDIcon:
                        id: photo_icon
                        icon: "camera-plus-outline"
                        font_size: "48sp"
                        theme_text_color: "Custom"
                        text_color: 0.678, 0.776, 1.0, 1
                        pos_hint: {"center_x": 0.5, "center_y": 0.5}

                    MDLabel:
                        id: photo_label
                        text: "Tocca per scattare una foto"
                        font_size: "13sp"
                        theme_text_color: "Custom"
                        text_color: 0.757, 0.776, 0.843, 1
                        halign: "center"
                        pos_hint: {"center_x": 0.5, "y": 0.12}

                    MDFlatButton:
                        id: photo_btn
                        text: "AGGIUNGI FOTO"
                        font_size: "12sp"
                        theme_text_color: "Custom"
                        text_color: 0.678, 0.776, 1.0, 1
                        md_bg_color: 0.208, 0.208, 0.216, 1
                        size_hint: None, None
                        height: "40dp"
                        width: "160dp"
                        radius: [20, 20, 20, 20]
                        pos_hint: {"center_x": 0.5, "y": 0.02}
                        on_release: root.take_photo()

                MDBoxLayout:
                    orientation: "vertical"
                    size_hint_y: None
                    height: "180dp"
                    padding: "16dp"
                    spacing: "12dp"
                    canvas.before:
                        Color:
                            rgba: 0.11, 0.11, 0.118, 0.8
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [16, 16, 16, 16]
                        Color:
                            rgba: 1, 1, 1, 0.05
                        Line:
                            rounded_rectangle: [self.x, self.y, self.width, self.height, 16, 16, 16, 16]
                            width: 0.5

                    MDLabel:
                        text: "Note di Posizione"
                        font_size: "11sp"
                        bold: True
                        theme_text_color: "Custom"
                        text_color: 0.757, 0.776, 0.843, 1
                        letter_spacing: 2

                    MDTextField:
                        id: notes_input
                        hint_text: "Es. Settore B, Piano -1"
                        mode: "fill"
                        fill_color: 0.12, 0.12, 0.13, 1
                        line_color_focus: 0.678, 0.776, 1.0, 1
                        text_color_focus: 0.894, 0.886, 0.894, 1
                        hint_text_color: 0.4, 0.4, 0.42, 1
                        multiline: True
                        size_hint_y: None
                        height: "80dp"

                MDBoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    height: "60dp"
                    spacing: "12dp"

                    MDFlatButton:
                        text: "Condividi"
                        icon: "share"
                        font_size: "13sp"
                        theme_text_color: "Custom"
                        text_color: 0.678, 0.776, 1.0, 1
                        md_bg_color: 0.11, 0.11, 0.118, 0.8
                        radius: [12, 12, 12, 12]
                        size_hint_x: 0.5
                        on_release: root.share_location()

                    MDFlatButton:
                        text: "Salva Note"
                        icon: "content-save"
                        font_size: "13sp"
                        theme_text_color: "Custom"
                        text_color: 0.678, 0.776, 1.0, 1
                        md_bg_color: 0.11, 0.11, 0.118, 0.8
                        radius: [12, 12, 12, 12]
                        size_hint_x: 0.5
                        on_release: root.save_notes()

                MDFlatButton:
                    id: nav_btn
                    text: root.nav_button_text
                    icon: "navigation"
                    font_size: "16sp"
                    bold: True
                    theme_text_color: "Custom"
                    text_color: 0.894, 0.886, 0.894, 1
                    md_bg_color: 0.294, 0.557, 1.0, 1
                    radius: [16, 16, 16, 16]
                    size_hint_y: None
                    height: "56dp"
                    on_release: root.navigate_to_car()

        MDBoxLayout:
            id: bottom_bar
            size_hint_y: None
            height: "72dp"
            md_bg_color: 0.122, 0.122, 0.129, 0.8
            spacing: 0
            padding: 0

            RelativeLayout:
                size_hint_x: 1/3
                on_touch_down: root._nav_tab("home") if self.collide_point(*args[1].pos) else None

                MDIcon:
                    icon: "home"
                    font_size: "24sp"
                    theme_text_color: "Custom"
                    text_color: 0.678, 0.776, 1.0, 1
                    pos_hint: {"center_x": 0.5, "center_y": 0.65}

                MDLabel:
                    text: "Home"
                    font_size: "10sp"
                    halign: "center"
                    valign: "center"
                    theme_text_color: "Custom"
                    text_color: 0.678, 0.776, 1.0, 1
                    pos_hint: {"center_x": 0.5, "y": 0.02}
                    size_hint_y: 0.3

            RelativeLayout:
                size_hint_x: 1/3
                on_touch_down: root._nav_tab("history") if self.collide_point(*args[1].pos) else None

                MDIcon:
                    icon: "history"
                    font_size: "24sp"
                    theme_text_color: "Custom"
                    text_color: 0.5, 0.5, 0.55, 1
                    pos_hint: {"center_x": 0.5, "center_y": 0.65}

                MDLabel:
                    text: "History"
                    font_size: "10sp"
                    halign: "center"
                    valign: "center"
                    theme_text_color: "Custom"
                    text_color: 0.5, 0.5, 0.55, 1
                    pos_hint: {"center_x": 0.5, "y": 0.02}
                    size_hint_y: 0.3

            RelativeLayout:
                size_hint_x: 1/3
                on_touch_down: root._nav_tab("settings") if self.collide_point(*args[1].pos) else None

                MDIcon:
                    icon: "cog"
                    font_size: "24sp"
                    theme_text_color: "Custom"
                    text_color: 0.5, 0.5, 0.55, 1
                    pos_hint: {"center_x": 0.5, "center_y": 0.65}

                MDLabel:
                    text: "Settings"
                    font_size: "10sp"
                    halign: "center"
                    valign: "center"
                    theme_text_color: "Custom"
                    text_color: 0.5, 0.5, 0.55, 1
                    pos_hint: {"center_x": 0.5, "y": 0.02}
                    size_hint_y: 0.3
""")


class DetailsScreen(Screen):
    photo_path = StringProperty("")
    nav_button_text = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._record = None
        self.gps_service = None
        self.storage_service = None
        self.nav_button_text = "Portami all\u2019auto"

    def on_enter(self):
        app = self._get_app()
        if app:
            self.gps_service = app.gps_service
            self.storage_service = app.storage_service

    def load_record(self, record):
        self._record = record
        if record.photo_path and os.path.exists(record.photo_path):
            self.photo_path = record.photo_path
            try:
                self.ids.photo_icon.icon = "image"
                self.ids.photo_label.text = "Foto presente"
            except:
                pass

    def take_photo(self):
        park_screen = self.manager.get_screen("park")
        park_screen.set_callback(self._on_photo_taken)
        park_screen.take_photo()
        self.manager.current = "park"

    def _on_photo_taken(self, photo_path):
        self.photo_path = photo_path
        if self._record:
            self._record.photo_path = photo_path
            if self.storage_service:
                self.storage_service._save()
        try:
            self.ids.photo_icon.icon = "image"
            self.ids.photo_label.text = "Foto aggiunta ✓"
        except:
            pass
        self.manager.current = "details"

    def save_notes(self):
        if not self._record or not self.storage_service:
            return
        try:
            notes = self.ids.notes_input.text
            self._record.notes = notes
            self.storage_service._save()
            self._show_toast("Note salvate")
        except Exception:
            pass

    def share_location(self):
        if not self._record:
            return
        try:
            from jnius import autoclass
            Intent = autoclass("android.content.Intent")
            Uri = autoclass("android.net.Uri")
            intent = Intent(Intent.ACTION_VIEW)
            uri = Uri.parse(f"geo:{self._record.latitude},{self._record.longitude}?q={self._record.latitude},{self._record.longitude}")
            intent.setData(uri)
            from android import mActivity
            mActivity.startActivity(intent)
        except Exception:
            self._show_toast("Condivisione non disponibile")

    def navigate_to_car(self):
        self.manager.current = "find"

    def go_back(self):
        self.manager.current = "home"

    def go_home(self):
        self.manager.current = "home"

    def go_to_history(self):
        self.manager.current = "history"

    def go_to_settings(self):
        self._show_toast("Impostazioni in arrivo")

    def _nav_tab(self, tab):
        if tab == "home":
            self.go_home()
        elif tab == "history":
            self.go_to_history()
        elif tab == "settings":
            self.go_to_settings()
        return True

    def _get_app(self):
        try:
            from kivy.app import App
            return App.get_running_app()
        except:
            return None

    def _show_toast(self, msg):
        try:
            from kivymd.uix.snackbar import Snackbar
            Snackbar(text=msg, duration=2).open()
        except Exception:
            pass
