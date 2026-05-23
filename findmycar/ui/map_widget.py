import os
import math
import struct
import io
from kivy.logger import Logger
from kivy.clock import Clock
from kivy.properties import NumericProperty, ObjectProperty, ListProperty
from kivy.graphics import Color, Rectangle, Line, Ellipse
from kivy.uix.widget import Widget
from kivy.core.image import Image as CoreImage
from kivy.loader import Loader
from kivy.cache import Cache
from plyer import gps
import concurrent.futures
import urllib.request


class OfflineMapWidget(Widget):
    center_lat = NumericProperty(0.0)
    center_lon = NumericProperty(0.0)
    zoom = NumericProperty(16)
    marker_color = ListProperty([0.0, 0.898, 1.0, 1.0])
    parked_color = ListProperty([1.0, 0.2, 0.2, 1.0])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._tiles = {}
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)
        self._tile_cache_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "assets", "tiles",
        )
        os.makedirs(self._tile_cache_dir, exist_ok=True)
        self.current_lat = None
        self.current_lon = None
        self.parked_lat = None
        self.parked_lon = None
        Clock.schedule_interval(self._update_tiles, 0.5)

    def _lat_lon_to_tile(self, lat, lon, zoom):
        lat_rad = math.radians(lat)
        n = 2.0 ** zoom
        x = int((lon + 180.0) / 360.0 * n)
        y = int((1.0 - math.log(math.tan(lat_rad) + 1.0 / math.cos(lat_rad)) / math.pi) / 2.0 * n)
        return x, y

    def _tile_to_lat_lon(self, x, y, zoom):
        n = 2.0 ** zoom
        lon = x / n * 360.0 - 180.0
        lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * y / n)))
        lat = math.degrees(lat_rad)
        return lat, lon

    def _get_tile_url(self, x, y, z):
        return f"https://tile.openstreetmap.org/{z}/{x}/{y}.png"

    def _get_tile_path(self, x, y, z):
        return os.path.join(self._tile_cache_dir, f"{z}_{x}_{y}.png")

    def _download_tile(self, x, y, z):
        tile_path = self._get_tile_path(x, y, z)
        if os.path.exists(tile_path):
            return tile_path

        try:
            url = self._get_tile_url(x, y, z)
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "FindMyCar/1.0 (car finder app)",
                },
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                data = response.read()
                with open(tile_path, "wb") as f:
                    f.write(data)
            return tile_path
        except Exception as e:
            Logger.warning(f"MapWidget: Failed to download tile {z}/{x}/{y} - {e}")
            return None

    def _lat_lon_to_screen(self, lat, lon):
        tile_x, tile_y = self._lat_lon_to_tile(lat, lon, int(self.zoom))
        n = 2.0 ** int(self.zoom)
        tile_size = 256.0

        world_x = (lon + 180.0) / 360.0 * n * tile_size
        world_y = (1.0 - math.log(math.tan(math.radians(lat)) + 1.0 / math.cos(math.radians(lat))) / math.pi) / 2.0 * n * tile_size

        center_x_tile, center_y_tile = self._lat_lon_to_tile(self.center_lat, self.center_lon, int(self.zoom))
        center_world_x = center_x_tile * tile_size + tile_size / 2
        center_world_y = center_y_tile * tile_size + tile_size / 2

        screen_x = self.center_x + (world_x - center_world_x)
        screen_y = self.center_y - (world_y - center_world_y)

        return screen_x, screen_y

    def set_center(self, lat, lon):
        self.center_lat = lat
        self.center_lon = lon

    def set_current_position(self, lat, lon):
        self.current_lat = lat
        self.current_lon = lon
        self.set_center(lat, lon)
        self.canvas.clear()
        self._draw_map()

    def set_parked_position(self, lat, lon):
        self.parked_lat = lat
        self.parked_lon = lon
        self.canvas.clear()
        self._draw_map()

    def _update_tiles(self, dt):
        if self.center_lat == 0 and self.center_lon == 0:
            return

        z = int(self.zoom)
        cx, cy = self._lat_lon_to_tile(self.center_lat, self.center_lon, z)

        for dx in range(-2, 3):
            for dy in range(-2, 3):
                tx, ty = cx + dx, cy + dy
                key = (tx, ty, z)
                if key not in self._tiles:
                    self._tiles[key] = "loading"
                    self._executor.submit(self._load_tile, tx, ty, z)

    def _load_tile(self, x, y, z):
        path = self._download_tile(x, y, z)
        if path:
            Clock.schedule_once(lambda dt, p=path, xx=x, yy=y, zz=z: self._on_tile_loaded(p, xx, yy, zz))

    def _on_tile_loaded(self, path, x, y, z):
        key = (x, y, z)
        try:
            texture = CoreImage(path).texture
            self._tiles[key] = texture
            self.canvas.clear()
            self._draw_map()
        except Exception as e:
            Logger.warning(f"MapWidget: Failed to load tile texture - {e}")
            self._tiles[key] = None

    def _draw_map(self):
        self.canvas.clear()
        if self.center_lat == 0 and self.center_lon == 0:
            return

        z = int(self.zoom)
        tile_size = 256.0
        cx_tile, cy_tile = self._lat_lon_to_tile(self.center_lat, self.center_lon, z)

        with self.canvas:
            Color(0.11, 0.13, 0.15, 1)
            Rectangle(pos=self.pos, size=self.size)

        for dx in range(-2, 3):
            for dy in range(-2, 3):
                tx, ty = cx_tile + dx, cy_tile + dy
                key = (tx, ty, z)
                texture = self._tiles.get(key)
                if texture and isinstance(texture, CoreImage):
                    world_x = tx * tile_size - (cx_tile * tile_size + tile_size / 2)
                    world_y = ty * tile_size - (cy_tile * tile_size + tile_size / 2)

                    x_pos = self.center_x + world_x
                    y_pos = self.center_y - world_y

                    if x_pos + tile_size >= self.x and x_pos <= self.x + self.width and y_pos + tile_size >= self.y and y_pos <= self.y + self.height:
                        with self.canvas:
                            Rectangle(
                                texture=texture,
                                pos=(x_pos, y_pos),
                                size=(tile_size, tile_size),
                            )

        if self.current_lat is not None:
            sx, sy = self._lat_lon_to_screen(self.current_lat, self.current_lon)
            with self.canvas:
                Color(*self.marker_color)
                Ellipse(pos=(sx - 10, sy - 10), size=(20, 20))
                Color(1, 1, 1, 1)
                Line(circle=(sx, sy, 20), width=2)

        if self.parked_lat is not None:
            sx, sy = self._lat_lon_to_screen(self.parked_lat, self.parked_lon)
            with self.canvas:
                Color(*self.parked_color)
                Ellipse(pos=(sx - 10, sy - 10), size=(20, 20))
                Color(1, 1, 1, 0.5)
                Line(circle=(sx, sy, 20), width=2)

            cx, cy_screen = self.center_x, self.center_y
            if self.current_lat is not None:
                csx, csy = self._lat_lon_to_screen(self.current_lat, self.current_lon)
                with self.canvas:
                    Color(0.0, 0.898, 1.0, 0.3)
                    Line(points=[csx, csy, sx, sy], width=2, dash_length=5, dash_offset=2)
