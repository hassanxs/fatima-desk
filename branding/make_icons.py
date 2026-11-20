"""Fatima Desk logo generator.

Draws the Fatima Desk logo (a monitor with a bold "F" and an amber remote
cursor, on a blue-to-violet rounded tile) and writes every icon file the
Windows, macOS, Linux and iOS builds use. Run from the repository root:

    python branding/make_icons.py            # write all icon files
    python branding/make_icons.py --preview  # only write branding/preview.png

All geometry lives on a 1024x1024 canvas and is shared by the SVG and the
PNG renderer, so the vector and raster icons always match.
"""
import os
import sys

from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---- Design tokens -------------------------------------------------------
BLUE = (59, 91, 255)      # #3B5BFF  gradient start (top-left)
VIOLET = (123, 63, 228)   # #7B3FE4  gradient end (bottom-right)
WHITE = (255, 255, 255)
AMBER = (255, 201, 74)    # #FFC94A  remote cursor
INK = (25, 25, 25)        # monochrome tray glyph on light menu bars

# ---- Geometry (1024 canvas) ---------------------------------------------
TILE_RADIUS = 224
MONITOR = (192, 232, 832, 712)          # outer box of the screen frame
MONITOR_RADIUS = 72
MONITOR_STROKE = 64
NECK = (472, 712, 552, 796)
BASE = (352, 792, 672, 848)
BASE_RADIUS = 28
F_BARS = [                              # the letter F, as three bars
    (372, 352, 452, 600),               # stem
    (372, 352, 652, 420),               # top arm
    (372, 452, 592, 520),               # middle arm
]
CURSOR = [(612, 470), (612, 614), (648, 580), (673, 638),
          (697, 628), (672, 572), (719, 572)]


def _hex(c):
    return '#%02X%02X%02X' % c


# ---- SVG -----------------------------------------------------------------
def svg(tile=True, glyph=WHITE, cursor=AMBER):
    s = MONITOR_STROKE / 2
    x0, y0, x1, y1 = MONITOR
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024" width="1024" height="1024">']
    if tile:
        parts += [
            '<defs><linearGradient id="fd-bg" x1="0" y1="0" x2="1" y2="1">',
            f'<stop offset="0" stop-color="{_hex(BLUE)}"/><stop offset="1" stop-color="{_hex(VIOLET)}"/>',
            '</linearGradient></defs>',
            f'<rect width="1024" height="1024" rx="{TILE_RADIUS}" fill="url(#fd-bg)"/>',
        ]
    g = _hex(glyph)
    parts.append(
        f'<rect x="{x0 + s}" y="{y0 + s}" width="{x1 - x0 - 2 * s}" height="{y1 - y0 - 2 * s}" '
        f'rx="{MONITOR_RADIUS - s}" fill="none" stroke="{g}" stroke-width="{MONITOR_STROKE}"/>')
    for (a, b, c, d) in [NECK] + F_BARS:
        parts.append(f'<rect x="{a}" y="{b}" width="{c - a}" height="{d - b}" fill="{g}"/>')
    a, b, c, d = BASE
    parts.append(f'<rect x="{a}" y="{b}" width="{c - a}" height="{d - b}" rx="{BASE_RADIUS}" fill="{g}"/>')
    pts = ' '.join(f'{x},{y}' for x, y in CURSOR)
    parts.append(f'<polygon points="{pts}" fill="{_hex(cursor)}" stroke-linejoin="round"/>')
    parts.append('</svg>')
    return '\n'.join(parts) + '\n'


def wordmark_svg():
    """Icon plus the "Fatima Desk" name, for headers and about pages."""
    inner = svg().split('\n', 1)[1].rsplit('</svg>', 1)[0]
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 3600 1024" width="3600" height="1024">\n'
        f'{inner}'
        f'<text x="1180" y="690" font-family="Segoe UI, Helvetica Neue, Arial, sans-serif" '
        f'font-size="460" font-weight="700" fill="{_hex(VIOLET)}">Fatima Desk</text>\n'
        '</svg>\n')


# ---- Raster --------------------------------------------------------------
def _gradient(size):
    """Diagonal blue-to-violet gradient, size x size."""
    ramp = Image.linear_gradient('L').resize((size * 2, size * 2)).rotate(45, resample=Image.BICUBIC)
    off = size // 2
    mask = ramp.crop((off, off, off + size, off + size))
    lo, hi = mask.getextrema()
    mask = mask.point(lambda v: int((v - lo) * 255 / max(1, hi - lo)))
    return Image.composite(Image.new('RGB', (size, size), VIOLET),
                           Image.new('RGB', (size, size), BLUE), mask)


def render(size, tile=True, glyph=WHITE, cursor=AMBER, margin=0.0):
    """Render the logo at `size` px. `margin` is the fraction of empty
    border around the tile (macOS icons use about 10%)."""
    ss = 4                                   # supersample for smooth edges
    big = 1024 * ss
    k = ss
    img = Image.new('RGBA', (big, big), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if tile:
        mask = Image.new('L', (big, big), 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, big - 1, big - 1), TILE_RADIUS * k, fill=255)
        img.paste(_gradient(big), (0, 0), mask)
    x0, y0, x1, y1 = (v * k for v in MONITOR)
    d.rounded_rectangle((x0, y0, x1, y1), MONITOR_RADIUS * k, fill=glyph + (255,))
    st = MONITOR_STROKE * k
    hole = Image.new('L', (big, big), 0)
    ImageDraw.Draw(hole).rounded_rectangle((x0 + st, y0 + st, x1 - st, y1 - st),
                                           (MONITOR_RADIUS - MONITOR_STROKE // 2) * k, fill=255)
    if tile:
        img.paste(_gradient(big), (0, 0), hole)
    else:
        img.paste((0, 0, 0, 0), (0, 0), hole)
    for box in [NECK] + F_BARS:
        d.rectangle(tuple(v * k for v in box), fill=glyph + (255,))
    d.rounded_rectangle(tuple(v * k for v in BASE), BASE_RADIUS * k, fill=glyph + (255,))
    d.polygon([(x * k, y * k) for x, y in CURSOR], fill=cursor + (255,))
    out = img.resize((size, size), Image.LANCZOS)
    if margin:
        inner = round(size * (1 - 2 * margin))
        canvas = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        canvas.paste(out.resize((inner, inner), Image.LANCZOS), ((size - inner) // 2,) * 2)
        out = canvas
    return out


# ---- Output --------------------------------------------------------------
def p(rel):
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path


def write_text(rel, text):
    with open(p(rel), 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)


def main():
    if '--preview' in sys.argv:
        sheet = Image.new('RGBA', (1400, 560), (245, 246, 250, 255))
        sheet.paste(render(512), (20, 24), render(512))
        x = 560
        for s in (256, 128, 64, 32, 16):
            im = render(s)
            sheet.paste(im, (x, 280 - s // 2), im)
            x += s + 30
        dark = Image.new('RGBA', (200, 120), (30, 30, 30, 255))
        g = render(48, tile=False, glyph=WHITE, cursor=WHITE)
        dark.paste(g, (20, 36), g)
        light = Image.new('RGBA', (200, 120), (236, 236, 236, 255))
        g = render(48, tile=False, glyph=INK, cursor=INK)
        light.paste(g, (110, 36), g)
        sheet.paste(dark, (560, 420)); sheet.paste(light, (780, 420))
        sheet.convert('RGB').save(p('branding/preview.png'))
        print('wrote branding/preview.png')
        return

    # Vector masters
    write_text('branding/fatima-desk-logo.svg', svg())
    write_text('branding/fatima-desk-wordmark.svg', wordmark_svg())
    write_text('res/scalable.svg', svg())
    write_text('res/logo.svg', svg())
    write_text('res/logo-header.svg', wordmark_svg())
    write_text('flutter/assets/icon.svg', svg())

    # Desktop PNGs
    render(1024).save(p('res/icon.png'))
    render(1024, margin=0.1).save(p('res/mac-icon.png'))
    for s, name in [(32, '32x32'), (64, '64x64'), (128, '128x128'), (256, '128x128@2x')]:
        render(s).save(p(f'res/{name}.png'))
    if os.path.exists(p('flutter/assets/icon.png')):
        render(512).save(p('flutter/assets/icon.png'))
    render(256).save(p('fastlane/metadata/android/en-US/images/icon.png'))

    # Windows ICO files (multi-resolution)
    ico_sizes = [16, 20, 24, 32, 40, 48, 64, 128, 256]
    master = render(256)
    for rel in ('res/icon.ico', 'flutter/windows/runner/resources/app_icon.ico'):
        master.save(p(rel), sizes=[(s, s) for s in ico_sizes],
                    append_images=[render(s) for s in ico_sizes])
    render(32).save(p('res/tray-icon.ico'), sizes=[(16, 16), (24, 24), (32, 32)],
                    append_images=[render(16), render(24)])

    # macOS app icon and menu-bar (tray) icons
    render(1024, margin=0.1).save(p('flutter/macos/Runner/AppIcon.icns'))
    render(60, tile=False, glyph=INK, cursor=INK).save(p('res/mac-tray-dark-x2.png'))
    render(48, tile=False, glyph=WHITE, cursor=WHITE).save(p('res/mac-tray-light-x2.png'))

    # iOS app icons (opaque, no transparency allowed)
    ios = 'flutter/ios/Runner/Assets.xcassets/AppIcon.appiconset'
    for f in os.listdir(p(ios)):
        if f.endswith('.png'):
            with Image.open(p(f'{ios}/{f}')) as old:
                w = old.size[0]
            bg = Image.new('RGB', (w, w), BLUE)
            icon = render(w)
            # iOS masks its own corners: fill the tile edge to edge.
            bg.paste(_gradient(w), (0, 0))
            bg.paste(icon, (0, 0), icon)
            bg.save(p(f'{ios}/{f}'))
    print('wrote all Fatima Desk icon files')


if __name__ == '__main__':
    main()
