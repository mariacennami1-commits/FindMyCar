import math


class KalmanFilter:
    def __init__(self):
        self.dt = 1.0
        self.x = [0.0, 0.0, 0.0, 0.0]
        self.P = [[100.0, 0, 0, 0],
                  [0, 100.0, 0, 0],
                  [0, 0, 100.0, 0],
                  [0, 0, 0, 100.0]]
        self.Q = 0.1
        self.R = 5.0
        self.initialized = False

    def initialize(self, lat, lon):
        self.x = [lat, lon, 0.0, 0.0]
        self.initialized = True

    def predict(self, step_length=0, heading=0):
        if not self.initialized:
            return None

        vx = step_length * math.sin(math.radians(heading))
        vy = step_length * math.cos(math.radians(heading))

        self.x[2] = vx
        self.x[3] = vy

        self.x[0] += self.x[2] * self.dt
        self.x[1] += self.x[3] * self.dt

        for i in range(4):
            self.P[i][i] += self.Q

        return (self.x[0], self.x[1])

    def update(self, lat, lon):
        if not self.initialized:
            self.initialize(lat, lon)
            return (lat, lon)

        y_lat = lat - self.x[0]
        y_lon = lon - self.x[1]

        S_lat = self.P[0][0] + self.R
        S_lon = self.P[1][1] + self.R

        K_lat = self.P[0][0] / S_lat
        K_lon = self.P[1][1] / S_lon

        self.x[0] += K_lat * y_lat
        self.x[1] += K_lon * y_lon

        self.P[0][0] = (1 - K_lat) * self.P[0][0]
        self.P[1][1] = (1 - K_lon) * self.P[1][1]

        return (self.x[0], self.x[1])


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
        magnitude = math.sqrt(x ** 2 + y ** 2 + z ** 2)
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
            return (self.kalman.x[0], self.kalman.x[1])
        return None

    def reset(self, lat=None, lon=None):
        self.step_count = 0
        if lat is not None and lon is not None:
            self.kalman.initialize(lat, lon)
