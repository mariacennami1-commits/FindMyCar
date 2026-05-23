import time
import math
from kivy.logger import Logger
from .position_estimator import SensorFusion
from ..services.navigation_service import NavigationService


class OfflineLocalizer:
    MODE_GPS = "gps"
    MODE_DEAD_RECKONING = "dead_reckoning"
    MODE_HYBRID = "hybrid"

    def __init__(self):
        self.sensor_fusion = SensorFusion()
        self.mode = self.MODE_HYBRID
        self.gps_position = None
        self.estimated_position = None
        self.gps_accuracy = 0.0
        self.last_gps_time = 0.0
        self.gps_timeout = 5.0
        self.distance_traveled = 0.0
        self._last_known_gps = None
        self._gps_lost_time = None

    def update_gps(self, lat, lon, accuracy=10.0):
        self.gps_position = (lat, lon)
        self.gps_accuracy = accuracy
        self.last_gps_time = time.time()

        if self._gps_lost_time is not None:
            lost_duration = time.time() - self._gps_lost_time
            Logger.info(f"OfflineLocalizer: GPS reacquired after {lost_duration:.1f}s")
            self._gps_lost_time = None

        if self._last_known_gps is not None:
            d = NavigationService.haversine(
                self._last_known_gps[0], self._last_known_gps[1], lat, lon
            )
            self.distance_traveled += d

        self._last_known_gps = (lat, lon)
        self.sensor_fusion.update_gps(lat, lon)
        self.estimated_position = (lat, lon)

    def update_sensors(self, accel_x=0, accel_y=0, accel_z=0, heading=0, gyro_x=0, gyro_y=0, gyro_z=0):
        if heading >= 0:
            self.sensor_fusion.process_magnetometer(heading)

        self.sensor_fusion.process_gyroscope(gyro_x, gyro_y, gyro_z)
        step_detected = self.sensor_fusion.process_accelerometer(accel_x, accel_y, accel_z)

        if not self._is_gps_valid() and self.mode != self.MODE_GPS:
            estimated = self.sensor_fusion.get_estimated_position()
            if estimated:
                self.estimated_position = estimated
                if self._gps_lost_time is None:
                    self._gps_lost_time = time.time()
                return step_detected, estimated, self.MODE_DEAD_RECKONING

        return step_detected, self.estimated_position, self.MODE_GPS

    def _is_gps_valid(self):
        if self.gps_position is None:
            return False
        if self.gps_accuracy > 50:
            return False
        if time.time() - self.last_gps_time > self.gps_timeout:
            return False
        return True

    def get_position(self):
        if self._is_gps_valid():
            return self.gps_position, self.MODE_GPS

        if self.estimated_position is not None:
            return self.estimated_position, self.MODE_DEAD_RECKONING

        return None, None

    def get_gps_lost_duration(self):
        if self._gps_lost_time is None:
            return 0.0
        return time.time() - self._gps_lost_time

    def reset(self, lat=None, lon=None):
        self.sensor_fusion.reset(lat, lon)
        self.distance_traveled = 0.0
        self._last_known_gps = (lat, lon) if lat else None
        self._gps_lost_time = None
        self.estimated_position = (lat, lon) if lat else None
        self.gps_position = (lat, lon) if lat else None

    def get_status_text(self):
        pos, mode = self.get_position()
        if pos is None:
            return "Nessun segnale"

        if mode == self.MODE_GPS:
            return "GPS"
        else:
            duration = self.get_gps_lost_duration()
            if duration < 60:
                return f"Offline ({int(duration)}s)"
            else:
                return f"Offline ({int(duration // 60)}m {int(duration % 60)}s)"
