#!/usr/bin/env python3
"""Generate a neon HUD-style background image for the password checker GUI.

This script uses Pillow to draw a stylized HUD background and saves it
as assets/background.png next to the GUI script.
"""
from PIL import Image, ImageDraw, ImageFilter
import os

OUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'assets')
os.makedirs(OUT_DIR, exist_ok=True)
OUT_PATH = os.path.join(OUT_DIR, 'background.png')

W, H = 1600, 900
img = Image.new('RGB', (W, H), '#0b0713')
d = ImageDraw.Draw(img)

def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

# vertical gradient base
for i, (c1, c2) in enumerate([('#3b0072', '#7c00ff'), ('#7c00ff', '#ff007f'), ('#ff007f', '#ff9a00')]):
    y0 = int(i * H / 3.0)
    y1 = int((i + 1) * H / 3.0)
    r1, g1, b1 = hex_to_rgb(c1)
    r2, g2, b2 = hex_to_rgb(c2)
    span = max(1, (y1 - y0))
    for y in range(y0, y1):
        t = (y - y0) / span
        r = int(r1 + (r2 - r1) * t)
        g = int(g1 + (g2 - g1) * t)
        b = int(b1 + (b2 - b1) * t)
        d.line([(0, y), (W, y)], fill=(r, g, b))

# Add subtle grid lines
for x in range(0, W, 80):
    d.line([(x, 0), (x, H)], fill=(255,255,255,20))
for y in range(0, H, 80):
    d.line([(0, y), (W, y)], fill=(255,255,255,12))

# Central HUD rectangle with rounded corners
rect_w, rect_h = int(W*0.6), int(H*0.55)
rx = (W - rect_w)//2
ry = (H - rect_h)//2
r = 18
# draw outer neon border
for off, col in [(0, '#ff3ec5'), (6, '#7c00ff'), (12, '#3b82f6')]:
    d.rounded_rectangle([rx-off, ry-off, rx+rect_w+off, ry+rect_h+off], radius=r+off, outline=col, width=3)

# inner lock circle
cx = W//2
cy = ry + 140
d.ellipse((cx-70, cy-70, cx+70, cy+70), outline='#ff3ec5', width=3)
# keyhole
d.ellipse((cx-15, cy-10, cx+15, cy+30), fill='#ff3ec5')
d.rectangle((cx-6, cy+20, cx+6, cy+45), fill='#ff3ec5')

# HUD decoration: some boxes and lines
for i in range(6):
    x0 = rx + 40
    y0 = ry + 40 + i*50
    d.rectangle((x0, y0, x0+220, y0+32), outline='#e879f9', width=2)

# subtle blur
img = img.filter(ImageFilter.GaussianBlur(radius=0.8))

img.save(OUT_PATH, format='PNG')
print('Generated', OUT_PATH)
