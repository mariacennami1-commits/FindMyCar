import math
from kivy.clock import Clock
from kivy.properties import StringProperty, NumericProperty, BooleanProperty
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.logger import Logger
from ..services.navigation_service import NavigationService
from ..ui.compass_widget import CompassWidget

Builder.load_string("""
<FindScreen>:
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
            left_action_items: [["arrow-left", lambda x: root.go_back()]]
            right_action_items: [["refresh", lambda x: root.refresh_data(), "Aggiorna"]]

        RelativeLayout:
            size_hint_y: 0.55

            BoxLayout:
                orientation: "vertical"
                pos_hint: {"center_x": 0.5, "center_y": 0.5}
                size_hint: 0.8, 0.8

                CompassWidget:
                    id: compass
                    pos_hint: {"center_x": 0.5, "center_y": 0.5}
                    size_hint: 0.7, 0.7

                MDLabel:
                    text: root.direction_label
                    font_size: "14sp"
                    theme_text_color: "Custom"
                    text_color: 0.678, 0.776, 1.0, 1
                    halign: "center"
                    pos_hint: {"center_x": 0.5, "y": 0.05}

        BoxLayout:
            orientation: "vertical"
            size_hint_y: 0.45
            padding: ["20dp", "16dp", "20dp", "16dp"]
            spacing: "12dp"

            MDLabel:
                id: address_label
                text: root.address_text
                font_size: "17sp"
                bold: True
                theme_text_color: "Custom"
                text_color: 0.894, 0.886, 0.894, 1

            MDLabel:
                text: root.car_position_text
                font_size: "13sp"
                theme_text_color: "Custom"
                text_color: 0.757, 0.776, 0.843, 1

            BoxLayout:
                orientation: "horizontal"
                size_hint_y: None
                height: "80dp"
                spacing: "12dp"

                BoxLayout:
                    orientation: "vertical"
                    padding: "12dp"
                    spacing: "4dp"
                    canvas.before:
                        Color:
                            rgba: 0.11, 0.11, 0.118, 0.8
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [12, 12, 12, 12]

                    MDIcon:
                        icon: "map-marker-distance"
                        font_size: "20sp"
                        theme_text_color: "Custom"
                        text_color: 0.678, 0.776, 1.0, 1
                        halign: "center"

                    MDLabel:
                        text: root.distance_text
                        font_size: "22sp"
                        theme_text_color: "Custom"
                        text_color: 0.894, 0.886, 0.894, 1
                        halign: "center"
                        bold: True

                    MDLabel:
                        text: "distanza"
                        font_size: "11sp"
                        theme_text_color: "Custom"
                        text_color: 0.5, 0.52, 0.55, 1
                        halign: "center"

                BoxLayout:
                    orientation: "vertical"
                    padding: "12dp"
                    spacing: "4dp"
                    canvas.before:
                        Color:
                            rgba: 0.11, 0.11, 0.118, 0.8
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [12, 12, 12, 12]

                    MDIcon:
                        icon: "walk"
                        font_size: "20sp"
                        theme_text_color: "Custom"
                        text_color: 0.678, 0.776, 1.0, 1
                        halign: "center"

                    MDLabel:
                        text: root.time_text
                        font_size: "22sp"
                        theme_text_color: "Custom"
                        text_color: 0.894, 0.886, 0.894, 1
                        halign: "center"
                        bold: True

                    MDLabel:
                        text: "a piedi"
                        font_size: "11sp"
                        theme_text_color: "Custom"
                        text_color: 0.5, 0.52, 0.55, 1
                        halign: "center"

            MDFlatButton:
                text: "AVVIA NAVIGAZIONE"
                font_size: "16sp"
                bold: True
                size_hint_y: None
                height: "56dp"
                theme_text_color: "Custom"
                text_color: 0.894, 0.886, 0.894, 1
                md_bg_color: 0.294, 0.557, 1.0, 1
                radius: [28, 28, 28, 28]
                on_release: root.start_navigation()
""")


class FindScreen(Screen):
    distance_text = StringProperty("---")
    time_text = StringProperty("---")
    direction_label = StringProperty("---")
    status_text = StringProperty("GPS")
    car_position_text = StringProperty("Auto non salvata")
    address_text = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.gps_service = None
        self.storage_service = None
        self.offline_localizer = None
        self._update_clock = None
        self._gps_listener_active = False
        self._parked_lat = None
        self._parked_lon = None
        self._no_parking = True

    def on_enter(self):
        try:
            app = self._get_app()
            if not app:
                return

            self.gps_service = app.gps_service
            self.storage_service = app.storage_service
            self.offline_localizer = app.offline_localizer

            latest = self.storage_service.get_latest()
            if latest:
                self._parked_lat = latest.latitude
                self._parked_lon = latest.longitude
                self._no_parking = False
                self.address_text = latest.address or f"{latest.latitude:.4f}, {latest.longitude:.4f}"
                self.car_position_text = f"Auto: {latest.latitude:.4f}, {latest.longitude:.4f}"
            else:
                self._no_parking = True
                self.car_position_text = "Nessuna auto parcheggiata salvata"
                self.address_text = ""

            if self.gps_service:
                self._gps_listener_active = True
                try:
                    self.gps_service.add_listener(self._on_gps_update)
                except Exception as e:
                    Logger.error(f"FindScreen: add_listener error - {e}")
                self._update_clock = Clock.schedule_interval(self._update_navigation, 0.5)

                if self.gps_service.has_fix():
                    pos = self.gps_service.get_position()
                    if pos:
                        self._on_position(pos[0], pos[1])
            else:
                Logger.warning("FindScreen: gps_service is None")
        except Exception as e:
            Logger.error(f"FindScreen: on_enter error - {e}")
            import traceback
            Logger.error(f"FindScreen: {traceback.format_exc()}")

    def on_leave(self):
        try:
            self._gps_listener_active = False
            if self.gps_service:
                try:
                    self.gps_service.remove_listener(self._on_gps_update)
                except Exception as e:
                    Logger.error(f"FindScreen: remove_listener error - {e}")
            if self._update_clock:
                self._update_clock.cancel()
                self._update_clock = None
        except Exception as e:
            Logger.error(f"FindScreen: on_leave error - {e}")

    def _get_app(self):
        try:
            from kivy.app import App
            return App.get_running_app()
        except:
            return None

    def _on_gps_update(self, gps_svc):
        if not self._gps_listener_active:
            return
        try:
            pos = gps_svc.get_position()
            if pos:
                self._on_position(pos[0], pos[1])
        except Exception as e:
            Logger.error(f"FindScreen: gps_update error - {e}")

    def _on_position(self, lat, lon):
        try:
            if self._no_parking or lat is None or lon is None:
                return

            dist = NavigationService.distance_meters(
                lat, lon, self._parked_lat, self._parked_lon
            )
            bearing_to_car = NavigationService.bearing(
                lat, lon, self._parked_lat, self._parked_lon
            )

            self.distance_text = NavigationService.distance_string(dist)
            self.time_text = NavigationService.time_estimate(dist)
            self.direction_label = f"{NavigationService.direction_label(bearing_to_car)} ({bearing_to_car:.0f}°)"

            if self.gps_service:
                current_heading = self.gps_service.bearing or 0
                try:
                    compass = self.ids.compass
                    compass.target_bearing = bearing_to_car
                    compass.bearing = current_heading
                except (AttributeError, KeyError):
                    pass
        except Exception as e:
            Logger.error(f"FindScreen: on_position error - {e}")

    def _update_navigation(self, dt):
        try:
            if self._no_parking or not self.gps_service:
                return

            pos = self.gps_service.get_position()
            if not pos:
                if self.offline_localizer:
                    try:
                        offline_pos, mode = self.offline_localizer.get_position()
                        if offline_pos:
                            self._on_position(offline_pos[0], offline_pos[1])
                    except Exception as e:
                        Logger.error(f"FindScreen: offline localizer error - {e}")
                return

            self._on_position(pos[0], pos[1])
        except Exception as e:
            Logger.error(f"FindScreen: update_navigation error - {e}")

    def refresh_data(self):
        try:
            self.on_enter()
        except Exception as e:
            Logger.error(f"FindScreen: refresh_data error - {e}")

    def start_navigation(self):
        try:
            if self._no_parking:
                self.direction_label = "Nessuna auto salvata!"
                return

            if not self.gps_service:
                self.direction_label = "GPS non disponibile"
                return

            if not self.gps_service.has_fix():
                self.direction_label = "GPS in aggancio..."
                return

            pos = self.gps_service.get_position()
            if not pos:
                self.direction_label = "Posizione non disponibile"
                return

            dist = NavigationService.distance_meters(
                pos[0], pos[1], self._parked_lat, self._parked_lon
            )
            bearing = NavigationService.bearing(
                pos[0], pos[1], self._parked_lat, self._parked_lon
            )

            direction = NavigationService.direction_label(bearing)
            msg = (
                f"{direction} · {NavigationService.distance_string(dist)} · "
                f"{NavigationService.time_estimate(dist)}"
            )
            self.direction_label = msg
        except Exception as e:
            Logger.error(f"FindScreen: Navigation error - {e}")
            import traceback
            Logger.error(f"FindScreen: {traceback.format_exc()}")
            self.direction_label = "Errore navigazione"

    def go_back(self):
        try:
            self.manager.current = "home"
        except Exception as e:
            Logger.error(f"FindScreen: go_back error - {e}")
