from kivy.config import Config
Config.set("kivy", "window_icon", "")
Config.set("graphics", "width", "400")
Config.set("graphics", "height", "750")
Config.set("graphics", "resizable", False)
Config.set("input", "mouse", "mouse,multitouch_on_demand")
from kivy.core.window import Window
from kivy.logger import Logger
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.properties import StringProperty
from kivymd.app import MDApp
from kivymd.uix.navigationdrawer import MDNavigationDrawer
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.list import MDList
from kivy.uix.widget import Widget
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from .services.gps_service import GPSService
from .services.storage_service import StorageService
from .ai.offline_localizer import OfflineLocalizer
from .screens.home_screen import HomeScreen
from .screens.park_screen import ParkScreen
from .screens.find_screen import FindScreen
from .screens.history_screen import HistoryScreen
from .screens.details_screen import DetailsScreen
from .ui.compass_widget import CompassWidget
from .ui.map_widget import OfflineMapWidget
Builder.load_string("""
<DrawerItem>:
    spacing: "12dp"
    padding: "16dp"
    size_hint_y: None
    height: "56dp"
    IconLeftWidget:
        icon: root.icon
        theme_text_color: "Custom"
        text_color: 0.79, 0.82, 0.85, 1
    MDLabel:
        text: root.text
        font_size: "15sp"
        theme_text_color: "Custom"
        text_color: 0.79, 0.82, 0.85, 1
""")
class DrawerItem(MDBoxLayout):
    icon = StringProperty("")
    text = StringProperty("")
    def __init__(self, icon="", text="", on_press=None, **kwargs):
        super().__init__(icon=icon, text=text, **kwargs)
        self._on_press = on_press
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if self._on_press:
                self._on_press()
            return True
        return super().on_touch_down(touch)
class FindMyCarApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.gps_service = GPSService()
        self.storage_service = StorageService()
        self.offline_localizer = OfflineLocalizer()
        self.nav_drawer = None
        self.screen_manager = None
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Indigo"
        self.theme_cls.accent_palette = "Cyan"
        self.theme_cls.material_style = "M3"
        self.theme_cls.primary_color = (0.678, 0.776, 1.0, 1)
        Window.clearcolor = (0.075, 0.075, 0.082, 1)
        from kivymd.uix.navigationdrawer import MDNavigationLayout
        root = MDNavigationLayout()
        self.screen_manager = ScreenManager(
            transition=SlideTransition(duration=0.2)
        )
        self.screen_manager.add_widget(HomeScreen(name="home"))
        self.screen_manager.add_widget(ParkScreen(name="park"))
        self.screen_manager.add_widget(FindScreen(name="find"))
        self.screen_manager.add_widget(HistoryScreen(name="history"))
        self.screen_manager.add_widget(DetailsScreen(name="details"))
        nav = MDNavigationDrawer(
            md_bg_color=(0.07, 0.08, 0.11, 1),
            radius=(0, 16, 16, 0),
        )
        drawer_content = MDBoxLayout(
            orientation="vertical",
            spacing="8dp",
            padding="16dp",
        )
        header = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height="160dp",
            padding="12dp",
            spacing="8dp",
        )
        from kivymd.uix.label import MDLabel, MDIcon
        from kivymd.uix.scrollview import MDScrollView
        icon_w = MDIcon(
            icon="map-marker-radius",
            font_size="48sp",
            theme_text_color="Custom",
            text_color=(0.0, 0.898, 1.0, 1),
            halign="left",
        )
        title_lbl = MDLabel(
            text="FindMyCar",
            font_size="22sp",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            bold=True,
        )
        version_lbl = MDLabel(
            text="v1.0.0",
            font_size="12sp",
            theme_text_color="Custom",
            text_color=(0.4, 0.42, 0.45, 1),
        )
        header.add_widget(icon_w)
        header.add_widget(title_lbl)
        header.add_widget(version_lbl)
        separator = Widget(size_hint_y=None, height="1dp")
        scroll = MDScrollView()
        self.drawer_list = MDList(spacing="4dp")
        items = [
            ("map-marker-radius", "Home", "home"),
            ("parking", "Parcheggia", "park"),
            ("navigation", "Trova Auto", "find"),
            ("history", "Cronologia", "history"),
            ("info", "Dettagli", "details"),
        ]
        for icon_name, text, screen_name in items:
            item = DrawerItem(
                icon=icon_name,
                text=text,
                on_press=lambda s=screen_name: self._navigate_to(s),
            )
            self.drawer_list.add_widget(item)
        scroll.add_widget(self.drawer_list)
        drawer_content.add_widget(header)
        drawer_content.add_widget(separator)
        drawer_content.add_widget(scroll)
        nav.add_widget(drawer_content)
        root.add_widget(self.screen_manager)
        root.add_widget(nav)
        self.nav_drawer = nav
        Clock.schedule_once(lambda dt: self._start_gps(), 0.5)
        return root
    def _start_gps(self):
        try:
            self.gps_service.start()
            Logger.info("App: GPS started")
        except Exception as e:
            Logger.warning(f"App: GPS start failed - {e}")
    def _navigate_to(self, screen_name):
        if self.nav_drawer:
            self.nav_drawer.set_state("close")
        if self.screen_manager and self.screen_manager.has_screen(screen_name):
            self.screen_manager.current = screen_name
            screen = self.screen_manager.get_screen(screen_name)
            if hasattr(screen, "on_enter"):
                screen.dispatch("on_enter")
    def on_stop(self):
        try:
            self.gps_service.stop()
        except:
            pass
        Logger.info("App: Stopped")