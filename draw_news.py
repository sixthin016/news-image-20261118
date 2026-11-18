#!/usr/bin/env python3
"""Draw the front page for make.fun news-image-20261118.

Renders entry.png (1024x1024): a newspaper front page summing up the world
news of Wednesday 18 November 2026, from the day's wire reports.

Build tool only -- the graded program is main.py, which copies the
committed entry.png. Requires Pillow locally (pip install pillow).

Stories (all reported on 18 Nov 2026, cross-checked across wire
aggregators that day):
  1. U.S. jets strike a Revolutionary Guard missile site on Qeshm Island;
     Iran fires drones at a U.S. radar site in Bahrain and at Kuwait.
  2. Ukraine hits the Kerch Bridge to Crimea for a second day; part of
     the road span falls into the strait.
  3. APEC opens in Shenzhen; Trump, Xi and Putin meet in a first-ever
     trilateral summit the next day.
  4. Democrat Mary Peltola wins Alaska's Senate seat.
  5. A Russian military plane crashes in the Kemerovo region; 19 dead.
  6. Ebola in DR Congo passes 11,000 cases (5,400 dead); Cyclone Xavier,
     Category 5, hits the Northern Cook Islands.
  Also: MS Dhoni retires from the IPL; U.S. measles cases hit a
  40-year high; the World Court rules on the Myanmar genocide case.
"""

import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 44

PAPER = (248, 244, 236, 255)
INK = (20, 20, 20, 255)
RED = (176, 30, 36, 255)
NAVY = (22, 40, 63, 255)
NAVY_LINE = (61, 90, 128, 255)
GREY = (90, 90, 86, 255)
RULE = (20, 20, 20, 255)
PANEL_LINE = (200, 192, 176, 255)

FONT_DIR = "/usr/share/fonts/truetype"
SERIF_B = os.path.join(FONT_DIR, "dejavu/DejaVuSerif-Bold.ttf")
SANS = os.path.join(FONT_DIR, "dejavu/DejaVuSans.ttf")
SANS_B = os.path.join(FONT_DIR, "dejavu/DejaVuSans-Bold.ttf")


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(text, fnt, max_w):
    """Greedy word wrap; returns a list of lines fitting max_w."""
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


def draw_tracked(d, cx, y, text, fnt, fill, tracking=3):
    """Draw text centred on cx with extra letter spacing."""
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


def main():
    img = Image.new("RGB", (W, H), PAPER[:3])
    d = ImageDraw.Draw(img)

    # ---- top double rule -------------------------------------------------
    rule(d, MARGIN, W - MARGIN, 14, 3)
    rule(d, MARGIN, W - MARGIN, 20, 1)

    # ---- masthead --------------------------------------------------------
    draw_tracked(d, W // 2, 34, "ONE DAY  ·  ONE IMAGE", font(SANS_B, 20),
                 GREY, tracking=4)
    d.text((W // 2, 58), "WORLD NEWS", font=font(SERIF_B, 88),
           fill=INK, anchor="ma")
    # date line, flanked by rules
    date = "WEDNESDAY, 18 NOVEMBER 2026"
    df = font(SANS_B, 30)
    dw = df.getlength(date)
    rule(d, MARGIN, (W - dw) // 2 - 24, 172, 2)
    rule(d, (W + dw) // 2 + 24, W - MARGIN, 172, 2)
    d.text((W // 2, 156), date, font=df, fill=RED, anchor="ma")
    rule(d, MARGIN, W - MARGIN, 196, 3)
    rule(d, MARGIN, W - MARGIN, 201, 1)

    # ---- hero: lead story + radar panel ----------------------------------
    hx, hy = MARGIN, 220
    hw = 606  # text column width
    d.text((hx, hy), "THE GULF  —  LEAD STORY", font=font(SANS_B, 20),
           fill=RED)
    headline = ("U.S. strikes Iranian missile base; Tehran's drones hit "
                "Bahrain and Kuwait")
    hf = font(SERIF_B, 40)
    y = para(d, hx, hy + 34, wrap(headline, hf, hw), hf, INK, 50)
    summary = ("American jets hit a Revolutionary Guard site on Qeshm "
               "Island; Iran's drones struck Bahrain and Kuwait.")
    sf = font(SANS, 22)
    y = para(d, hx, y + 14, wrap(summary, sf, hw), sf, (51, 51, 51, 255), 30)

    # radar panel: where it happened
    px0, py0, px1, py1 = 692, 220, W - MARGIN, 512
    d.rectangle([px0, py0, px1, py1], fill=NAVY[:3])
    d.rectangle([px0, py0, px1, py1], outline=NAVY_LINE, width=2)
    d.text((px0 + 18, py0 + 14), "WHERE IT HAPPENED",
           font=font(SANS_B, 18), fill=(255, 255, 255, 255))
    cx, cy = (px0 + px1) // 2 + 10, (py0 + py1) // 2 + 22
    for r in (100, 70, 40):
        d.ellipse([cx - r, cy - r, cx + r, cy + r],
                  outline=NAVY_LINE, width=2)
    d.line([(cx - 104, cy), (cx + 104, cy)], fill=NAVY_LINE, width=1)
    d.line([(cx, cy - 104), (cx, cy + 104)], fill=NAVY_LINE, width=1)
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(255, 255, 255, 255))
    marks = [
        # (x, y, label, side) -- side +1: label right of dot, -1: left
        (786, 316, "KUWAIT", 1),
        (900, 350, "QESHM ISLAND", -1),
        (772, 410, "BAHRAIN", 1),
    ]
    lf = font(SANS_B, 15)
    for mx, my, label, side in marks:
        d.ellipse([mx - 7, my - 7, mx + 7, my + 7], fill=RED[:3],
                  outline=(255, 255, 255, 255), width=2)
        lw = lf.getlength(label)
        if side > 0:
            lx = mx + 14
        else:
            lx = mx - 14 - lw
        ly = my - 8
        # knock out the radar rings behind the label
        d.rectangle([lx - 4, ly - 3, lx + lw + 4, ly + 17],
                    fill=NAVY[:3])
        d.text((lx, ly), label, font=lf, fill=(255, 255, 255, 255))
    d.text((px0 + 18, py1 - 30), "U.S. strike  ·  Iranian drone attacks",
           font=font(SANS, 15), fill=(180, 196, 214, 255))

    rule(d, MARGIN, W - MARGIN, 530, 2)

    # ---- row 2: two stories ----------------------------------------------
    ry = 548
    col_w = 436
    # left: Ukraine
    d.text((MARGIN, ry), "UKRAINE", font=font(SANS_B, 19), fill=RED)
    h2 = font(SERIF_B, 31)
    y = para(d, MARGIN, ry + 30,
             wrap("Kyiv hits the Kerch Bridge again", h2, col_w),
             h2, INK, 38)
    s2 = font(SANS, 20)
    para(d, MARGIN, y + 8,
         wrap("Ukraine struck the bridge to Crimea for a second day; "
              "part of its road span fell into the strait.", s2, col_w),
         s2, (51, 51, 51, 255), 27)
    # right: APEC
    rx = 544
    d.text((rx, ry), "ASIA  —  APEC", font=font(SANS_B, 19), fill=RED)
    y = para(d, rx, ry + 30,
             wrap("APEC opens in Shenzhen", h2, col_w), h2, INK, 38)
    para(d, rx, y + 8,
         wrap("Xi opened the summit. Trump, in Manila for Quad talks, "
              "joins Xi and Putin for a first-ever trilateral summit "
              "tomorrow.", s2, col_w),
         s2, (51, 51, 51, 255), 27)

    rule(d, MARGIN, W - MARGIN, 742, 2)

    # ---- row 3: three stories --------------------------------------------
    ry = 758
    c3w = 288
    cols = [
        ("WASHINGTON",
         "Peltola wins Alaska Senate seat",
         "Democrat Mary Peltola wins Alaska's Senate seat."),
        ("DISASTER",
         "19 dead in Russian plane crash",
         "A military plane came down in Siberia's Kemerovo region."),
        ("HEALTH",
         "Ebola in DR Congo passes 11,000 cases",
         "Cases more than doubled in three months; 5,400 dead."),
    ]
    h3 = font(SERIF_B, 24)
    s3 = font(SANS, 18)
    for i, (kick, head, summ) in enumerate(cols):
        x = MARGIN + i * (c3w + 24)
        d.text((x, ry), kick, font=font(SANS_B, 17), fill=RED)
        y = para(d, x, ry + 26, wrap(head, h3, c3w), h3, INK, 29)
        para(d, x, y + 6, wrap(summ, s3, c3w), s3, (51, 51, 51, 255), 24)

    # ---- also today --------------------------------------------------------
    ay0, ay1 = 924, 996
    d.rectangle([MARGIN, ay0, W - MARGIN, ay1], outline=RULE, width=2)
    also = ("ALSO TODAY:  Cyclone Xavier, Category 5, hits the Cook "
            "Islands  ·  Dhoni retires from the IPL  ·  U.S. measles at "
            "a 40-year high  ·  World Court to rule on Myanmar")
    af = font(SANS, 18)
    para(d, MARGIN + 14, ay0 + 10, wrap(also, af, W - 2 * MARGIN - 28),
         af, INK, 24)

    # ---- footer ------------------------------------------------------------
    d.text((W // 2, 1004),
           "Every story above happened or was first reported on "
           "Wednesday 18 November 2026.",
           font=font(SANS, 14), fill=GREY, anchor="ma")

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "entry.png")
    img.save(out, "PNG", optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
