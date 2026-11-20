#!/usr/bin/env python3
"""THE WORLD TODAY - Friday 20 November 2026, in one image.

Pure-stdlib Python 3.13 program. Draws a newspaper front page summing up
the day's world news and writes it to /output/entry.png (1024x1024 PNG,
under 1 MiB, byte-identical on every run: no network, no clock, no random).

Stories (all happened or first reported on Friday 20 November 2026):
  LEAD    The International Court of Justice rules Myanmar committed
          genocide against the Rohingya - the first such ruling against a
          state in the court's history. Nine judges to six.
  WEATHER Cyclone Akvan makes landfall near Gopalpur, Odisha, 8.30 am,
          70-80 km/h gusting to 90; 300,000 evacuated, 69 trains cancelled.
  SUMMIT  First-ever Trump-Xi-Putin trilateral in Shenzhen; a four-point
          joint declaration, but no deal on Ukraine or nuclear arms.
  MARKETS Nikkei -4.8% in Tokyo, S&P 500 -2% for a fifth straight day;
          SoftBank -16%. Anthropic debuts on Nasdaq, +17% at $97.
  CULTURE GTA VI: Sensor Tower estimates 24.6m copies and $2.36bn on its
          first day - the biggest entertainment launch ever.
  CONFLICT A Houthi missile damages the Saudi wealth-fund tower in Riyadh;
          Ukraine hits the Kerch Bridge a third time in four days.
  ALSO    COP31 draft drops fossil fuels; Kenya's last Ebola patient goes
          home; U.S. Senate rejects Iran war-powers 51-48; U.S. loses
          measles elimination status; Jeffries nominated Speaker 251-11;
          Cambridge Dictionary's word of the year is "Human".

Run it:  mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""
import binascii
import math
import os
import struct
import sys
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from font_data import FONT_SIZE, GLYPHS

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (246, 240, 226)
PANEL = (255, 253, 247)
INK = (22, 18, 13)
MUTED = (96, 88, 74)
RED = (158, 27, 30)
RED_DK = (120, 18, 22)
NAVY = (28, 54, 90)
STEEL = (70, 108, 150)
GOLD = (168, 124, 0)
TEAL = (14, 90, 96)
SEA = (186, 214, 230)
SEA_DK = (140, 182, 206)
COAST = (232, 218, 184)
COAST_DK = (204, 186, 138)
PURPLE = (88, 24, 88)
ORANGE = (244, 140, 40)
SUN = (250, 204, 72)
PINK = (232, 90, 130)
WHITE = (255, 255, 255)
SKY_TOP = (46, 24, 64)
SKY_BOT = (232, 90, 130)


# ------------------------------------------------------------------- PNG
def _chunk(kind, payload):
    blob = struct.pack(">I", len(payload)) + kind + payload
    return blob + struct.pack(">I", binascii.crc32(kind + payload) & 0xFFFFFFFF)


def encode_png(pixels, width, height):
    body = bytearray()
    stride = width * 3
    for row in range(height):
        body.append(0)
        body += pixels[row * stride:(row + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr)
            + _chunk(b"IDAT", zlib.compress(bytes(body), 9))
            + _chunk(b"IEND", b""))


# ---------------------------------------------------------------- screen
class Screen:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.buf = bytearray(bg * (w * h))

    def dot(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i:i + 3] = bytes(c)

    def fill(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(c) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.buf[i:i + (x1 - x0) * 3] = row

    def hrule(self, x, y, w, c, t=1):
        self.fill(x, y, w, t, c)

    def vrule(self, x, y, h, c, t=1):
        self.fill(x, y, t, h, c)

    def disc(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            dx = int(math.sqrt(max(0, r * r - (yy - cy) ** 2)))
            self.fill(cx - dx, yy, dx * 2 + 1, 1, c)

    def ring(self, cx, cy, r, c, t=2):
        for yy in range(cy - r, cy + r + 1):
            dx = int(math.sqrt(max(0, r * r - (yy - cy) ** 2)))
            self.fill(cx - dx, yy, dx * 2 + 1, t, c)
            self.fill(cx - dx, yy + (2 * r - t) if False else yy, 0, 0, c)
        # redraw as outline: outer disc minus inner disc
        for yy in range(cy - r, cy + r + 1):
            dxo = int(math.sqrt(max(0, r * r - (yy - cy) ** 2)))
            dxi = int(math.sqrt(max(0, (r - t) * (r - t) - (yy - cy) ** 2))) if abs(yy - cy) < r - t else 0
            if dxo > dxi:
                self.fill(cx - dxo, yy, dxo - dxi, 1, c)
                self.fill(cx + dxi + 1, yy, dxo - dxi, 1, c)

    def seg(self, x0, y0, x1, y1, c, t=1):
        dx, dy = x1 - x0, y1 - y0
        steps = max(abs(dx), abs(dy), 1)
        r = max(1, t // 2)
        for s in range(steps + 1):
            self.disc(x0 + dx * s // steps, y0 + dy * s // steps, r, c)

    def fill_poly(self, pts, c):
        ys = [p[1] for p in pts]
        n = len(pts)
        for y in range(max(0, min(ys)), min(self.h, max(ys) + 1)):
            xs = []
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.fill(int(xs[i]), y, max(1, int(xs[i + 1]) - int(xs[i])), 1, c)


# ------------------------------------------------------------------ text
def measure(s, size, bold=False):
    weight = "bold" if bold else "regular"
    scale = size / FONT_SIZE
    total = 0.0
    for ch in s:
        g = GLYPHS.get((weight, ch), GLYPHS[(weight, " ")])
        total += g[2] * scale
    return total


def render_text(cv, x, y, s, size, color, bold=False, align="left"):
    """Draw text with the ascender top at y. Returns the width drawn."""
    weight = "bold" if bold else "regular"
    if align == "center":
        x = x - measure(s, size, bold) / 2
    elif align == "right":
        x = x - measure(s, size, bold)
    scale = size / FONT_SIZE
    cx = float(x)
    for ch in s:
        g = GLYPHS.get((weight, ch))
        if g is None:
            g = GLYPHS[(weight, " ")]
        w, h, adv, yoff, data = g
        if w and h and data:
            bits = bytes.fromhex(data)
            dw = max(1, int(round(w * scale)))
            dh = max(1, int(round(h * scale)))
            top = int(y + yoff * scale)
            for dy in range(dh):
                sy = min(h - 1, int(dy / scale)) if scale > 0 else 0
                for dx in range(dw):
                    sx = min(w - 1, int(dx / scale)) if scale > 0 else 0
                    bit = sy * w + sx
                    if bits[bit // 8] & (0x80 >> (bit % 8)):
                        cv.dot(int(cx) + dx, top + dy, color)
        cx += adv * scale
    return cx - x


def wrap_text(s, size, bold, maxw):
    lines, cur = [], ""
    for word in s.split(" "):
        trial = word if not cur else cur + " " + word
        if measure(trial, size, bold) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def block_text(cv, x, y, s, size, color, bold, maxw, leading=None):
    lead = leading if leading is not None else int(size * 1.28)
    for ln in wrap_text(s, size, bold, maxw):
        render_text(cv, x, y, ln, size, color, bold)
        y += lead
    return y


# -------------------------------------------------------------- furniture
def panel(cv, x, y, w, h, kicker, kcolor):
    cv.fill(x, y, w, h, PANEL)
    cv.hrule(x, y, w, INK, 2)
    cv.hrule(x, y + h - 2, w, INK, 2)
    cv.vrule(x, y, h, INK, 2)
    cv.vrule(x + w - 2, y, h, INK, 2)
    cv.fill(x, y, w, 26, kcolor)
    render_text(cv, x + 10, y + 5, kicker, 14, WHITE, bold=True)


def flag_us(cv, x, y, w, h):
    for i in range(13):
        cv.fill(x, y + i * h // 13, w, h // 13 + 1,
                WHITE if i % 2 else RED)
    cv.fill(x, y, w * 2 // 5, h * 7 // 13, NAVY)
    for r in range(3):
        for c in range(5):
            cv.disc(x + 5 + c * 7, y + 4 + r * 6, 1, WHITE)


def flag_cn(cv, x, y, w, h):
    cv.fill(x, y, w, h, RED)
    cx, cy = x + 16, y + 12
    star = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = 11 if i % 2 == 0 else 4
        star.append((int(cx + rr * math.cos(ang)), int(cy + rr * math.sin(ang))))
    cv.fill_poly(star, SUN)


def flag_ru(cv, x, y, w, h):
    cv.fill(x, y, w, h // 3 + 1, WHITE)
    cv.fill(x, y + h // 3, w, h // 3 + 1, STEEL)
    cv.fill(x, y + 2 * h // 3, w, h - 2 * h // 3, RED)


# -------------------------------------------------------------- masthead
def draw_masthead(cv):
    cv.hrule(26, 20, 972, INK, 3)
    cv.hrule(26, 24, 972, INK, 1)
    render_text(cv, 26, 28, "EST. 2026", 14, MUTED, bold=True)
    render_text(cv, 998, 28, "ONE DAY \u00b7 ONE IMAGE", 14, MUTED,
                bold=True, align="right")
    render_text(cv, 512, 32, "THE WORLD TODAY", 64, INK, bold=True,
                align="center")
    cv.hrule(26, 108, 972, INK, 1)
    cv.hrule(26, 112, 972, INK, 3)
    render_text(cv, 512, 120, "FRIDAY, 20 NOVEMBER 2026", 22, RED_DK,
                bold=True, align="center")
    render_text(cv, 26, 122, "THE WORLD IN FULL", 14, MUTED, bold=True)
    render_text(cv, 998, 122, "EVERY STORY REPORTED TODAY", 14, MUTED,
                bold=True, align="right")


# ------------------------------------------------------------ lead: ICJ
def draw_scales(cv, x, y, w, h):
    """Scales of justice, drawn in ink and gold."""
    cx = x + w // 2
    top = y + 4
    base = y + h - 6
    cv.fill(cx - 3, top + 12, 6, base - top - 18, INK)
    cv.fill(cx - 26, base, 52, 5, INK)
    cv.fill(cx - 40, base + 5, 80, 3, GOLD)
    cv.seg(cx - 52, top + 12, cx + 52, top + 12, INK, 3)
    cv.disc(cx, top + 6, 6, GOLD)
    for sx in (cx - 52, cx + 52):
        cv.seg(sx, top + 12, sx - 16, top + 34, INK, 2)
        cv.seg(sx, top + 12, sx + 16, top + 34, INK, 2)
        cv.seg(sx - 16, top + 34, sx + 16, top + 34, INK, 2)
        cv.fill_poly([(sx - 16, top + 34), (sx + 16, top + 34),
                      (sx, top + 52)], GOLD)
    cv.disc(cx, top + 12, 3, GOLD)


def draw_lead(cv, y0):
    x, w, h = 26, 620, 318
    panel(cv, x, y0, w, h, "LEAD \u2014 JUSTICE AT THE HAGUE", RED)
    y = y0 + 34
    render_text(cv, x + 12, y, "WORLD COURT RULES", 38, INK, bold=True)
    render_text(cv, x + 12, y + 44, "MYANMAR COMMITTED", 38, INK, bold=True)
    render_text(cv, x + 12, y + 88, "GENOCIDE", 38, RED_DK, bold=True)
    y = y0 + 172
    y = block_text(cv, x + 12, y,
                   "The International Court of Justice finds Myanmar "
                   "responsible for genocide against the Rohingya minority "
                   "\u2014 the first such ruling against a state in the "
                   "court\u2019s history. Nine judges to six.",
                   17, INK, False, w - 24, 21)
    # Scales at right, two fact lines at left.
    sx = x + w - 150
    draw_scales(cv, sx, y0 + 226, 130, 78)
    render_text(cv, x + 12, y0 + 240, "The case was brought", 15, INK)
    render_text(cv, x + 12, y0 + 260, "by The Gambia in 2019.", 15, INK)
    render_text(cv, x + 12, y0 + 280, "Ruling delivered in", 15, MUTED)
    render_text(cv, x + 12, y0 + 300, "The Hague, Thursday.", 15, MUTED)
    return y0 + h


# ---------------------------------------------------------- Akvan panel
def draw_cyclone(cv, x, y, w, h):
    """Schematic Bay of Bengal: coast at left, spiral storm at sea."""
    cv.fill(x, y, w, h, SEA)
    # Land: India's east coast, a diagonal band at the left.
    cv.fill_poly([(x, y), (x + 92, y), (x + 118, y + 44),
                  (x + 104, y + 92), (x + 122, y + h), (x, y + h)], COAST)
    cv.seg(x + 92, y, x + 118, y + 44, COAST_DK, 2)
    cv.seg(x + 118, y + 44, x + 104, y + 92, COAST_DK, 2)
    cv.seg(x + 104, y + 92, x + 122, y + h, COAST_DK, 2)
    render_text(cv, x + 8, y + 8, "INDIA", 12, NAVY, bold=True)
    render_text(cv, x + w - 8, y + h - 20, "BAY OF BENGAL", 11, NAVY,
                bold=True, align="right")
    # Spiral: Archimedean, three turns, centred at sea.
    cx, cy = x + w - 108, y + 62
    pts = []
    for i in range(0, 121):
        t = i * 4.4 * math.pi / 120
        r = 3 + 9.5 * t / math.pi
        pts.append((int(cx + r * math.cos(t)), int(cy + r * math.sin(t))))
    for i in range(len(pts) - 1):
        cv.seg(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], TEAL, 3)
    cv.disc(cx, cy, 6, RED)
    cv.disc(cx, cy, 2, WHITE)
    # Gopalpur marker on the coast.
    gx, gy = x + 112, y + 66
    cv.disc(gx, gy, 7, RED)
    cv.disc(gx, gy, 3, WHITE)
    render_text(cv, gx + 12, gy - 10, "GOPALPUR", 12, INK, bold=True)


def draw_akvan(cv, y0):
    x, w, h = 662, 336, 318
    panel(cv, x, y0, w, h, "WEATHER \u00b7 EASTERN INDIA", TEAL)
    y = y0 + 34
    render_text(cv, x + 12, y, "AKVAN HITS THE", 25, INK, bold=True)
    render_text(cv, x + 12, y + 29, "ODISHA COAST", 25, INK, bold=True)
    draw_cyclone(cv, x + 12, y0 + 98, w - 24, 128)
    y = y0 + 236
    render_text(cv, x + 12, y, "Landfall 8.30 am near Gopalpur", 14, INK)
    render_text(cv, x + 12, y + 19, "Winds 70\u201380 km/h, gusts to 90", 14, INK)
    render_text(cv, x + 12, y + 38, "300,000 evacuated; 69 trains cut", 14, INK)
    render_text(cv, x + 12, y + 57, "No deaths reported so far", 14, MUTED)
    return y0 + h


# ------------------------------------------------------------ row 2
def draw_summit(cv, x, y, w, h):
    panel(cv, x, y, w, h, "SUMMIT \u00b7 SHENZHEN, CHINA", NAVY)
    ty = y + 34
    render_text(cv, x + 12, ty, "TRUMP, XI AND PUTIN", 25, INK, bold=True)
    render_text(cv, x + 12, ty + 29, "MEET AT LAST", 25, INK, bold=True)
    block_text(cv, x + 12, ty + 62,
               "The first-ever three-way summit. A four-point joint "
               "declaration \u2014 but no deal on Ukraine or nuclear arms.",
               15, INK, False, w - 24, 19)
    fw, fh = 84, 40
    gap = (w - 24 - 3 * fw) // 2
    fy = y + h - 58
    flag_us(cv, x + 12, fy, fw, fh)
    flag_cn(cv, x + 12 + fw + gap, fy, fw, fh)
    flag_ru(cv, x + 12 + 2 * (fw + gap), fy, fw, fh)
    render_text(cv, x + 12 + fw // 2, fy + fh + 4, "U.S.A.", 12, INK,
                bold=True, align="center")
    render_text(cv, x + 12 + fw + gap + fw // 2, fy + fh + 4, "CHINA", 12,
                INK, bold=True, align="center")
    render_text(cv, x + 12 + 2 * (fw + gap) + fw // 2, fy + fh + 4,
                "RUSSIA", 12, INK, bold=True, align="center")


def draw_markets(cv, x, y, w, h):
    panel(cv, x, y, w, h, "MARKETS \u00b7 TOKYO & NEW YORK", RED_DK)
    ty = y + 34
    render_text(cv, x + 12, ty, "STOCKS SLIDE AS", 25, INK, bold=True)
    render_text(cv, x + 12, ty + 29, "AI FEARS SPREAD", 25, INK, bold=True)
    block_text(cv, x + 12, ty + 62,
               "Nikkei -4.8% in Tokyo; SoftBank -16%. S&P 500 -2% \u2014 a "
               "fifth straight day down. Anthropic debuts on Nasdaq, "
               "+17% at $97.",
               15, INK, False, w - 24, 19)
    # Falling chart, Mon to Fri.
    cx, cy, cw, ch = x + 12, y + 158, w - 24, 30
    cv.hrule(cx, cy + ch, cw, INK, 1)
    cv.vrule(cx, cy, ch, INK, 1)
    pts = [(int(cx + cw * f / 4), int(cy + ch * v)) for f, v in
           ((0, 0.15), (1, 0.30), (2, 0.48), (3, 0.72), (4, 0.92))]
    for i in range(len(pts) - 1):
        cv.seg(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], RED, 3)
    for px, py in pts:
        cv.disc(px, py, 4, RED)
        cv.disc(px, py, 2, WHITE)
    render_text(cv, cx, cy + ch + 4, "MON", 11, MUTED, bold=True)
    render_text(cv, cx + cw, cy + ch + 4, "FRI", 11, MUTED, bold=True,
                align="right")


# ------------------------------------------------------------ row 3
def draw_gta(cv, x, y, w, h):
    panel(cv, x, y, w, h, "CULTURE \u00b7 LEONIDA", PURPLE)
    ty = y + 34
    render_text(cv, x + 12, ty, "GTA VI: $2.36BN", 25, INK, bold=True)
    render_text(cv, x + 12, ty + 29, "IN A SINGLE DAY", 25, INK, bold=True)
    # Neon dusk sky strip with a Vice City skyline.
    sx, sy, sw, sh = x + 12, y + 96, w - 24, 42
    for i in range(sh):
        t = i / sh
        r = int(SKY_TOP[0] + (SKY_BOT[0] - SKY_TOP[0]) * t)
        g = int(SKY_TOP[1] + (SKY_BOT[1] - SKY_TOP[1]) * t)
        b = int(SKY_TOP[2] + (SKY_BOT[2] - SKY_TOP[2]) * t)
        cv.hrule(sx, sy + i, sw, (r, g, b))
    cv.disc(sx + sw - 52, sy + 14, 10, SUN)
    heights = [16, 24, 20, 28, 18, 26, 22, 30, 18, 26, 20, 28]
    bw = sw // len(heights)
    for i, hh in enumerate(heights):
        cv.fill(sx + i * bw + 2, sy + sh - hh, bw - 4, hh, (20, 10, 30))
    render_text(cv, sx + 10, sy + 4, "VI", 30, WHITE, bold=True)
    block_text(cv, x + 12, y + 144,
               "24.6 million copies on launch day, Sensor Tower estimates "
               "\u2014 the biggest entertainment launch ever.",
               14, INK, False, w - 24, 18)


def draw_conflict(cv, x, y, w, h):
    panel(cv, x, y, w, h, "CONFLICT \u00b7 RIYADH & CRIMEA", RED_DK)
    ty = y + 34
    render_text(cv, x + 12, ty, "MISSILE HITS", 25, INK, bold=True)
    render_text(cv, x + 12, ty + 29, "RIYADH TOWER", 25, INK, bold=True)
    block_text(cv, x + 12, ty + 62,
               "A Houthi missile damages Saudi Arabia\u2019s sovereign "
               "wealth-fund tower in the capital\u2019s financial district. "
               "Ukraine hits the Kerch Bridge a third time in four days.",
               15, INK, False, w - 24, 19)


# ------------------------------------------------------------ also today
def draw_also(cv, y):
    x, w = 26, 972
    cv.hrule(x, y, w, INK, 2)
    render_text(cv, x, y + 6, "ALSO TODAY", 16, RED_DK, bold=True)
    render_text(cv, x + w, y + 6,
                "Sources: Reuters, AP, The Hindu, IMD, Sensor Tower",
                13, MUTED, align="right")
    colw = (w - 40) // 3
    items = [
        ("COP31", "Draft deal drops fossil fuels; Adaptation Fund wins "
         "$50m in pledges."),
        ("EBOLA", "Kenya discharges its last Ebola patient, 37 days after "
         "the first case."),
        ("IRAN VOTE", "U.S. Senate rejects war-powers resolution, 51\u201348."),
        ("MEASLES", "U.S. loses measles elimination status, first time "
         "since 2000."),
        ("SPEAKER", "Democrats nominate Hakeem Jeffries, 251\u201311."),
        ("WORD OF THE YEAR", "Cambridge Dictionary picks \u201cHuman\u201d "
         "for 2026."),
    ]
    for row in range(2):
        ty = y + 30 + row * 44
        for col in range(3):
            head, body = items[row * 3 + col]
            cx = x + col * (colw + 20)
            render_text(cv, cx, ty, head, 13, INK, bold=True)
            block_text(cv, cx, ty + 17, body, 12, INK, False, colw, 15)
    return y + 30 + 2 * 44


# ------------------------------------------------------------------ main
def build():
    cv = Screen(W, H, PAPER)
    cv.hrule(0, 0, W, INK, 4)
    cv.hrule(0, H - 4, W, INK, 4)
    cv.vrule(0, 0, H, INK, 4)
    cv.vrule(W - 4, 0, H, INK, 4)
    draw_masthead(cv)
    draw_lead(cv, 152)
    draw_akvan(cv, 152)
    gap, pw = 16, (972 - 16) // 2
    row2 = 478
    draw_summit(cv, 26, row2, pw, 210)
    draw_markets(cv, 26 + pw + gap, row2, pw, 210)
    row3 = 696
    draw_gta(cv, 26, row3, pw, 180)
    draw_conflict(cv, 26 + pw + gap, row3, pw, 180)
    y = draw_also(cv, 880)
    cv.hrule(26, y + 4, 972, INK, 1)
    render_text(cv, 512, y + 10,
                "Every story above happened or was first reported on "
                "Friday 20 November 2026",
                12, MUTED, align="center")
    return cv, y + 10 + 12


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    cv, bottom = build()
    data = encode_png(bytes(cv.buf), W, H)
    path = os.path.join(outdir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    print("WROTE", path, len(data), "bytes; bottom edge at y =", bottom)


if __name__ == "__main__":
    main()
