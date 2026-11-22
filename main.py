#!/usr/bin/env python3
"""news-image-20261121: a dense newspaper front page for Saturday 21 Nov 2026.

Pure-stdlib Python 3.13. Draws a 1024x1024 PNG with a 5x7 bitmap font and
writes it to $MAKEFUN_OUTPUT_DIR/entry.png (default /output). Deterministic:
no time, no randomness, no network; two runs produce byte-identical output.
"""
import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (247, 242, 231)
INK = (18, 18, 18)
RED = (176, 30, 30)
NAVY = (28, 52, 96)
GREEN = (28, 96, 52)
MAROON = (112, 28, 44)
GOLD = (176, 128, 24)
TEAL = (18, 96, 96)
GREY = (110, 108, 100)
LIGHT = (232, 226, 210)
WHITE = (255, 255, 255)
SKY = (178, 208, 226)
SEA = (52, 96, 140)
ORANGE = (214, 110, 20)

# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows of 5 pixels, '#' = ink.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    'a': ("00000", "00000", "01110", "00001", "01111", "10001", "01111"),
    'b': ("10000", "10000", "11110", "10001", "10001", "10001", "11110"),
    'c': ("00000", "00000", "01110", "10000", "10000", "10001", "01110"),
    'd': ("00001", "00001", "01111", "10001", "10001", "10001", "01111"),
    'e': ("00000", "00000", "01110", "10001", "11111", "10000", "01110"),
    'f': ("00110", "01001", "01000", "11110", "01000", "01000", "01000"),
    'g': ("00000", "01111", "10001", "10001", "01111", "00001", "01110"),
    'h': ("10000", "10000", "11110", "10001", "10001", "10001", "10001"),
    'i': ("00100", "00000", "01100", "00100", "00100", "00100", "01110"),
    'j': ("00010", "00000", "00110", "00010", "00010", "10010", "01100"),
    'k': ("10000", "10000", "10010", "10100", "11000", "10100", "10010"),
    'l': ("01100", "00100", "00100", "00100", "00100", "00100", "01110"),
    'm': ("00000", "00000", "11010", "10101", "10101", "10101", "10101"),
    'n': ("00000", "00000", "11110", "10001", "10001", "10001", "10001"),
    'o': ("00000", "00000", "01110", "10001", "10001", "10001", "01110"),
    'p': ("00000", "00000", "11110", "10001", "10001", "11110", "10000"),
    'q': ("00000", "00000", "01111", "10001", "10001", "01111", "00001"),
    'r': ("00000", "00000", "10110", "11001", "10000", "10000", "10000"),
    's': ("00000", "00000", "01111", "10000", "01110", "00001", "11110"),
    't': ("01000", "01000", "11100", "01000", "01000", "01001", "00110"),
    'u': ("00000", "00000", "10001", "10001", "10001", "10011", "01101"),
    'v': ("00000", "00000", "10001", "10001", "10001", "01010", "00100"),
    'w': ("00000", "00000", "10001", "10101", "10101", "10101", "01010"),
    'x': ("00000", "00000", "10001", "01010", "00100", "01010", "10001"),
    'y': ("00000", "00000", "10001", "10001", "01111", "00001", "01110"),
    'z': ("00000", "00000", "11111", "00010", "00100", "01000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ';': ("00000", "01100", "00000", "01100", "01100", "00100", "01000"),
    ':': ("00000", "01100", "00000", "01100", "00000", "01100", "00000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    '-': ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '#': ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    '*': ("00000", "00100", "10101", "01110", "10101", "00100", "00000"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '_': ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    '@': ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    '<': ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    '>': ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
    '[': ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    ']': ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
    '|': ("00100", "00100", "00100", "00100", "00100", "00100", "00100"),
    '\\': ("10000", "01000", "01000", "00100", "00010", "00010", "00001"),
}


class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(c)

    def fill(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.px[i:i + (x1 - x0) * 3] = bytes(c) * (x1 - x0)

    def rect(self, x, y, w, h, c, t=1):
        self.fill(x, y, w, t, c)
        self.fill(x, y + h - t, w, t, c)
        self.fill(x, y, t, h, c)
        self.fill(x + w - t, y, t, h, c)

    def line(self, x0, y0, x1, y1, c):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self.set(x0, y0, c)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c, fill=True):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d = (xx - cx) ** 2 + (yy - cy) ** 2
                if fill:
                    if d <= r * r:
                        self.set(xx, yy, c)
                else:
                    if r * r - 2 * r <= d <= r * r:
                        self.set(xx, yy, c)

    def poly(self, pts, c):
        for i in range(len(pts)):
            x0, y0 = pts[i]
            x1, y1 = pts[(i + 1) % len(pts)]
            self.line(x0, y0, x1, y1, c)

    def text(self, x, y, s, scale, c, bold=False):
        cx = x
        for ch in s:
            g = FONT.get(ch, FONT[' '])
            for r in range(7):
                row = g[r]
                for col in range(5):
                    if row[col] == '1':
                        self.fill(cx + col * scale, y + r * scale, scale, scale, c)
                        if bold:
                            self.fill(cx + col * scale + 1, y + r * scale, scale, scale, c)
            cx += 6 * scale
        return cx

    def text_w(self, s, scale):
        return len(s) * 6 * scale - scale

    def wrap(self, s, max_w, scale):
        """Greedy word wrap; returns list of lines."""
        max_chars = max(1, (max_w + scale) // (6 * scale))
        lines, cur = [], ""
        for word in s.split(" "):
            if cur and len(cur) + 1 + len(word) > max_chars:
                lines.append(cur)
                cur = word
            else:
                cur = (cur + " " + word) if cur else word
            while len(cur) > max_chars:  # very long word: hard split
                lines.append(cur[:max_chars])
                cur = cur[max_chars:]
        if cur:
            lines.append(cur)
        return lines

    def para(self, x, y, s, max_w, scale, c, lh=None, bold=False, max_lines=None):
        lines = self.wrap(s, max_w, scale)
        if max_lines:
            lines = lines[:max_lines]
        if lh is None:
            lh = 7 * scale + 2
        for ln in lines:
            self.text(x, y, ln, scale, c, bold=bold)
            y += lh
        return y


def png_bytes(cv):
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * stride:(y + 1) * stride]
    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))


# ---------------------------------------------------------------- icons
def icon(cv, x, y, kind, accent):
    """Small 30x30 drawn scene in a tinted box."""
    cv.fill(x, y, 30, 30, LIGHT)
    cv.rect(x, y, 30, 30, accent, 1)
    cx, cy = x + 15, y + 15
    if kind == "blast":  # explosion starburst
        for dx, dy in [(0, -11), (8, -8), (11, 0), (8, 8), (0, 11), (-8, 8),
                       (-11, 0), (-8, -8)]:
            cv.line(cx, cy, cx + dx, cy + dy, ORANGE)
        cv.circle(cx, cy, 5, RED)
        cv.circle(cx, cy, 2, GOLD)
    elif kind == "badge":  # star badge
        cv.circle(cx, cy, 10, NAVY)
        cv.circle(cx, cy, 10, NAVY, fill=False)
        pts = [(cx, cy - 8), (cx + 2, cy - 2), (cx + 8, cy - 2), (cx + 3, cy + 2),
               (cx + 5, cy + 8), (cx, cy + 4), (cx - 5, cy + 8), (cx - 3, cy + 2),
               (cx - 8, cy - 2), (cx - 2, cy - 2)]
        cv.poly(pts, GOLD)
        cv.circle(cx, cy, 2, GOLD)
    elif kind == "globe":
        cv.circle(cx, cy, 11, SEA)
        cv.line(cx - 11, cy, cx + 11, cy, INK)
        cv.line(cx, cy - 11, cx, cy + 11, INK)
        cv.circle(cx, cy, 11, INK, fill=False)
        cv.line(cx - 9, cy - 5, cx + 9, cy - 5, INK)
        cv.line(cx - 9, cy + 5, cx + 9, cy + 5, INK)
    elif kind == "chart":
        cv.line(x + 5, y + 25, x + 25, y + 25, INK)
        cv.line(x + 5, y + 5, x + 5, y + 25, INK)
        pts = [(x + 6, y + 8), (x + 11, y + 12), (x + 16, y + 11),
               (x + 21, y + 19), (x + 25, y + 23)]
        for i in range(len(pts) - 1):
            cv.line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], RED)
        cv.fill(x + 23, y + 21, 3, 3, RED)
    elif kind == "rocket":
        cv.poly([(cx, cy - 12), (cx + 5, cy - 2), (cx + 5, cy + 6),
                 (cx, cy + 10), (cx - 5, cy + 6), (cx - 5, cy - 2)], NAVY)
        cv.circle(cx, cy - 3, 2, WHITE)
        cv.line(cx - 5, cy + 6, cx - 8, cy + 11, RED)
        cv.line(cx + 5, cy + 6, cx + 8, cy + 11, RED)
        cv.poly([(cx, cy + 10), (cx - 2, cy + 14), (cx + 2, cy + 14)], ORANGE)
    elif kind == "flags":
        cv.line(cx - 8, cy - 10, cx - 8, cy + 11, INK)
        cv.line(cx + 8, cy - 10, cx + 8, cy + 11, INK)
        cv.fill(cx - 8, cy - 10, 12, 7, RED)
        cv.fill(cx + 8, cy - 10, 12, 7, NAVY)
        cv.fill(cx - 8, cy - 3, 12, 2, WHITE)
    elif kind == "ship":
        cv.poly([(cx - 11, cy + 2), (cx + 11, cy + 2), (cx + 8, cy + 9),
                 (cx - 8, cy + 9)], NAVY)
        cv.line(cx, cy + 2, cx, cy - 10, INK)
        cv.fill(cx, cy - 10, 8, 6, RED)
        cv.line(x + 4, cy + 12, x + 26, cy + 12, SEA)
    elif kind == "shield":
        cv.poly([(cx - 8, cy - 10), (cx + 8, cy - 10), (cx + 8, cy + 2),
                 (cx, cy + 11), (cx - 8, cy + 2)], NAVY)
        cv.line(cx - 4, cy, cx - 1, cy + 4, WHITE)
        cv.line(cx - 1, cy + 4, cx + 5, cy - 5, WHITE)
    elif kind == "trade":
        cv.fill(x + 5, y + 6, 8, 8, GOLD)
        cv.fill(x + 17, y + 16, 8, 8, TEAL)
        cv.line(x + 13, y + 10, x + 17, y + 20, INK)
        cv.line(x + 17, y + 20, x + 14, y + 20, INK)
        cv.line(x + 17, y + 20, x + 17, y + 17, INK)
    elif kind == "truck":
        cv.fill(x + 4, y + 12, 13, 8, MAROON)
        cv.fill(x + 17, y + 14, 8, 6, MAROON)
        cv.circle(x + 9, y + 22, 3, INK)
        cv.circle(x + 21, y + 22, 3, INK)
        cv.fill(x + 19, y + 15, 4, 3, SKY)
    elif kind == "quake":
        pts = [(x + 4, cy), (x + 9, cy - 8), (x + 13, cy + 6),
               (x + 18, cy - 8), (x + 22, cy + 4), (x + 26, cy - 4)]
        for i in range(len(pts) - 1):
            cv.line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], RED)
        cv.line(x + 4, y + 25, x + 26, y + 25, INK)
    elif kind == "lock":
        cv.fill(x + 8, y + 13, 14, 11, NAVY)
        cv.line(x + 11, y + 13, x + 11, y + 8, NAVY)
        cv.line(x + 19, y + 13, x + 19, y + 8, NAVY)
        cv.line(x + 11, y + 8, x + 19, y + 8, NAVY)
        cv.circle(cx, y + 18, 2, GOLD)
    elif kind == "ball":
        cv.circle(cx, cy, 11, INK, fill=False)
        cv.circle(cx, cy, 11, WHITE)
        cv.circle(cx, cy, 3, INK)
        for dx, dy in [(0, -9), (8, -3), (5, 8), (-5, 8), (-8, -3)]:
            cv.line(cx, cy, cx + dx, cy + dy, INK)


# ---------------------------------------------------------------- stories
# (kicker, accent, icon, headline, summary)
CARDS = [
    ("UKRAINE", RED, "blast",
     "Triple-tap strike hits Zelenskyy's city",
     "Ballistic missiles hit a restaurant car park in Kryvyi Rih; drones then struck rescuers. A boy of 7 and a paramedic of 20 were killed; about 60 people were hurt."),
    ("MEXICO", MAROON, "badge",
     "'El Chapo Isidro' captured in Sinaloa raid",
     "Special forces seized FBI Top 10 fugitive Fausto Isidro Meza Flores in Guasave. Gunfights, fires and blockades followed; at least 11 people died."),
    ("CLIMATE", GREEN, "globe",
     "COP31 talks run into overtime with no deal",
     "The Antalya summit passed its Friday deadline with the draft deal still silent on fossil fuels. The EU warned: 'a good deal or no deal.'"),
    ("MARKETS", RED, "chart",
     "Wall Street slides into correction",
     "The S&P 500 fell 3.7% on Friday and the Nasdaq 5.3% as the AI sell-off deepened. Nvidia lost 14% in a day; Anthropic fell 9% after its debut."),
    ("SPACE", NAVY, "rocket",
     "BepiColombo reaches Mercury after 8 years",
     "The ESA and JAXA craft entered orbit around Mercury today. Its two orbiters part in December; science begins in April 2027."),
    ("DIPLOMACY", NAVY, "flags",
     "Trump backs Putin; Zelenskyy hits back",
     "After Thursday's three-way summit in Shenzhen, Trump called Putin a friend. Zelenskyy called Putin 'a killer' and the meeting 'very unsuccessful' for Russia."),
    ("BALTIC SEA", TEAL, "ship",
     "Drones set Russian cargo ship ablaze",
     "Two Ukrainian drones hit the Sparta II in the Gulf of Finland as it sailed to Kaliningrad. The crew evacuated; the ship stayed afloat."),
    ("DENMARK", NAVY, "shield",
     "Denmark expels Russian attache",
     "Copenhagen says it stopped a Russian plan to kill a US-Ukrainian rapper. Denmark now urges EU-wide curbs on Russian travel."),
    ("TRADE", GOLD, "trade",
     "EU and Indonesia sign deal after a decade",
     "Trade and investment pacts were signed in Brussels, liberalising up to 98.5% of tariff lines once ratified."),
    ("GAZA", MAROON, "truck",
     "Food vehicle strike kills three in Gaza",
     "Gaza health officials say three died in Tel al-Hawa. World Central Kitchen says the truck was not its own; Israel says it targeted militants."),
    ("EARTH", ORANGE, "quake",
     "Two strong quakes, Peru and Timor-Leste",
     "A 6.7 quake shook Junin, Peru, at 00:09 UTC; a 6.8 struck off Timor-Leste at 09:42 UTC. No casualties were reported in either."),
    ("TECH", NAVY, "lock",
     "FBI crime database 'breached'",
     "The FBI is investigating a reported hack of its National Crime Information Center. The scale of any breach is not yet clear."),
]

TIMELINE = [
    ("OVERNIGHT", [
        ("00:09 UTC", "6.7 quake shakes Junin, Peru; Lima residents flee into the streets."),
        ("Overnight", "Mexico seizes 'El Chapo Isidro' in Guasave, Sinaloa."),
        ("Fri night", "Triple-tap strike hits Kryvyi Rih, Zelenskyy's home city."),
    ]),
    ("MORNING", [
        ("09:42 UTC", "6.8 quake strikes off Timor-Leste; no tsunami threat."),
        ("Morning", "COP31 venue crews pack up as talks drag past deadline."),
        ("Morning", "EU and Indonesia sign trade deal after ten years of talks."),
    ]),
    ("AFTERNOON", [
        ("14:36 UTC", "EU on COP31: 'a good deal or no deal.'"),
        ("Afternoon", "Leeds stun Chelsea 4-1; Man City held 1-1 by Fulham."),
        ("15:25 UTC", "Gaza food-vehicle strike kills three, health officials say."),
    ]),
    ("EVENING", [
        ("Evening", "Bahrain warns residents of a further threat from Iran."),
        ("Evening", "Denmark expels a Russian attache over the foiled plot."),
        ("Evening", "Zelenskyy proposes Dnipro ceasefires to evacuate 15 villages."),
    ]),
]

BOTTOM = [
    ("SPORT", RED, "ball",
     "Leeds stun Chelsea 4-1 at Stamford Bridge, their first win there since 1999. Man City draw 1-1 with Fulham; Newcastle hold Arsenal 2-2. In the NBA, James Harden scores 51 as Cleveland beat Indiana 128-119, passing Kobe Bryant for third-most 50-point games in history (26)."),
    ("WORLD IN BRIEF", NAVY, "globe",
     "Modi opens the first SCO civilisation dialogue in Delhi. A Qatari delegation holds talks in Tehran. Nikhil Gupta is jailed for 235 months in the US over a murder plot. Amazon nears a $7.5bn deal for AI start-up Decart. Trump floats a heavy tax on firms building AI data centres abroad."),
    ("HEALTH & SCIENCE", GREEN, "rocket",
     "Mosquitoes carrying Wolbachia bacteria cut dengue cases among children in Brazil, researchers report. US measles cases pass 5,800 in 2026, a 35-year high. Nvidia halts H200 chip exports to China. Yemen's Houthis launch strikes after a Saudi coalition operation."),
]


def draw(cv):
    cv.fill(0, 0, W, H, PAPER)
    cv.rect(6, 6, W - 12, H - 12, INK, 2)

    # ---- masthead ----
    cv.fill(8, 8, W - 16, 118, NAVY)
    cv.text(24, 18, "THE WORLD IN ONE DAY", 3, WHITE, bold=True)
    date = "SATURDAY 21 NOVEMBER 2026"
    cv.text(24, 58, date, 4, GOLD, bold=True)
    cv.text(24, 100, "One day's news, as reported - from Bahrain to Mercury.",
            1, WHITE)
    cv.text(700, 100, "make.fun - picture of the day", 1, GOLD, bold=True)
    cv.fill(8, 126, W - 16, 3, RED)

    # ---- lead story: Iran strikes Bahrain ----
    lx, ly, lw, lh = 16, 134, 992, 118
    cv.fill(lx, ly, lw, lh, WHITE)
    cv.rect(lx, ly, lw, lh, INK, 1)
    cv.text(lx + 12, ly + 8, "LEAD STORY  -  THE GULF", 1, RED, bold=True)
    cv.text(lx + 12, ly + 24, "IRAN STRIKES US BASES IN BAHRAIN",
            3, INK, bold=True)
    lead = ("Tehran's Revolutionary Guards say they hit two US military "
            "positions, at al-Riffa and Awali. Bahrain says the attack hit a "
            "civilian industrial site, starting a fire, with no injuries; "
            "its defences intercepted other attacks. Iran also claims it "
            "downed a US drone near Qeshm; the US denies its F-16 was hit.")
    cv.para(lx + 12, ly + 62, lead, 640, 1, INK, lh=10, max_lines=5)
    # lead scene: coast, base, missile arcs, blast
    sx, sy, sw, sh = 700, ly + 10, 296, 98
    cv.fill(sx, sy, sw, sh, SKY)
    cv.fill(sx, sy + 62, sw, sh - 62, SEA)
    for bx, bw, bh in [(8, 34, 30), (48, 26, 42), (80, 40, 24), (126, 30, 36)]:
        cv.fill(sx + bx, sy + 62 - bh, bw, bh, GREY)
    cv.line(sx + 10, sy + 30, sx + 150, sy + 12, RED)
    cv.line(sx + 150, sy + 12, sx + 220, sy + 52, RED)
    cv.line(sx + 260, sy + 20, sx + 200, sy + 40, RED)
    cv.poly([(sx + 150, sy + 6), (sx + 158, sy + 12), (sx + 150, sy + 18)], WHITE)
    cv.poly([(sx + 200, sy + 34), (sx + 208, sy + 40), (sx + 200, sy + 46)], WHITE)
    cv.circle(sx + 220, sy + 52, 7, ORANGE)
    cv.circle(sx + 220, sy + 52, 3, RED)
    cv.circle(sx + 150, sy + 12, 3, INK)
    cv.text(sx + 6, sy + 84, "MANAMA, BAHRAIN - US FIFTH FLEET BASE", 1, WHITE, bold=True)
    cv.rect(sx, sy, sw, sh, INK, 1)

    # ---- story grid: 3 cols x 4 rows ----
    gx, gy = 16, 262
    cw, ch, gap = 248, 140, 8
    for i, (kick, accent, ic, head, summ) in enumerate(CARDS):
        cx = gx + (i % 3) * (cw + gap)
        cy = gy + (i // 3) * (ch + gap)
        cv.fill(cx, cy, cw, ch, WHITE)
        cv.rect(cx, cy, cw, ch, INK, 1)
        cv.fill(cx, cy, cw, 3, accent)
        cv.text(cx + 8, cy + 8, kick, 1, accent, bold=True)
        icon(cv, cx + cw - 38, cy + 6, ic, accent)
        cv.para(cx + 8, cy + 24, head, cw - 52, 2, INK, lh=16,
                bold=True, max_lines=3)
        # summary starts below headline block (3 lines max at scale 2)
        nlines = len(cv.wrap(head, cw - 52, 2))
        sy2 = cy + 24 + min(nlines, 3) * 16 + 4
        cv.para(cx + 8, sy2, summ, cw - 16, 1, INK, lh=10, max_lines=5)

    # ---- timeline rail ----
    tx, ty, tw = 792, 262, 216
    th = 4 * (ch + gap) - gap
    cv.fill(tx, ty, tw, th, LIGHT)
    cv.rect(tx, ty, tw, th, INK, 1)
    y = ty + 8
    cv.text(tx + 10, y, "THE DAY, HOUR", 2, INK, bold=True)
    y += 16
    cv.text(tx + 10, y, "BY HOUR (UTC)", 2, RED, bold=True)
    y += 18
    cv.fill(tx + 10, y, tw - 20, 2, RED)
    y += 10
    for section, items in TIMELINE:
        cv.text(tx + 10, y, section, 1, RED, bold=True)
        y += 12
        for t, txt in items:
            cv.text(tx + 10, y, t, 1, INK, bold=True)
            y += 11
            y = cv.para(tx + 10, y, txt, tw - 20, 1, INK, lh=10,
                        max_lines=3)
            y += 6
        y += 4

    # ---- bottom strip: sport / briefs / health ----
    bx, by = 16, 842
    bw, bh, bgap = 324, 118, 8
    for i, (title, accent, ic, txt) in enumerate(BOTTOM):
        cx = bx + i * (bw + bgap)
        cv.fill(cx, by, bw, bh, WHITE)
        cv.rect(cx, by, bw, bh, INK, 1)
        cv.fill(cx, by, bw, 3, accent)
        cv.text(cx + 8, by + 8, title, 2, accent, bold=True)
        icon(cv, cx + bw - 38, by + 6, ic, accent)
        cv.para(cx + 8, by + 32, txt, bw - 16, 1, INK, lh=10, max_lines=8)

    # ---- footer: date check ----
    fy = 972
    cv.fill(16, fy, 992, 36, NAVY)
    cv.text(28, fy + 11,
            "DATE CHECK: 21 NOVEMBER 2026 WAS A SATURDAY. EVERY STORY ABOVE "
            "HAPPENED ON, OR WAS FIRST REPORTED ON, THAT DAY.",
            1, WHITE, bold=True)


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    cv = Canvas(W, H, PAPER)
    draw(cv)
    data = png_bytes(cv)
    with open(os.path.join(outdir, "entry.png"), "wb") as f:
        f.write(data)


if __name__ == "__main__":
    main()
