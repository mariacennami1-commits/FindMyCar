from PIL import Image, ImageDraw

SIZE = 512
img = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

def rounded_rect(d, xy, r, fill):
    x0, y0, x1, y1 = xy
    d.rounded_rectangle([x0, y0, x1, y1], radius=r, fill=fill)

bg = (19, 19, 21, 255)
accent = (53, 225, 111, 255)
primary = (173, 198, 255, 255)
white = (255, 255, 255, 255)

S = SIZE
C = S // 2

# Background rounded square
rounded_rect(draw, (8, 8, S - 9, S - 9), 96, bg)

# Subtle top glow
for i in range(180):
    y = 80 + i
    alpha = max(0, 14 - int(i * 0.08))
    if alpha <= 0:
        break
    draw.line([(80, y), (S - 80, y)], fill=(173, 198, 255, alpha))

# --- Map Pin ---
px, py = C, C - 30
pr = 140

# Pin shadow
draw.ellipse([px - 150, py + 80, px + 150, py + 120], fill=(0, 0, 0, 60))

# Pin body
draw.ellipse([px - pr, py - pr, px + pr, py + pr], fill=primary)
draw.polygon([
    (px - pr // 3, py + pr // 2 + 5),
    (px + pr // 3, py + pr // 2 + 5),
    (px, py + int(pr * 0.92)),
], fill=primary)

# Inner circle (dark)
ir = 50
draw.ellipse([px - ir, py - ir, px + ir, py + ir], fill=bg)

# --- Car silhouette inside pin ---
car_w, car_h = 72, 28
cx, cy = px - car_w // 2, py - car_h // 2 + 3
draw.rounded_rectangle([cx, cy, cx + car_w, cy + car_h], radius=8, fill=primary)

# Roof
rw, rh = 44, 20
rx = px - rw // 2
ry = cy - rh + 6
draw.rounded_rectangle([rx, ry, rx + rw, ry + rh], radius=6, fill=primary)

# Windshield
draw.rounded_rectangle([cx + 8, cy + 2, cx + car_w - 8, cy + car_h - 2], radius=4, fill=white)

# Wheels
wr = 9
wy = cy + car_h
for wx in [cx + 14, cx + car_w - 14]:
    draw.ellipse([wx - wr, wy - wr, wx + wr, wy + wr], fill=accent)
    draw.ellipse([wx - 3, wy - 3, wx + 3, wy + 3], fill=bg)

# Accent dot
draw.ellipse([px + 120, py - 135, px + 145, py - 110], fill=accent)

# Save
sizes = [
    (512, "icon.png"),
    (192, "icon_192.png"),
    (144, "icon_144.png"),
    (96, "icon_96.png"),
    (72, "icon_72.png"),
    (48, "icon_48.png"),
]
for sz, name in sizes:
    resized = img.resize((sz, sz), Image.LANCZOS)
    resized.save(name)
    print(f"Saved {name} ({sz}x{sz})")
