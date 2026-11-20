#!/usr/bin/env python3
"""Build-time glyph table for the 20 November front-page renderer.

Uses the local DejaVu fonts (via Pillow) to rasterise every character the
page needs at 64 px, then writes font_data.py next to main.py: a dict of
bit-packed bitmaps with per-glyph metrics. This script runs only at build
time; the graded program (main.py) is pure Python stdlib and never imports
Pillow or touches the network.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PX = 64
REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

WANTED = "".join(chr(c) for c in range(32, 127))
WANTED += "\u2014\u2013\u00b7\u2022\u2018\u2019\u201c\u201d\u20ac\u00d7\u00b0\u2026"


def glyph_bitmap(font, ch):
    """Rasterise one glyph; return (w, h, advance, yoff, hexbits).

    yoff is the ink-top offset from the ascender line, so the renderer can
    line every glyph up on one shared baseline. Bits are packed MSB-first,
    row-major, over the ink bounding box only.
    """
    canvas = Image.new("L", (PX * 3, PX * 3), 0)
    pen = ImageDraw.Draw(canvas)
    pen.text((PX, PX), ch, font=font, fill=255)
    box = canvas.getbbox()
    if box is None:
        return 0, 0, int(round(font.getlength(ch))), 0, ""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    px = canvas.load()
    packed = bytearray()
    acc, n = 0, 0
    for yy in range(y0, y1):
        for xx in range(x0, x1):
            acc = (acc << 1) | (1 if px[xx, yy] > 110 else 0)
            n += 1
            if n == 8:
                packed.append(acc)
                acc, n = 0, 0
    if n:
        packed.append(acc << (8 - n))
    return w, h, int(round(font.getlength(ch))), y0 - PX, packed.hex()


def main():
    fonts = {
        "regular": ImageFont.truetype(REG, PX),
        "bold": ImageFont.truetype(BOLD, PX),
    }
    out = Path(__file__).resolve().parent.parent / "font_data.py"
    buf = [
        "# Glyph bitmaps, generated at build time by",
        "# tools/generate_font_data.py from the local DejaVu fonts.",
        "# GLYPHS[(weight, char)] = (width, height, advance, y-offset, hex).",
        "# Bitmaps are 1 bit per pixel, MSB first, row-major over the ink box.",
        "FONT_SIZE = %d" % PX,
        "GLYPHS = {",
    ]
    count = 0
    for weight in ("regular", "bold"):
        font = fonts[weight]
        for ch in WANTED:
            w, h, adv, yoff, hexbits = glyph_bitmap(font, ch)
            buf.append("    (%r, %r): (%d, %d, %d, %d, %r)," % (
                weight, ch, w, h, adv, yoff, hexbits))
            count += 1
    buf.append("}")
    buf.append("")
    out.write_text("\n".join(buf), encoding="utf-8")
    print("wrote", out, "glyphs:", count, "bytes:", out.stat().st_size)


if __name__ == "__main__":
    main()
