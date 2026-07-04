import threading
import time
import os
from kivy.logger import Logger
from kivy.clock import mainthread


class GPSService:
    def __init__(self):
        self.latitude = None
        self.longitude = None
        self.accuracy = None
        self.altitude = None
        self.bearing = None
        self.speed = None
        self.is_running = False
        self.listeners = []
        self.last_fix_time = None
        self._gps = None
        self._init_gps()

    def _init_gps(self):
        try:
            from kivy.utils import platform
            if platform == 'android':
                from .android_gps import AndroidGPS
                self._gps = AndroidGPS()
                Logger.info('GPSService: Using AndroidGPS (native LocationListener)')
            else:
                raise ImportError('Non-Android platform')
        except Exception:
            from plyer import gps
            self._gps = gps
            Logger.info('GPSService: Using plyer GPS')

    def start(self, min_time=1000, min_distance=1):
        try:
            self._gps.configure(on_location=self._on_location, on_status=self._on_status)
            self._gps.start(min_time, min_distance)
            self.is_running = True
            Logger.info("GPSService: GPS started")
        except Exception as e:
            Logger.error(f"GPSService: Failed to start GPS - {e}")

    def stop(self):
        try:
            self._gps.stop()
            self.is_running = False
            Logger.info("GPSService: GPS stopped")
        except Exception as e:
            Logger.error(f"GPSService: Failed to stop GPS - {e}")

    def _on_location(self, **kwargs):
        self.latitude = kwargs.get("lat")
        self.longitude = kwargs.get("lon")
        self.accuracy = kwargs.get("accuracy")
        self.altitude = kwargs.get("altitude")
        self.bearing = kwargs.get("bearing")
        self.speed = kwargs.get("speed")
        self.last_fix_time = time.time()
        self._notify_listeners()

    def _on_status(self, stype, status):
        Logger.info(f"GPSService: Status - {stype}: {status}")

    def add_listener(self, callback):
        self.listeners.append(callback)

    def remove_listener(self, callback):
        if callback in self.listeners:
            self.listeners.remove(callback)

    def _notify_listeners(self):
        for callback in self.listeners:
            try:
                callback(self)
            except Exception as e:
                Logger.error(f"GPSService: Listener error - {e}")

    def has_fix(self):
        return self.latitude is not None and self.longitude is not None

    def get_position(self):
        if self.has_fix():
            return (self.latitude, self.longitude)
        return None

    def has_recent_fix(self, max_age=10):
        if self.last_fix_time is None:
            return False
        return (time.time() - self.last_fix_time) < max_age
