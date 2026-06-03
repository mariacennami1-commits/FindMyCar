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
    height: "200dp"
    padding: "4dp"

    MDBoxLayout:
        orientation: "vertical"
        padding: "16dp"
        spacing: "8dp"
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

        MDBoxLayout:
            orientation: "horizontal"
            size_hint_y: None
            height: "24dp"

            MDLabel:
                id: date_label
                text: root.date_text
                font_size: "11sp"
                bold: True
                theme_text_color: "Custom"
                text_color: 0.678, 0.776, 1.0, 1
                letter_spacing: 2

            MDIconButton:
                icon: "delete"
                theme_text_color: "Custom"
                text_color: 1, 0.706, 0.671, 1
                size_hint: None, None
                size: "36dp", "36dp"
                on_release: root.delete_self()

        MDLabel:
            id: address_label
            text: root.address_label
            font_size: "17sp"
            bold: True
            theme_text_color: "Custom"
            text_color: 0.894, 0.886, 0.894, 1

        MDLabel:
            id: location_label
            text: root.coords_label
            font_size: "13sp"
            theme_text_color: "Custom"
            text_color: 0.757, 0.776, 0.843, 1

        RelativeLayout:
            size_hint_y: None
            height: "80dp"
            canvas.before:
                Color:
                    rgba: 0.05, 0.05, 0.06, 0.5
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [12, 12, 12, 12]

            BoxLayout:
                orientation: "horizontal"
                pos_hint: {"center_x": 0.5, "center_y": 0.5}
                spacing: "12dp"

                MDIcon:
                    icon: "map-marker"
                    font_size: "32sp"
                    theme_text_color: "Custom"
                    text_color: 0.678, 0.776, 1.0, 1

                MDLabel:
                    text: root.distance_label
                    font_size: "14sp"
                    theme_text_color: "Custom"
                    text_color: 0.894, 0.886, 0.894, 1
                    valign: "middle"


<HistoryScreen>:
    canvas.before:
        Color:
            rgba: 0.075, 0.075, 0.082, 1
        Rectangle:
            pos: self.pos
            size: self.size

    BoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "Cronologia"
            md_bg_color: 0.075, 0.075, 0.082, 1
            specific_text_color: 0.678, 0.776, 1.0, 1
            elevation: 0
            left_action_items: [["arrow-left", lambda x: root.go_back()]]
            right_action_items: [["delete-sweep", lambda x: root.clear_history(), "Pulisci"]]

        MDTextField:
            id: search_input
            hint_text: "Cerca parcheggio..."
            mode: "fill"
            fill_color: 0.12, 0.12, 0.13, 1
            line_color_focus: 0.678, 0.776, 1.0, 1
            text_color_focus: 0.894, 0.886, 0.894, 1
            hint_text_color: 0.5, 0.52, 0.55, 1
            size_hint_y: None
            height: "56dp"
            padding: "0dp", "0dp", "0dp", "0dp"

        MDScrollView:
            id: scroll_view

            MDBoxLayout:
                id: list_container
                orientation: "vertical"
                size_hint_y: None
                padding: ["12dp", "8dp", "12dp", "8dp"]
                spacing: "8dp"

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


class HistoryItem(MDBoxLayout):
    address_label = StringProperty("")
    coords_label = StringProperty("")
    time_label = StringProperty("")
    date_text = StringProperty("")
    distance_label = StringProperty("")
    _record = None

    def __init__(self, record, gps_service=None, **kwargs):
        super().__init__(**kwargs)
        self._record = record
        self.gps_service = gps_service
        self.address_label = record.address or f"Parcheggio #{record.id}"
        self.coords_label = f"{record.latitude:.6f}, {record.longitude:.6f}"

        try:
            ts = datetime.fromisoformat(record.timestamp)
            now = datetime.now()
            if ts.date() == now.date():
                self.date_text = "Oggi, " + ts.strftime("%H:%M")
            else:
                delta = (now.date() - ts.date()).days
                if delta == 1:
                    self.date_text = "Ieri, " + ts.strftime("%H:%M")
                else:
                    self.date_text = ts.strftime("%d/%m/%Y, %H:%M")
        except:
            self.date_text = record.timestamp

        if self.gps_service and self.gps_service.has_fix():
            pos = self.gps_service.get_position()
            if pos:
                dist = NavigationService.distance_meters(
                    pos[0], pos[1], record.latitude, record.longitude
                )
                self.distance_label = NavigationService.distance_string(dist)

    def delete_self(self):
        try:
            from kivy.app import App
            app = App.get_running_app()
            if app and hasattr(app, "storage_service"):
                app.storage_service.delete(self._record.id)
                screen = app.screen_manager.get_screen("history")
                screen._populate_list()
        except:
            pass

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

    def go_home(self):
        self.manager.current = "home"

    def go_to_history(self):
        pass

    def go_to_settings(self):
        from kivymd.uix.snackbar import Snackbar
        Snackbar(text="Impostazioni in arrivo", duration=2).open()

    def go_back(self):
        self.manager.current = "home"
