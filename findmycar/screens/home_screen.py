from kivy.clock import Clock
from kivy.properties import StringProperty, BooleanProperty
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.logger import Logger
from datetime import datetime

Builder.load_string("""
<HomeScreen>:
    BoxLayout:
        orientation: "vertical"
        canvas.before:
            Color:
                rgba: 0.075, 0.075, 0.082, 1
            Rectangle:
                pos: self.pos
                size: self.size

        MDTopAppBar:
            title: "Trova la mia auto"
            md_bg_color: 0.075, 0.075, 0.082, 1
            specific_text_color: 1, 1, 1, 1
            elevation: 0
            left_action_items: [["arrow-left", lambda x: root.open_nav_drawer()]]
            right_action_items: [["account-circle", lambda x: None]]

        RelativeLayout:

            MDCard:
                id: gps_badge
                size_hint: None, None
                height: "32dp"
                width: "200dp"
                pos_hint: {"center_x": 0.5, "top": 0.93}
                md_bg_color: 0.09, 0.1, 0.13, 0.95
                radius: [16, 16, 16, 16]
                padding: "14dp", "6dp"
                spacing: "6dp"

                MDIcon:
                    id: gps_dot
                    icon: "circle"
                    font_size: "8sp"
                    theme_text_color: "Custom"
                    text_color: 0.133, 0.773, 0.369, 1

                MDLabel:
                    id: gps_label
                    text: "Precisione: 5 metri"
                    font_size: "11sp"
                    theme_text_color: "Custom"
                    text_color: 0.133, 0.773, 0.369, 1
                    halign: "left"
                    valign: "middle"

            Widget:
                pos_hint: {"center_x": 0.5, "center_y": 0.50}
                size_hint: None, None
                size: "300dp", "300dp"
                canvas:
                    Color:
                        rgba: 0, 0.48, 1, 0.13
                    Ellipse:
                        pos: self.pos
                        size: self.size

            MDBoxLayout:
                id: save_area
                orientation: "vertical"
                pos_hint: {"center_x": 0.5, "center_y": 0.52}
                size_hint: None, None
                size: "220dp", "220dp"
                spacing: "8dp"
                padding: "30dp"

                canvas.before:
                    Color:
                        rgba: 0, 0.48, 1, 1
                    Ellipse:
                        pos: self.pos
                        size: self.size
                    Color:
                        rgba: 0, 0.48, 1, 0.2
                    Ellipse:
                        pos: [self.x - 8, self.y - 8]
                        size: [self.width + 16, self.height + 16]

                MDIcon:
                    icon: "map-marker-radius"
                    font_size: "64sp"
                    theme_text_color: "Custom"
                    text_color: 1, 1, 1, 1
                    halign: "center"
                    valign: "middle"

                MDLabel:
                    text: "Salva Posizione"
                    font_size: "15sp"
                    bold: True
                    theme_text_color: "Custom"
                    text_color: 1, 1, 1, 1
                    halign: "center"
                    valign: "middle"

            MDLabel:
                text: "Tocca il pulsante per memorizzare dove hai parcheggiato."
                font_size: "13sp"
                theme_text_color: "Custom"
                text_color: 0.4, 0.42, 0.45, 1
                halign: "center"
                pos_hint: {"center_x": 0.5, "y": 0.26}
                size_hint_x: 0.7
                text_size: self.width, None

            MDCard:
                id: parking_card
                orientation: "vertical"
                size_hint_x: 0.9
                size_hint_y: None
                height: "210dp"
                pos_hint: {"center_x": 0.5, "y": 0.03}
                md_bg_color: 0.106, 0.106, 0.114, 1
                radius: [24, 24, 24, 24]
                padding: "20dp"
                spacing: "16dp"
                elevation: 0

                MDBoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    height: "48dp"
                    spacing: "12dp"

                    MDCard:
                        size_hint: None, None
                        size: "44dp", "44dp"
                        md_bg_color: 0.12, 0.12, 0.15, 1
                        radius: [12, 12, 12, 12]
                        padding: 0
                        MDIcon:
                            icon: "store-outline"
                            font_size: "24sp"
                            theme_text_color: "Custom"
                            text_color: 0.6, 0.6, 0.65, 1
                            halign: "center"
                            valign: "middle"

                    MDBoxLayout:
                        orientation: "vertical"
                        spacing: "2dp"
                        MDLabel:
                            text: "Ultimo parcheggio"
                            font_size: "16sp"
                            bold: True
                            theme_text_color: "Custom"
                            text_color: 1, 1, 1, 1
                        MDLabel:
                            id: time_label
                            text: ""
                            font_size: "12sp"
                            theme_text_color: "Custom"
                            text_color: 0.4, 0.42, 0.45, 1

                MDBoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    height: "24dp"
                    spacing: "8dp"

                    MDIcon:
                        icon: "map-marker"
                        font_size: "18sp"
                        theme_text_color: "Custom"
                        text_color: 0, 0.48, 1, 1

                    MDLabel:
                        id: address_label
                        text: "Nessun parcheggio salvato"
                        font_size: "14sp"
                        theme_text_color: "Custom"
                        text_color: 0.8, 0.8, 0.85, 1

                MDRoundFlatIconButton:
                    id: navigate_btn
                    text: "PORTAMI QUI"
                    icon: "navigation-outline"
                    font_size: "14sp"
                    bold: True
                    size_hint_y: None
                    height: "48dp"
                    theme_text_color: "Custom"
                    text_color: 1, 1, 1, 1
                    md_bg_color: 0.12, 0.12, 0.15, 1
                    line_color: 0.12, 0.12, 0.15, 1
                    radius: [16, 16, 16, 16]
                    on_release: root.navigate_to_car()

        MDBoxLayout:
            size_hint_y: None
            height: "80dp"
            md_bg_color: 0.075, 0.075, 0.082, 1
            padding: "0dp", "8dp", "0dp", "24dp"
            spacing: 0
            canvas.before:
                Color:
                    rgba: 1, 1, 1, 0.05
                Line:
                    points: [self.x, self.y + self.height, self.right, self.y + self.height]
                    width: 0.5

            MDBoxLayout:
                id: tab_home
                orientation: "vertical"
                spacing: "4dp"
                MDIcon:
                    icon: "home"
                    font_size: "24sp"
                    theme_text_color: "Custom"
                    text_color: 0, 0.48, 1, 1
                    halign: "center"
                MDLabel:
                    text: "Home"
                    font_size: "11sp"
                    bold: True
                    theme_text_color: "Custom"
                    text_color: 0, 0.48, 1, 1
                    halign: "center"

            MDBoxLayout:
                id: tab_history
                orientation: "vertical"
                spacing: "4dp"
                MDIcon:
                    icon: "history"
                    font_size: "24sp"
                    theme_text_color: "Custom"
                    text_color: 0.4, 0.4, 0.45, 1
                    halign: "center"
                MDLabel:
                    text: "History"
                    font_size: "11sp"
                    theme_text_color: "Custom"
                    text_color: 0.4, 0.4, 0.45, 1
                    halign: "center"

            MDBoxLayout:
                id: tab_settings
                orientation: "vertical"
                spacing: "4dp"
                MDIcon:
                    icon: "cog"
                    font_size: "24sp"
                    theme_text_color: "Custom"
                    text_color: 0.4, 0.4, 0.45, 1
                    halign: "center"
                MDLabel:
                    text: "Settings"
                    font_size: "11sp"
                    theme_text_color: "Custom"
                    text_color: 0.4, 0.4, 0.45, 1
                    halign: "center"
""")


class HomeScreen(Screen):
    status_text = StringProperty("Inizializzazione...")
    address_text = StringProperty("Attivazione GPS in corso")
    gps_waiting = BooleanProperty(True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.gps_service = None
        self.storage_service = None
        self.offline_localizer = None
        self._update_clock = None
        self._has_parks = False

    def on_enter(self):
        Clock.schedule_once(self._setup, 0.1)

    def on_leave(self):
        if self._update_clock:
            self._update_clock.cancel()
        if self.gps_service:
            self.gps_service.remove_listener(self._on_gps_update)

    def _setup(self, dt):
        app = self._get_app()
        if not app:
            return

        self.gps_service = app.gps_service
        self.storage_service = app.storage_service
        self.offline_localizer = app.offline_localizer

        self.gps_service.add_listener(self._on_gps_update)
        self._update_clock = Clock.schedule_interval(self._periodic_update, 1.0)

        if self.gps_service.has_fix():
            pos = self.gps_service.get_position()
            if pos:
                accuracy = self.gps_service.accuracy if self.gps_service.accuracy is not None else 0
                self._update_gps_badge(accuracy)

        self._load_latest_parking()

    def _load_latest_parking(self):
        if not self.storage_service:
            return
        latest = self.storage_service.get_latest()
        if latest:
            self._has_parks = True
            try:
                self.ids.time_label.text = self._format_timestamp(latest.timestamp)
            except (AttributeError, KeyError):
                self.ids.time_label.text = ""
            addr = latest.address or f"{latest.latitude:.4f}, {latest.longitude:.4f}"
            try:
                self.ids.address_label.text = addr
            except (AttributeError, KeyError):
                pass
        else:
            self._has_parks = False
            try:
                self.ids.time_label.text = ""
                self.ids.address_label.text = "Nessun parcheggio salvato"
            except (AttributeError, KeyError):
                pass

    def _format_timestamp(self, ts_str):
        try:
            ts = datetime.fromisoformat(ts_str)
            now = datetime.now()
            if ts.date() == now.date():
                return f"Oggi, {ts.strftime('%H:%M')}"
            delta = (now.date() - ts.date()).days
            if delta == 1:
                return f"Ieri, {ts.strftime('%H:%M')}"
            return ts.strftime("%d/%m/%Y, %H:%M")
        except:
            return ts_str

    def _get_app(self):
        try:
            from kivy.app import App
            return App.get_running_app()
        except:
            return None

    def _on_gps_update(self, gps_svc):
        if not self.gps_service:
            return
        accuracy = self.gps_service.accuracy if self.gps_service.accuracy is not None else 0
        self._update_gps_badge(accuracy)

    def _update_gps_badge(self, accuracy):
        try:
            label = self.ids.gps_label
            if accuracy > 0:
                label.text = f"Precisione: {accuracy:.0f} metri"
            else:
                label.text = "GPS in aggancio..."
        except (AttributeError, KeyError):
            pass

    def _periodic_update(self, dt):
        if not self.gps_service:
            return
        if not self.gps_service.has_fix():
            try:
                self.ids.gps_label.text = "GPS in aggancio..."
            except (AttributeError, KeyError):
                pass

    def on_touch_down(self, touch):
        try:
            if self.ids.save_area.collide_point(*touch.pos):
                self.save_position()
                return True
        except (AttributeError, KeyError):
            pass

        try:
            if self.ids.tab_history.collide_point(*touch.pos):
                self.go_to_history()
                return True
        except (AttributeError, KeyError):
            pass

        try:
            if self.ids.tab_settings.collide_point(*touch.pos):
                self.go_to_settings()
                return True
        except (AttributeError, KeyError):
            pass

        return super().on_touch_down(touch)

    def save_position(self):
        self.manager.current = "park"

    def navigate_to_car(self):
        if self._has_parks:
            self.manager.current = "find"
        else:
            self._show_toast("Nessun parcheggio salvato")

    def go_to_history(self):
        self.manager.current = "history"

    def go_to_settings(self):
        self._show_toast("Impostazioni in arrivo")

    def open_nav_drawer(self):
        app = self._get_app()
        if app and hasattr(app, "nav_drawer"):
            app.nav_drawer.set_state("open")

    def _show_toast(self, msg):
        try:
            from kivymd.uix.snackbar import Snackbar
            Snackbar(text=msg, duration=2).open()
        except Exception:
            pass
