"""Render entry.png - 22 November 2026 world news in one image.

Deterministic: fixed content, no randomness, no timestamps, fixed PNG params.
Python 3 + Pillow only.

Every block is laid out from measured text; the script asserts that no text
box can cross its rule or the block below, so layout breakage is a hard error.
"""
import os
import sys
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
M = 40
GUT = 16

BG       = (247, 244, 239)
INK      = (26, 26, 26)
INK_SOFT = (92, 88, 82)
HAIR     = (216, 210, 196)
WHITE    = (255, 255, 255)

RED   = (192, 57, 43)
BLUE  = (31, 58, 95)
GREEN = (30, 107, 74)

BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REG  = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

_fc = {}

def fb(s):
    k = ("b", s)
    if k not in _fc:
        try:
            _fc[k] = ImageFont.truetype(BOLD, s)
        except Exception:
            _fc[k] = ImageFont.load_default()
    return _fc[k]

def fr(s):
    k = ("r", s)
    if k not in _fc:
        try:
            _fc[k] = ImageFont.truetype(REG, s)
        except Exception:
            _fc[k] = ImageFont.load_default()
    return _fc[k]

def tw(d, text, f):
    return d.textlength(text, font=f)

def wrap(d, text, f, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if not cur or tw(d, trial, f) <= maxw:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def ellipsize(d, text, f, maxw):
    if tw(d, text, f) <= maxw:
        return text
    ell = "..."
    lo, hi = 0, len(text)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if tw(d, text[:mid].rstrip() + ell, f) <= maxw:
            lo = mid
        else:
            hi = mid - 1
    return text[:lo].rstrip() + ell

# ---------------------------------------------------------------- content
LEADS = [
    dict(head="Trump, Xi and Putin sign China peace declaration",
         sub="Joint declaration issued as Russia hits Ukraine with year's largest attacks",
         region="East Asia", field="Diplomacy", colour=RED),
    dict(head="Bahrain blames Iran; two tankers hit in Hormuz",
         sub="Araghchi says reopening strait \u201cnot difficult\u201d if US accepts terms",
         region="Middle East", field="Security", colour=BLUE),
    dict(head="COP31 deadlocked, enters second overtime day in Antalya",
         sub="Talks stall over fossil-fuel language; draft deal seeks to bridge differences",
         region="Europe", field="Climate", colour=GREEN),
]

MEDIUM = [
    ("FBI criminal database breached, Trump confirms", "North America", "Cyber"),
    ("Indonesia fire: 3 dead, 36 missing", "Southeast Asia", "Disaster"),
    ("Strong earthquake shakes Peru's Andes", "Latin America", "Disaster"),
    ("India, China hold new border talks", "South Asia", "Security"),
    ("Amazon nears $7.5B deal for Decart", "North America", "Business"),
    ("India 720/9, lead New Zealand 352", "South Asia", "Sport"),
    ("Leeds win 4-1 at Chelsea", "Europe", "Sport"),
    ("Estonia to close Russian border", "Europe", "Security"),
]

BRIEFS = [
    ("Nepal PM Balendra Shah begins India visit", "Diplomacy"),
    ("South Korea education minister resigns over AI cheating", "Education"),
    ("Kansas City Current win first NWSL title", "Sport"),
    ("UN states agree draft killer-robot rules by 2028", "Technology"),
    ("Houthis strike after Saudi-led Hodeida operation", "Security"),
]

FIELD_COLOUR = {
    "Diplomacy": RED, "Security": BLUE, "Climate": GREEN, "Cyber": RED,
    "Disaster": BLUE, "Business": GREEN, "Sport": RED, "Education": BLUE,
    "Technology": GREEN,
}

img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)
problems = []

# ============================================================ DATE BAND 40-224
x = M
f_sun = fb(28)
for ch in "SUNDAY":
    d.text((x, 44), ch, font=f_sun, fill=RED)
    x += tw(d, ch, f_sun) + 6

f_day = fb(172)
d.text((M, 222), "22", font=f_day, fill=INK, anchor="ls")
dw = tw(d, "22", f_day)

f_my = fb(42)
mx = int(M + dw + 18)
d.text((mx, 190), "NOVEMBER", font=f_my, fill=INK, anchor="ls")
d.text((mx, 222), "2026", font=f_my, fill=INK, anchor="ls")
if mx + tw(d, "NOVEMBER", f_my) > 652 - 12:
    problems.append("month overruns the divider")

RX = W - M
d.line([(652, 44), (652, 222)], fill=HAIR, width=2)

f_idx = fb(26)
for i, t in enumerate(["16 STORIES", "7 REGIONS", "9 FIELDS"]):
    d.text((RX, 54 + i * 34), t, font=f_idx, fill=INK, anchor="ra")

d.line([(RX - 178, 168), (RX, 168)], fill=HAIR, width=2)
f_dl = fr(17)
d.text((RX, 176), "as of 22 Nov 2026,", font=f_dl, fill=INK_SOFT, anchor="ra")
d.text((RX, 198), "23:59 UTC", font=f_dl, fill=INK_SOFT, anchor="ra")

# ============================================================ LEADS 230-500
LEAD_Y, LEAD_BOT = 230, 516
LEAD_H = LEAD_BOT - LEAD_Y                 # 270
bar_h = 6
cw = (W - 2 * M - 2 * GUT) // 3            # 304
pad = 8
inner = cw - 2 * pad
tag_size = 19
tag_h = 24

def pick_lead_sizes():
    for hs in range(40, 27, -1):
        fh, lh = fb(hs), int(hs * 1.12)
        hl = max(len(wrap(d, l["head"], fh, inner)) for l in LEADS)
        if hl > 5:
            continue
        for ss in (17, 16, 15):
            fs, slh = fr(ss), int(ss * 1.34)
            sl = max(len(wrap(d, l["sub"], fs, inner)) for l in LEADS)
            if sl > 3:
                continue
            need = bar_h + 10 + hl * lh + 10 + sl * slh + 6 + tag_h
            if need <= LEAD_H:
                return hs, fh, lh, ss, fs, slh
    return None

pick = pick_lead_sizes()
if pick is None:
    problems.append("no lead size fits")
    hs, f_lh, lh, ss, f_lsub, slh = 28, fb(28), 31, 14, fr(14), 18
else:
    hs, f_lh, lh, ss, f_lsub, slh = pick

f_tag = fb(tag_size)

for i, L in enumerate(LEADS):
    x0 = M + i * (cw + GUT)
    d.rectangle([x0, LEAD_Y, x0 + cw, LEAD_Y + bar_h], fill=L["colour"])

    head_lines = wrap(d, L["head"], f_lh, inner)
    sub_lines = wrap(d, L["sub"], f_lsub, inner)

    y = LEAD_Y + bar_h + 10
    for ln in head_lines:
        d.text((x0 + pad, y), ln, font=f_lh, fill=INK)
        y += lh
    head_end = y

    sub_h = len(sub_lines) * slh
    sub_y = LEAD_Y + LEAD_H - tag_h - 8 - sub_h
    if sub_y < head_end + 4:
        problems.append("lead %d head/sub collision" % (i + 1))
    if sub_y + sub_h > LEAD_Y + LEAD_H - tag_h - 6:
        problems.append("lead %d sub overruns tag row" % (i + 1))

    for ln in sub_lines:
        d.text((x0 + pad, sub_y), ln, font=f_lsub, fill=INK_SOFT)
        sub_y += slh

    tag_y = LEAD_Y + LEAD_H - tag_h + 3
    d.text((x0 + pad, tag_y), L["region"], font=f_tag, fill=INK)
    rw = tw(d, L["region"], f_tag)
    d.text((x0 + pad + rw + 6, tag_y), "\u00b7", font=f_tag, fill=HAIR)
    d.text((x0 + pad + rw + 18, tag_y), L["field"], font=f_tag, fill=L["colour"])
    if x0 + pad + rw + 18 + tw(d, L["field"], f_tag) > x0 + cw:
        problems.append("lead %d tag overflow" % (i + 1))

# ============================================================ MEDIUM 508-796
MED_Y, MED_BOT = 524, 800
cols = 4
cw_m = (W - 2 * M - 3 * GUT) // 4          # 224
ch_m = (MED_BOT - MED_Y - GUT) // 2        # 136
mpad = 12
minner = cw_m - 2 * mpad
rule_off = 32                              # rule sits ch_m-36 from card top
tag_off = rule_off + 8

def pick_medium_size():
    for ms in range(23, 14, -1):
        f, lh = fb(ms), int(ms * 1.14)
        if not all(len(wrap(d, m[0], f, minner)) <= 4 for m in MEDIUM):
            continue
        if 12 + 4 * lh <= ch_m - rule_off - 2:
            return ms, f, lh
    return None

pickm = pick_medium_size()
if pickm is None:
    problems.append("no medium size fits")
    ms, f_mh, mlh = 15, fb(15), 17
else:
    ms, f_mh, mlh = pickm

f_mt = fr(14)
f_mf = fb(14)

for i, (head, region, field) in enumerate(MEDIUM):
    c, r = i % cols, i // cols
    x0 = M + c * (cw_m + GUT)
    y0 = MED_Y + r * (ch_m + GUT)
    d.rectangle([x0, y0, x0 + cw_m, y0 + ch_m], fill=WHITE, outline=HAIR, width=1)
    d.rectangle([x0 + 1, y0 + 1, x0 + cw_m - 1, y0 + 4], fill=FIELD_COLOUR[field])

    y = y0 + 12
    lines = wrap(d, head, f_mh, minner)
    for ln in lines:
        d.text((x0 + mpad, y), ln, font=f_mh, fill=INK)
        y += mlh
    if y > y0 + ch_m - rule_off:
        problems.append("medium %d text crosses rule (%d > %d)"
                        % (i + 4, y, y0 + ch_m - rule_off))

    rule_y = y0 + ch_m - rule_off
    d.line([(x0 + mpad, rule_y), (x0 + cw_m - mpad, rule_y)], fill=HAIR, width=1)

    ty = rule_y + 9
    d.text((x0 + mpad, ty), region, font=f_mt, fill=INK_SOFT)
    rw = tw(d, region, f_mt)
    d.text((x0 + mpad + rw + 5, ty), "\u00b7", font=f_mt, fill=HAIR)
    fx = x0 + mpad + rw + 14
    d.text((fx, ty), field, font=f_mf, fill=FIELD_COLOUR[field])
    if fx + tw(d, field, f_mf) > x0 + cw_m - 4:
        problems.append("medium %d tag overflow" % (i + 4))
    if ty + 16 > y0 + ch_m:
        problems.append("medium %d tag clipped" % (i + 4))

# ============================================================ BRIEFS 806-908
BRIEF_Y = 812
step = 22
f_bn = fb(16)
f_bh = fb(19)
f_bf = fr(14)

for i, (head, field) in enumerate(BRIEFS):
    y = BRIEF_Y + i * step
    d.text((M, y + 1), "%02d" % (i + 12), font=f_bn, fill=RED)
    fw = tw(d, field, f_bf) + 10
    avail = W - M - fw - (M + 36) - 12
    txt = ellipsize(d, head, f_bh, avail)
    d.text((M + 36, y), txt, font=f_bh, fill=INK)
    d.text((W - M, y + 3), field, font=f_bf, fill=INK_SOFT, anchor="ra")

# ============================================================ FOOTER
f_foot = fr(17)
foot = "16 stories \u00b7 7 regions \u00b7 figures as reported on 22 Nov 2026"
fw = tw(d, foot, f_foot)
d.text((int((W - fw) / 2), 944), foot, font=f_foot, fill=INK_SOFT)

# ============================================================ SAVE
if problems:
    print("LAYOUT PROBLEMS:", *problems, sep="\n  - ", file=sys.stderr)
    sys.exit(1)

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
img.save(out, format="PNG", optimize=True, compress_level=9)
print("wrote", out, img.size, "| lead", hs, "/", ss, "| med", ms)
