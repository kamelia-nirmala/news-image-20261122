"""Render entry.png - 22 November 2026 world news in one image (v3.1, 22 stories).

Layout is v1 (clean): 172px day numeral, borderless leads, 4x2 medium grid,
numbered brief list in two columns (6+5) - same architecture as v3, with the
story list replaced by stories dated 21-22 Nov 2026.

Deterministic: fixed content, no randomness, no timestamps, fixed PNG params.
Python 3 + Pillow only.

Every text draw is measured against an explicit clip box, region and field
tallies are checked against the declared counts, and every headline is checked
to have been drawn word for word. Any layout problem exits non-zero.
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

# ---------------------------------------------------------------- content
LEADS = [
    dict(head="Bahrain blames Iran; two tankers hit in Hormuz",
         sub="Bahrain seeks UN action after Saturday strikes",
         region="Middle East", field="Security"),
    dict(head="COP31 collapses",
         sub="Talks in Antalya collapsed on Sunday, 22 Nov, after delegates "
             "failed to agree a final text",
         region="Europe", field="Climate"),
    dict(head="Russia strikes Zelenskyy's hometown; 2 killed",
         sub="Triple-tap hits restaurant, then rescuers; 60 wounded",
         region="Europe", field="Conflict"),
]

MEDIUM = [
    ("Sudan accuses RSF of executing captured soldiers in Blue Nile",
     "Africa", "Conflict"),
    ("Nigeria boat capsize kills 24", "Africa", "Disaster"),
    ("Drones hit Russian ship in Baltic", "Europe", "Conflict"),
    ("KEPCO data breach exposes 1.52 million in South Korea",
     "Asia-Pacific", "Cyber"),
    ("Mexico captures \u2018El Chapo Isidro\u2019", "Latin America", "Security"),
    ("Indonesia fire: 3 dead, 36 missing", "Asia-Pacific", "Disaster"),
    ("Von der Leyen condemns Russian assassination plot in Denmark",
     "Europe", "Politics"),
    ("Saudi intercepts three Houthi missiles over Riyadh",
     "Middle East", "Security"),
]

BRIEFS = [
    ("Magnitude 6.8-7.2 quake strikes Banda Sea near Timor-Leste",
     "Asia-Pacific", "Disaster"),
    ("India, China hold new border talks", "Asia-Pacific", "Security"),
    ("India 720/9, lead New Zealand 352", "Asia-Pacific", "Sport"),
    ("NATO vows to defend Poland after Russian missiles land",
     "Europe", "Security"),
    ("Mexico confirms 4 soldiers, 7 gunmen killed in Chapo Isidro raid",
     "Latin America", "Security"),
    ("Iraq power station fire kills at least four", "Middle East", "Disaster"),
    ("Verstappen wins Las Vegas GP", "North America", "Sport"),
    ("Leeds win 4-1 at Chelsea", "Europe", "Sport"),
    ("Nepal PM Balendra Shah begins India visit", "Asia-Pacific", "Diplomacy"),
    ("S. Korea education minister resigns over AI cheating",
     "Asia-Pacific", "Education"),
    ("Australia beat Wales 29-26", "Oceania", "Sport"),
]

# declared tallies: region -> stories (7 regions, 22 stories)
REGIONS = {
    "Middle East": 3, "Europe": 6, "Africa": 2, "Asia-Pacific": 7,
    "Latin America": 2, "North America": 1, "Oceania": 1,
}

FIELD_COLOUR = {
    "Diplomacy": RED, "Security": BLUE, "Climate": GREEN,
    "Health": (156, 40, 48), "Disaster": (150, 92, 22),
    "Conflict": (90, 26, 26), "Cyber": (122, 38, 88),
    "Politics": (118, 62, 30), "Economy": (26, 100, 68),
    "Sport": (104, 52, 108), "Education": (60, 74, 120),
}

# ------------------------------------------------------------- tally checks
tally = {}
for r in [l["region"] for l in LEADS] + [m[1] for m in MEDIUM] + [b[1] for b in BRIEFS]:
    tally[r] = tally.get(r, 0) + 1
if tally != REGIONS:
    problems.append("region tally %s != declared %s"
                    % (sorted(tally.items()), sorted(REGIONS.items())))
N_STORIES = 3 + len(MEDIUM) + len(BRIEFS)
if N_STORIES != 22:
    problems.append("story count %d != 22" % N_STORIES)
if sum(REGIONS.values()) != N_STORIES:
    problems.append("region sum %d != %d stories"
                    % (sum(REGIONS.values()), N_STORIES))
if len(REGIONS) != 7:
    problems.append("region count %d != 7" % len(REGIONS))
fields = sorted(set([l["field"] for l in LEADS]
                    + [m[2] for m in MEDIUM]
                    + [b[2] for b in BRIEFS]))
if len(fields) != 9:
    problems.append("field count %d != 9: %s" % (len(fields), fields))
for f in fields:
    if f not in FIELD_COLOUR:
        problems.append("no colour for field %s" % f)
N_FIELDS = len(fields)

# per-field declared counts, 22 stories / 9 fields
FIELD_STORIES = {
    "Security": 6, "Climate": 1, "Conflict": 3, "Disaster": 4, "Cyber": 1,
    "Politics": 1, "Sport": 4, "Diplomacy": 1, "Education": 1,
}
ftally = {}
for f in [l["field"] for l in LEADS] + [m[2] for m in MEDIUM] + [b[2] for b in BRIEFS]:
    ftally[f] = ftally.get(f, 0) + 1
if ftally != FIELD_STORIES:
    problems.append("field tally %s != declared %s"
                    % (sorted(ftally.items()), sorted(FIELD_STORIES.items())))
if sum(FIELD_STORIES.values()) != N_STORIES:
    problems.append("field sum %d != %d stories"
                    % (sum(FIELD_STORIES.values()), N_STORIES))

# ============================================================ DATE BAND 40-224
x = M
f_sun = fb(28)
for ch in "SUNDAY":
    d.text((x, 44), ch, font=f_sun, fill=RED)
    x += tw(ch, f_sun) + 6

f_day = fb(172)
db = d.textbbox((M, 222), "22", font=f_day, anchor="ls")
if db[3] > 226 or db[1] < 34:
    problems.append("day numeral leaves band: %s"
                    % (tuple(round(v, 1) for v in db),))
d.text((M, 222), "22", font=f_day, fill=INK, anchor="ls")
dw = tw("22", f_day)

f_my = fb(42)
mx = int(M + dw + 18)
d.text((mx, 190), "NOVEMBER", font=f_my, fill=INK, anchor="ls")
d.text((mx, 222), "2026", font=f_my, fill=INK, anchor="ls")
if mx + tw("NOVEMBER", f_my) > 652 - 12:
    problems.append("month overruns the divider")

RX = W - M
d.line([(652, 44), (652, 222)], fill=HAIR, width=2)

f_idx = fb(26)
index_rows = ["%d STORIES" % N_STORIES, "%d REGIONS" % len(REGIONS),
              "%d FIELDS" % N_FIELDS]
for i, t in enumerate(index_rows):
    put(RX, 54 + i * 34, t, f_idx, INK,
        (668, 44 + i * 34, RX, 84 + i * 34), anchor="ra", name="index%d" % (i + 1))

d.line([(RX - 178, 168), (RX, 168)], fill=HAIR, width=2)
f_dl = fr(17)
put(RX, 176, "as of 22 Nov 2026,", f_dl, INK_SOFT, (RX - 178, 170, RX, 198),
    anchor="ra", name="dateline1")
put(RX, 198, "23:59 UTC", f_dl, INK_SOFT, (RX - 178, 194, RX, 226),
    anchor="ra", name="dateline2")

# ============================================================ LEADS 230-470
LEAD_Y, LEAD_BOT = 230, 470
LEAD_H = LEAD_BOT - LEAD_Y                 # 240
bar_h = 6
cw = (W - 2 * M - 2 * GUT) // 3            # 304
pad = 8
inner = cw - 2 * pad
tag_h = 24
tag_size = 19

def pick_lead_sizes():
    for hs in range(40, 27, -1):
        fh, lh = fb(hs), int(hs * 1.12)
        if max(len(wrap(l["head"], fh, inner)) for l in LEADS) > 5:
            continue
        for ss in (17, 16, 15):
            fs, slh = fr(ss), int(ss * 1.34)
            if max(len(wrap(l["sub"], fs, inner)) for l in LEADS) > 3:
                continue
            need = max(len(wrap(l["head"], fh, inner)) * lh + 10
                       + len(wrap(l["sub"], fs, inner)) * slh for l in LEADS)
            if bar_h + 10 + need + 6 + tag_h <= LEAD_H:
                return hs, fh, lh, ss, fs, slh
    return None

pick = pick_lead_sizes()
if pick is None:
    problems.append("no lead size fits")
    hs, f_lh, lh, ss, f_lsub, slh = 28, fb(28), 31, 15, fr(15), 20
else:
    hs, f_lh, lh, ss, f_lsub, slh = pick

f_tag = fb(tag_size)

for i, L in enumerate(LEADS):
    x0 = M + i * (cw + GUT)
    col = FIELD_COLOUR[L["field"]]
    d.rectangle([x0, LEAD_Y, x0 + cw, LEAD_Y + bar_h], fill=col)

    head_lines = wrap(L["head"], f_lh, inner)
    sub_lines = wrap(L["sub"], f_lsub, inner)

    # all three headlines share one top edge, so a short headline does not
    # appear to sag; the deck follows directly under its own headline
    top = LEAD_Y + bar_h + 10
    bot = LEAD_Y + LEAD_H - tag_h - 6

    y = top
    for ln in head_lines:
        put(x0 + pad, y, ln, f_lh, INK,
            (x0 + 1, y - 4, x0 + cw - 1, y + lh + 6), name="lead%d.head" % (i + 1))
        y += lh
    head_end = y

    sub_y = head_end + 10
    sub_h = len(sub_lines) * slh
    if sub_y + sub_h > bot:
        problems.append("lead %d sub overruns tag row (%d > %d)"
                        % (i + 1, sub_y + sub_h, bot))

    for ln in sub_lines:
        put(x0 + pad, sub_y, ln, f_lsub, INK_SOFT,
            (x0 + 1, sub_y - 3, x0 + cw - 1, sub_y + slh + 1),
            name="lead%d.sub" % (i + 1))
        sub_y += slh

    tag_y = LEAD_Y + LEAD_H - tag_h + 3
    tbox = (x0 + 1, tag_y - 2, x0 + cw - 2, LEAD_Y + LEAD_H + 2)
    put(x0 + pad, tag_y, L["region"], f_tag, INK, tbox,
        name="lead%d.region" % (i + 1))
    rw = tw(L["region"], f_tag)
    put(x0 + pad + rw + 6, tag_y, "\u00b7", f_tag, HAIR, tbox,
        name="lead%d.dot" % (i + 1))
    put(x0 + pad + rw + 18, tag_y, L["field"], f_tag, col, tbox,
        name="lead%d.field" % (i + 1))

# ============================================================ MEDIUM 479-739
MED_Y = LEAD_BOT + 9                       # 479
cols = 4
cw_m = (W - 2 * M - 3 * GUT) // 4          # 224
ch_m = 122
MED_BOT = MED_Y + 2 * ch_m + GUT           # 739
mpad = 10
minner = cw_m - 2 * mpad                   # 204
rule_off = 30

def pick_medium_size():
    for ms in range(23, 14, -1):
        f, lh = fb(ms), int(ms * 1.14)
        lines = [len(wrap(m[0], f, minner)) for m in MEDIUM]
        if max(lines) > 4:
            continue
        if 12 + max(lines) * lh <= ch_m - rule_off - 2:
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
    d.rectangle([x0 + 1, y0 + 1, x0 + cw_m - 1, y0 + 4],
                fill=FIELD_COLOUR[field])

    y = y0 + 12
    for ln in wrap(head, f_mh, minner):
        put(x0 + mpad, y, ln, f_mh, INK,
            (x0 + 2, y - 4, x0 + cw_m - 2, y + mlh + 4), name="med%d.head" % (i + 4))
        y += mlh
    if y > y0 + ch_m - rule_off:
        problems.append("medium %d text crosses rule (%d > %d)"
                        % (i + 4, y, y0 + ch_m - rule_off))

    rule_y = y0 + ch_m - rule_off
    d.line([(x0 + mpad, rule_y), (x0 + cw_m - mpad, rule_y)], fill=HAIR, width=1)

    ty = rule_y + 9
    tbox = (x0 + 2, ty - 2, x0 + cw_m - 3, y0 + ch_m - 1)
    put(x0 + mpad, ty, region, f_mt, INK_SOFT, tbox, name="med%d.region" % (i + 4))
    rw = tw(region, f_mt)
    put(x0 + mpad + rw + 5, ty, "\u00b7", f_mt, HAIR, tbox, name="med%d.dot" % (i + 4))
    put(x0 + mpad + rw + 14, ty, field, f_mf, FIELD_COLOUR[field], tbox,
        name="med%d.field" % (i + 4))

# ============================================================ BRIEFS 761-932
# 11 items in 2 columns (6 + 5), numbered 12-22: bold headline, red number,
# no field label on the right (saves width for the headline).
BR_Y = MED_BOT + 22
SPLIT = 6
FOOT_TOP = 944
col_w = (W - 2 * M - 14) // 2              # 465
num_w = 30
brief_inner = col_w - num_w
BR_SPACE = FOOT_TOP - 10 - BR_Y            # 173

d.line([(M, BR_Y - 11), (W - M, BR_Y - 11)], fill=HAIR, width=2)

column_items = [BRIEFS[:SPLIT], BRIEFS[SPLIT:]]

def pick_brief_size():
    for bs in range(20, 16, -1):
        f = fb(bs)
        lh = bs + 2
        if not all(len(wrap(b[0], f, brief_inner)) <= 2 for b in BRIEFS):
            continue
        height = max(sum(len(wrap(b[0], f, brief_inner)) for b in items) * lh
                     for items in column_items)
        if height <= BR_SPACE:
            return bs, f, lh
    return None

pickb = pick_brief_size()
if pickb is None:
    problems.append("no brief size >=17px fits in two columns")
    bs, f_bh, b_lh = 17, fb(17), 19
else:
    bs, f_bh, b_lh = pickb
f_bn = fb(16)

FIRST_BRIEF_NUM = 3 + len(MEDIUM) + 1      # 12
bottom = BR_Y
n = FIRST_BRIEF_NUM
for c, items in enumerate(column_items):
    x0 = M + c * (col_w + 14)
    y = BR_Y
    for head, region, field in items:
        lines = wrap(head, f_bh, brief_inner)
        put(x0, y, "%02d" % n, f_bn, RED,
            (x0 - 1, y - 3, x0 + num_w - 5, y + b_lh), name="brief%d.num" % n)
        for li, ln in enumerate(lines):
            put(x0 + num_w, y + li * b_lh, ln, f_bh, INK,
                (x0 + num_w - 1, y + li * b_lh - 4,
                 x0 + col_w - 1, y + li * b_lh + b_lh + 1),
                name="brief%d.head" % n)
        y += len(lines) * b_lh
        n += 1
    bottom = max(bottom, y)

# ============================================================ FOOTER
f_foot = fr(17)
foot = "%d stories \u00b7 %d regions \u00b7 figures as reported on 22 Nov 2026" % (
    N_STORIES, len(REGIONS))
FW = tw(foot, f_foot)
fx = int((W - FW) / 2)
put(fx, FOOT_TOP, foot, f_foot, INK_SOFT,
    (fx - 1, FOOT_TOP - 3, fx + int(FW) + 1, FOOT_TOP + 22), name="footer")
if FOOT_TOP + 22 > H:
    problems.append("footer overruns page")
if bottom + 8 > FOOT_TOP:
    problems.append("brief block ends at %d, collides with footer" % bottom)

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
    n = i + FIRST_BRIEF_NUM
    if " ".join(wrap(b[0], f_bh, brief_inner)).strip() != b[0].strip():
        problems.append("brief %d headline not fully drawn: %s" % (n, b[0]))
    got = [t for nm, t in drawn if nm == "brief%d.head" % n]
    if not got:
        problems.append("brief %d headline missing" % n)

nums = [t for nm, t in drawn if nm.endswith(".num")]
for n in range(FIRST_BRIEF_NUM, FIRST_BRIEF_NUM + len(BRIEFS)):
    if ("%02d" % n) not in nums:
        problems.append("number %02d not drawn" % n)
if len(nums) != len(BRIEFS):
    problems.append("brief numbers %d != %d briefs" % (len(nums), len(BRIEFS)))
if [len(items) for items in column_items] != [6, 5]:
    problems.append("brief columns are not 6+5: %s"
                    % [len(items) for items in column_items])

if problems:
    print("LAYOUT PROBLEMS:", *problems, sep="\n  - ", file=sys.stderr)
    sys.exit(1)

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
img.save(out, format="PNG", optimize=True, compress_level=9)
print("wrote", out, img.size)
print("date 172 | lead %d/%d | medium %d | brief %d | index: %s"
      % (hs, ss, ms, bs, " / ".join(index_rows)))
print("brief bottom %d | footer bottom %d" % (bottom, FOOT_TOP + 22))
