from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivy.logger import Logger


class MapScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._gps_listener_active = False
        self._bridge = None
        self._app = None

    def get_app(self):
        if not self._app:
            try:
                from kivy.app import App
                self._app = App.get_running_app()
            except:
                pass
        return self._app

    def on_enter(self):
        app = self.get_app()
        if not app:
            return
        self._bridge = getattr(app, "webview_bridge", None)
        if not self._bridge:
            Logger.warning("MapScreen: No webview bridge")
            return
        self._bridge.show()
        self._gps_listener_active = True
        gps = getattr(app, "gps_service", None)
        if gps:
            gps.add_listener(self._on_gps)
            if gps.has_fix():
                pos = gps.get_position()
                if pos:
                    self._send_position(pos[0], pos[1], gps.accuracy or 0, gps.bearing or 0)
        storage = getattr(app, "storage_service", None)
        if storage:
            latest = storage.get_latest()
            if latest:
                addr = latest.address or f"{latest.latitude:.4f}, {latest.longitude:.4f}"
                self._bridge.send_js(
                    'updateCarParked('
                    + str(latest.latitude) + ','
                    + str(latest.longitude) + ','
                    + '"' + self._escape_js(addr) + '",'
                    + '"' + self._escape_js(self._format_time(latest.timestamp)) + '"'
                    + ')'
                )
            else:
                self._bridge.send_js("clearCarParked()")

    def on_leave(self):
        self._gps_listener_active = False
        if self._bridge:
            self._bridge.hide()
        app = self.get_app()
        if app:
            gps = getattr(app, "gps_service", None)
            if gps:
                gps.remove_listener(self._on_gps)

    def _on_gps(self, gps_svc):
        if not self._gps_listener_active:
            return
        pos = gps_svc.get_position()
        if pos:
            self._send_position(pos[0], pos[1], gps_svc.accuracy or 0, gps_svc.bearing or 0)

    def _send_position(self, lat, lng, acc, bearing):
        if not self._bridge:
            return
        js = (
            "updatePosition("
            + str(lat) + ","
            + str(lng) + ","
            + str(acc) + ","
            + str(bearing)
            + ")"
        )
        self._bridge.send_js(js)

    def _escape_js(self, s):
        if not s:
            return ""
        return str(s).replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")

    def _format_time(self, ts_str):
        if not ts_str:
            return ""
        try:
            from datetime import datetime
            ts = datetime.fromisoformat(ts_str)
            now = datetime.now()
            if ts.date() == now.date():
                return "Oggi " + ts.strftime("%H:%M")
            delta = (now.date() - ts.date()).days
            if delta == 1:
                return "Ieri " + ts.strftime("%H:%M")
            return ts.strftime("%d/%m %H:%M")
        except:
            return ts_str
