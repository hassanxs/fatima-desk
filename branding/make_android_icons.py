"""Write the Fatima Desk Android launcher and notification icons.

Uses the same logo geometry as make_icons.py. Run from the repository root:

    python branding/make_android_icons.py

Writes, for every density bucket under flutter/android/app/src/main/res:
  mipmap-*/ic_launcher.png             legacy square icon (rounded tile)
  mipmap-*/ic_launcher_round.png       legacy round icon (gradient circle)
  mipmap-*/ic_launcher_foreground.png  adaptive-icon foreground (glyph only)
  mipmap-*/ic_stat_logo.png            white notification glyph
The adaptive-icon background is the gradient in
drawable/ic_launcher_background.xml.
"""
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_icons as mi  # noqa: E402

RES = os.path.join(mi.ROOT, 'flutter', 'android', 'app', 'src', 'main', 'res')
DENSITIES = {'mdpi': 1.0, 'hdpi': 1.5, 'xhdpi': 2.0, 'xxhdpi': 3.0, 'xxxhdpi': 4.0}

# The glyph (monitor + stand) spans x 192..832 and y 232..848 of the 1024 canvas,
# so its centre sits 28 px below the canvas centre.
GLYPH_DY = (232 + 848) / 2 - 512


def glyph_on(size, scale, glyph=mi.WHITE, cursor=mi.AMBER):
    """Transparent size x size image with the bare glyph rendered at
    `scale` * size and centred on the glyph's own bounding box."""
    g = round(size * scale)
    im = mi.render(g, tile=False, glyph=glyph, cursor=cursor)
    out = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    off = (size - g) // 2
    out.paste(im, (off, off - round(GLYPH_DY * g / 1024)), im)
    return out


def round_icon(size):
    ss = 4
    big = size * ss
    mask = Image.new('L', (big, big), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, big - 1, big - 1), fill=255)
    mask = mask.resize((size, size), Image.LANCZOS)
    out = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    out.paste(mi._gradient(size), (0, 0), mask)
    g = glyph_on(size, 0.78)
    out.alpha_composite(g)
    return out


def main():
    for name, k in DENSITIES.items():
        d = os.path.join(RES, f'mipmap-{name}')
        os.makedirs(d, exist_ok=True)
        legacy = round(48 * k)
        mi.render(legacy, margin=0.04).save(os.path.join(d, 'ic_launcher.png'))
        round_icon(legacy).save(os.path.join(d, 'ic_launcher_round.png'))
        # Adaptive foreground: 108dp canvas, keep the glyph inside the 66dp safe circle.
        glyph_on(round(108 * k), 0.70).save(os.path.join(d, 'ic_launcher_foreground.png'))
        stat = round(24 * k)
        glyph_on(stat, 1.0, glyph=mi.WHITE, cursor=mi.WHITE).convert('LA').save(
            os.path.join(d, 'ic_stat_logo.png'))
    print('wrote Fatima Desk Android icons')


if __name__ == '__main__':
    main()
