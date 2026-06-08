from kivy.clock import Clock
from kivy.properties import StringProperty, BooleanProperty, ListProperty
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.logger import Logger
from datetime import datetime


class GlassCard(BoxLayout):
    radius = ListProperty([16, 16, 16, 16])


Builder.load_string("""
<GlassCard>:
    canvas.before:
        Color:
            rgba: 0.11, 0.11, 0.118, 0.8
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: root.radius
        Color:
            rgba: 1, 1, 1, 0.05
        Line:
            rounded_rectangle: [self.x, self.y, self.width, self.height, root.radius[0] if root.radius else 16]
            width: 0.5


<HomeScreen>:
    canvas.before:
        Color:
            rgba: 0.075, 0.075, 0.082, 1
        Rectangle:
            pos: self.pos
            size: self.size

    BoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "Trova la mia auto"
            md_bg_color: 0.075, 0.075, 0.082, 1
            specific_text_color: 0.678, 0.776, 1.0, 1
            elevation: 0
            left_action_items: [["arrow-left", lambda x: root.open_nav_drawer()]]
            right_action_items: [["account-circle", lambda x: None]]

        FloatLayout:

            GlassCard:
                id: gps_badge
                size_hint: None, None
                height: "32dp"
                width: "220dp"
                pos_hint: {"center_x": 0.5, "top": 0.93}
                padding: "14dp", "6dp"
                spacing: "6dp"

                Widget:
                    size_hint: None, None
                    size: "8dp", "8dp"
                    pos_hint: {"center_y": 0.5}
                    canvas:
                        Color:
                            rgba: 0.325, 0.882, 0.435, 1
                        Ellipse:
                            pos: self.pos
                            size: self.size

                MDLabel:
                    id: gps_label
                    text: "Precisione: 5 metri"
                    font_size: "11sp"
                    theme_text_color: "Custom"
                    text_color: 0.325, 0.882, 0.435, 1
                    halign: "left"
                    valign: "middle"

            BoxLayout:
                orientation: "vertical"
                pos_hint: {"center_x": 0.5, "center_y": 0.62}
                size_hint: None, None
                width: "180dp"
                height: "200dp"
                spacing: "12dp"

                MDBoxLayout:
                    id: save_area
                    size_hint: None, None
                    size: "160dp", "160dp"
                    pos_hint: {"center_x": 0.5, "center_y": 0.5}
                    orientation: "vertical"
                    spacing: "6dp"
                    padding: "20dp"

                    canvas.before:
                        Color:
                            rgba: 0.678, 0.776, 1.0, 0.15
                        Ellipse:
                            pos: [self.x - 6, self.y - 6]
                            size: [self.width + 12, self.height + 12]
                        Color:
                            rgba: 0.678, 0.776, 1.0, 1
                        Ellipse:
                            pos: self.pos
                            size: self.size

                    MDIcon:
                        id: save_icon
                        icon: "map-marker-radius"
                        font_size: "52sp"
                        theme_text_color: "Custom"
                        text_color: 0, 0.18, 0.41, 1
                        halign: "center"
                        valign: "middle"

                    MDLabel:
                        id: save_label
                        text: "SALVA POSIZIONE"
                        font_size: "10sp"
                        bold: True
                        theme_text_color: "Custom"
                        text_color: 0, 0.18, 0.41, 1
                        halign: "center"
                        valign: "middle"
                        letter_spacing: 2

                MDLabel:
                    text: "Tocca il pulsante per memorizzare dove hai parcheggiato."
                    font_size: "13sp"
                    theme_text_color: "Custom"
                    text_color: 0.757, 0.776, 0.843, 1
                    halign: "center"
                    size_hint_x: 0.9
                    text_size: self.width, None

            GlassCard:
                id: parking_card
                orientation: "vertical"
                size_hint_x: 0.9
                size_hint_y: None
                height: "180dp"
                pos_hint: {"center_x": 0.5, "y": 0.1}
                padding: "16dp"
                spacing: "8dp"

                MDBoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    height: "44dp"
                    spacing: "12dp"

                    MDBoxLayout:
                        size_hint: None, None
                        size: "40dp", "40dp"
                        md_bg_color: 0.208, 0.208, 0.216, 1
                        radius: [12, 12, 12, 12]
                        MDIcon:
                            icon: "car"
                            font_size: "22sp"
                            theme_text_color: "Custom"
                            text_color: 0.678, 0.776, 1.0, 1
                            halign: "center"
                            valign: "center"

                    MDBoxLayout:
                        orientation: "vertical"
                        spacing: "2dp"
                        MDLabel:
                            text: "Ultimo parcheggio"
                            font_size: "16sp"
                            bold: True
                            theme_text_color: "Custom"
                            text_color: 0.894, 0.886, 0.894, 1
                        MDLabel:
                            id: time_label
                            text: ""
                            font_size: "12sp"
                            theme_text_color: "Custom"
                            text_color: 0.757, 0.776, 0.843, 1

                MDBoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    height: "22dp"
                    spacing: "8dp"

                    MDIcon:
                        icon: "map-marker"
                        font_size: "16sp"
                        theme_text_color: "Custom"
                        text_color: 0.678, 0.776, 1.0, 1

                    MDLabel:
                        id: address_label
                        text: "Nessun parcheggio salvato"
                        font_size: "14sp"
                        theme_text_color: "Custom"
                        text_color: 0.894, 0.886, 0.894, 1

                MDFlatButton:
                    id: navigate_btn
                    text: "PORTAMI QUI"
                    font_size: "12sp"
                    bold: True
                    size_hint_y: None
                    height: "44dp"
                    theme_text_color: "Custom"
                    text_color: 0.678, 0.776, 1.0, 1
                    md_bg_color: 0.208, 0.208, 0.216, 1
                    radius: [16, 16, 16, 16]
                    on_release: root.navigate_to_car()

        MDBottomNavigation:
            id: bottom_nav
            size_hint_y: None
            height: "72dp"
            md_bg_color: 0.122, 0.122, 0.129, 0.8
            panel_color: 0.122, 0.122, 0.129, 0.8
            selected_color: 0.678, 0.776, 1.0, 1
            unselected_color: 0.5, 0.5, 0.55, 1

            MDBottomNavigationItem:
                name: "home_tab"
                text: "Home"
                icon: "home"
                on_tab_press: root.go_home()

            MDBottomNavigationItem:
                name: "history_tab"
                text: "History"
                icon: "history"
                on_tab_press: root.go_to_history()

            MDBottomNavigationItem:
                name: "settings_tab"
                text: "Settings"
                icon: "cog"
                on_tab_press: root.go_to_settings()
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

        return super().on_touch_down(touch)

    def save_position(self):
        if not self.gps_service or not self.gps_service.has_fix():
            self._show_toast("GPS non disponibile")
            return

        pos = self.gps_service.get_position()
        if not pos:
            return

        lat, lon = pos
        address = ""
        if self.offline_localizer:
            pass

        record = self.storage_service.save_parking(lat, lon, address)
        Logger.info(f"HomeScreen: Saved parking #{record.id} at {lat:.4f}, {lon:.4f}")

        self.ids.save_icon.icon = "check-circle"
        self.ids.save_label.text = "SALVATO!"

        Clock.schedule_once(lambda dt: self._after_save(record), 1.5)

    def _after_save(self, record):
        self.ids.save_icon.icon = "map-marker-radius"
        self.ids.save_label.text = "SALVA POSIZIONE"

        details = self.manager.get_screen("details")
        details.load_record(record)
        self.manager.current = "details"

    def navigate_to_car(self):
        if self._has_parks:
            self.manager.current = "find"
        else:
            self._show_toast("Nessun parcheggio salvato")

    def go_home(self):
        pass

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
