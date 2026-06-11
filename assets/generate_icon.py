from PIL import Image, ImageDraw, ImageFont

bg = (19, 19, 21, 255)
accent = (53, 225, 111, 255)
primary = (173, 198, 255, 255)
white = (255, 255, 255, 255)
muted = (120, 130, 150, 255)


def draw_pin(d, cx, cy, scale=1.0):
    pr = int(140 * scale)
    draw.ellipse([cx - pr, cy - pr, cx + pr, cy + pr], fill=primary)
    draw.polygon([
        (cx - pr // 3, cy + pr // 2 + 5),
        (cx + pr // 3, cy + pr // 2 + 5),
        (cx, cy + int(pr * 0.92)),
    ], fill=primary)

    ir = int(50 * scale)
    draw.ellipse([cx - ir, cy - ir, cx + ir, cy + ir], fill=bg)

    cw = int(72 * scale)
    ch = int(28 * scale)
    cx2 = cx - cw // 2
    cy2 = cy - ch // 2 + int(3 * scale)
    draw.rounded_rectangle([cx2, cy2, cx2 + cw, cy2 + ch], radius=int(8 * scale), fill=primary)

    rw = int(44 * scale)
    rh = int(20 * scale)
    rx = cx - rw // 2
    ry = cy2 - rh + int(6 * scale)
    draw.rounded_rectangle([rx, ry, rx + rw, ry + rh], radius=int(6 * scale), fill=primary)

    draw.rounded_rectangle([cx2 + int(8 * scale), cy2 + int(2 * scale),
                            cx2 + cw - int(8 * scale), cy2 + ch - int(2 * scale)],
                           radius=int(4 * scale), fill=white)

    wr = int(9 * scale)
    wy = cy2 + ch
    for wx in [cx2 + int(14 * scale), cx2 + cw - int(14 * scale)]:
        draw.ellipse([wx - wr, wy - wr, wx + wr, wy + wr], fill=accent)
        draw.ellipse([wx - int(3 * scale), wy - int(3 * scale),
                      wx + int(3 * scale), wy + int(3 * scale)], fill=bg)


# ===== ICON =====
SIZE = 512
img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

draw.rounded_rectangle([8, 8, SIZE - 9, SIZE - 9], radius=96, fill=bg)

for i in range(180):
    y = 80 + i
    alpha = max(0, 14 - int(i * 0.08))
    if alpha <= 0:
        break
    draw.line([(80, y), (SIZE - 80, y)], fill=(173, 198, 255, alpha))

C = SIZE // 2
draw.ellipse([C - 150, C + 50, C + 150, C + 90], fill=(0, 0, 0, 60))
draw_pin(draw, C, C - 30, 1.0)
draw.ellipse([C + 120, C - 165, C + 145, C - 140], fill=accent)

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
    print(f"Icon saved {name} ({sz}x{sz})")


# ===== LOGO / PRESPLASH =====
def make_logo(size):
    img = Image.new("RGBA", (size, size), bg)
    draw = ImageDraw.Draw(img)
    C = size // 2

    try:
        font_title = ImageFont.truetype("arialbd.ttf", int(size * 0.075))
    except:
        font_title = ImageFont.truetype("arial.ttf", int(size * 0.075))
    try:
        font_sub = ImageFont.truetype("arial.ttf", int(size * 0.035))
    except:
        font_sub = ImageFont.truetype("arial.ttf", int(size * 0.035))
    try:
        font_ver = ImageFont.truetype("arial.ttf", int(size * 0.025))
    except:
        font_ver = ImageFont.truetype("arial.ttf", int(size * 0.025))

    scale = size / 512
    pin_y = int(C * 0.75)
    draw_pin(draw, C, pin_y, scale)

    title = "FindMyCar"
    bbox = draw.textbbox((0, 0), title, font=font_title)
    tw = bbox[2] - bbox[0]
    tx = C - tw // 2
    ty = pin_y + int(140 * scale) + int(50 * scale)
    draw.text((tx, ty), title, fill=primary, font=font_title)

    sub = "Trova il tuo parcheggio"
    bbox = draw.textbbox((0, 0), sub, font=font_sub)
    sw = bbox[2] - bbox[0]
    sx = C - sw // 2
    sy = ty + int(size * 0.09)
    draw.text((sx, sy), sub, fill=muted, font=font_sub)

    ver = "v1.0.0"
    vy = size - int(size * 0.05)
    bbox = draw.textbbox((0, 0), ver, font=font_ver)
    vw = bbox[2] - bbox[0]
    vx = C - vw // 2
    draw.text((vx, vy), ver, fill=(80, 85, 95, 255), font=font_ver)

    return img


make_logo(512).save("logo.png")
print("Saved logo.png (512x512)")

make_logo(1024).save("logo_big.png")
print("Saved logo_big.png (1024x1024)")
