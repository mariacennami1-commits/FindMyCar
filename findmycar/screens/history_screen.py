import os
from datetime import datetime
from kivy.clock import Clock
from kivy.properties import StringProperty, NumericProperty, ListProperty
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.logger import Logger
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from ..services.navigation_service import NavigationService

Builder.load_string("""
<HistoryItem>:
    size_hint_y: None
    height: "80dp"
    padding: "4dp"

    MDCard:
        orientation: "horizontal"
        md_bg_color: 0.09, 0.1, 0.13, 1
        radius: [16, 16, 16, 16]
        padding: "12dp"
        spacing: "12dp"
        elevation: 2

        MDBoxLayout:
            orientation: "vertical"
            size_hint_x: 0.15
            halign: "center"

            MDIcon:
                icon: "map-marker"
                font_size: "28sp"
                theme_text_color: "Custom"
                text_color: 0.0, 0.898, 1.0, 1
                halign: "center"

        MDBoxLayout:
            orientation: "vertical"
            size_hint_x: 0.6
            spacing: "2dp"

            MDLabel:
                text: root.address_label
                font_size: "13sp"
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1
                bold: True
                shorten: True

            MDLabel:
                text: root.coords_label
                font_size: "11sp"
                theme_text_color: "Custom"
                text_color: 0.5, 0.52, 0.55, 1

            MDLabel:
                text: root.time_label
                font_size: "11sp"
                theme_text_color: "Custom"
                text_color: 0.4, 0.42, 0.45, 1

        MDRelativeLayout:
            size_hint_x: 0.25

            MDIconButton:
                icon: "navigation"
                theme_text_color: "Custom"
                text_color: 0.0, 0.898, 1.0, 1
                pos_hint: {"center_x": 0.5, "center_y": 0.6}
                on_release: root.navigate_to()

            MDLabel:
                text: root.distance_label
                font_size: "10sp"
                theme_text_color: "Custom"
                text_color: 0.3, 0.32, 0.35, 1
                halign: "center"
                pos_hint: {"center_y": 0.15}


<HistoryScreen>:
    MDBoxLayout:
        orientation: "vertical"
        md_bg_color: 0.05, 0.07, 0.09, 1

        MDTopAppBar:
            title: "Cronologia"
            md_bg_color: 0.05, 0.07, 0.09, 1
            specific_text_color: 1, 1, 1, 1
            left_action_items: [["arrow-left", lambda x: root.go_back(), "Indietro"]]
            right_action_items: [["delete-sweep", lambda x: root.clear_history(), "Cancella"]]

        MDScrollView:
            id: scroll_view

            MDBoxLayout:
                id: list_container
                orientation: "vertical"
                size_hint_y: None
                padding: ["12dp", "8dp", "12dp", "8dp"]
                spacing: "4dp"

        MDBoxLayout:
            orientation: "vertical"
            size_hint_y: 0.08
            padding: ["24dp", "0dp", "24dp", "12dp"]

            MDRoundFlatIconButton:
                id: back_btn
                text: "Torna alla Mappa"
                icon: "arrow-left"
                font_size: "14sp"
                size_hint_x: 1
                theme_text_color: "Custom"
                text_color: 0.0, 0.898, 1.0, 1
                line_color: 0.0, 0.4, 0.6, 1
                radius: [28, 28, 28, 28]
                on_release: root.go_back()
""")


class HistoryItem(MDBoxLayout):
    address_label = StringProperty("")
    coords_label = StringProperty("")
    time_label = StringProperty("")
    distance_label = StringProperty("")
    _record = None

    def __init__(self, record, gps_service=None, **kwargs):
        super().__init__(**kwargs)
        self._record = record
        self.gps_service = gps_service
        self.address_label = record.notes or f"Parcheggio #{record.id}"
        self.coords_label = f"{record.latitude:.6f}, {record.longitude:.6f}"

        try:
            ts = datetime.fromisoformat(record.timestamp)
            self.time_label = ts.strftime("%d/%m/%Y %H:%M")
        except:
            self.time_label = record.timestamp

        if self.gps_service and self.gps_service.has_fix():
            pos = self.gps_service.get_position()
            if pos:
                dist = NavigationService.distance_meters(
                    pos[0], pos[1], record.latitude, record.longitude
                )
                self.distance_label = NavigationService.distance_string(dist)

    def navigate_to(self):
        screen_manager = None
        parent = self.parent
        while parent:
            if hasattr(parent, "current"):
                screen_manager = parent
                break
            parent = parent.parent

        if screen_manager:
            find_screen = screen_manager.get_screen("find")
            find_screen._parked_lat = self._record.latitude
            find_screen._parked_lon = self._record.longitude
            find_screen._no_parking = False
            find_screen.car_position_text = f"Auto: {self._record.latitude:.4f}, {self._record.longitude:.4f}"
            find_screen.on_enter()
            screen_manager.current = "find"


class HistoryScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.gps_service = None
        self.storage_service = None

    def on_enter(self):
        Clock.schedule_once(self._setup, 0.1)

    def _setup(self, dt):
        app = self._get_app()
        if not app:
            return
        self.gps_service = app.gps_service
        self.storage_service = app.storage_service
        self._populate_list()

    def _get_app(self):
        try:
            from kivy.app import App
            return App.get_running_app()
        except:
            return None

    def _populate_list(self):
        container = self.ids.list_container
        container.clear_widgets()

        records = self.storage_service.get_all()
        if not records:
            container.add_widget(
                MDBoxLayout(
                    orientation="vertical",
                    size_hint_y=None,
                    height=dp(200),
                    adaptive_height=True,
                )
            )
            lbl = MDLabel(
                text="Nessun parcheggio salvato",
                font_size="16sp",
                halign="center",
                theme_text_color="Custom",
                text_color=(0.5, 0.52, 0.55, 1),
                pos_hint={"center_y": 0.5},
            )
            container.add_widget(lbl)
            return

        for record in records:
            item = HistoryItem(record, self.gps_service)
            container.add_widget(item)

    def clear_history(self):
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.button import MDRaisedButton

        dialog = MDDialog(
            title="Cancella cronologia",
            text="Eliminare tutti i parcheggi salvati?",
            buttons=[
                MDRaisedButton(
                    text="Annulla",
                    on_release=lambda x: dialog.dismiss(),
                ),
                MDRaisedButton(
                    text="Cancella",
                    on_release=lambda x: (
                        self.storage_service.clear_all(),
                        dialog.dismiss(),
                        self._populate_list(),
                    ),
                ),
            ],
        )
        dialog.open()

    def go_back(self):
        self.manager.current = "home"
