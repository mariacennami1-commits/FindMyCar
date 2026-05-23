import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math


def create_logo(size=512):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    cx = cy = size // 2

    outer_r = size // 2 - 10
    inner_r = size // 4

    for i in range(360):
        angle = math.radians(i)
        x = cx + outer_r * math.cos(angle)
        y = cy + outer_r * math.sin(angle)

        intensity = int(20 + 15 * math.sin(angle * 4))
        r = int(10 + 7 * math.sin(angle * 3 + 0.5))
        g = int(40 + 10 * math.sin(angle * 2 + 1.0))
        b = int(80 + 15 * math.sin(angle * 5 + 1.5))
        draw.point((x, y), fill=(r, g, b, intensity))

    glow_layers = 40
    for i in range(glow_layers):
        t = i / glow_layers
        radius = int(inner_r + (outer_r - inner_r) * t)
        alpha = int(60 * (1 - t))
        draw.ellipse(
            [cx - radius, cy - radius, cx + radius, cy + radius],
            outline=(0, 120, 200, alpha),
            width=2,
        )

    draw.ellipse(
        [cx - inner_r, cy - inner_r, cx + inner_r, cy + inner_r],
        fill=(10, 15, 30, 230),
        outline=(0, 180, 255, 150),
        width=3,
    )

    draw.ellipse(
        [cx - inner_r + 8, cy - inner_r + 8, cx + inner_r - 8, cy + inner_r - 8],
        outline=(0, 100, 200, 80),
        width=1,
    )

    car_center_x = cx
    car_center_y = cy - 5
    car_w = int(inner_r * 0.8)
    car_h = int(inner_r * 0.55)

    car_body = [
        (car_center_x - car_w // 2, car_center_y + car_h // 4),
        (car_center_x - car_w // 2, car_center_y - car_h // 4),
        (car_center_x - car_w // 4 + 5, car_center_y - car_h // 2),
        (car_center_x + car_w // 4 - 5, car_center_y - car_h // 2),
        (car_center_x + car_w // 2, car_center_y - car_h // 4),
        (car_center_x + car_w // 2, car_center_y + car_h // 4),
    ]
    draw.polygon(car_body, fill=(30, 40, 60, 240), outline=(0, 200, 255, 180), width=2)

    roof = [
        (car_center_x - car_w // 4 + 10, car_center_y - car_h // 2),
        (car_center_x - car_w // 4 + 8, car_center_y - car_h // 2 + 2),
        (car_center_x - car_w // 5, car_center_y - car_h // 2 + 2),
    ]

    windshield = [
        (car_center_x - car_w // 4 + 8, car_center_y - car_h // 2 + 2),
        (car_center_x - car_w // 4 + 14, car_center_y - car_h // 4 + 5),
        (car_center_x + car_w // 4 - 14, car_center_y - car_h // 4 + 5),
        (car_center_x + car_w // 4 - 8, car_center_y - car_h // 2 + 2),
    ]
    draw.polygon(windshield, fill=(0, 150, 220, 100), outline=(0, 180, 255, 120), width=1)

    wheel_r = int(car_h * 0.18)
    for wx in [-car_w // 3 + 5, car_w // 3 - 5]:
        draw.ellipse(
            [car_center_x + wx - wheel_r, car_center_y + car_h // 4 - wheel_r + 3,
             car_center_x + wx + wheel_r, car_center_y + car_h // 4 + wheel_r + 3],
            fill=(10, 10, 15, 240),
            outline=(0, 180, 255, 150),
            width=1,
        )
        draw.ellipse(
            [car_center_x + wx - wheel_r // 2, car_center_y + car_h // 4 - wheel_r // 2 + 3,
             car_center_x + wx + wheel_r // 2, car_center_y + car_h // 4 + wheel_r // 2 + 3],
            fill=(0, 100, 150, 100),
        )

    headlight_r = 5
    draw.ellipse(
        [car_center_x + car_w // 2 - headlight_r - 2, car_center_y + car_h // 6 - headlight_r,
         car_center_x + car_w // 2 - 2, car_center_y + car_h // 6 + headlight_r],
        fill=(0, 200, 255, 200),
    )

    tail_r = 4
    draw.ellipse(
        [car_center_x - car_w // 2 + 2, car_center_y + car_h // 6 - tail_r,
         car_center_x - car_w // 2 + tail_r + 2, car_center_y + car_h // 6 + tail_r],
        fill=(255, 50, 50, 200),
    )

    pin_len = int(inner_r * 0.35)
    pin_x = car_center_x + car_w // 2 + 15
    pin_y = car_center_y + car_h // 4 + 5

    draw.line(
        [(pin_x, pin_y), (pin_x, pin_y - pin_len)],
        fill=(0, 200, 255, 180),
        width=3,
    )

    point_size = 8
    draw.ellipse(
        [pin_x - point_size, pin_y - pin_len - point_size,
         pin_x + point_size, pin_y - pin_len + point_size],
        fill=(255, 50, 50, 230),
        outline=(255, 100, 100, 100),
        width=1,
    )

    arc_start = 200
    arc_end = 340
    arc_r = int(outer_r * 0.55)
    for a in range(arc_start, arc_end, 2):
        angle = math.radians(a)
        x1 = cx + (arc_r - 3) * math.cos(angle)
        y1 = cy + (arc_r - 3) * math.sin(angle)
        x2 = cx + (arc_r + 3) * math.cos(angle)
        y2 = cy + (arc_r + 3) * math.sin(angle)
        draw.line([(x1, y1), (x2, y2)], fill=(0, 150, 255, 120), width=1)

    img = img.filter(ImageFilter.SMOOTH_MORE)
    img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)

    return img


def generate_all_formats():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(base_dir, "assets")
    os.makedirs(assets_dir, exist_ok=True)

    sizes = {
        "logo.png": 512,
        "icon.png": 256,
        "icon_192.png": 192,
        "icon_144.png": 144,
        "icon_96.png": 96,
        "icon_72.png": 72,
        "icon_48.png": 48,
    }

    for filename, size in sizes.items():
        logo = create_logo(size)
        path = os.path.join(assets_dir, filename)
        logo.save(path, "PNG")
        print(f"Created: {path} ({size}x{size})")

    logo_big = create_logo(1024)
    path_big = os.path.join(assets_dir, "logo_big.png")
    logo_big.save(path_big, "PNG")
    print(f"Created: {path_big} (1024x1024)")


if __name__ == "__main__":
    generate_all_formats()
    print("\nLogo generato con successo!")
