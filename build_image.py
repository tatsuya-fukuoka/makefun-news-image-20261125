#!/usr/bin/env python3
"""Build entry.png: newspaper-style front page for Wednesday 25 November 2026.
Deterministic: fixed fonts, no randomness, no timestamps in PNG metadata."""
import math
import os
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
PAPER = (244, 238, 224)
INK = (20, 20, 20)
RED = (200, 24, 30)
FONT_DIR = "/usr/share/fonts/truetype/noto/"
F_BOLD = FONT_DIR + "NotoSans-Bold.ttf"
F_BLACK = FONT_DIR + "NotoSans-Black.ttf"
F_COND = FONT_DIR + "NotoSans-CondensedBold.ttf"
F_REG = FONT_DIR + "NotoSans-Medium.ttf"
if not os.path.exists(F_REG):
    F_REG = FONT_DIR + "NotoSans-Regular.ttf"

def font(path, size):
    return ImageFont.truetype(path, size)

def tw(d, text, f, spacing=0):
    return d.textlength(text, font=f) + spacing * max(0, len(text) - 1)

def spaced(d, xy, text, f, fill, spacing):
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=f, fill=fill)
        x += d.textlength(ch, font=f) + spacing

def wrap(d, text, f, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if tw(d, t, f) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur); cur = w
    lines.append(cur)
    return lines

def fit_lines(d, text, path, maxw, max_lines, start, minimum):
    for s in range(start, minimum - 1, -1):
        f = font(path, s)
        lines = wrap(d, text, f, maxw)
        if len(lines) <= max_lines and all(tw(d, l, f) <= maxw for l in lines):
            return f, lines, s
    raise SystemExit("text does not fit: " + text)

# ---------------- pictograms (drawn at 4x on a transparent layer) ----------------
S = 4
PW, PH = 150, 118

def star_pts(cx, cy, r_out, r_in, n, rot=-90):
    pts = []
    for i in range(n * 2):
        r = r_out if i % 2 == 0 else r_in
        a = math.radians(rot + i * 180 / n)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts

class P:
    def __init__(self):
        self.im = Image.new("RGBA", (PW * S, PH * S), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.im)
    def pts(self, pts): return [(x * S, y * S) for x, y in pts]
    def rect(self, x0, y0, x1, y1, fill=INK):
        self.d.rectangle([x0 * S, y0 * S, x1 * S, y1 * S], fill=fill)
    def poly(self, pts, fill=INK): self.d.polygon(self.pts(pts), fill=fill)
    def ell(self, x0, y0, x1, y1, fill=INK, outline=None, w=0):
        self.d.ellipse([x0 * S, y0 * S, x1 * S, y1 * S], fill=fill, outline=outline, width=int(w * S))
    def line(self, pts, w, fill=INK):
        self.d.line(self.pts(pts), fill=fill, width=int(w * S), joint="curve")
    def burst(self, cx, cy, ro, ri, n=10, fill=RED):
        self.poly(star_pts(cx, cy, ro, ri, n), fill)
    def waves(self, y, x0, x1, amp=2.5, period=14, w=2.4, fill=INK):
        pts = []
        x = x0
        while x <= x1:
            pts.append((x, y + amp * math.sin((x - x0) / period * 2 * math.pi)))
            x += 1
        self.line(pts, w, fill)
    def out(self):
        return self.im.resize((PW, PH), Image.LANCZOS)

def pic_tower():
    p = P()
    p.rect(8, 100, 142, 104)                      # ground
    p.rect(14, 70, 38, 100); p.rect(112, 62, 136, 100)   # neighbours
    p.rect(48, 34, 102, 100)                      # main body
    p.rect(58, 24, 92, 34); p.rect(68, 14, 82, 24)
    p.rect(73, 2, 77, 14)                         # antenna
    for r in range(4):                            # windows
        for c in range(4):
            p.rect(54 + c * 12, 42 + r * 14, 60 + c * 12, 50 + r * 14, PAPER)
    for r in range(3):
        p.rect(18, 76 + r * 8, 24, 80 + r * 8, PAPER); p.rect(28, 76 + r * 8, 34, 80 + r * 8, PAPER)
        p.rect(116, 68 + r * 10, 122, 73 + r * 10, PAPER); p.rect(126, 68 + r * 10, 132, 73 + r * 10, PAPER)
    p.burst(75, 20, 26, 11, 12, RED)
    p.burst(75, 20, 12, 5, 8, PAPER)
    return p.out()

def pic_gaza():
    p = P()
    p.rect(4, 104, 146, 108)
    blds = [(8, 66, 30), (30, 48, 52), (54, 74, 74), (76, 56, 96), (98, 80, 118), (120, 60, 142)]
    for x0, top, x1 in blds:
        p.rect(x0, top, x1 - 2, 104)
        for yy in range(top + 8, 98, 12):
            p.rect(x0 + 4, yy, x0 + 8, yy + 5, PAPER)
            if x1 - x0 > 20:
                p.rect(x0 + 13, yy, x0 + 17, yy + 5, PAPER)
    p.poly([(58, 74), (64, 66), (70, 74)], INK)   # rubble/damage notch
    p.burst(62, 76, 15, 7, 10, RED)
    # drone
    cx, cy = 104, 24
    p.ell(cx - 14, cy - 5, cx + 14, cy + 6, INK)
    p.poly([(cx - 4, cy + 6), (cx + 4, cy + 6), (cx, cy + 12)], INK)
    for dx in (-26, 26):
        p.line([(cx, cy), (cx + dx, cy - 6)], 3)
        p.rect(cx + dx - 9, cy - 10, cx + dx + 9, cy - 8)
    p.rect(cx - 2, cy - 12, cx + 2, cy - 5)
    p.line([(cx, cy + 12), (80, 62)], 2, RED)    # strike line
    return p.out()

def pic_ship():
    p = P()
    p.burst(112, 38, 24, 11, 12, RED)
    p.burst(112, 38, 11, 5, 8, PAPER)
    p.poly([(14, 70), (136, 70), (122, 90), (30, 90)])           # hull
    p.rect(40, 54, 98, 70)                                       # deck block
    p.rect(52, 42, 82, 54)
    p.rect(60, 34, 70, 42)
    p.rect(64, 12, 67, 34)                                       # mast
    p.line([(55, 22), (79, 22)], 2)
    p.rect(86, 58, 94, 70, PAPER)
    p.rect(100, 62, 118, 66)                                     # gun
    p.rect(20, 62, 36, 70)
    for x in (46, 56, 66, 76):
        p.ell(x, 46, x + 5, 51, PAPER)
    p.waves(95, 2, 148, 3, 20, 3, INK)
    p.waves(106, 2, 148, 3, 20, 3, INK)
    return p.out()

def pic_treaty():
    p = P()
    # two islands
    p.poly([(2, 96), (10, 80), (26, 70), (42, 78), (50, 96)])
    p.poly([(100, 96), (108, 82), (124, 72), (140, 80), (148, 96)])
    # palms
    for x, y in ((26, 70), (124, 72)):
        p.line([(x, y), (x + 2, y - 16)], 2.5)
        for ang in (-150, -110, -70, -30):
            a = math.radians(ang)
            p.line([(x + 2, y - 16), (x + 2 + 10 * math.cos(a), y - 16 + 8 * math.sin(a) + 3)], 2.5)
    p.waves(103, 2, 148, 2.5, 18, 3, INK)
    # document
    p.rect(52, 8, 98, 78, INK)
    p.rect(55, 11, 95, 75, PAPER)
    for i in range(5):
        p.rect(61, 20 + i * 8, 89, 22 + i * 8, INK)
    p.rect(61, 62, 78, 64, INK)
    p.burst(87, 64, 8, 4, 10, RED)                # seal
    # pen
    p.poly([(96, 40), (101, 36), (124, 58), (118, 62)], RED)
    p.poly([(96, 40), (118, 62), (92, 66)], INK)
    return p.out()

def pic_space():
    p = P()
    # flag motif (abstract): crescent + star on a panel
    p.rect(4, 14, 74, 78, INK)
    p.ell(12, 26, 46, 60, PAPER)
    p.ell(20, 23, 54, 57, INK)
    p.poly(star_pts(55, 40, 9, 3.8, 5), PAPER)
    # rocket (right)
    p.poly([(112, 6), (124, 26), (124, 78), (100, 78), (100, 26)])
    p.ell(105, 28, 119, 42, PAPER)
    p.poly([(100, 58), (86, 82), (100, 78)])
    p.poly([(124, 58), (138, 82), (124, 78)])
    p.rect(104, 78, 120, 84)
    p.poly([(104, 84), (120, 84), (112, 112)], RED)
    p.poly([(108, 84), (116, 84), (112, 100)], PAPER)
    p.line([(112, 6), (112, 6)], 1)
    # stars
    p.poly(star_pts(88, 22, 4, 1.6, 4, 0), INK)
    p.poly(star_pts(142, 40, 4, 1.6, 4, 0), INK)
    p.waves(100, 6, 76, 0, 10, 0.1, INK)
    p.rect(6, 96, 76, 99)
    return p.out()

def pic_mine():
    p = P()
    p.poly([(75, 4), (146, 108), (4, 108)], RED)
    p.poly([(75, 22), (130, 100), (20, 100)], PAPER)
    # mine disc with spikes
    cx, cy = 75, 78
    for a in range(0, 360, 45):
        r = math.radians(a)
        p.line([(cx, cy), (cx + 22 * math.cos(r), cy + 22 * math.sin(r))], 4)
    p.ell(cx - 17, cy - 17, cx + 17, cy + 17, INK)
    p.ell(cx - 7, cy - 7, cx + 7, cy + 7, PAPER)
    p.ell(cx - 3, cy - 3, cx + 3, cy + 3, RED)
    # exclamation
    p.rect(72, 34, 78, 52, INK)
    p.ell(71.5, 55, 78.5, 62, INK)
    return p.out()

# ---------------- content ----------------
STORIES = [
    ("MIDDLE EAST", "RIYADH TOWER HIT AGAIN", "Houthi attack injures 11", pic_tower),
    ("GAZA", "STRIKE KILLS HAMAS SECURITY CHIEF", "Israeli drone strike on Gaza City", pic_gaza),
    ("UKRAINE WAR", "STRIKES HIT KYIV", "Ukraine hits Russian warship off Libya", pic_ship),
    ("PACIFIC", "AUSTRALIA–SOLOMON ISLANDS TREATY", "Pact bars foreign bases", pic_treaty),
    ("SPACE", "PAKISTAN’S FIRST ASTRONAUT IN ORBIT", "Flies on a Chinese mission", pic_space),
    ("WORLD", "LANDMINE TOLL HITS 5-YEAR HIGH", "Nearly 7,000 casualties in 2025", pic_mine),
]
BRIEFS = ["US PLANS NEW TARIFFS ON CHINA & EU",
          "HUAWEI CONVICTED IN US TRADE-SECRETS CASE",
          "HOSTAGES FREED AFTER CARTAGENA SUPERMARKET RAID"]

def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    report = []

    # --- header ---
    d.rectangle([17, 12, W - 17, 16], fill=INK)
    f_kick = font(F_BOLD, 21)
    kick = "THE WORLD IN ONE DAY"
    sp = 7
    kw = tw(d, kick, f_kick, sp)
    spaced(d, ((W - kw) / 2, 24), kick, f_kick, RED, sp)
    date = "WEDNESDAY 25 NOVEMBER 2026"
    for size in range(70, 30, -1):
        f_date = font(F_BLACK, size)
        if tw(d, date, f_date) <= W - 2 * 22:
            break
    bb = d.textbbox((0, 0), date, font=f_date)
    d.text(((W - (bb[2] - bb[0])) / 2 - bb[0], 56), date, font=f_date, fill=INK)
    report.append(f"date font {size}px")
    d.rectangle([17, 136, W - 17, 138], fill=INK)
    d.rectangle([17, 142, W - 17, 143], fill=INK)

    # --- grid ---
    PWID, PHT, GAP, X0, Y0, RGAP = 490, 250, 10, 17, 152, 8
    pad = 14
    for i, (tag, head, sub, pic) in enumerate(STORIES):
        col, row = i % 2, i // 2
        x = X0 + col * (PWID + GAP)
        y = Y0 + row * (PHT + RGAP)
        d.rectangle([x, y, x + PWID, y + PHT], outline=INK, width=2)
        # region tag pill
        f_tag = font(F_BOLD, 19)
        tgw = tw(d, tag, f_tag, 2)
        d.rectangle([x + pad, y + 12, x + pad + tgw + 18, y + 40], fill=RED)
        spaced(d, (x + pad + 9, y + 14), tag, f_tag, PAPER, 2)
        # pictogram
        im = pic()
        img.paste(im, (x + PWID - PW - 36, y + 8), im)
        # headline
        f_h, lines, hs = fit_lines(d, head, F_COND, PWID - 2 * pad, 2, 34, 28)
        ty = y + 124
        for ln in lines:
            d.text((x + pad, ty), ln, font=f_h, fill=INK)
            ty += int(hs * 1.12)
        f_s, slines, ss = fit_lines(d, sub, F_REG, PWID - 2 * pad, 1, 21, 17)
        d.text((x + pad, y + 212), slines[0], font=f_s, fill=INK)
        report.append(f"panel {i+1} {tag}: headline {hs}px lines={len(lines)} sub {ss}px")

    # --- footer ---
    fy0 = Y0 + 3 * PHT + 2 * RGAP + 8   # 926
    d.rectangle([17, fy0, W - 17, fy0 + 2], fill=INK)
    d.rectangle([17, fy0 + 3, W - 17, H - 8], fill=INK)
    MIN_FOOT = 24
    maxw = W - 2 * 17 - 2 * 14
    used = None
    for n in (3, 2, 1):
        for s in range(30, MIN_FOOT - 1, -1):
            f = font(F_COND, s)
            sep = "  •  "
            text = sep.join(BRIEFS[:n])
            if tw(d, text, f) <= maxw:
                used = (n, s, f, text)
                break
        if used:
            break
    n, s, f, text = used
    report.append(f"footer: {n} briefs at {s}px")
    parts = text.split("•")
    # draw with red bullets
    total = tw(d, text, f)
    bbx = d.textbbox((0, 0), "H", font=f)
    ty = fy0 + 3 + ((H - 8) - (fy0 + 3) - (bbx[3] - bbx[1])) / 2 - bbx[1]
    cx = (W - total) / 2
    for k, part in enumerate(parts):
        d.text((cx, ty), part, font=f, fill=PAPER)
        cx += d.textlength(part, font=f)
        if k < len(parts) - 1:
            d.text((cx, ty), "•", font=f, fill=(255, 90, 90))
            cx += d.textlength("•", font=f)
    return img, report

if __name__ == "__main__":
    img, report = build()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, format="PNG", optimize=True)
    print("\n".join(report))
    print(out, img.size, os.path.getsize(out))
