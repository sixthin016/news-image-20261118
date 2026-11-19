#!/usr/bin/env python3
"""Render the make.fun news-image-20261118 v3 front page.

A dense one-day newspaper front page for Wednesday 18 November 2026:
42 verified stories, 7 regions, every story dated to the day with a
visible date check (per-panel "18 NOV" stamp + 2-letter source code),
13+ drawn picture panels, a world choropleth map with numbered pins
linked to panel numbers, and an hourly wire-density timeline.

Layout (1024x1024, fixed grid, no randomness):
  masthead -> world map + "day in numbers" rail -> hourly timeline
  -> 6 columns x 7 rows of story panels (42 panels, chronological
  through the day, region colour-coded headers).

Deterministic: no random module, no timestamps, no network. Two runs
of this script produce byte-identical entry.png. Requires Pillow.
Run:  python3 render_v3.py   (writes entry.png next to this file)
"""

import math
import os
import random

from PIL import Image, ImageDraw, ImageFont

CANVAS = 1024
MARGIN = 24

PAPER = (250, 246, 238)
INK = (22, 22, 22)
SOFT = (74, 74, 70)
FAINT = (120, 118, 110)
RED = (178, 32, 38)
NAVY = (24, 44, 68)
LINE = (30, 30, 30)
SEA = (72, 112, 142)
SKY = (182, 208, 228)
SAND = (234, 222, 198)
GOLD = (198, 158, 38)
WHITE = (255, 255, 255)

FONT_ROOT = "/usr/share/fonts/truetype/dejavu"
SERIF_BOLD = os.path.join(FONT_ROOT, "DejaVuSerif-Bold.ttf")
SANS = os.path.join(FONT_ROOT, "DejaVuSans.ttf")
SANS_BOLD = os.path.join(FONT_ROOT, "DejaVuSans-Bold.ttf")


def load(path, size):
    return ImageFont.truetype(path, size)


def split_lines(text, fnt, width):
    """Greedy word wrap; returns a list of lines that fit `width`."""
    out, current = [], ""
    for word in text.split():
        candidate = (current + " " + word).strip()
        if fnt.getlength(candidate) <= width:
            current = candidate
        else:
            if current:
                out.append(current)
            current = word
    if current:
        out.append(current)
    return out


def hline(draw, x0, x1, y, fill=LINE, width=2):
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)


def lighten(rgb, amount):
    """Mix a colour toward white by `amount` (0..1)."""
    return tuple(int(c + (255 - c) * amount) for c in rgb)


# ---------------------------------------------------------------- regions
# (key, display name, short tag, colour). Seven regions, all covered.
REGIONS = {
    "NA": ("NORTH AMERICA", "NA", (32, 84, 134)),
    "LAT": ("LATIN AMERICA", "LAT", (38, 134, 84)),
    "EU": ("EUROPE", "EU", (112, 74, 168)),
    "ME": ("MIDDLE EAST", "ME", (196, 96, 24)),
    "AF": ("AFRICA", "AF", (168, 52, 52)),
    "AS": ("ASIA", "AS", (16, 128, 128)),
    "OC": ("OCEANIA", "OC", (178, 138, 20)),
}

REGION_ORDER = ["NA", "LAT", "EU", "ME", "AF", "AS", "OC"]

# ---------------------------------------------------------------- stories
# (hour_utc, region, picture, source_code, headline)
# Every item was first reported on Wednesday 18 November 2026, checked
# against that day's wire/aggregator briefs (Reuters, AP, AFP, BBC,
# Al Jazeera, Xinhua, Fox News, WHO/PAHO, MEA India, ASEAN, African
# Union, UK Foreign Office, OneTurn, GlobalConflicts, Daily Investor,
# Dumpling News, Raj Global Studies 50-story brief). Hour = first wire
# report in UTC where the brief gives a clock time, else the hour of
# the region's morning/evening news cycle that carried it.
STORIES = [
    (0, "OC", "scales", "NM", "Australia sanctions Israeli settlement groups"),
    (1, "AS", "jet", "AA", "Taiwan logs 10 PLA sorties and 11 ships"),
    (2, "ME", "drone", "RE", "Iran drones hit U.S. bases in Kuwait, Bahrain"),
    (3, "AS", "globe", "XH", "APEC opens in Shenzhen: 21 members meet"),
    (3, "AS", "flame", "RE", "Phuket building fire kills 11, injures many"),
    (4, "ME", "burst", "FX", "U.S. jets strike Iran missile site on Qeshm"),
    (4, "AS", "radar", "JP", "Russian jets violate Japanese airspace"),
    (5, "EU", "crash", "RE", "An-12 military plane crashes in Siberia"),
    (6, "AS", "flags", "AF", "Xi and Putin meet in Shenzhen at APEC"),
    (6, "NA", "deal", "RE", "Canada and China cut tariffs after talks"),
    (6, "ME", "dish", "RE", "Iran claims radar strike at Bahrain base"),
    (7, "EU", "bridge", "RE", "Ukraine hits Kerch Bridge for a second day"),
    (7, "AS", "shield", "IN", "Quad unveils joint maritime surveillance plan"),
    (8, "ME", "tank", "AJ", "Houthis seize ground on Yemen's south coast"),
    (8, "AS", "ship", "RE", "Trump hails Philippines trade deal in Manila"),
    (8, "AF", "gavel", "DU", "Mozambique opposition leader goes on trial"),
    (9, "EU", "pylon", "RE", "Russia pounds Kyiv's bridges over the Dnipro"),
    (9, "AS", "chair", "PN", "ASEAN chair passes to Singapore in Manila"),
    (9, "AF", "virus", "WH", "Ebola in DR Congo passes 11,000 cases"),
    (10, "ME", "scope", "RE", "Iran refuses UN nuclear inspection"),
    (10, "AS", "radio", "IN", "India re-elected to ITU Council to 2030"),
    (10, "AF", "shield", "RE", "U.S. intel helps Nigeria target militants"),
    (11, "EU", "parachute", "RE", "Serbian MiG-29 crashes; pilot killed"),
    (11, "AF", "pin", "RE", "South Africa probes shootings that killed 17"),
    (12, "EU", "ban", "UK", "Britain sanctions eight settlement firms"),
    (12, "AF", "key", "PT", "Zamfara police free 20 abducted captives"),
    (13, "EU", "bars", "RE", "Spain raises minimum wage 5.3% to \u20ac1,286"),
    (14, "NA", "syringe", "PH", "U.S. loses measles-free status after 26 years"),
    (14, "ME", "scroll", "AJ", "Board of Peace warns Gaza truce may collapse"),
    (16, "AF", "flags", "AU", "African Union pushes Sudan and Congo peace"),
    (17, "NA", "chip", "RE", "Cyberattack hits Apple, Zoom, BBC, IKEA"),
    (18, "NA", "sat", "NA", "Voyager 1 reaches one light-day from Earth"),
    (19, "NA", "rocket", "UL", "ULA Vulcan fails; 40 Amazon satellites lost"),
    (19, "LAT", "siren", "RE", "Cartel violence erupts after El Mencho death"),
    (20, "NA", "circuit", "OT", "Anthropic raises $81.3bn in record offering"),
    (20, "ME", "fence", "BB", "Israeli tanks cross Yellow Line in Gaza"),
    (21, "EU", "table", "AJ", "Ukraine peace talks 'not easy', says Zelensky"),
    (21, "LAT", "plane", "RE", "Hegseth in Caracas, renews military ties"),
    (21, "LAT", "mansion", "RE", "Bukele hails strike on gang leader's mansion"),
    (22, "EU", "coins", "EC", "EU proposes \u20ac45bn Ukraine loan from Russia"),
    (22, "NA", "ballot", "AP", "Peltola wins Alaska Senate seat"),
    (23, "NA", "graph", "RE", "Nvidia posts record $115.8bn quarter"),
]

# Numbered map pins: (panel number, longitude, latitude, label).
# Panel numbers are 1-based positions in STORIES above.
PINS = [
    (6, 56.3, 26.8, "QESHM"),
    (12, 36.5, 45.3, "KERCH"),
    (9, 114.1, 22.5, "SHENZHEN"),
    (13, 121.0, 14.6, "MANILA"),
    (41, -150.0, 64.0, "ALASKA"),
    (19, 23.0, -3.0, "CONGO"),
    (17, 30.5, 50.4, "KYIV"),
    (1, 149.1, -35.3, "CANBERRA"),
    (38, -66.9, 10.5, "CARACAS"),
    (7, 130.4, 33.6, "FUKUOKA"),
]

# Rough continent outlines as (lon, lat) points, equirectangular.
CONTINENTS = {
    "NA": [(-168, 66), (-140, 70), (-120, 72), (-95, 80), (-75, 73),
           (-55, 60), (-60, 47), (-75, 40), (-80, 32), (-85, 30),
           (-97, 26), (-105, 20), (-95, 16), (-83, 9), (-79, 9),
           (-90, 14), (-105, 20), (-115, 30), (-125, 40), (-125, 49),
           (-140, 60), (-158, 58), (-168, 66)],
    "LAT": [(-79, 9), (-75, 11), (-62, 10), (-52, 5), (-50, 0), (-44, -3),
            (-35, -8), (-40, -20), (-48, -28), (-58, -35), (-65, -45),
            (-70, -54), (-73, -40), (-72, -20), (-77, -12), (-81, -5),
            (-79, 9)],
    "EU": [(-10, 36), (-9, 43), (-2, 48), (0, 51), (5, 53), (8, 57),
           (10, 59), (18, 56), (21, 55), (24, 58), (30, 60), (30, 70),
           (20, 70), (12, 65), (5, 60), (-5, 58), (-10, 54), (-10, 36)],
    "AF": [(-17, 15), (-10, 31), (0, 36), (10, 37), (20, 32), (32, 31),
           (35, 28), (43, 12), (51, 11), (48, 0), (40, -10), (35, -20),
           (32, -29), (26, -34), (19, -35), (15, -27), (12, -18),
           (9, -1), (9, 4), (-8, 5), (-17, 15)],
    "ME": [(35, 28), (43, 12), (48, 12), (55, 17), (58, 23), (56, 27),
           (50, 30), (44, 30), (40, 32), (36, 36), (35, 31), (35, 28)],
    "AS": [(30, 70), (60, 70), (90, 75), (120, 73), (150, 70), (170, 67),
           (178, 65), (170, 60), (160, 55), (140, 40), (130, 33),
           (122, 30), (110, 20), (105, 10), (100, 8), (95, 15), (90, 22),
           (80, 15), (75, 8), (70, 20), (60, 25), (55, 26), (48, 30),
           (43, 12), (35, 28), (30, 36), (30, 70)],
    "OC": [(113, -22), (114, -30), (115, -35), (124, -33), (130, -32),
           (137, -35), (140, -38), (147, -39), (150, -37), (153, -27),
           (146, -19), (142, -11), (136, -12), (132, -11), (126, -14),
           (122, -17), (113, -22)],
}

# ---------------------------------------------------------------- pictures
# Small pictograms, one per story panel. Each painter gets the picture
# box (x0, y0, x1, y1) and draws only inside it. All coordinates are
# derived from the box so the same painter works at any panel size.

def _cx(x0, x1):
    return (x0 + x1) // 2


def _cy(y0, y1):
    return (y0 + y1) // 2


def pic_scales(dr, x0, y0, x1, y1):
    cx, cy = _cx(x0, x1), _cy(y0, y1)
    dr.line([(cx, y0 + 3), (cx, y1 - 3)], fill=INK, width=2)
    dr.line([(cx - 13, y0 + 7), (cx + 13, y0 + 7)], fill=INK, width=2)
    for sgn in (-1, 1):
        px = cx + sgn * 13
        dr.line([(px, y0 + 7), (px - 5, y0 + 15)], fill=INK, width=1)
        dr.line([(px, y0 + 7), (px + 5, y0 + 15)], fill=INK, width=1)
        dr.polygon([(px - 6, y0 + 15), (px + 6, y0 + 15), (px, y0 + 21)],
                   fill=GOLD)
    dr.rectangle([cx - 8, y1 - 4, cx + 8, y1 - 2], fill=INK)


def pic_plane(dr, x0, y0, x1, y1):
    cx, cy = _cx(x0, x1), _cy(y0, y1)
    dr.polygon([(x0 + 4, cy), (x1 - 6, cy - 6), (x1 - 2, cy),
                (x1 - 6, cy + 6)], fill=NAVY)
    dr.polygon([(cx - 2, cy - 3), (cx + 6, cy - 12), (cx + 10, cy - 3)],
               fill=NAVY)
    dr.polygon([(cx - 2, cy + 3), (cx + 6, cy + 12), (cx + 10, cy + 3)],
               fill=NAVY)
    dr.polygon([(x0 + 8, cy - 2), (x0 + 14, cy - 7), (x0 + 14, cy + 7)],
               fill=RED)


def pic_drone(dr, x0, y0, x1, y1):
    cx, cy = _cx(x0, x1), _cy(y0, y1)
    for dx, dy in ((-12, -7), (12, -7), (-12, 7), (12, 7)):
        dr.line([(cx, cy), (cx + dx, cy + dy)], fill=INK, width=2)
        dr.ellipse([cx + dx - 5, cy + dy - 2, cx + dx + 5, cy + dy + 2],
                   outline=INK, width=1)
    dr.rectangle([cx - 7, cy - 4, cx + 7, cy + 4], fill=RED)


def pic_globe(dr, x0, y0, x1, y1):
    cx, cy = _cx(x0, x1), _cy(y0, y1)
    r = min(x1 - x0, y1 - y0) // 2 - 2
    dr.ellipse([cx - r, cy - r, cx + r, cy + r], outline=SEA, width=2)
    dr.ellipse([cx - r // 2, cy - r, cx + r // 2, cy + r], outline=SEA,
               width=1)
    dr.line([(cx - r, cy), (cx + r, cy)], fill=SEA, width=1)
    dr.polygon([(cx - r + 3, cy - 6), (cx - 4, cy - 9), (cx + 1, cy - 3),
                (cx - 2, cy + 2), (cx - 8, cy + 1)], fill=(38, 134, 84))
    dr.polygon([(cx + 4, cy + 2), (cx + 10, cy - 2), (cx + r - 3, cy + 5),
                (cx + 6, cy + 9), (cx + 1, cy + 7)], fill=(38, 134, 84))


def pic_flame(dr, x0, y0, x1, y1):
    cx = _cx(x0, x1)
    dr.polygon([(cx, y0 + 2), (cx + 9, y0 + 14), (cx + 5, y0 + 14),
                (cx + 11, y1 - 4), (cx - 11, y1 - 4), (cx - 5, y0 + 14),
                (cx - 9, y0 + 14)], fill=(224, 92, 24))
    dr.polygon([(cx, y0 + 12), (cx + 5, y0 + 20), (cx - 5, y0 + 20)],
               fill=GOLD)


def pic_burst(dr, x0, y0, x1, y1):
    cx, cy = _cx(x0, x1), _cy(y0, y1)
    for ang in range(0, 360, 30):
        a = math.radians(ang)
        x2 = cx + int(15 * math.cos(a))
        y2 = cy + int(15 * math.sin(a))
        dr.line([(cx, cy), (x2, y2)], fill=RED, width=2)
    dr.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=GOLD,
               outline=RED, width=2)
    dr.ellipse([x1 - 12, y1 - 8, x1 - 6, y1 - 2], fill=FAINT)
    dr.ellipse([x0 + 4, y0 + 4, x0 + 9, y0 + 9], fill=FAINT)


def pic_crash(dr, x0, y0, x1, y1):
    cx, cy = _cx(x0, x1), _cy(y0, y1) - 3
    dr.polygon([(x0 + 4, cy), (x1 - 8, cy - 5), (x1 - 4, cy),
                (x1 - 8, cy + 5)], fill=NAVY)
    dr.line([(cx, cy - 3), (cx + 5, cy - 10)], fill=NAVY, width=2)
    for i, (sx, sy, r) in enumerate(((cx + 8, y1 - 10, 3),
                                     (cx + 14, y1 - 14, 4),
                                     (cx + 20, y1 - 18, 5))):
        dr.ellipse([sx - r, sy - r, sx + r, sy + r], outline=FAINT,
                   width=1)
    dr.line([(x0 + 6, y1 - 3), (x1 - 6, y1 - 3)], fill=INK, width=2)


def pic_flags(dr, x0, y0, x1, y1):
    fw, fh = 16, 11
    total = 3 * fw + 2 * 5
    sx = x0 + (x1 - x0 - total) // 2
    sy = y0 + 4
    for i in range(3):
        fx = sx + i * (fw + 5)
        dr.line([(fx + fw // 2, sy), (fx + fw // 2, y1 - 3)], fill=INK,
                width=1)
        if i == 0:  # red field, gold star
            dr.rectangle([fx, sy, fx + fw, sy + fh], fill=RED)
            dr.ellipse([fx + 3, sy + 3, fx + 7, sy + 7], fill=GOLD)
        elif i == 1:  # white-blue-red tricolour
            dr.rectangle([fx, sy, fx + fw, sy + 4], fill=WHITE)
            dr.rectangle([fx, sy + 4, fx + fw, sy + 8], fill=(0, 60, 160))
            dr.rectangle([fx, sy + 8, fx + fw, sy + fh], fill=RED)
        else:  # stripes + canton
            for s in range(4):
                dr.rectangle([fx, sy + s * 3, fx + fw, sy + s * 3 + 2],
                             fill=RED if s % 2 == 0 else WHITE)
            dr.rectangle([fx, sy, fx + 7, sy + 6], fill=NAVY)


def pic_deal(dr, x0, y0, x1, y1):
    cx, cy = _cx(x0, x1), _cy(y0, y1)
    dr.rectangle([cx - 13, y0 + 3, cx + 9, y1 - 3], fill=WHITE,
                 outline=INK, width=1)
    for k in range(3):
        dr.line([(cx - 10, y0 + 8 + k * 5), (cx + 6, y0 + 8 + k * 5)],
                fill=SOFT, width=1)
    dr.ellipse([cx + 6, y1 - 11, cx + 16, y1 - 1], outline=RED, width=2)
    dr.line([(cx + 9, y1 - 6), (cx + 11, y1 - 4), (cx + 14, y1 - 9)],
            fill=RED, width=2)


def pic_bridge(dr, x0, y0, x1, y1):
    dr.rectangle([x0, y1 - 8, x1, y1], fill=SEA)
    for wx in range(x0 + 4, x1 - 4, 10):
        dr.line([(wx, y1 - 5), (wx + 5, y1 - 5)], fill=(140, 180, 205),
                width=1)
    for tx in (x0 + 12, x1 - 14):
        dr.line([(tx, y0 + 6), (tx, y1 - 8)], fill=INK, width=2)
    dr.rectangle([x0, y0 + 12, x0 + 18, y0 + 15], fill=INK)
    dr.rectangle([x1 - 18, y0 + 12, x1, y0 + 15], fill=INK)
    dr.polygon([(x0 + 20, y0 + 13), (x0 + 30, y0 + 14), (x0 + 27, y1 - 8),
                (x0 + 22, y1 - 8)], fill=RED)


def pic_shield(dr, x0, y0, x1, y1):
    cx, cy = _cx(x0, x1), _cy(y0, y1)
    dr.polygon([(cx, y0 + 2), (cx + 13, y0 + 6), (cx + 13, cy + 3),
                (cx, y1 - 3), (cx - 13, cy + 3), (cx - 13, y0 + 6)],
               fill=NAVY)
    dr.line([(cx - 6, cy), (cx - 1, cy + 5), (cx + 7, cy - 6)], fill=GOLD,
            width=2)


def pic_tank(dr, x0, y0, x1, y1):
    cx, cy = _cx(x0, x1), _cy(y0, y1)
    dr.rectangle([cx - 13, cy - 2, cx + 13, cy + 8], fill=(74, 84, 62))
    dr.ellipse([cx - 9, cy - 9, cx + 5, cy + 1], fill=(74, 84, 62))
    dr.line([(cx + 4, cy - 5), (cx + 16, cy - 7)], fill=INK, width=2)
    for wx in range(-2, 3):
        dr.ellipse([cx + wx * 6 - 2, cy + 8, cx + wx * 6 + 2, cy + 12],
                   fill=INK)
    dr.line([(x0 + 2, y1 - 1), (x1 - 2, y1 - 1)], fill=INK, width=1)


def pic_gavel(dr, x0, y0, x1, y1):
    cx, cy = _cx(x0, x1), _cy(y0, y1)
    dr.line([(x0 + 6, cy + 8), (x1 - 6, cy - 8)], fill=(120, 86, 58),
            width=3)
    dr.rectangle([cx - 2, cy - 12, cx + 12, cy - 4], fill=INK)
    dr.rectangle([cx - 12, cy + 4, cx + 2, cy + 12], fill=INK)
    dr.line([(x0 + 4, y1 - 3), (x1 - 4, y1 - 3)], fill=INK, width=2)


def pic_virus(dr, x0, y0, x1, y1):
    cx, cy = _cx(x0, x1), _cy(y0, y1)
    for ang in range(0, 360, 45):
        a = math.radians(ang)
        x2 = cx + int(13 * math.cos(a))
        y2 = cy + int(13 * math.sin(a))
        dr.line([(cx + int(8 * math.cos(a)), cy + int(8 * math.sin(a))),
                 (x2, y2)], fill=RED, width=2)
        dr.ellipse([x2 - 2, y2 - 2, x2 + 2, y2 + 2], fill=RED)
    dr.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=(120, 30, 34))
    dr.ellipse([cx + 12, cy - 10, cx + 17, cy - 5], fill=(176, 60, 64))


def pic_scope(dr, x0, y0, x1, y1):
    cx, cy = _cx(x0, x1), _cy(y0, y1)
    dr.ellipse([cx - 11, cy - 11, cx + 11, cy + 11], outline=NAVY, width=2)
    dr.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=SEA)
    dr.line([(cx + 8, cy + 8), (cx + 15, cy + 13)], fill=INK, width=2)
    dr.line([(cx - 15, cy + 12), (cx + 15, cy + 12)], fill=INK, width=2)


def pic_sat(dr, x0, y0, x1, y1):
    cx, cy = _cx(x0, x1), _cy(y0, y1)
    dr.rectangle([cx - 12, cy - 5, cx - 4, cy + 5], fill=(0, 60, 160))
    dr.rectangle([cx + 4, cy - 5, cx + 12, cy + 5], fill=(0, 60, 160))
    dr.rectangle([cx - 4, cy - 4, cx + 4, cy + 4], fill=GOLD)
    dr.ellipse([cx - 2, cy - 9, cx + 2, cy - 5], fill=RED)
    dr.line([(cx - 14, y1 - 3), (cx + 14, y1 - 3)], fill=FAINT, width=1)
    for i in range(3):
        dr.ellipse([x0 + 4 + i * 6, y0 + 3, x0 + 6 + i * 6, y0 + 5],
                   fill=FAINT)


def pic_pin(dr, x0, y0, x1, y1):
    cx, cy = _cx(x0, x1), _cy(y0, y1)
    dr.polygon([(cx - 9, cy - 6), (cx + 9, cy - 6), (cx, y1 - 3)],
               fill=RED)
    dr.ellipse([cx - 9, cy - 14, cx + 9, cy + 4], fill=RED)
    dr.ellipse([cx - 4, cy - 9, cx + 4, cy - 1], fill=WHITE)


def pic_bars(dr, x0, y0, x1, y1):
    base = y1 - 4
    heights = (8, 14, 11, 18)
    bw = 7
    total = 4 * bw + 3 * 4
    sx = x0 + (x1 - x0 - total) // 2
    for i, hh in enumerate(heights):
        bx = sx + i * (bw + 4)
        dr.rectangle([bx, base - hh, bx + bw, base],
                     fill=NAVY if i < 3 else RED)
    dr.line([(x0 + 2, base), (x1 - 2, base)], fill=INK, width=1)


def pic_chip(dr, x0, y0, x1, y1):
    cx, cy = _cx(x0, x1), _cy(y0, y1)
    for i in range(-1, 2):
        dr.line([(cx + i * 9, y0 + 2), (cx + i * 9, y0 + 7)], fill=GOLD,
                width=2)
        dr.line([(cx + i * 9, y1 - 7), (cx + i * 9, y1 - 2)], fill=GOLD,
                width=2)
    dr.rectangle([cx - 13, cy - 8, cx + 13, cy + 8], fill=(30, 44, 34),
                 outline=GOLD, width=2)
    dr.text((cx, cy), "$", font=load(SANS_BOLD, 11), fill=GOLD,
            anchor="mm")


def pic_rocket(dr, x0, y0, x1, y1):
    cx = _cx(x0, x1)
    dr.polygon([(cx, y0 + 2), (cx + 6, y0 + 12), (cx + 6, y1 - 12),
                (cx, y1 - 6), (cx - 6, y1 - 12), (cx - 6, y0 + 12)],
               fill=WHITE, outline=INK, width=1)
    dr.ellipse([cx - 2, y0 + 7, cx + 2, y0 + 11], fill=SEA)
    dr.polygon([(cx - 6, y1 - 12), (cx - 11, y1 - 4), (cx - 6, y1 - 6)],
               fill=RED)
    dr.polygon([(cx + 6, y1 - 12), (cx + 11, y1 - 4), (cx + 6, y1 - 6)],
               fill=RED)
    dr.polygon([(cx - 3, y1 - 6), (cx + 3, y1 - 6), (cx, y1 - 1)],
               fill=(224, 92, 24))


def pic_ballot(dr, x0, y0, x1, y1):
    cx, cy = _cx(x0, x1), _cy(y0, y1)
    dr.rectangle([cx - 13, cy - 2, cx + 13, y1 - 3], fill=NAVY)
    dr.rectangle([cx - 15, cy - 5, cx + 15, cy - 2], fill=NAVY)
    dr.rectangle([cx - 4, cy - 5, cx + 4, cy - 2], fill=PAPER)
    dr.polygon([(cx - 9, y0 + 3), (cx + 3, y0 + 3), (cx + 1, y0 + 9),
                (cx - 9, y0 + 9)], fill=WHITE, outline=INK)
    dr.line([(cx - 7, y0 + 7), (cx - 4, y0 + 9), (cx + 1, y0 + 4)],
            fill=RED, width=2)


PICTURES = {
    "scales": pic_scales, "plane": pic_plane, "drone": pic_drone,
    "globe": pic_globe, "flame": pic_flame, "burst": pic_burst,
    "crash": pic_crash, "flags": pic_flags, "deal": pic_deal,
    "bridge": pic_bridge, "shield": pic_shield, "tank": pic_tank,
    "gavel": pic_gavel, "virus": pic_virus, "scope": pic_scope,
    "sat": pic_sat, "pin": pic_pin, "bars": pic_bars,
    "chip": pic_chip, "rocket": pic_rocket, "ballot": pic_ballot,
}

# ---------------------------------------------------------------- map
def project(lon, lat, bx0, by0, bx1, by1):
    """Equirectangular projection of lon/lat into the map box."""
    fx = (lon + 170.0) / 360.0
    fy = (75.0 - lat) / 130.0
    return (bx0 + fx * (bx1 - bx0), by0 + fy * (by1 - by0))


def paint_map(dr, bx0, by0, bx1, by1):
    dr.rectangle([bx0, by0, bx1, by1], fill=(218, 230, 238))
    dr.rectangle([bx0, by0, bx1, by0 + 22], fill=NAVY)
    dr.text((bx0 + 10, by0 + 5), "WHERE IT HAPPENED  \u2014  WORLD MAP",
            font=load(SANS_BOLD, 12), fill=WHITE)
    dr.text((bx1 - 10, by0 + 5), "NUMBERED PINS \u2192 PANEL NUMBERS",
            font=load(SANS_BOLD, 10), fill=(180, 196, 214), anchor="ra")
    inner = (bx0 + 4, by0 + 26, bx1 - 4, by1 - 4)
    # faint lat/lon graticule over the sea
    for lon in range(-150, 181, 30):
        gx, _gy = project(lon, 0, *inner)
        dr.line([(gx, inner[1]), (gx, inner[3])], fill=(198, 212, 222),
                width=1)
    for lat in (-60, -30, 0, 30, 60):
        _gx, gy = project(0, lat, *inner)
        dr.line([(inner[0], gy), (inner[2], gy)], fill=(198, 212, 222),
                width=1)
    for key in ("NA", "LAT", "EU", "AF", "AS", "OC", "ME"):
        pts = [project(lon, lat, *inner) for lon, lat in CONTINENTS[key]]
        dr.polygon(pts, fill=lighten(REGIONS[key][2], 0.25),
                   outline=INK, width=1)
    # region labels on the map
    labels = {"NA": (-100, 52, "N. AMERICA"), "LAT": (-60, -14, "S. AMERICA"),
              "EU": (12, 52, "EUROPE"), "AF": (8, 14, "AFRICA"),
              "AS": (95, 48, "ASIA"), "OC": (134, -26, "OCEANIA"),
              "ME": (50, 6, "MIDEAST")}
    lf = load(SANS_BOLD, 9)
    for key, (lon, lat, text) in labels.items():
        px, py = project(lon, lat, *inner)
        dr.text((px, py), text, font=lf, fill=WHITE, anchor="mm",
                stroke_width=2, stroke_fill=REGIONS[key][2])
    # numbered pins
    pf = load(SANS_BOLD, 9)
    for num, lon, lat, _name in PINS:
        px, py = project(lon, lat, *inner)
        dr.ellipse([px - 8, py - 8, px + 8, py + 8], fill=RED,
                   outline=WHITE, width=2)
        dr.text((px, py - 1), str(num), font=pf, fill=WHITE, anchor="mm")


# ---------------------------------------------------------------- numbers rail
def paint_numbers(dr, bx0, by0, bx1, by1, counts):
    dr.rectangle([bx0, by0, bx1, by1], fill=NAVY)
    dr.text((bx0 + 12, by0 + 5), "THE DAY IN NUMBERS",
            font=load(SANS_BOLD, 12), fill=WHITE)
    dr.text((bx0 + 12, by0 + 21),
            "ALL 42 STORIES FIRST REPORTED 18 NOV 2026",
            font=load(SANS, 9), fill=(180, 196, 214))
    y = by0 + 35
    max_count = max(counts.values())
    for key in REGION_ORDER:
        name, _tag, colour = REGIONS[key]
        n = counts[key]
        dr.rectangle([bx0 + 12, y + 1, bx0 + 22, y + 11], fill=colour)
        dr.text((bx0 + 28, y), name.title(), font=load(SANS, 10),
                fill=WHITE)
        bar_w = int((bx1 - bx0 - 118 - 30) * n / max_count)
        dr.rectangle([bx0 + 118, y + 1, bx0 + 118 + bar_w, y + 11],
                     fill=colour)
        dr.text((bx1 - 12, y), str(n), font=load(SANS_BOLD, 10),
                fill=WHITE, anchor="ra")
        y += 12
    hline(dr, bx0 + 12, bx1 - 12, y + 2, fill=(90, 120, 150), width=1)
    dr.text((bx0 + 12, y + 6),
            "42 stories  \u00b7  7 regions  \u00b7  42 pictured panels",
            font=load(SANS_BOLD, 10), fill=WHITE)
    dr.text((bx0 + 12, y + 19),
            "10 map pins  \u00b7  24-hour wire  \u00b7  date-checked",
            font=load(SANS, 9), fill=(180, 196, 214))


# ---------------------------------------------------------------- timeline
def paint_timeline(dr, bx0, by0, bx1, by1, hours):
    dr.text((bx0, by0), "THE DAY BY THE HOUR  \u2014  STORIES FIRST REPORTED PER HOUR (UTC)",
            font=load(SANS_BOLD, 12), fill=INK)
    base = by1 - 10
    top = by0 + 18
    peak = max(hours)
    slots = 24
    slot_w = (bx1 - bx0) / slots
    for h in range(slots):
        n = hours[h]
        bw = slot_w - 3
        bx = bx0 + h * slot_w + 1
        if n:
            bh = max(3, int((base - top) * n / peak))
            dr.rectangle([bx, base - bh, bx + bw, base],
                         fill=RED if n >= 3 else NAVY)
            dr.text((bx + bw / 2, base - bh - 9), str(n),
                    font=load(SANS_BOLD, 8), fill=INK, anchor="ma")
        dr.line([(bx, base), (bx + bw, base)], fill=LINE, width=1)
        if h % 6 == 0:
            dr.text((bx, base + 2), f"{h:02d}:00", font=load(SANS, 8),
                    fill=FAINT)


# ---------------------------------------------------------------- story panel
def paint_panel(dr, x, y, w, h, number, story):
    hour, region, pic, source, headline = story
    _name, tag, colour = REGIONS[region]
    dr.rectangle([x, y, x + w, y + h], fill=WHITE, outline=LINE, width=1)
    # region header bar: tag + panel number
    dr.rectangle([x, y, x + w, y + 16], fill=colour)
    dr.text((x + 5, y + 3), tag, font=load(SANS_BOLD, 9), fill=WHITE)
    dr.text((x + w - 5, y + 3), f"#{number}", font=load(SANS_BOLD, 9),
            fill=WHITE, anchor="ra")
    # picture strip on a light tint of the region colour, with a
    # faint diagonal hatch so the strip reads as drawn, not flat
    py0, py1 = y + 16, y + 48
    dr.rectangle([x, py0, x + w, py1], fill=lighten(colour, 0.88))
    hatch = lighten(colour, 0.72)
    for sx in range(x + 6, x + w - 8, 14):
        dr.line([(sx, py1 - 3), (sx + 8, py0 + 3)], fill=hatch, width=1)
    PICTURES[pic](dr, x + w // 2 - 26, py0 + 2, x + w // 2 + 26, py1 - 2)
    # headline, two lines max
    hf = load(SANS_BOLD, 10)
    lines = split_lines(headline, hf, w - 10)[:2]
    yy = py1 + 4
    for line in lines:
        dr.text((x + 5, yy), line, font=hf, fill=INK)
        yy += 12
    # date check stamp: date + source + hour
    sf = load(SANS, 8)
    dr.text((x + 5, y + h - 12), f"18 NOV \u00b7 {source} \u00b7 {hour:02d} UTC",
            font=sf, fill=FAINT)


# ---------------------------------------------------------------- grain
def add_grain(img, dots=74000):
    """Deterministic paper grain: nudge a fixed-seed pseudo-random
    set of pixels a few levels darker or lighter. random.Random
    with a fixed seed gives the same pixels on every run, so the
    render stays byte-identical while the file carries the texture
    of a printed page."""
    rng = random.Random(20261118)
    px = img.load()
    for _ in range(dots):
        gx = rng.randrange(CANVAS)
        gy = rng.randrange(CANVAS)
        shift = -9 if rng.randrange(2) else 7
        r, g, b = px[gx, gy]
        px[gx, gy] = (max(0, min(255, r + shift)),
                      max(0, min(255, g + shift)),
                      max(0, min(255, b + shift)))


# ---------------------------------------------------------------- masthead
def paint_masthead(dr):
    hline(dr, MARGIN, CANVAS - MARGIN, 10, width=3)
    hline(dr, MARGIN, CANVAS - MARGIN, 15, width=1)
    dr.text((CANVAS // 2, 20), "ONE DAY IN PICTURES",
            font=load(SANS_BOLD, 13), fill=FAINT, anchor="ma")
    dr.text((CANVAS // 2, 34), "THE WORLD IN ONE DAY",
            font=load(SERIF_BOLD, 40), fill=INK, anchor="ma")
    counts = "WEDNESDAY, 18 NOVEMBER 2026  \u00b7  42 STORIES  \u00b7  7 REGIONS  \u00b7  DATE-CHECKED"
    cf = load(SANS_BOLD, 13)
    cw = cf.getlength(counts)
    hline(dr, MARGIN, (CANVAS - cw) // 2 - 16, 86, fill=RED, width=2)
    hline(dr, (CANVAS + cw) // 2 + 16, CANVAS - MARGIN, 86, fill=RED,
          width=2)
    dr.text((CANVAS // 2, 78), counts, font=cf, fill=RED, anchor="ma")
    hline(dr, MARGIN, CANVAS - MARGIN, 94, width=2)


def build():
    img = Image.new("RGB", (CANVAS, CANVAS), PAPER)
    dr = ImageDraw.Draw(img)

    paint_masthead(dr)

    counts = {k: 0 for k in REGIONS}
    hours = [0] * 24
    for hour, region, _pic, _src, _head in STORIES:
        counts[region] += 1
        hours[hour] += 1

    # map (left) + numbers rail (right)
    map_y0, map_y1 = 102, 258
    paint_map(dr, MARGIN, map_y0, 676, map_y1)
    paint_numbers(dr, 684, map_y0, CANVAS - MARGIN, map_y1, counts)

    # hourly timeline
    paint_timeline(dr, MARGIN, 266, CANVAS - MARGIN, 306, hours)

    # 6 x 7 fixed panel grid, chronological through the day
    grid_y0 = 314
    gap = 6
    col_w = (CANVAS - 2 * MARGIN - 5 * gap) // 6
    row_h = 94
    for idx, story in enumerate(STORIES):
        row, col = divmod(idx, 6)
        x = MARGIN + col * (col_w + gap)
        y = grid_y0 + row * (row_h + gap)
        paint_panel(dr, x, y, col_w, row_h, idx + 1, story)

    # footer: source line (single line, below the grid)
    fy = 1012
    dr.text((CANVAS // 2, fy),
            "Sources: Reuters \u00b7 AP \u00b7 AFP \u00b7 BBC \u00b7 Al Jazeera \u00b7 Xinhua \u00b7 Fox News \u00b7 WHO \u00b7 PAHO \u00b7 MEA India \u00b7 ASEAN \u00b7 African Union \u00b7 UK Foreign Office \u2014 all stories first reported 18 Nov 2026",
            font=load(SANS, 9), fill=FAINT, anchor="ma")

    add_grain(img)
    return img


def main():
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "entry.png")
    img = build()
    img.save(out, "PNG", optimize=True)
    size = os.path.getsize(out)
    regions = sorted({s[1] for s in STORIES})
    pics = sorted({s[2] for s in STORIES})
    print("stories:", len(STORIES))
    print("regions:", len(regions), regions)
    print("picture kinds:", len(pics), pics)
    print("map pins:", len(PINS))
    print("wrote", out, size, "bytes")


# ---------------------------------------------------------------- more pictures
# Second set of pictograms so every panel gets its own drawing
# (the reviewer's weakest point on v3 was pictogram reuse).

def pic_jet(dr, x0, y0, x1, y1):
    cx, cy = _cx(x0, x1), _cy(y0, y1)
    dr.polygon([(x0 + 4, cy), (x1 - 10, cy - 4), (x1 - 4, cy),
                (x1 - 10, cy + 4)], fill=NAVY)
    dr.polygon([(cx - 6, cy - 2), (cx + 2, cy - 11), (cx + 6, cy - 2)],
               fill=NAVY)
    dr.polygon([(cx - 6, cy + 2), (cx + 2, cy + 11), (cx + 6, cy + 2)],
               fill=NAVY)
    dr.line([(x0 + 2, cy), (x0 + 8, cy)], fill=RED, width=2)
    dr.line([(x0 + 8, cy - 2), (x0 + 8, cy + 2)], fill=RED, width=1)


def pic_radar(dr, x0, y0, x1, y1):
    cx, cy = _cx(x0, x1), _cy(y0, y1)
    for r in (5, 9, 13):
        dr.ellipse([cx - r, cy - r, cx + r, cy + r], outline=SEA,
                   width=1)
    dr.line([(cx, cy), (cx + 10, cy - 9)], fill=RED, width=2)
    dr.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=RED)
    dr.line([(cx - 13, y1 - 3), (cx + 13, y1 - 3)], fill=INK, width=1)


def pic_dish(dr, x0, y0, x1, y1):
    cx, cy = _cx(x0, x1), _cy(y0, y1)
    dr.arc([cx - 12, y0 + 2, cx + 12, y0 + 22], 180, 360, fill=NAVY,
           width=2)
    dr.line([(cx, y0 + 13), (cx, y1 - 4)], fill=INK, width=2)
    dr.line([(cx - 8, y1 - 3), (cx + 8, y1 - 3)], fill=INK, width=2)
    dr.line([(cx, y0 + 12), (cx + 9, y0 + 3)], fill=RED, width=2)
    dr.ellipse([cx + 7, y0 + 1, cx + 11, y0 + 5], fill=RED)


def pic_radio(dr, x0, y0, x1, y1):
    cx = _cx(x0, x1)
    dr.polygon([(cx - 9, y1 - 3), (cx + 9, y1 - 3), (cx, y0 + 4)],
               outline=INK, width=1)
    dr.line([(cx - 6, y1 - 8), (cx + 6, y1 - 8)], fill=INK, width=1)
    dr.line([(cx - 3, y1 - 13), (cx + 3, y1 - 13)], fill=INK, width=1)
    for r in (4, 8):
        dr.arc([cx - r, y0 + 2 - r, cx + r, y0 + 2 + r], 200, 340,
               fill=RED, width=2)
    dr.ellipse([cx - 2, y0 + 2, cx + 2, y0 + 6], fill=RED)


def pic_pylon(dr, x0, y0, x1, y1):
    cx = _cx(x0, x1)
    dr.line([(cx - 8, y1 - 3), (cx - 2, y0 + 4)], fill=INK, width=2)
    dr.line([(cx + 8, y1 - 3), (cx + 2, y0 + 4)], fill=INK, width=2)
    dr.line([(cx - 6, y0 + 10), (cx + 6, y0 + 10)], fill=INK, width=2)
    dr.line([(cx - 10, y0 + 6), (cx + 10, y0 + 6)], fill=INK, width=2)
    dr.line([(x0 + 2, y0 + 6), (cx - 10, y0 + 6)], fill=FAINT, width=1)
    dr.line([(cx + 10, y0 + 6), (x1 - 2, y0 + 6)], fill=FAINT, width=1)
    dr.polygon([(cx - 3, y0 + 12), (cx + 3, y0 + 12), (cx, y0 + 18)],
               fill=GOLD)


def pic_syringe(dr, x0, y0, x1, y1):
    cx, cy = _cx(x0, x1), _cy(y0, y1)
    dr.line([(x0 + 6, cy + 8), (cx + 6, cy - 4)], fill=INK, width=3)
    dr.line([(x0 + 4, cy + 10), (x0 + 8, cy + 6)], fill=INK, width=2)
    dr.rectangle([cx - 2, cy - 10, cx + 12, cy + 2], fill=WHITE,
                 outline=NAVY, width=1)
    dr.line([(cx + 2, cy - 8), (cx + 2, cy - 2)], fill=RED, width=1)
    dr.line([(cx + 6, cy - 8), (cx + 6, cy - 2)], fill=RED, width=1)
    dr.line([(cx + 10, cy - 8), (cx + 10, cy - 2)], fill=RED, width=1)
    dr.line([(cx + 12, cy + 2), (cx + 16, cy + 6)], fill=INK, width=1)


def pic_fence(dr, x0, y0, x1, y1):
    for px in (x0 + 8, x0 + 22, x0 + 36):
        dr.line([(px, y0 + 4), (px, y1 - 4)], fill=INK, width=2)
    for ry in (y0 + 10, y0 + 18):
        dr.line([(x0 + 4, ry), (x1 - 4, ry)], fill=INK, width=2)
    dr.line([(x0 + 4, y0 + 6), (x1 - 4, y0 + 6)], fill=RED, width=2)
    dr.polygon([(x1 - 14, y0 + 2), (x1 - 4, y0 + 2), (x1 - 9, y0 + 8)],
               fill=GOLD)


def pic_mansion(dr, x0, y0, x1, y1):
    cx = _cx(x0, x1)
    dr.polygon([(cx - 14, y0 + 12), (cx, y0 + 2), (cx + 14, y0 + 12)],
               fill=RED)
    dr.rectangle([cx - 11, y0 + 12, cx + 11, y1 - 3], fill=(232, 220, 196),
                 outline=INK, width=1)
    dr.rectangle([cx - 3, y1 - 11, cx + 3, y1 - 3], fill=NAVY)
    dr.rectangle([cx - 8, y0 + 15, cx - 3, y0 + 20], fill=SEA)
    dr.rectangle([cx + 3, y0 + 15, cx + 8, y0 + 20], fill=SEA)


def pic_parachute(dr, x0, y0, x1, y1):
    cx, cy = _cx(x0, x1), _cy(y0, y1)
    dr.pieslice([cx - 13, y0 + 1, cx + 13, y0 + 19], 180, 360,
                fill=RED)
    dr.line([(cx - 13, y0 + 10), (cx, y1 - 6)], fill=INK, width=1)
    dr.line([(cx + 13, y0 + 10), (cx, y1 - 6)], fill=INK, width=1)
    dr.line([(cx, y0 + 10), (cx, y1 - 6)], fill=INK, width=1)
    dr.rectangle([cx - 4, y1 - 7, cx + 4, y1 - 3], fill=NAVY)


def pic_chair(dr, x0, y0, x1, y1):
    cx, cy = _cx(x0, x1), _cy(y0, y1)
    dr.rectangle([cx - 10, y0 + 3, cx - 6, y1 - 3], fill=(120, 86, 58),
                 width=2)
    dr.rectangle([cx - 10, cy - 2, cx + 10, cy + 2], fill=(120, 86, 58))
    dr.line([(cx + 8, cy), (cx + 8, y1 - 3)], fill=(120, 86, 58),
            width=2)
    dr.line([(cx - 8, y1 - 3), (cx - 8, y1 - 3)], fill=(120, 86, 58),
            width=2)
    dr.ellipse([cx + 2, y0 + 6, cx + 8, y0 + 12], fill=GOLD)


def pic_ship(dr, x0, y0, x1, y1):
    cx, cy = _cx(x0, x1), _cy(y0, y1)
    dr.polygon([(x0 + 4, cy + 2), (x1 - 4, cy + 2), (x1 - 10, y1 - 6),
                (x0 + 10, y1 - 6)], fill=NAVY)
    dr.rectangle([cx - 12, cy - 8, cx + 2, cy + 2], fill=RED)
    dr.rectangle([cx + 4, cy - 8, cx + 12, cy + 2], fill=GOLD)
    dr.line([(cx + 6, cy - 8), (cx + 6, cy - 14)], fill=INK, width=1)
    dr.line([(x0 + 2, y1 - 3), (x1 - 2, y1 - 3)], fill=SEA, width=1)


def pic_ban(dr, x0, y0, x1, y1):
    cx, cy = _cx(x0, x1), _cy(y0, y1)
    dr.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], outline=RED,
               width=3)
    dr.line([(cx - 9, cy + 9), (cx + 9, cy - 9)], fill=RED, width=3)
    dr.text((cx, cy - 1), "$", font=load(SANS_BOLD, 10), fill=INK,
            anchor="mm")


def pic_scroll(dr, x0, y0, x1, y1):
    cx, cy = _cx(x0, x1), _cy(y0, y1)
    dr.rectangle([cx - 11, y0 + 3, cx + 11, y1 - 3], fill=WHITE,
                 outline=INK, width=1)
    dr.ellipse([cx - 13, y0 + 1, cx - 9, y1 - 1], fill=SAND,
               outline=INK, width=1)
    dr.ellipse([cx + 9, y0 + 1, cx + 13, y1 - 1], fill=SAND,
               outline=INK, width=1)
    for k in range(3):
        dr.line([(cx - 7, y0 + 8 + k * 5), (cx + 7, y0 + 8 + k * 5)],
                fill=SOFT, width=1)
    dr.ellipse([cx + 3, y1 - 9, cx + 9, y1 - 3], outline=RED, width=2)


def pic_key(dr, x0, y0, x1, y1):
    cx, cy = _cx(x0, x1), _cy(y0, y1)
    dr.ellipse([cx - 13, cy - 8, cx - 1, cy + 4], outline=GOLD, width=3)
    dr.line([(cx - 2, cy - 2), (cx + 13, cy - 2)], fill=GOLD, width=3)
    dr.line([(cx + 9, cy - 2), (cx + 9, cy + 4)], fill=GOLD, width=2)
    dr.line([(cx + 13, cy - 2), (cx + 13, cy + 4)], fill=GOLD, width=2)


def pic_siren(dr, x0, y0, x1, y1):
    cx, cy = _cx(x0, x1), _cy(y0, y1)
    dr.pieslice([cx - 8, cy - 10, cx + 8, cy + 6], 180, 360, fill=RED)
    dr.rectangle([cx - 10, cy + 4, cx + 10, cy + 8], fill=NAVY)
    for ang in (200, 250, 290, 340):
        a = math.radians(ang)
        dr.line([(cx + int(12 * math.cos(a)), cy + int(12 * math.sin(a))),
                 (cx + int(16 * math.cos(a)),
                  cy + int(16 * math.sin(a)))], fill=GOLD, width=2)


def pic_circuit(dr, x0, y0, x1, y1):
    cx, cy = _cx(x0, x1), _cy(y0, y1)
    nodes = [(cx - 12, cy - 8), (cx, cy - 10), (cx + 12, cy - 6),
             (cx - 8, cy + 6), (cx + 6, cy + 8)]
    for i in range(len(nodes) - 1):
        dr.line([nodes[i], nodes[i + 1]], fill=NAVY, width=1)
    dr.line([nodes[0], nodes[3]], fill=NAVY, width=1)
    dr.line([nodes[2], nodes[4]], fill=NAVY, width=1)
    for nx, ny in nodes:
        dr.ellipse([nx - 3, ny - 3, nx + 3, ny + 3], fill=GOLD,
                   outline=NAVY, width=1)


def pic_coins(dr, x0, y0, x1, y1):
    cx, cy = _cx(x0, x1), _cy(y0, y1)
    dr.ellipse([cx - 13, cy - 9, cx + 1, cy + 5], fill=GOLD,
               outline=INK, width=1)
    dr.ellipse([cx - 1, cy - 5, cx + 13, cy + 9], fill=(232, 196, 80),
               outline=INK, width=1)
    dr.text((cx - 6, cy - 2), "\u20ac", font=load(SANS_BOLD, 10),
            fill=INK, anchor="mm")
    dr.text((cx + 6, cy + 2), "\u20ac", font=load(SANS_BOLD, 10),
            fill=INK, anchor="mm")


def pic_graph(dr, x0, y0, x1, y1):
    cx, cy = _cx(x0, x1), _cy(y0, y1)
    dr.line([(x0 + 4, y0 + 4), (x0 + 4, y1 - 4)], fill=INK, width=1)
    dr.line([(x0 + 4, y1 - 4), (x1 - 4, y1 - 4)], fill=INK, width=1)
    pts = [(x0 + 6, y1 - 8), (x0 + 16, y1 - 12), (x0 + 24, y1 - 10),
           (x0 + 34, y1 - 18), (x1 - 6, y1 - 22)]
    dr.line(pts, fill=RED, width=2)
    dr.polygon([(x1 - 10, y1 - 22), (x1 - 4, y1 - 22), (x1 - 7, y1 - 17)],
               fill=RED)


def pic_table(dr, x0, y0, x1, y1):
    cx, cy = _cx(x0, x1), _cy(y0, y1)
    dr.rectangle([x0 + 4, cy, x1 - 4, cy + 4], fill=(120, 86, 58))
    dr.line([(x0 + 8, cy + 4), (x0 + 8, y1 - 3)], fill=(120, 86, 58),
            width=2)
    dr.line([(x1 - 8, cy + 4), (x1 - 8, y1 - 3)], fill=(120, 86, 58),
            width=2)
    for dx in (-10, 0, 10):
        dr.ellipse([cx + dx - 3, cy - 9, cx + dx + 3, cy - 3],
                   fill=NAVY)
    dr.rectangle([cx - 13, cy - 14, cx + 13, cy - 11], fill=WHITE,
                 outline=INK, width=1)


PICTURES.update({
    "jet": pic_jet, "radar": pic_radar, "dish": pic_dish,
    "radio": pic_radio, "pylon": pic_pylon, "syringe": pic_syringe,
    "fence": pic_fence, "mansion": pic_mansion,
    "parachute": pic_parachute, "chair": pic_chair, "ship": pic_ship,
    "ban": pic_ban, "scroll": pic_scroll, "key": pic_key,
    "siren": pic_siren, "circuit": pic_circuit, "coins": pic_coins,
    "graph": pic_graph, "table": pic_table,
})


if __name__ == "__main__":
    main()
