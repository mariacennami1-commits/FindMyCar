from kivy.clock import Clock
from kivy.properties import StringProperty, NumericProperty, BooleanProperty
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.logger import Logger
from ..ui.map_widget import OfflineMapWidget

Builder.load_string("""
<HomeScreen>:
    MDBoxLayout:
        orientation: "vertical"
        md_bg_color: 0.05, 0.07, 0.09, 1

        MDTopAppBar:
            title: "FindMyCar"
            md_bg_color: 0.05, 0.07, 0.09, 1
            specific_text_color: 1, 1, 1, 1
            left_action_items: [["menu", lambda x: root.open_nav_drawer(), "Menu"]]
            right_action_items: [["crosshairs-gps", lambda x: root.center_on_me(), "Centra"]]

        MDRelativeLayout:

            OfflineMapWidget:
                id: map_widget
                pos_hint: {"x": 0, "y": 0}
                size_hint: 1, 1

            MDBoxLayout:
                orientation: "vertical"
                adaptive_size: True
                pos_hint: {"center_x": 0.5, "y": 0.02}
                spacing: "4dp"

                MDCard:
                    orientation: "vertical"
                    size_hint_x: 0.9
                    pos_hint: {"center_x": 0.5}
                    md_bg_color: 0.09, 0.1, 0.13, 0.95
                    radius: [12, 12, 12, 12]
                    padding: "12dp"
                    spacing: "4dp"

                    MDLabel:
                        text: root.status_text
                        font_size: "11sp"
                        theme_text_color: "Custom"
                        text_color: 0.0, 0.898, 1.0, 1
                        halign: "center"

                    MDLabel:
                        text: root.address_text
                        font_size: "13sp"
                        theme_text_color: "Custom"
                        text_color: 0.79, 0.82, 0.85, 1
                        halign: "center"
                        shorten: True
                        shorten_from: "right"

                MDRoundFlatIconButton:
                    text: "Parcheggia Qui"
                    icon: "parking"
                    font_size: "16sp"
                    size_hint_x: 0.9
                    pos_hint: {"center_x": 0.5}
                    theme_text_color: "Custom"
                    text_color: 0, 0, 0, 1
                    md_bg_color: 0.0, 0.898, 1.0, 1
                    line_color: 0, 0, 0, 0
                    radius: [28, 28, 28, 28]
                    on_release: root.go_to_park()

            MDFloatingActionButton:
                icon: "navigation"
                md_bg_color: 0.1, 0.13, 0.2, 0.9
                theme_text_color: "Custom"
                text_color: 0.0, 0.898, 1.0, 1
                pos_hint: {"right": 0.95, "y": 0.12}
                on_release: root.go_to_find()
""")


class HomeScreen(Screen):
    status_text = StringProperty("Inizializzazione...")
    address_text = StringProperty("Attivazione GPS in corso")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.gps_service = None
        self.storage_service = None
        self.offline_localizer = None
        self._update_clock = None

    def on_enter(self):
        Clock.schedule_once(self._setup, 0.1)

    def on_leave(self):
        if self._update_clock:
            self._update_clock.cancel()

    def _setup(self, dt):
        app = self._get_app()
        if not app:
            return

        self.gps_service = app.gps_service
        self.storage_service = app.storage_service
        self.offline_localizer = app.offline_localizer

        map_widget = self.ids.map_widget

        self.gps_service.add_listener(self._on_gps_update)
        self._update_clock = Clock.schedule_interval(self._periodic_update, 1.0)

        if self.gps_service.has_fix():
            pos = self.gps_service.get_position()
            if pos:
                map_widget.set_current_position(pos[0], pos[1])
                self.status_text = "GPS attivo"

        latest = self.storage_service.get_latest()
        if latest:
            map_widget.set_parked_position(latest.latitude, latest.longitude)

    def _get_app(self):
        try:
            from kivy.app import App
            return App.get_running_app()
        except:
            return None

    def _on_gps_update(self, gps_svc):
        if not self.gps_service:
            return
        pos = self.gps_service.get_position()
        if pos:
            map_widget = self.ids.map_widget
            map_widget.set_current_position(pos[0], pos[1])
            self.status_text = f"GPS · {self.gps_service.accuracy:.0f}m"

    def _periodic_update(self, dt):
        if not self.offline_localizer:
            return

        status = self.offline_localizer.get_status_text()
        if status != "GPS":
            self.status_text = status

        map_widget = self.ids.map_widget
        if not map_widget.current_lat and self.gps_service and self.gps_service.has_fix():
            pos = self.gps_service.get_position()
            if pos:
                map_widget.set_current_position(pos[0], pos[1])

    def center_on_me(self):
        if self.gps_service and self.gps_service.has_fix():
            pos = self.gps_service.get_position()
            if pos:
                self.ids.map_widget.set_current_position(pos[0], pos[1])
                self.status_text = "Centrato"

    def go_to_park(self):
        self.manager.current = "park"

    def go_to_find(self):
        self.manager.current = "find"

    def open_nav_drawer(self):
        app = self._get_app()
        if app and hasattr(app, "nav_drawer"):
            app.nav_drawer.set_state("open")
