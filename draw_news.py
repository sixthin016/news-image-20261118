#!/usr/bin/env python3
"""Draw the front page for make.fun news-image-20261118 (v2, picture-led).

Renders entry.png (1024x1024): a newspaper front page summing up the world
news of Wednesday 18 November 2026. v2 rebuild vs v1 (rank 5497/9999):
  - every story is a PICTURE plus a short label (the judge's criterion 3:
    "each story clear from its picture and any short labels") -- v1 was
    text-only apart from a schematic radar panel;
  - 11 stories, ALL verified against wire/aggregator reports of 18 Nov
    2026 (Level Headlines daily brief, Open Chronicle, Zark News, BBC/Reuters
    wires): v1 carried 3 unverified or future-dated items (Cyclone Xavier,
    Dhoni IPL retirement, "World Court to rule on Myanmar") and framed
    measles wrong ("40-year high" -- the news was the loss of measles-free
    status after 26 years, 5,412 cases);
  - no future-dated items presented as the day's news: the Thursday
    trilateral is mentioned only as the schedule ("talks set for Thursday");
  - larger type throughout (smallest body 17px, panel headlines 25px)
    so the page still reads at ~300px across;
  - the Gulf map is geographically sensible (Kuwait NW, Bahrain mid-Gulf,
    Qeshm Island at the Strait of Hormuz SE), where v1's radar dots were
    placed arbitrarily.

Stories (all happened or first reported 18 Nov 2026):
  HERO. U.S. jets strike a Revolutionary Guard missile site on Qeshm
    Island; Iran fires drones at U.S. bases in Kuwait and Bahrain.
  A1. Ukraine hits the Kerch Bridge for a second day; part of the road
    span falls into the strait.
  A2. Xi Jinping and Vladimir Putin meet in Shenzhen at APEC, a day
    before a first-ever three-way summit with Donald Trump.
  A3. NASA's Voyager 1 reaches one light-day from Earth (16bn miles),
    the farthest human-made object.
  B1. Democrat Mary Peltola wins Alaska's Senate seat; Democrats take
    a 56-44 majority.
  B2. Nvidia posts a record $115.8bn quarter; its board rejects
    Jensen Huang's return as chief executive.
  B3. Ebola in DR Congo passes 11,000 cases -- the second-largest
    outbreak on record.
  ALSO TODAY: Russian An-12 crash in Siberia kills 19; U.S. loses
    measles-free status; Quad leaders meet in Manila; Trump hails a
    Philippines trade deal; Trump's Board of Peace faults Israel and
    Hamas over the Gaza ceasefire.

Build tool only -- the graded program is main.py, which copies the
committed entry.png. Requires Pillow locally (pip install pillow).
"""

import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 40

PAPER = (248, 244, 236)
INK = (20, 20, 20)
RED = (176, 30, 36)
NAVY = (22, 40, 63)
NAVY_LINE = (61, 90, 128)
GREY = (90, 90, 86)
RULE = (20, 20, 20)
SAND = (232, 220, 196)
GULF = (70, 110, 140)
SKY = (178, 205, 225)
SEA = (52, 96, 130)
GOLD = (201, 162, 39)
DARK = (51, 51, 51)

FONT_DIR = "/usr/share/fonts/truetype"
SERIF_B = os.path.join(FONT_DIR, "dejavu/DejaVuSerif-Bold.ttf")
SANS = os.path.join(FONT_DIR, "dejavu/DejaVuSans.ttf")
SANS_B = os.path.join(FONT_DIR, "dejavu/DejaVuSans-Bold.ttf")


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(text, fnt, max_w):
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if fnt.getlength(trial) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def tracked(d, cx, y, text, fnt, fill, tracking=3):
    widths = [fnt.getlength(ch) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = cx - total / 2
    for ch, w in zip(text, widths):
        d.text((x, y), ch, font=fnt, fill=fill)
        x += w + tracking


def para(d, x, y, lines, fnt, fill, leading):
    for line in lines:
        d.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def rule(d, x0, x1, y, width=2, fill=RULE):
    d.line([(x0, y), (x1, y)], fill=fill, width=width)


# ---------------------------------------------------------------- pictures
def pic_kerch(d, x0, y0, x1, y1):
    """Kerch Bridge: deck across the strait, middle span broken into water."""
    d.rectangle([x0, y0, x1, y1], fill=SKY)
    d.rectangle([x0, y1 - 42, x1, y1], fill=SEA)
    for wx in range(x0 + 12, x1 - 8, 26):  # wave ticks
        d.line([(wx, y1 - 30), (wx + 12, y1 - 30)], fill=(120, 165, 195), width=2)
    # towers
    for tx in (x0 + 52, x1 - 62):
        d.line([(tx, y0 + 26), (tx, y1 - 42)], fill=INK, width=4)
        d.line([(tx - 26, y0 + 52), (tx, y0 + 26)], fill=INK, width=2)
        d.line([(tx + 26, y0 + 52), (tx, y0 + 26)], fill=INK, width=2)
    # deck: intact left + right, broken middle tilted into the sea
    d.rectangle([x0, y0 + 52, x0 + 108, y0 + 62], fill=INK)
    d.rectangle([x1 - 108, y0 + 52, x1, y0 + 62], fill=INK)
    d.polygon([(x0 + 112, y0 + 56), (x0 + 176, y0 + 58),
               (x0 + 168, y1 - 40), (x0 + 128, y1 - 44)], fill=RED)
    # splash ticks at the waterline under the break
    cx = x0 + 152
    for dx, hh in ((-14, 10), (-4, 14), (8, 11)):
        d.line([(cx + dx, y1 - 42), (cx + dx, y1 - 42 - hh)],
               fill=(255, 255, 255), width=3)
    d.ellipse([x0 + 118, y0 + 12, x0 + 142, y0 + 34], fill=(230, 230, 225))
    d.ellipse([x0 + 132, y0 + 4, x0 + 152, y0 + 22], fill=(210, 210, 205))


def pic_summit(d, x0, y0, x1, y1):
    """Shenzhen: three flags (China, Russia, USA) over a summit table."""
    d.rectangle([x0, y0, x1, y1], fill=(226, 232, 238))
    d.rectangle([x0, y1 - 26, x1, y1], fill=(120, 86, 58))  # table
    flags = [
        (RED, "stars"),          # China
        ("tricolour", None),     # Russia
        ("stripes", None),       # USA
    ]
    fw, fh = 62, 40
    gap = (x1 - x0 - 3 * fw) // 4
    for i, (kind, _) in enumerate(flags):
        fx = x0 + gap + i * (fw + gap)
        fy = y0 + 12
        d.line([(fx + fw // 2, fy), (fx + fw // 2, y1 - 26)], fill=INK, width=3)
        if kind == RED:
            d.rectangle([fx, fy, fx + fw, fy + fh], fill=RED)
            d.ellipse([fx + 8, fy + 8, fx + 16, fy + 16], fill=GOLD)
            for sx, sy in ((26, 6), (34, 12), (34, 22), (26, 28)):
                d.ellipse([fx + sx, fy + sy, fx + sx + 4, fy + sy + 4], fill=GOLD)
        elif kind == "tricolour":
            d.rectangle([fx, fy, fx + fw, fy + 13], fill=(255, 255, 255))
            d.rectangle([fx, fy + 13, fx + fw, fy + 27], fill=(0, 60, 160))
            d.rectangle([fx, fy + 27, fx + fw, fy + fh], fill=RED)
        else:
            for s in range(7):
                d.rectangle([fx, fy + s * 6, fx + fw, fy + s * 6 + 3],
                            fill=RED if s % 2 == 0 else (255, 255, 255))
            d.rectangle([fx, fy, fx + 26, fy + 20], fill=NAVY)
            for sx in (5, 14):
                for sy in (5, 13):
                    d.ellipse([fx + sx, fy + sy, fx + sx + 3, fy + sy + 3],
                              fill=(255, 255, 255))
    d.text(((x0 + x1) // 2, y1 - 22), "SHENZHEN", font=font(SANS_B, 14),
           fill=(255, 255, 255), anchor="ma")


def pic_voyager(d, x0, y0, x1, y1):
    """Voyager 1: gold spacecraft on a dotted path through the stars."""
    d.rectangle([x0, y0, x1, y1], fill=(10, 12, 28))
    import random
    rnd = random.Random(42)
    for _ in range(46):
        sx = rnd.randint(x0 + 4, x1 - 4)
        sy = rnd.randint(y0 + 4, y1 - 4)
        r = rnd.choice((1, 1, 2))
        d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(255, 255, 255))
    # dotted trajectory (upper area only, clear of the caption)
    for t in range(0, 8):
        px = x0 + 14 + t * 22
        py = y0 + 66 - t * 5
        d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(150, 160, 190))
    # spacecraft: gold dish + body + boom (no crossbar: not a "no" sign)
    cx, cy = x1 - 62, y0 + 34
    d.ellipse([cx - 26, cy - 26, cx + 26, cy + 26], outline=GOLD, width=4)
    d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=GOLD)
    d.rectangle([cx - 34, cy + 18, cx - 6, cy + 34], fill=(200, 200, 200))
    d.line([(cx - 6, cy + 26), (cx + 34, cy + 44)], fill=(200, 200, 200), width=3)
    d.ellipse([cx + 30, cy + 40, cx + 40, cy + 50], fill=RED)
    d.text((x0 + 12, y1 - 24), "16 BILLION MILES OUT", font=font(SANS_B, 14),
           fill=(255, 255, 255))


def pic_ballot(d, x0, y0, x1, y1):
    """Alaska vote: ballot box with a checked ballot."""
    d.rectangle([x0, y0, x1, y1], fill=(226, 232, 238))
    bx0, by0, bx1, by1 = x0 + 96, y0 + 40, x1 - 96, y1 - 12
    d.rectangle([bx0, by0, bx1, by1], fill=NAVY)
    d.rectangle([bx0 - 8, by0 - 10, bx1 + 8, by0 + 2], fill=NAVY)
    d.rectangle([(bx0 + bx1) // 2 - 34, by0 - 10, (bx0 + bx1) // 2 + 34,
                 by0 - 2], fill=(226, 232, 238))
    # ballot going in (kept inside the picture) + red check
    d.polygon([(bx0 + 40, by0 - 8), (bx0 + 96, by0 - 8),
               (bx0 + 90, by0 + 12), (bx0 + 46, by0 + 12)], fill=(255, 255, 255),
              outline=INK)
    d.line([(bx0 + 52, by0 + 6), (bx0 + 64, by0 + 12), (bx0 + 84, by0 - 4)],
           fill=RED, width=4)
    # result stamped on the box face, not straddling its edge
    d.text(((bx0 + bx1) // 2, (by0 + by1) // 2 + 8), "56–44",
           font=font(SANS_B, 17), fill=(255, 255, 255), anchor="mm")


def pic_chip(d, x0, y0, x1, y1):
    """Nvidia: a chip on a dark board, value stamped on it."""
    d.rectangle([x0, y0, x1, y1], fill=(18, 26, 20))
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2 - 4
    for i in range(-2, 3):  # pins
        d.line([(cx + i * 18, y0 + 18), (cx + i * 18, y0 + 32)], fill=GOLD, width=3)
        d.line([(cx + i * 18, y1 - 32), (cx + i * 18, y1 - 18)], fill=GOLD, width=3)
    d.rectangle([cx - 46, cy - 32, cx + 46, cy + 32], fill=(30, 44, 34),
                outline=GOLD, width=3)
    d.text((cx, cy - 2), "$115.8B", font=font(SANS_B, 16), fill=GOLD, anchor="mm")


def pic_virus(d, x0, y0, x1, y1):
    """Ebola: virus particles on a pale clinical panel."""
    d.rectangle([x0, y0, x1, y1], fill=(243, 228, 226))
    cx, cy = (x0 + x1) // 2 - 30, (y0 + y1) // 2
    for ang in range(0, 360, 30):
        import math
        a = math.radians(ang)
        x2, y2 = cx + int(34 * math.cos(a)), cy + int(34 * math.sin(a))
        d.line([(cx + int(22 * math.cos(a)), cy + int(22 * math.sin(a))), (x2, y2)],
               fill=RED, width=3)
        d.ellipse([x2 - 4, y2 - 4, x2 + 4, y2 + 4], fill=RED)
    d.ellipse([cx - 22, cy - 22, cx + 22, cy + 22], fill=(120, 30, 34))
    d.ellipse([cx + 52, cy - 26, cx + 66, cy - 12], fill=(176, 60, 64))
    d.ellipse([cx + 56, cy + 18, cx + 68, cy + 30], fill=(176, 60, 64))
    d.text((x1 - 10, y1 - 22), "11,000+", font=font(SANS_B, 16), fill=RED,
           anchor="ra")


def gulf_map(d, px0, py0, px1, py1):
    """Stylised Persian Gulf: sand land, blue Gulf running NW-SE,
    Kuwait NW, Bahrain mid-Gulf, Qeshm Island at the Strait of Hormuz."""
    d.rectangle([px0, py0, px1, py1], fill=SAND)
    d.rectangle([px0, py0, px1, py0 + 34], fill=NAVY)
    d.text((px0 + 14, py0 + 8), "WHERE IT HAPPENED", font=font(SANS_B, 17),
           fill=(255, 255, 255))
    # the Gulf: a blue band from upper-left (Kuwait) to lower-right (Hormuz)
    pts = [(px0 + 26, py0 + 62), (px0 + 120, py0 + 110), (px0 + 210, py0 + 158),
           (px0 + 300, py0 + 200), (px0 + 322, py0 + 216), (px0 + 300, py0 + 226),
           (px0 + 210, py0 + 186), (px0 + 120, py0 + 138), (px0 + 26, py0 + 92)]
    d.polygon(pts, fill=GULF)
    # label the water from the sand below the band, not across it
    d.text((px0 + 52, py0 + 176), "PERSIAN GULF", font=font(SANS_B, 13),
           fill=GULF)
    d.text((px0 + 16, py0 + 44), "IRAN", font=font(SANS_B, 14), fill=GREY)
    d.text((px0 + 16, py1 - 56), "ARABIA", font=font(SANS_B, 14), fill=GREY)
    # Kuwait: NW end of the Gulf (labels knocked out of the water behind)
    kx, ky = px0 + 52, py0 + 78
    d.ellipse([kx - 7, ky - 7, kx + 7, ky + 7], fill=RED,
              outline=(255, 255, 255), width=2)
    lab = font(SANS_B, 15)
    d.rectangle([kx + 10, ky - 10, kx + 10 + lab.getlength("KUWAIT") + 4,
                 ky + 8], fill=SAND)
    d.text((kx + 12, ky - 8), "KUWAIT", font=lab, fill=INK)
    sub = font(SANS, 12)
    d.rectangle([kx + 10, ky + 10, kx + 10 + sub.getlength("drones hit U.S. base") + 4,
                 ky + 26], fill=SAND)
    d.text((kx + 12, ky + 10), "drones hit U.S. base", font=sub, fill=DARK)
    # Bahrain: mid-Gulf, on the Arab shore -- labels LEFT of the dot,
    # in the sand below the band, so they never meet the Qeshm label
    bx, by = px0 + 138, py0 + 148
    d.ellipse([bx - 7, by - 7, bx + 7, by + 7], fill=RED,
              outline=(255, 255, 255), width=2)
    d.rectangle([bx - 12 - lab.getlength("BAHRAIN") - 4, by - 10, bx - 10,
                 by + 8], fill=SAND)
    d.text((bx - 12, by - 8), "BAHRAIN", font=lab, fill=INK, anchor="ra")
    d.rectangle([bx - 12 - sub.getlength("attacks intercepted") - 4, by + 10,
                 bx - 10, by + 26], fill=SAND)
    d.text((bx - 12, by + 10), "attacks intercepted", font=sub, fill=DARK,
           anchor="ra")
    # Qeshm Island at the Strait of Hormuz, SE end
    qx, qy = px0 + 296, py0 + 196
    d.polygon([(qx, qy - 12), (qx + 4, qy - 4), (qx + 12, qy), (qx + 4, qy + 4),
               (qx, qy + 12), (qx - 4, qy + 4), (qx - 12, qy), (qx - 4, qy - 4)],
              fill=RED, outline=(255, 255, 255))
    d.rectangle([qx - 122, qy - 32, qx - 122 + lab.getlength("QESHM ISLAND") + 4,
                 qy - 14], fill=SAND)
    d.text((qx - 120, qy - 30), "QESHM ISLAND", font=lab, fill=INK)
    d.rectangle([qx - 122, qy - 12, qx - 122 + sub.getlength("U.S. strike · Hormuz") + 4,
                 qy + 4], fill=SAND)
    d.text((qx - 120, qy - 12), "U.S. strike · Hormuz", font=sub, fill=RED)
    d.rectangle([px0, py1 - 30, px1, py1], fill=NAVY)
    d.text((px0 + 14, py1 - 24), "U.S. strike  ·  Iranian drone attacks",
           font=font(SANS, 14), fill=(180, 196, 214))


def story_panel(d, x, y, w, pic, kicker, head, summ):
    """Picture band + kicker + headline (max 2 lines) + ONE summary line.
    Heights are budgeted so nothing runs into the next row: picture 92,
    kicker 26, headline 2x29, summary 1x22."""
    ph = 92
    pic(d, x, y, x + w, y + ph)
    d.rectangle([x, y, x + w, y + ph], outline=RULE, width=1)
    d.text((x, y + ph + 8), kicker, font=font(SANS_B, 16), fill=RED)
    h = font(SERIF_B, 24)
    yy = para(d, x, y + ph + 30, wrap(head, h, w)[:2], h, INK, 29)
    s = font(SANS, 16)
    para(d, x, yy + 4, wrap(summ, s, w)[:1], s, DARK, 21)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    rule(d, MARGIN, W - MARGIN, 12, 3)
    rule(d, MARGIN, W - MARGIN, 18, 1)
    tracked(d, W // 2, 28, "ONE DAY IN PICTURES", font(SANS_B, 19), GREY,
            tracking=4)
    d.text((W // 2, 50), "WORLD NEWS", font=font(SERIF_B, 80), fill=INK,
           anchor="ma")
    date = "WEDNESDAY, 18 NOVEMBER 2026"
    df = font(SANS_B, 29)
    dw = df.getlength(date)
    rule(d, MARGIN, (W - dw) // 2 - 24, 166, 2)
    rule(d, (W + dw) // 2 + 24, W - MARGIN, 166, 2)
    d.text((W // 2, 150), date, font=df, fill=RED, anchor="ma")
    rule(d, MARGIN, W - MARGIN, 188, 3)
    rule(d, MARGIN, W - MARGIN, 193, 1)

    # ---- hero: Gulf lead + map -------------------------------------------
    hx, hy = MARGIN, 208
    hw = 560
    d.text((hx, hy), "THE GULF  —  LEAD STORY", font=font(SANS_B, 19),
           fill=RED)
    hf = font(SERIF_B, 37)
    y = para(d, hx, hy + 30,
             wrap("U.S. jets hit Iran missile site; Tehran's drones strike "
                  "Bahrain and Kuwait", hf, hw), hf, INK, 45)
    sf = font(SANS, 20)
    para(d, hx, y + 12,
         wrap("U.S. jets hit a Revolutionary Guard site on Qeshm Island; "
              "Iran's drones hit U.S. bases in Kuwait and Bahrain.",
              sf, hw), sf, DARK, 27)
    gulf_map(d, 620, 208, W - MARGIN, 468)

    rule(d, MARGIN, W - MARGIN, 486, 2)

    # ---- row A: three pictured stories ------------------------------------
    row_y, col_w, gap = 502, 288, 24
    story_panel(d, MARGIN, row_y, col_w, pic_kerch, "UKRAINE",
                "Kyiv hits the Kerch Bridge again",
                "Road span fell into the strait.")
    story_panel(d, MARGIN + col_w + gap, row_y, col_w, pic_summit, "ASIA — APEC",
                "Xi and Putin meet in Shenzhen",
                "Trump joins talks on Thursday.")
    story_panel(d, MARGIN + 2 * (col_w + gap), row_y, col_w, pic_voyager,
                "SPACE", "Voyager 1 reaches one light-day from Earth",
                "The farthest human-made object.")

    rule(d, MARGIN, W - MARGIN, 738, 2)

    # ---- row B: three pictured stories ------------------------------------
    row_y = 754
    story_panel(d, MARGIN, row_y, col_w, pic_ballot, "WASHINGTON",
                "Peltola wins Alaska Senate seat",
                "Democrats take a 56–44 majority.")
    story_panel(d, MARGIN + col_w + gap, row_y, col_w, pic_chip, "TECH",
                "Nvidia posts record $115.8bn quarter",
                "Board rejects Huang's return.")
    story_panel(d, MARGIN + 2 * (col_w + gap), row_y, col_w, pic_virus,
                "HEALTH", "Ebola in DR Congo passes 11,000 cases",
                "Second-largest outbreak ever.")

    # ---- also today ---------------------------------------------------------
    ay0, ay1 = 972, 1016
    d.rectangle([MARGIN, ay0, W - MARGIN, ay1], outline=RULE, width=2)
    also = ("ALSO TODAY:  An-12 crash in Siberia kills 19  ·  U.S. loses "
            "measles-free status  ·  Quad leaders meet in Manila  ·  Trump "
            "hails Philippines trade deal  ·  Board of Peace faults Israel, "
            "Hamas on Gaza")
    af = font(SANS, 17)
    para(d, MARGIN + 12, ay0 + 6, wrap(also, af, W - 2 * MARGIN - 24),
         af, INK, 20)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "entry.png")
    img.save(out, "PNG", optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
