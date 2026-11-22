"""Render entry.png - 22 November 2026 world news in one image (v2.1, 32 stories).

Deterministic: fixed content, no randomness, no timestamps, fixed PNG params.
Python 3 + Pillow only.

Extends the v1 pattern: every block is laid out from measured text, and every
text draw is checked against an explicit clip box. Any overflow, collision or
tally mismatch raises a layout problem and the script exits non-zero.
"""
import os
import sys
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
M = 36
GUT = 12
CW = W - 2 * M                      # 952

BG       = (247, 244, 239)
CARD     = (255, 253, 249)
INK      = (26, 26, 26)
INK_SOFT = (94, 89, 82)
HAIR     = (214, 206, 190)
WHITE    = (255, 255, 255)

RED    = (176, 45, 33)
NAVY   = (31, 58, 95)
GREEN  = (26, 100, 68)
OCHRE  = (150, 92, 22)
PLUM   = (104, 52, 108)
TEAL   = (28, 98, 112)
BRICK  = (140, 52, 38)
SLATE  = (70, 74, 82)
MAROON = (90, 26, 26)

BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REG  = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

_fc = {}


def _f(path, s):
    k = (path, s)
    if k not in _fc:
        try:
            _fc[k] = ImageFont.truetype(path, s)
        except Exception:
            _fc[k] = ImageFont.load_default()
    return _fc[k]


def fb(s):
    return _f(BOLD, s)


def fr(s):
    return _f(REG, s)


img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)
problems = []
rects = []
drawn = []


def tw(text, f):
    return d.textlength(text, font=f)


def wrap(text, f, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if not cur or tw(trial, f) <= maxw:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def put(x, y, text, f, fill, box, anchor=None, name="text"):
    """Draw text and fail if its measured bbox leaves the given clip box."""
    bb = d.textbbox((x, y), text, font=f, anchor=anchor)
    bx0, by0, bx1, by1 = box
    if bb[0] < bx0 - 0.5 or bb[1] < by0 - 0.5 or bb[2] > bx1 + 0.5 or bb[3] > by1 + 0.5:
        problems.append("%s: %r bbox=%s box=%s" % (
            name, text, tuple(round(v, 1) for v in bb), box))
    rects.append((bb, name, text))
    drawn.append((name, text))
    d.text((x, y), text, font=f, fill=fill, anchor=anchor)
    return bb


# ------------------------------------------------------------------ content
LEADS = [
    dict(head="Bahrain blames Iran; two tankers hit in Hormuz",
         sub="Bahrain seeks UN action after Saturday strikes",
         region="Middle East", field="Security"),
    dict(head="Russia strikes Zelenskyy's hometown; 2 killed",
         sub="'Triple-tap' hits restaurant, then rescuers; 60 wounded",
         region="Europe", field="Conflict"),
    dict(head="COP31 deadlocked, enters second overtime day in Antalya",
         sub="New draft draws pushback; EU warns good deal or no deal",
         region="Europe", field="Climate"),
]

# 10 medium cards: (headline, region, field)
MEDIUM = [
    ("Congo Ebola cases top 11,000", "Africa", "Health"),
    ("Nigeria boat capsize kills 24", "Africa", "Disaster"),
    ("Drones hit Russian ship in Baltic", "Europe", "Conflict"),
    ("FBI criminal database breached", "North America", "Cyber"),
    ("Mexico captures \u2018El Chapo Isidro\u2019", "Latin America", "Security"),
    ("Indonesia fire: 3 dead, 36 missing", "Asia-Pacific", "Disaster"),
    ("Gen Z protests sweep 25 nations", "Europe", "Politics"),
    ("Peru quake shakes central Andes", "Latin America", "Disaster"),
    ("BepiColombo enters Mercury orbit", "Global", "Science"),
    ("EU-Indonesia sign trade deal", "Asia-Pacific", "Economy"),
]

# 19 in-brief items, numbered 14-32: (headline, region, field)
BRIEFS = [
    ("India, China hold new border talks", "Asia-Pacific", "Security"),
    ("India 720/9, lead New Zealand 352", "Asia-Pacific", "Sport"),
    ("Estonia to close Russian border", "Europe", "Security"),
    ("US, Venezuela sign military deal", "Latin America", "Security"),
    ("Iraq power station fire kills at least four", "Middle East", "Disaster"),
    ("Amazon nears $7.5B deal for Decart", "North America", "Economy"),
    ("Bukele seeks third term", "Latin America", "Politics"),
    ("Virginia's first measles death of 2026", "North America", "Health"),
    ("Leeds win 4-1 at Chelsea", "Europe", "Sport"),
    ("Nepal PM Balendra Shah begins India visit", "Asia-Pacific", "Diplomacy"),
    ("S. Korea education minister resigns over AI cheating", "Asia-Pacific", "Education"),
    ("Verstappen wins Las Vegas GP", "North America", "Sport"),
    ("Kansas City Current win first NWSL title", "North America", "Sport"),
    ("Australia beat Wales 29-26", "Oceania", "Sport"),
    ("UN states agree draft killer-robot rules by 2028", "Europe", "Technology"),
    ("FDA clears first drugs for two rare diseases", "North America", "Health"),
    ("Endometriosis study maps 58 gene regions", "Global", "Health"),
    ("Dhurandhar sweeps Phalke film awards", "Asia-Pacific", "Culture"),
    ("Houthis strike after Saudi-led Hodeida operation", "Middle East", "Security"),
]

REGIONS = [
    ("Asia-Pacific", 7, NAVY),
    ("Europe", 7, BRICK),
    ("Middle East", 3, OCHRE),
    ("North America", 6, GREEN),
    ("Latin America", 4, PLUM),
    ("Africa", 2, (168, 84, 40)),
    ("Oceania", 1, TEAL),
    ("Global", 2, SLATE),
]

REGION_COLOUR = {name: col for name, n, col in REGIONS}

FIELD_COLOUR = {
    "Diplomacy": RED, "Security": NAVY, "Climate": GREEN, "Cyber": (122, 38, 88),
    "Disaster": OCHRE, "Economy": (26, 100, 68), "Sport": PLUM, "Technology": TEAL,
    "Education": (60, 74, 120), "Health": (156, 40, 48), "Politics": (118, 62, 30),
    "Science": (28, 98, 112), "Culture": (132, 72, 40), "Conflict": MAROON,
}

# key numbers, each one taken from the 2-source verified story files
FACTS = [
    ("11,000", "EBOLA CASES"),
    ("24", "DEAD, NIGERIA"),
    ("11", "KILLED, MEXICO"),
    ("720/9", "INDIA V NZ"),
    ("4-1", "LEEDS AT CHELSEA"),
]

# ------------------------------------------------------------- tally checks
tally = {}
for r in [l["region"] for l in LEADS] + [m[1] for m in MEDIUM] + [b[1] for b in BRIEFS]:
    tally[r] = tally.get(r, 0) + 1
declared = {name: n for name, n, _ in REGIONS}
if tally != declared:
    problems.append("region tally %s != declared %s"
                    % (sorted(tally.items()), sorted(declared.items())))
if sum(declared.values()) != 32:
    problems.append("region bar does not sum to 32")
if 3 + len(MEDIUM) + len(BRIEFS) != 32:
    problems.append("story count is not 32")
fields = set([l["field"] for l in LEADS] + [m[2] for m in MEDIUM] + [b[2] for b in BRIEFS])
if len(fields) != 14:
    problems.append("field count %d != 14: %s" % (len(fields), sorted(fields)))
for f in fields:
    if f not in FIELD_COLOUR:
        problems.append("no colour for field %s" % f)
for name in tally:
    if name not in REGION_COLOUR:
        problems.append("region %r has no bar colour" % name)

# ============================================================ TOP BAR 0-28
d.rectangle([0, 0, W, 28], fill=(32, 30, 28))
put(M, 7, "SUNDAY \u00b7 22 NOV 2026", fb(13), (238, 232, 220),
    (M, 3, 380, 27), name="topbar.date")
put(W - M, 5, "32 STORIES \u00b7 8 REGIONS \u00b7 14 FIELDS", fb(15), WHITE,
    (W - M - 400, 1, W - M, 28), anchor="ra", name="topbar.index")
d.rectangle([0, 28, W, 31], fill=RED)

# ============================================================ DATE
date_size = 0
for s in range(96, 56, -1):
    if tw("22 NOVEMBER 2026", fb(s)) <= CW:
        date_size = s
        break
if not date_size:
    problems.append("date does not fit")
    date_size = 56
f_date = fb(date_size)
db = put(M, 32, "22 NOVEMBER 2026", f_date, INK,
         (M, 30, M + CW, 140), name="date")
DATE_BOT = int(db[3])

d.rectangle([M, DATE_BOT + 4, M + CW, DATE_BOT + 7], fill=INK)
KY = DATE_BOT + 11
put(M, KY, "THE WORLD IN ONE PAGE \u00b7 3 LEADS \u00b7 10 MEDIUM \u00b7 19 IN BRIEF",
    fb(13), INK_SOFT, (M, KY - 1, M + 600, KY + 18), name="kicker")
put(M + CW, KY, "ALL 32 VERIFIED", fb(13), RED,
    (M + CW - 220, KY - 1, M + CW, KY + 18), anchor="ra", name="kicker.right")

# ============================================================ REGION BAR
RB_Y = KY + 23
RB_H = 38
seg_w = CW / 8.0
for i, (name, n, col) in enumerate(REGIONS):
    x0 = int(round(M + i * seg_w))
    x1 = int(round(M + (i + 1) * seg_w)) - 2
    d.rectangle([x0, RB_Y, x1, RB_Y + RB_H], fill=col)
    put(x0 + 7, RB_Y + 3, str(n), fb(20), WHITE,
        (x0, RB_Y + 1, x1, RB_Y + 25), name="region.n")
    put(x0 + 6, RB_Y + 24, name.upper(), fb(11), WHITE,
        (x0 + 1, RB_Y + 22, x1 - 1, RB_Y + RB_H), name="region.label")

# ============================================================ FACT STRIP
FS_Y = RB_Y + RB_H + 6
FS_H = 46
d.rectangle([M, FS_Y, M + CW, FS_Y + FS_H], fill=WHITE, outline=HAIR, width=1)
cell = CW / len(FACTS)
for i, (num, label) in enumerate(FACTS):
    x0 = M + i * cell
    if i:
        d.line([(x0, FS_Y + 6), (x0, FS_Y + FS_H - 6)], fill=HAIR, width=1)
    put(int(x0 + 10), FS_Y + 3, num, fb(24), INK,
        (int(x0) + 2, FS_Y + 1, int(x0 + cell) - 3, FS_Y + 31), name="fact.num")
    put(int(x0 + 11), FS_Y + 31, label, fb(11), INK_SOFT,
        (int(x0) + 2, FS_Y + 30, int(x0 + cell) - 4, FS_Y + FS_H - 1),
        name="fact.label")

# ============================================================ LEADS
LEAD_Y = FS_Y + FS_H + 8
LEAD_H = 220
LEAD_BOT = LEAD_Y + LEAD_H
bar_h = 6
cw = (CW - 2 * GUT) // 3
pad = 9
inner = cw - 2 * pad
tag_h = 17


def pick_lead():
    for hs in range(32, 17, -1):
        fh, lh = fb(hs), int(round(hs * 1.20))
        heads = [wrap(l["head"], fh, inner) for l in LEADS]
        if max(len(h) for h in heads) > 4:
            continue
        for ss in (15, 14, 13):
            fs, slh = fr(ss), int(round(ss * 1.42))
            subs = [wrap(l["sub"], fs, inner) for l in LEADS]
            if max(len(s) for s in subs) > 2:
                continue
            need = bar_h + 9 + 4 * lh + 8 + 2 * slh + 6 + tag_h + 8
            if need <= LEAD_H:
                return hs, fh, lh, ss, fs, slh, max(len(h) for h in heads)
    return None


pick = pick_lead()
if pick is None:
    problems.append("no lead size fits")
    hs, f_lh, lh, ss, f_lsub, slh, hmax = 24, fb(24), 29, 13, fr(13), 18, 4
else:
    hs, f_lh, lh, ss, f_lsub, slh, hmax = pick

f_tag = fb(11)

for i, L in enumerate(LEADS):
    x0 = M + i * (cw + GUT)
    d.rectangle([x0, LEAD_Y, x0 + cw, LEAD_BOT], fill=CARD, outline=HAIR, width=1)
    d.rectangle([x0 + 1, LEAD_Y + 1, x0 + cw - 1, LEAD_Y + bar_h],
                fill=REGION_COLOUR[L["region"]])

    y = LEAD_Y + bar_h + 9
    for ln in wrap(L["head"], f_lh, inner):
        put(x0 + pad, y, ln, f_lh, INK, (x0 + 1, y, x0 + cw - 1, y + lh),
            name="lead%d.head" % (i + 1))
        y += lh
    head_end = y

    sub_lines = wrap(L["sub"], f_lsub, inner)
    # decks share one baseline across the three cards, so the row reads as a grid
    sub_y = LEAD_Y + bar_h + 9 + hmax * lh + 8
    if sub_y < head_end + 1:
        problems.append("lead %d head/sub collision (%d < %d)"
                        % (i + 1, sub_y, head_end + 1))
    if sub_y + len(sub_lines) * slh > LEAD_BOT - 8 - tag_h - 2:
        problems.append("lead %d deck overruns tag row" % (i + 1))
    for ln in sub_lines:
        put(x0 + pad, sub_y, ln, f_lsub, INK_SOFT,
            (x0 + 1, sub_y, x0 + cw - 1, sub_y + slh),
            name="lead%d.sub" % (i + 1))
        sub_y += slh

    tag_y = LEAD_BOT - 8 - tag_h + 2
    tbox = (x0 + 1, tag_y, x0 + cw - 2, LEAD_BOT - 2)
    put(x0 + pad, tag_y, L["region"], f_tag, INK, tbox, name="lead%d.region" % (i + 1))
    rw = tw(L["region"], f_tag)
    put(x0 + pad + rw + 4, tag_y, "\u00b7", f_tag, HAIR, tbox, name="lead%d.dot" % (i + 1))
    put(x0 + pad + rw + 12, tag_y, L["field"].upper(), f_tag,
        FIELD_COLOUR[L["field"]], tbox,
        name="lead%d.field" % (i + 1))

# ============================================================ MEDIUM 2x5
MED_Y = LEAD_BOT + 8
MED_COLS = 5
cw_m = (CW - (MED_COLS - 1) * GUT) // MED_COLS
ch_m = 114
MED_BOT = MED_Y + 2 * ch_m + 8
mpad = 10
minner = cw_m - 2 * mpad
rule_off = 24


def pick_medium():
    for ms in range(21, 10, -1):
        f, lh = fb(ms), int(round(ms * 1.22))
        if all(len(wrap(m[0], f, minner)) <= 3 for m in MEDIUM):
            if 10 + 3 * lh <= ch_m - rule_off - 2:
                return ms, f, lh
    return None


pickm = pick_medium()
if pickm is None:
    problems.append("no medium size fits")
    ms, f_mh, mlh = 14, fb(14), 17
else:
    ms, f_mh, mlh = pickm

f_mt = fr(10)
f_mf = fb(10)

for i, (head, region, field) in enumerate(MEDIUM):
    c, r = i % MED_COLS, i // MED_COLS
    x0 = M + c * (cw_m + GUT)
    y0 = MED_Y + r * (ch_m + 8)
    d.rectangle([x0, y0, x0 + cw_m, y0 + ch_m], fill=CARD, outline=HAIR, width=1)
    d.rectangle([x0 + 1, y0 + 1, x0 + cw_m - 1, y0 + 5], fill=REGION_COLOUR[region])

    y = y0 + 10
    for ln in wrap(head, f_mh, minner):
        put(x0 + mpad, y, ln, f_mh, INK, (x0 + 1, y, x0 + cw_m - 1, y + mlh),
            name="med%d.head" % (i + 4))
        y += mlh
    if y > y0 + ch_m - rule_off:
        problems.append("medium %d text crosses rule (%d > %d)"
                        % (i + 4, y, y0 + ch_m - rule_off))

    rule_y = y0 + ch_m - rule_off
    d.line([(x0 + mpad, rule_y), (x0 + cw_m - mpad, rule_y)], fill=HAIR, width=1)

    ty = rule_y + 5
    tbox = (x0 + 1, ty, x0 + cw_m - 2, y0 + ch_m - 1)
    put(x0 + mpad, ty, region, f_mt, INK_SOFT, tbox, name="med%d.region" % (i + 4))
    rw = tw(region, f_mt)
    put(x0 + mpad + rw + 4, ty, "\u00b7", f_mt, HAIR, tbox, name="med%d.dot" % (i + 4))
    put(x0 + mpad + rw + 10, ty, field.upper(), f_mf, FIELD_COLOUR[field], tbox,
        name="med%d.field" % (i + 4))

# ============================================================ BRIEFS 2 cols
BR_Y = MED_BOT + 10
BR_STEP = 25
BR_COLS = 2
col_w = (CW - 20) // 2
rows = (len(BRIEFS) + BR_COLS - 1) // BR_COLS
BR_BOT = BR_Y + rows * BR_STEP
num_w = 24
swatch = 6


def pick_brief():
    for bs in range(15, 9, -1):
        if all(tw(b[0], fb(bs)) <= col_w - num_w - swatch - 8 for b in BRIEFS):
            return bs, fb(bs)
    return None


pickb = pick_brief()
if pickb is None:
    problems.append("no brief size fits")
    bs, f_bh = 10, fb(10)
else:
    bs, f_bh = pickb
f_bn = fb(12)

d.line([(M, BR_Y - 5), (M + CW, BR_Y - 5)], fill=HAIR, width=1)

for i, (head, region, field) in enumerate(BRIEFS):
    c, r = i // rows, i % rows
    x0 = M + c * (col_w + 20)
    y = BR_Y + r * BR_STEP
    n = i + 14
    put(x0, y, "%02d" % n, f_bn, RED, (x0, y - 1, x0 + num_w - 2, y + BR_STEP),
        name="brief%d.num" % n)
    d.rectangle([x0 + num_w, y + 6, x0 + num_w + swatch - 2, y + 6 + swatch - 2],
                fill=REGION_COLOUR[region])
    put(x0 + num_w + swatch + 2, y, head, f_bh, INK,
        (x0 + num_w + swatch, y - 1, x0 + col_w - 1, y + BR_STEP),
        name="brief%d.head" % n)

# ============================================================ FOOTER
d.line([(M, BR_BOT + 8), (M + CW, BR_BOT + 8)], fill=HAIR, width=1)
FY = BR_BOT + 14
foot = "32 stories \u00b7 8 regions \u00b7 figures as reported on 22 Nov 2026"
put(M, FY, foot, fr(13), INK_SOFT, (M, FY - 1, M + 560, FY + 16), name="footer.left")
put(M + CW, FY, "SUNDAY 22 NOVEMBER 2026", fb(12), RED,
    (M + CW - 280, FY - 1, M + CW, FY + 16), anchor="ra", name="footer.right")
if FY + 16 > H - 8:
    problems.append("footer overruns page")

# ------------------------------------------------------- global overlap check
for i in range(len(rects)):
    a, an, at = rects[i]
    for j in range(i + 1, len(rects)):
        b, bn, bt = rects[j]
        ox = min(a[2], b[2]) - max(a[0], b[0])
        oy = min(a[3], b[3]) - max(a[1], b[1])
        if ox > 0.6 and oy > 0.6:
            problems.append("text overlap: %r [%s] / %r [%s]" % (at, an, bt, bn))

# every headline must have been drawn in full, word for word
for i, l in enumerate(LEADS):
    if " ".join(wrap(l["head"], f_lh, inner)).strip() != l["head"].strip():
        problems.append("lead %d headline not fully drawn: %s" % (i + 1, l["head"]))
for i, m in enumerate(MEDIUM):
    if " ".join(wrap(m[0], f_mh, minner)).strip() != m[0].strip():
        problems.append("medium %d headline not fully drawn: %s" % (i + 4, m[0]))
for i, b in enumerate(BRIEFS):
    n = i + 14
    got = [t for nm, t in drawn if nm == "brief%d.head" % n]
    if not got or got[0] != b[0]:
        problems.append("brief %d headline mismatch" % n)
for n in range(4, 14):
    if not any(nm.startswith("med%d." % n) for nm, _ in drawn):
        problems.append("medium %d missing" % n)
for n in range(14, 33):
    if not any(nm.startswith("brief%d." % n) for nm, _ in drawn):
        problems.append("brief %d missing" % n)
drawn_nums = set(t for nm, t in drawn if nm.endswith(".num"))
for n in range(14, 33):
    if ("%02d" % n) not in drawn_nums:
        problems.append("number %02d not drawn" % n)

if problems:
    print("LAYOUT PROBLEMS:", *problems, sep="\n  - ", file=sys.stderr)
    sys.exit(1)

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
img.save(out, format="PNG", optimize=True, compress_level=9)
print("wrote", out, img.size, "| date", date_size, "| lead", hs, "/", ss,
      "| med", ms, "| brief", bs, "| bottom", FY + 16)
