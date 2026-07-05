import traceback
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
from kivy.uix.screenmanager import ScreenManager, NoTransition
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
from .screens.map_screen import MapScreen
from .screens.park_screen import ParkScreen
from .screens.find_screen import FindScreen
from .screens.history_screen import HistoryScreen
from .screens.details_screen import DetailsScreen
from .ui.compass_widget import CompassWidget
from .webview_bridge import WebViewBridge

_APP_VERSION = "1.0.112"
_CRASH_LOG = None
Builder.load_string("""
<DrawerItem>:
    spacing: "8dp"
    padding: "12dp", 0, "12dp", 0
    size_hint_y: None
    height: "52dp"
    IconLeftWidget:
        icon: root.icon
        theme_text_color: "Custom"
        text_color: 0.79, 0.82, 0.85, 1
    MDLabel:
        text: root.text
        font_size: "14sp"
        theme_text_color: "Custom"
        text_color: 0.79, 0.82, 0.85, 1
        text_size: self.width, None
        shorten: True
        valign: "middle"
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
def _write_crash_log(msg):
    global _CRASH_LOG
    _CRASH_LOG = msg
    try:
        path = "/sdcard/findmycar_crash.txt"
        with open(path, "w") as f:
            f.write(msg + "\n")
        Logger.error(f"Crash log written to {path}")
    except:
        try:
            path = os.path.join(os.path.expanduser("~"), "findmycar_crash.txt")
            with open(path, "w") as f:
                f.write(msg + "\n")
        except:
            pass

class FindMyCarApp(MDApp):
    VERSION = _APP_VERSION

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.gps_service = GPSService()
        self.storage_service = StorageService()
        self.offline_localizer = OfflineLocalizer()
        self.webview_bridge = WebViewBridge()
        self.nav_drawer = None
        self.screen_manager = None

    def build(self):
        try:
            return self._build()
        except Exception as e:
            tb = traceback.format_exc()
            msg = f"FINDMYCAR CRASH:\nVersion: {self.VERSION}\nError: {e}\n\n{tb}"
            Logger.error(msg)
            _write_crash_log(msg)
            from kivymd.uix.boxlayout import MDBoxLayout as BL
            from kivymd.uix.label import MDLabel as ML
            box = BL(orientation="vertical", padding="20dp", spacing="10dp")
            box.add_widget(ML(
                text=f"ERRORE AVVIO",
                font_size="18sp",
                theme_text_color="Custom",
                text_color=(1, 0.3, 0.3, 1),
                halign="center",
            ))
            box.add_widget(ML(
                text=str(e)[:200],
                font_size="14sp",
                theme_text_color="Custom",
                text_color=(1, 0.6, 0.6, 1),
                halign="center",
            ))
            return box

    def _build(self):
        self.theme_cls.theme_style = "Dark"
        from kivymd.uix.navigationdrawer import MDNavigationLayout
        root = MDNavigationLayout()
        self.screen_manager = ScreenManager(
            transition=NoTransition()
        )
        self.screen_manager.add_widget(MapScreen(name="home"))
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
            text=f"v{self.VERSION}",
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
            ("update", "Verifica aggiornamenti", None),
        ]
        for icon_name, text, screen_name in items:
            if screen_name is None:
                item = DrawerItem(
                    icon=icon_name,
                    text=text,
                    on_press=lambda: self.check_for_updates(),
                )
            else:
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
        self.nav_drawer.bind(state=self._on_drawer_state)
        Clock.schedule_once(lambda dt: self._start_gps(), 0.5)
        Clock.schedule_once(lambda dt: self._init_webview(), 0.8)
        Clock.schedule_once(lambda dt: self._check_updates_background(), 3)
        Clock.schedule_once(lambda dt: self._set_window_bg(), 0.3)
        Logger.info("App: _build returning")
        return root
    def _set_window_bg(self):
        try:
            Window.clearcolor = (0.075, 0.075, 0.082, 1)
            Logger.info("App: Window background set")
        except Exception as e:
            Logger.warning("App: Window bg error - " + str(e))

    def _refocus_activity(self):
        try:
            from kivy.utils import platform
            if platform != "android":
                return
            from jnius import autoclass
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            activity = PythonActivity.mActivity
            if activity.isFinishing() or not activity.hasWindowFocus():
                Intent = autoclass("android.content.Intent")
                intent = Intent(activity, activity.getClass())
                intent.addFlags(Intent.FLAG_ACTIVITY_REORDER_TO_FRONT | Intent.FLAG_ACTIVITY_NEW_TASK)
                activity.startActivity(intent)
                Logger.info("App: Refocused activity")
        except Exception as e:
            Logger.warning("App: Refocus error - " + str(e))

    def _init_webview(self):
        try:
            self.webview_bridge.setup(callback=self._on_map_callback)
            Logger.info("App: WebView bridge initialized")
            self.gps_service.add_listener(self._on_gps_update)
            Clock.schedule_once(lambda dt: self._ensure_map_visible(), 0.5)
        except Exception as e:
            Logger.warning("App: WebView init failed - " + str(e))

    def _on_gps_update(self, gps_service):
        lat = gps_service.latitude
        lng = gps_service.longitude
        if lat is None or lng is None:
            return
        acc = gps_service.accuracy or 10
        bearing = gps_service.bearing or 0
        js = f"updatePosition({lat}, {lng}, {acc}, {bearing})"
        self.webview_bridge.send_js(js)
    def _on_drawer_state(self, instance, state):
        if state == "close":
            Clock.schedule_once(lambda dt: self._ensure_map_visible(), 0.05)
    def _ensure_map_visible(self):
        if not self.screen_manager:
            Logger.warning("App: _ensure_map_visible - no screen manager")
            return
        if self.screen_manager.current != "home":
            Logger.warning("App: _ensure_map_visible - current is " + str(self.screen_manager.current))
            return
        if not self.webview_bridge._webview:
            Logger.warning("App: _ensure_map_visible - webview not ready, retrying")
            Clock.schedule_once(lambda dt: self._ensure_map_visible(), 0.3)
            return
        try:
            self.webview_bridge.show()
            screen = self.screen_manager.get_screen("home")
            if screen and hasattr(screen, "on_enter"):
                screen.dispatch("on_enter")
            Logger.info("App: _ensure_map_visible done")
        except Exception as e:
            Logger.warning("App: _ensure_map_visible error: " + str(e))
    def _on_map_callback(self, event, data):
        Logger.info("App: Map callback event=" + str(event) + " data=" + str(data))
        if event == "save":
            self._save_from_map()
        elif event == "navigate":
            if data and self.screen_manager and self.screen_manager.has_screen(data):
                self.screen_manager.current = data
                screen = self.screen_manager.get_screen(data)
                if hasattr(screen, "on_enter"):
                    screen.dispatch("on_enter")
        elif event == "open_drawer":
            if self.nav_drawer:
                self._close_map_for_drawer()
                self.nav_drawer.set_state("open")
        elif event == "toast":
            self._show_snackbar(str(data))
    def _close_map_for_drawer(self):
        Logger.info("App: close map for drawer")
        try:
            self.webview_bridge.hide()
            Logger.info("App: webview hidden for drawer")
        except Exception as e:
            Logger.error("App: close map error - " + str(e))
    def _save_from_map(self):
        try:
            pos = self.gps_service.get_position()
            if not pos:
                self._show_snackbar("GPS non disponibile")
                self.webview_bridge.send_js("showToast('GPS non disponibile')")
                return
            record = self.storage_service.save_parking(pos[0], pos[1], "")
            Logger.info("App: Saved from map #" + str(record.id))
            self.webview_bridge.send_js("onSaved()")
            addr = record.address or f"{pos[0]:.4f}, {pos[1]:.4f}"
            from datetime import datetime
            now = datetime.now()
            time_str = "Oggi " + now.strftime("%H:%M")
            js = (
                "updateCarParked("
                + str(pos[0]) + ","
                + str(pos[1]) + ","
                + '"' + str(addr).replace("\\", "\\\\").replace('"', '\\"') + '",'
                + '"' + time_str + '"'
                + ")"
            )
            self.webview_bridge.send_js(js)
        except Exception as e:
            Logger.error("App: Save from map error - " + str(e))
    def _start_gps(self):
        try:
            from kivy.utils import platform
            if platform == "android":
                from android.permissions import request_permissions, Permission
                request_permissions(
                    [Permission.ACCESS_FINE_LOCATION, Permission.ACCESS_COARSE_LOCATION],
                    callback=self._on_location_permission,
                )
            else:
                self.gps_service.start()
                Logger.info("App: GPS started")
        except Exception as e:
            Logger.warning(f"App: GPS start failed - {e}")

    def _on_location_permission(self, permissions, grant_results):
        if len(grant_results) > 0 and all(r for r in grant_results):
            Logger.info("App: Location permission granted")
            self.gps_service.start()
            Logger.info("App: GPS started")
        else:
            Logger.warning("App: Location permission denied")
            self._show_snackbar("Permesso GPS negato")
    def _navigate_to(self, screen_name):
        if self.nav_drawer:
            self.nav_drawer.set_state("close")
        if self.screen_manager and self.screen_manager.has_screen(screen_name):
            self.screen_manager.current = screen_name
            screen = self.screen_manager.get_screen(screen_name)
            if hasattr(screen, "on_enter"):
                screen.dispatch("on_enter")
    def check_for_updates(self):
        self._do_update_check(show_ui=True)

    def _check_updates_background(self):
        self._do_update_check(show_ui=False)

    def _do_update_check(self, show_ui=True):
        try:
            import json
            import urllib.request
            url = "https://api.github.com/repos/mariacennami1-commits/FindMyCar/releases/latest"
            req = urllib.request.Request(url, headers={"User-Agent": "FindMyCar/1.0", "Accept": "application/vnd.github.v3+json"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())

            latest_tag = data.get("tag_name", "").lstrip("v")
            current = self.VERSION
            Logger.info(f"App: Update check - current={current} latest={latest_tag}")

            if self._is_newer(latest_tag, current):
                msg = f"Aggiornamento disponibile: v{latest_tag}"
                Logger.info(f"App: {msg}")
                self._show_update_dialog(data)
            elif show_ui:
                self._show_snackbar("Nessun aggiornamento disponibile")
        except Exception as e:
            if show_ui:
                self._show_snackbar(f"Errore controllo: {e}")

    def _is_newer(self, latest, current):
        try:
            lp = [int(x) for x in latest.split(".")]
            cp = [int(x) for x in current.split(".")]
            for i in range(max(len(lp), len(cp))):
                lv = lp[i] if i < len(lp) else 0
                cv = cp[i] if i < len(cp) else 0
                if lv > cv:
                    return True
                elif lv < cv:
                    return False
            return False
        except:
            return latest != current

    def _show_update_dialog(self, release_data):
        try:
            from kivymd.uix.dialog import MDDialog
            from kivymd.uix.button import MDRaisedButton
            assets = release_data.get("assets", [])
            apk_url = None
            for a in assets:
                if a["name"].endswith(".apk"):
                    apk_url = a["browser_download_url"]
                    break
            body = release_data.get("body", "")[:300]
            dialog = MDDialog(
                title=f"v{release_data.get('tag_name', '').lstrip('v')} disponibile",
                text=f"{body}\n\nScaricare e installare?",
                buttons=[
                    MDRaisedButton(text="Annulla", on_release=lambda x: dialog.dismiss()),
                    MDRaisedButton(
                        text="Scarica",
                        on_release=lambda x: (
                            dialog.dismiss(),
                            self._download_and_install(release_data["zipball_url"], apk_url),
                        )
                    ),
                ],
            )
            dialog.open()
        except Exception as e:
            Logger.error(f"App: Update dialog error - {e}")

    def _download_and_install(self, release_url, apk_url):
        if not apk_url:
            self._show_snackbar("APK non trovato nella release")
            return
        try:
            from kivy.utils import platform
            if platform != "android":
                self._show_snackbar("Apri browser: " + apk_url)
                return
            from jnius import autoclass
            Intent = autoclass("android.content.Intent")
            Uri = autoclass("android.net.Uri")
            intent = Intent(Intent.ACTION_VIEW)
            intent.setData(Uri.parse(apk_url))
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            from android import mActivity
            mActivity.startActivity(intent)
        except Exception as e:
            Logger.error(f"App: Open browser error - {e}")
            self._show_snackbar(f"Apri manualmente: {apk_url}")

    def _show_snackbar(self, msg):
        try:
            from kivymd.uix.snackbar import Snackbar
            Snackbar(text=msg, duration=4).open()
        except:
            pass

    def on_stop(self):
        try:
            self.gps_service.stop()
        except:
            pass
        Logger.info("App: Stopped")