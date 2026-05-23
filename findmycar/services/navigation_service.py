import math
from datetime import datetime
from kivy.logger import Logger


class NavigationService:
    @staticmethod
    def haversine(lat1, lon1, lat2, lon2):
        R = 6371000
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)

        a = (
            math.sin(dphi / 2) ** 2
            + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    @staticmethod
    def bearing(lat1, lon1, lat2, lon2):
        dlambda = math.radians(lon2 - lon1)
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)

        x = math.sin(dlambda) * math.cos(phi2)
        y = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(dlambda)

        bearing = math.degrees(math.atan2(x, y))
        return (bearing + 360) % 360

    @staticmethod
    def distance_meters(lat1, lon1, lat2, lon2):
        return NavigationService.haversine(lat1, lon1, lat2, lon2)

    @staticmethod
    def distance_string(meters):
        if meters < 1000:
            return f"{int(meters)} m"
        else:
            return f"{meters / 1000:.1f} km"

    @staticmethod
    def time_estimate(distance_meters, walking_speed=1.4):
        seconds = distance_meters / walking_speed
        minutes = int(seconds / 60)
        if minutes < 1:
            return "< 1 min"
        elif minutes < 60:
            return f"{minutes} min"
        else:
            hours = minutes // 60
            mins = minutes % 60
            return f"{hours}h {mins}min"

    @staticmethod
    def direction_label(bearing_deg):
        directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
        index = round(bearing_deg / 45) % 8
        return directions[index]

    @staticmethod
    def relative_bearing(from_bearing, to_bearing):
        diff = to_bearing - from_bearing
        if diff > 180:
            diff -= 360
        elif diff < -180:
            diff += 360
        return diff
