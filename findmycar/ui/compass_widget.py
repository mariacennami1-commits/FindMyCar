import math
from kivy.clock import Clock
from kivy.properties import NumericProperty, ListProperty
from kivy.graphics import Color, Rotate, PushMatrix, PopMatrix, Line, Rectangle
from kivy.uix.widget import Widget
from kivy.core.image import Image as CoreImage
import io
from PIL import Image, ImageDraw


class CompassWidget(Widget):
    bearing = NumericProperty(0)
    target_bearing = NumericProperty(0)
    colors = ListProperty([0.0, 0.898, 1.0, 1.0])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._texture = None
        self._compass_cache = None
        Clock.schedule_once(self._create_compass, 0)

    def _create_compass(self, dt):
        size = self.width or 200
        img = Image.new("RGBA", (int(size), int(size)), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        cx = cy = size / 2
        r = size / 2 - 5

        draw.ellipse(
            [cx - r, cy - r, cx + r, cy + r],
            outline=(255, 255, 255, 60),
            width=2,
        )

        inner_r = r - 15
        draw.ellipse(
            [cx - inner_r, cy - inner_r, cx + inner_r, cy + inner_r],
            outline=(255, 255, 255, 20),
            width=1,
        )

        for deg in range(0, 360, 30):
            rad = math.radians(deg - 90)
            outer = r - 5
            if deg % 90 == 0:
                inner = r - 20
                color = (255, 255, 255, 200)
                w = 3
            else:
                inner = r - 12
                color = (255, 255, 255, 100)
                w = 1
            x1 = cx + outer * math.cos(rad)
            y1 = cy + outer * math.sin(rad)
            x2 = cx + inner * math.cos(rad)
            y2 = cy + inner * math.sin(rad)
            draw.line([(x1, y1), (x2, y2)], fill=color, width=w)

        for label, deg in [("N", 0), ("E", 90), ("S", 180), ("W", 270)]:
            rad = math.radians(deg - 90)
            label_r = r - 30
            x = cx + label_r * math.cos(rad)
            y = cy + label_r * math.sin(rad)

            bbox = draw.textbbox((0, 0), label, font=None)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            color = (255, 50, 50, 255) if label == "N" else (255, 255, 255, 200)
            draw.text((x - tw / 2, y - th / 2), label, fill=color)

        needle_len = r - 25
        needle_start = 20

        for angle, color, width in [
            (0, (255, 50, 50, 255), 4),
            (180, (255, 255, 255, 200), 3),
        ]:
            rad = math.radians(angle - 90)
            x1 = cx + needle_start * math.cos(rad)
            y1 = cy + needle_start * math.sin(rad)
            x2 = cx + needle_len * math.cos(rad)
            y2 = cy + needle_len * math.sin(rad)
            draw.line([(x1, y1), (x2, y2)], fill=color, width=width)

        draw.ellipse(
            [cx - 6, cy - 6, cx + 6, cy + 6],
            fill=(255, 255, 255, 255),
        )

        buf = io.BytesIO()
        img.save(buf, format="png")
        buf.seek(0)
        self._texture = CoreImage(buf, ext="png").texture

    def on_size(self, *args):
        self._create_compass(None)
        self.canvas.clear()

    def on_bearing(self, *args):
        self.canvas.clear()
        if not self._texture:
            return
        with self.canvas:
            PushMatrix()
            Rotate(
                angle=-self.bearing,
                origin=(self.center_x, self.center_y),
            )
            Rectangle(
                texture=self._texture,
                pos=(self.x, self.y),
                size=(self.width, self.height),
            )
            PopMatrix()
