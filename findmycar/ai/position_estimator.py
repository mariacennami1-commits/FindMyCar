import numpy as np
from kivy.logger import Logger


class KalmanFilter:
    def __init__(self):
        self.dt = 1.0
        self.A = np.array([[1, 0, self.dt, 0],
                           [0, 1, 0, self.dt],
                           [0, 0, 1, 0],
                           [0, 0, 0, 1]])
        self.H = np.array([[1, 0, 0, 0],
                           [0, 1, 0, 0]])
        self.Q = np.eye(4) * 0.1
        self.R = np.eye(2) * 5.0
        self.P = np.eye(4) * 100.0
        self.x = np.zeros((4, 1))
        self.initialized = False

    def initialize(self, lat, lon):
        self.x = np.array([[lat], [lon], [0], [0]], dtype=float)
        self.initialized = True

    def predict(self, step_length=0, heading=0):
        if not self.initialized:
            return None

        vx = step_length * np.sin(np.radians(heading))
        vy = step_length * np.cos(np.radians(heading))

        self.x[2] = vx
        self.x[3] = vy

        self.x = self.A @ self.x
        self.P = self.A @ self.P @ self.A.T + self.Q
        return (float(self.x[0]), float(self.x[1]))

    def update(self, lat, lon):
        if not self.initialized:
            self.initialize(lat, lon)
            return (lat, lon)

        z = np.array([[lat], [lon]], dtype=float)
        y = z - self.H @ self.x
        S = self.H @ self.P @ self.H.T + self.R
        K = self.P @ self.H.T @ np.linalg.inv(S)

        self.x = self.x + K @ y
        self.P = (np.eye(4) - K @ self.H) @ self.P

        return (float(self.x[0]), float(self.x[1]))


class SensorFusion:
    def __init__(self):
        self.kalman = KalmanFilter()
        self.step_count = 0
        self.last_accel_magnitude = 0
        self.step_threshold = 12.0
        self.step_length = 0.7
        self.heading = 0.0
        self.is_moving = False

    def process_accelerometer(self, x, y, z):
        magnitude = np.sqrt(x ** 2 + y ** 2 + z ** 2)
        if self.last_accel_magnitude == 0:
            self.last_accel_magnitude = magnitude
            return False

        diff = magnitude - self.last_accel_magnitude
        self.last_accel_magnitude = magnitude

        if abs(diff) > self.step_threshold:
            self.step_count += 1
            self.is_moving = True
            new_lat_lon = self.kalman.predict(self.step_length, self.heading)
            self.is_moving = False
            return True

        return False

    def process_gyroscope(self, x, y, z):
        pass

    def process_magnetometer(self, heading):
        self.heading = heading % 360

    def update_gps(self, lat, lon):
        return self.kalman.update(lat, lon)

    def get_estimated_position(self):
        if self.kalman.initialized:
            return (float(self.kalman.x[0]), float(self.kalman.x[1]))
        return None

    def reset(self, lat=None, lon=None):
        self.step_count = 0
        if lat is not None and lon is not None:
            self.kalman.initialize(lat, lon)
