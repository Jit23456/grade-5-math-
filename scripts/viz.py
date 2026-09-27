# -*- coding: utf-8 -*-
"""Small inline-SVG diagram generators for the seed content.

Every function returns a complete <svg>...</svg> string sized with explicit
width/height (so it has an intrinsic aspect ratio) and styled with the site's
own colour tokens. These are pasted as-is into the `visual` column and
rendered with Jinja's |safe filter inside a white card (.heroviz / .qviz),
so every colour here is chosen to read on a light surface.
"""
import math

INK = "#12303a"
BLUE = "#1b6fd4"
AMBER = "#c9750d"
GREEN = "#1f9d6c"
RED = "#b4302b"
PURPLE = "#7a4fc9"
GRAY = "#cfdbdf"
MUTE = "#4a6773"
PAPER = "#eef3f4"


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def svg(w, h, body):
    return ('<svg viewBox="0 0 %d %d" width="%d" height="%d" '
            'xmlns="http://www.w3.org/2000/svg" '
            'style="font-family:Arial,Helvetica,sans-serif">%s</svg>') % (w, h, w, h, body)


def text(x, y, s, size=13, color=INK, anchor="middle", weight="400"):
    return ('<text x="%.1f" y="%.1f" font-size="%s" fill="%s" text-anchor="%s" '
            'style="font-weight:%s">%s</text>') % (x, y, size, color, anchor, weight, esc(s))


def fmt_int(n):
    neg = n < 0
    n = abs(int(n))
    s = str(n)
    groups = []
    while len(s) > 3:
        groups.insert(0, s[-3:])
        s = s[:-3]
    groups.insert(0, s)
    return ("-" if neg else "") + " ".join(groups)


def fmt_dec(x, places=2):
    neg = x < 0
    x = abs(x)
    s = ("%." + str(places) + "f") % x
    intpart, frac = s.split(".")
    return ("-" if neg else "") + fmt_int(int(intpart)) + "." + frac


ONES = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
        "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen",
        "eighteen", "nineteen"]
TENS = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]


def three_digit_words(n):
    words = []
    h, rem = divmod(n, 100)
    if h:
        words.append(ONES[h] + " hundred")
    if rem:
        if rem < 20:
            words.append(ONES[rem])
        else:
            t, o = divmod(rem, 10)
            words.append(TENS[t] + ("-" + ONES[o] if o else ""))
    return " ".join(words)


def num_to_words(n):
    if n == 0:
        return "zero"
    thousands, rem = divmod(n, 1000)
    parts = []
    if thousands:
        parts.append(three_digit_words(thousands) + " thousand")
    if rem:
        parts.append(three_digit_words(rem))
    return " ".join(parts)


def expanded_form(n):
    s = str(n)
    places = len(s)
    parts = []
    for i, ch in enumerate(s):
        d = int(ch)
        if d:
            parts.append(fmt_int(d * 10 ** (places - i - 1)))
    return " + ".join(parts) if parts else "0"


# ---------------------------------------------------------------- number line
def number_line(lo, hi, step, points=(), arcs=(), below=(), w=460, h=120, tick_every=1):
    x0, x1, y = 34, w - 34, 58
    span = hi - lo
    if below:
        h = max(h, 130)

    def X(v):
        return x0 + (v - lo) / span * (x1 - x0)

    body = ['<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="%s" stroke-width="2"/>'
            % (x0, y, x1, y, INK)]
    n = round(span / step)
    for i in range(n + 1):
        v = lo + i * step
        xx = X(v)
        body.append('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="%s" stroke-width="2"/>'
                     % (xx, y - 7, xx, y + 7, INK))
        if i % tick_every == 0:
            lbl = fmt_dec(v, 2).rstrip("0").rstrip(".") if isinstance(v, float) else fmt_int(v)
            if isinstance(v, float) and "." not in lbl:
                lbl = fmt_int(int(v))
            body.append(text(xx, y + 24, lbl, size=11, color=MUTE))
    for i, (v1, v2, color, label) in enumerate(arcs):
        xa, xb = X(v1), X(v2)
        mid = (xa + xb) / 2
        top = y - 34 - 12 * (i % 2)
        body.append('<path d="M%.1f %d Q %.1f %d %.1f %d" fill="none" stroke="%s" '
                     'stroke-width="2.5" marker-end="url(#arrow-%s)"/>'
                     % (xa, y - 2, mid, top, xb, y - 2, color, color.strip("#")))
        if label:
            body.append(text(mid, top - 6, label, size=11.5, color=color, weight="700"))
    placed = []          # label x positions already used, with their row
    for v, color, label in sorted(points, key=lambda p: p[0]):
        xx = X(v)
        body.append('<circle cx="%.1f" cy="%d" r="7" fill="%s" stroke="#fff" stroke-width="2"/>'
                     % (xx, y, color))
        if label:
            # step a crowded label up a row so two nearby labels never overlap
            row = 0
            while any(abs(px - xx) < 8 * len(label) and prow == row for px, prow in placed):
                row += 1
            placed.append((xx, row))
            tx = min(max(xx, 4 * len(label)), w - 4 * len(label))
            body.append(text(tx, y - 16 - row * 15, label, size=12, color=color, weight="700"))
    for v, color, label in below:
        xx = X(v)
        body.append('<polygon points="%.1f,%d %.1f,%d %.1f,%d" fill="%s"/>'
                     % (xx, y + 34, xx - 6, y + 44, xx + 6, y + 44, color))
        if label:
            tx = min(max(xx, 4 * len(label)), w - 4 * len(label))
            body.append(text(tx, y + 58, label, size=11.5, color=color, weight="700"))
    defs = "".join(
        '<marker id="arrow-%s" markerWidth="8" markerHeight="8" refX="6" refY="3" '
        'orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="%s"/></marker>' % (c.strip("#"), c)
        for c in {a[2] for a in arcs})
    return svg(w, h, "<defs>%s</defs>" % defs + "".join(body))


# ------------------------------------------------------------- place value
def place_value_grid(number, digits=6, highlight=None, decimals=0, blank=False):
    """`blank` draws the empty frame — place labels only, no digits — so the
    grid scaffolds a question without handing over its answer."""
    if decimals:
        whole = int(number)
        s = str(whole).zfill(digits - decimals) + ("%.*f" % (decimals, number - whole))[1:]
        s = s.replace(".", "")
        labels_all = ["Hundred\nThousands", "Ten\nThousands", "Thousands", "Hundreds",
                      "Tens", "Ones", "Tenths", "Hundredths", "Thousandths"]
        labels = labels_all[6 - (digits - decimals):6] + labels_all[6:6 + decimals]
    else:
        s = str(int(number)).zfill(digits)
        labels_all = ["Hundred\nThousands", "Ten\nThousands", "Thousands", "Hundreds",
                      "Tens", "Ones"]
        labels = labels_all[6 - digits:]
    n = len(s)
    box = 58
    gap = 5
    w = n * box + (n - 1) * gap + 20
    h = 118
    body = []
    x = 10
    for i, ch in enumerate(s):
        hi = highlight is not None and i == highlight
        fill = AMBER if hi else "#fff"
        stroke = AMBER if hi else GRAY
        body.append('<rect x="%d" y="14" width="%d" height="%d" rx="7" fill="%s" '
                     'stroke="%s" stroke-width="%s"/>' % (x, box, box, fill, stroke,
                                                           "3" if hi else "1.5"))
        body.append(text(x + box / 2, 14 + box / 2 + 8, "" if blank else ch, size=26,
                          color="#fff" if hi else INK, weight="800"))
        lbl = labels[i] if i < len(labels) else ""
        for j, line in enumerate(lbl.split("\n")):
            body.append(text(x + box / 2, 14 + box + 16 + j * 12, line, size=9.5,
                              color=AMBER if hi else MUTE, weight="600" if hi else "400"))
        if decimals and i == n - decimals - 1:
            x2 = x + box + gap / 2
            body.append(text(x2, 14 + box / 2 + 10, ".", size=26, color=INK, weight="800"))
        x += box + gap
    return svg(w, h, "".join(body))


# ------------------------------------------------------------------- grids
def hundred_grid(shaded, rows=10, cols=10, color=AMBER, cell=15):
    w = cols * cell + 20
    h = rows * cell + 20
    body = []
    i = 0
    for r in range(rows):
        for c in range(cols):
            x, y = 10 + c * cell, 10 + r * cell
            fill = color if i < shaded else "#fff"
            body.append('<rect x="%d" y="%d" width="%d" height="%d" fill="%s" '
                         'stroke="%s" stroke-width="1"/>' % (x, y, cell, cell, fill, GRAY))
            i += 1
    body.append('<rect x="10" y="10" width="%d" height="%d" fill="none" stroke="%s" '
                 'stroke-width="2.5"/>' % (cols * cell, rows * cell, INK))
    return svg(w, h, "".join(body))


def fraction_bar(numerator, denominator, w=300, h=54, color=AMBER, y=10):
    seg = (w - 20) / denominator
    body = []
    for i in range(denominator):
        x = 10 + i * seg
        fill = color if i < numerator else "#fff"
        body.append('<rect x="%.1f" y="%d" width="%.1f" height="34" fill="%s" '
                     'stroke="%s" stroke-width="1.5"/>' % (x, y, seg, fill, INK))
    return "".join(body)


def fraction_bar_pair(n1, d1, n2, d2, w=320, hide_second=False):
    """`hide_second` labels the lower bar '?' instead of naming it, for
    questions whose answer is that very fraction."""
    b1 = fraction_bar(n1, d1, w=w, y=14)
    b2 = fraction_bar(n2, d2, w=w, y=76)
    lbl1 = text(w / 2, 62, "%d/%d" % (n1, d1), size=13, color=MUTE, weight="600")
    second = "?" if hide_second else "%d/%d" % (n2, d2)
    lbl2 = text(w / 2, 124, second, size=13, color=AMBER if hide_second else MUTE, weight="700")
    return svg(w, 136, b1 + lbl1 + b2 + lbl2)


def single_fraction_svg(n, d, w=320, h=70):
    return svg(w, h, fraction_bar(n, d, w=w, y=14))


# ------------------------------------------------------------------ area
def area_grid(rows, cols, w_max=300, unit=""):
    cell = min(26, (w_max - 60) / max(cols, 1))
    gx, gy = 46, 34
    w = gx + cols * cell + 20
    h = gy + rows * cell + 40
    body = []
    for r in range(rows):
        for c in range(cols):
            x, y = gx + c * cell, gy + r * cell
            body.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" '
                         'stroke="%s" stroke-width="1"/>' % (x, y, cell, cell, "#eaf2fb", BLUE))
    body.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="none" '
                 'stroke="%s" stroke-width="2.5"/>' % (gx, gy, cols * cell, rows * cell, INK))
    body.append(text(gx + cols * cell / 2, gy - 12, "%d %s" % (cols, unit), size=12,
                      color=MUTE, weight="600"))
    body.append('<text x="%d" y="%.1f" font-size="12" fill="%s" text-anchor="middle" '
                 'transform="rotate(-90 %d %.1f)" style="font-weight:600">%d %s</text>'
                 % (gx - 24, gy + rows * cell / 2, MUTE, gx - 24, gy + rows * cell / 2, rows, unit))
    return svg(w, h, "".join(body))


# ------------------------------------------------------------------ clock
def clock_face(hour, minute, w=170, h=170):
    cx, cy, r = w / 2, h / 2, 68
    body = ['<circle cx="%.1f" cy="%.1f" r="%.1f" fill="#fff" stroke="%s" stroke-width="3"/>'
            % (cx, cy, r, INK)]
    for i in range(12):
        a = math.radians(i * 30 - 90)
        x1, y1 = cx + (r - 8) * math.cos(a), cy + (r - 8) * math.sin(a)
        x2, y2 = cx + (r - 2) * math.cos(a), cy + (r - 2) * math.sin(a)
        body.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="2"/>'
                     % (x1, y1, x2, y2, MUTE))
        if i % 3 == 0:
            lx, ly = cx + (r - 20) * math.cos(a), cy + (r - 20) * math.sin(a)
            num = i if i != 0 else 12
            body.append(text(lx, ly + 5, str(num), size=13, color=INK, weight="700"))
    ha = math.radians((hour % 12 + minute / 60) * 30 - 90)
    ma = math.radians(minute * 6 - 90)
    body.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="4" '
                 'stroke-linecap="round"/>' % (cx, cy, cx + r * 0.5 * math.cos(ha),
                                               cy + r * 0.5 * math.sin(ha), INK))
    body.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="2.5" '
                 'stroke-linecap="round"/>' % (cx, cy, cx + r * 0.78 * math.cos(ma),
                                               cy + r * 0.78 * math.sin(ma), AMBER))
    body.append('<circle cx="%.1f" cy="%.1f" r="4" fill="%s"/>' % (cx, cy, INK))
    return svg(w, h, "".join(body))


# ----------------------------------------------------------------- arrays
def array_grid(rows, cols, w_max=260, color=BLUE):
    cell = min(24, (w_max - 20) / max(cols, 1))
    w = cols * cell + 20
    h = rows * cell + 20
    body = []
    for r in range(rows):
        for c in range(cols):
            cx = 10 + c * cell + cell / 2
            cy = 10 + r * cell + cell / 2
            body.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s"/>'
                         % (cx, cy, cell * 0.32, color))
    return svg(w, h, "".join(body))


# --------------------------------------------------------------- patterns
SHAPE_DRAW = {
    "square": lambda x, y, s, c: '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" rx="3"/>' % (x, y, s, s, c),
    "circle": lambda x, y, s, c: '<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s"/>' % (x + s / 2, y + s / 2, s / 2, c),
    "triangle": lambda x, y, s, c: '<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>' % (x + s / 2, y, x, y + s, x + s, y + s, c),
}


def pattern_row(counts, shape="square", color=BLUE, w=460, unknown_index=None, cap=20):
    """`counts` are the true term values: they are what the labels print.
    Only the drawing is capped at `cap` icons, so a large term stays legible
    without the label ever disagreeing with the question."""
    h = 140
    cell = 15
    slot_w = w / len(counts)
    body = []
    for i, value in enumerate(counts):
        n = min(value, cap)
        cx0 = i * slot_w
        cols = min(n, 5)
        rows = math.ceil(n / 5) if n else 1
        gx = cx0 + (slot_w - cols * cell) / 2
        gy = 70 - rows * cell
        if unknown_index == i:
            body.append('<rect x="%.1f" y="14" width="%.1f" height="70" rx="8" fill="#fff" '
                         'stroke="%s" stroke-width="2" stroke-dasharray="5,4"/>'
                         % (cx0 + 8, slot_w - 16, AMBER))
            body.append(text(cx0 + slot_w / 2, 56, "?", size=30, color=AMBER, weight="800"))
        else:
            for k in range(n):
                r, c = divmod(k, 5)
                body.append(SHAPE_DRAW[shape](gx + c * cell, gy + r * cell, cell - 3, color))
            if value > cap:
                body.append(text(cx0 + slot_w / 2, 88, "...", size=13, color=MUTE, weight="700"))
        body.append(text(cx0 + slot_w / 2, 110, "Term %d" % (i + 1), size=11, color=MUTE))
        body.append(text(cx0 + slot_w / 2, 128, str(value) if unknown_index != i else "?", size=14,
                          color=INK, weight="700"))
    return svg(w, h, "".join(body))


# --------------------------------------------------------------- balance
def balance_scale(left_text, right_text, w=300, h=170):
    cx, beam_y = w / 2, 70
    body = [
        '<line x1="%.1f" y1="30" x2="%.1f" y2="%d" stroke="%s" stroke-width="3"/>' % (cx, cx, h - 20, MUTE),
        '<polygon points="%.1f,%d %.1f,%d %.1f,%d" fill="%s"/>' % (cx - 22, h - 20, cx + 22, h - 20, cx, h - 46, INK),
        '<line x1="40" y1="%d" x2="%.1f" y2="%d" stroke="%s" stroke-width="4" stroke-linecap="round"/>' % (beam_y, w - 40, beam_y, INK),
    ]
    for side_x, val in ((70, left_text), (w - 70, right_text)):
        body.append('<line x1="%.1f" y1="%d" x2="%.1f" y2="118" stroke="%s" stroke-width="2"/>' % (side_x - 34, beam_y, side_x - 34, MUTE))
        body.append('<line x1="%.1f" y1="%d" x2="%.1f" y2="118" stroke="%s" stroke-width="2"/>' % (side_x + 34, beam_y, side_x + 34, MUTE))
        body.append('<path d="M%.1f 118 L%.1f 140 Q%.1f 148 %.1f 140 L%.1f 118 Z" fill="#eaf2fb" stroke="%s" stroke-width="2"/>'
                     % (side_x - 38, side_x - 30, side_x, side_x + 30, side_x + 38, BLUE))
        body.append(text(side_x, 133, val, size=16, color=INK, weight="700"))
    return svg(w, h, "".join(body))


# --------------------------------------------------------------- bar chart
def double_bar_chart(labels, series_a, series_b, name_a="A", name_b="B", w=380, unit=""):
    n = len(labels)
    h = 210
    gx, gy, gh = 40, 20, 140
    raw = max(max(series_a), max(series_b), 1)
    step = math.ceil(raw / 4)                      # a round scale, so values can be read off
    for cand in (1, 2, 5, 10, 20, 25, 50, 100):
        if cand >= step:
            step = cand
            break
    maxv = step * 4
    slot = (w - gx - 20) / n
    body = []
    for i in range(1, 5):
        yy = gy + gh - gh * i / 4
        body.append('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="%s" stroke-width="1"/>'
                     % (gx, yy, w - 20, yy, GRAY))
        body.append(text(gx - 8, yy + 4, str(step * i), size=9.5, color=MUTE, anchor="end"))
    body.append('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="%s" stroke-width="2"/>'
                 % (gx, gy + gh, w - 20, gy + gh, INK))
    bw = slot * 0.32
    for i, lbl in enumerate(labels):
        x0 = gx + i * slot + slot / 2
        ha = series_a[i] / maxv * gh
        hb = series_b[i] / maxv * gh
        body.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="2" fill="%s"/>'
                     % (x0 - bw - 2, gy + gh - ha, bw, ha, BLUE))
        body.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="2" fill="%s"/>'
                     % (x0 + 2, gy + gh - hb, bw, hb, AMBER))
        body.append(text(x0, gy + gh + 16, lbl, size=10.5, color=INK))
    body.append('<rect x="%d" y="0" width="10" height="10" fill="%s"/>' % (gx, BLUE))
    body.append(text(gx + 16, 9, name_a, size=11, color=MUTE, anchor="start"))
    body.append('<rect x="%d" y="0" width="10" height="10" fill="%s"/>' % (gx + 16 + len(name_a) * 6 + 14, AMBER))
    body.append(text(gx + 16 + len(name_a) * 6 + 30, 9, name_b, size=11, color=MUTE, anchor="start"))
    return svg(w, h, "".join(body))


# --------------------------------------------------------------- spinner
def spinner(sectors, w=200, h=200):
    cx, cy, r = w / 2, h / 2, 78
    body = []
    total = sum(s[1] for s in sectors)
    a0 = -90
    for label, weight, color in sectors:
        a1 = a0 + weight / total * 360
        x0 = cx + r * math.cos(math.radians(a0))
        y0 = cy + r * math.sin(math.radians(a0))
        x1 = cx + r * math.cos(math.radians(a1))
        y1 = cy + r * math.sin(math.radians(a1))
        large = 1 if (a1 - a0) > 180 else 0
        body.append('<path d="M%.1f %.1f L%.1f %.1f A%.1f %.1f 0 %d 1 %.1f %.1f Z" '
                     'fill="%s" stroke="#fff" stroke-width="2"/>'
                     % (cx, cy, x0, y0, r, r, large, x1, y1, color))
        mid = math.radians((a0 + a1) / 2)
        lx, ly = cx + r * 0.62 * math.cos(mid), cy + r * 0.62 * math.sin(mid)
        body.append(text(lx, ly, label, size=12, color="#fff", weight="700"))
        a0 = a1
    body.append('<circle cx="%.1f" cy="%.1f" r="4" fill="%s"/>' % (cx, cy, INK))
    body.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s" stroke="#fff" stroke-width="1.5"/>'
                 % (cx - 4, cy - r - 4, cx + 4, cy - r - 4, cx, cy - r + 12, INK))
    return svg(w, h, "".join(body))


# ----------------------------------------------------------------- money
BILLS = [100, 50, 20, 10, 5]
COINS = [2, 1, 0.25, 0.10, 0.05]


def money_breakdown(amount):
    """Greedy Canadian breakdown of `amount` into bills and coins, so a money
    diagram always shows the sum the question actually names."""
    cents = int(round(amount * 100))
    bills, coins = [], []
    for b in BILLS:
        while cents >= b * 100:
            bills.append(b)
            cents -= b * 100
    for c in COINS:
        cc = int(round(c * 100))
        while cents >= cc:
            coins.append(c)
            cents -= cc
    return bills, coins


def money_row(amount, w=380):
    return coin_bill_row(*money_breakdown(amount), w=w)


def coin_bill_row(bills, coins, w=380):
    h = 100
    body = []
    x = 14
    for val in bills:
        body.append('<rect x="%.1f" y="20" width="64" height="38" rx="5" fill="#e4f3ed" '
                     'stroke="%s" stroke-width="2"/>' % (x, GREEN))
        body.append(text(x + 32, 44, "$%d" % val, size=14, color=GREEN, weight="800"))
        x += 74
    for val in coins:
        label = "$%s" % fmt_dec(val, 2) if val >= 1 else "%d¢" % round(val * 100)
        body.append('<circle cx="%.1f" cy="39" r="21" fill="#fdf3dd" stroke="%s" stroke-width="2"/>'
                     % (x + 21, AMBER))
        body.append(text(x + 21, 43, label, size=10.5, color="#6b4c07", weight="700"))
        x += 52
    return svg(max(w, x + 10), h, "".join(body))


# ------------------------------------------------------------------ shapes
def prism_pyramid_icon(kind, w=180, h=160):
    body = []
    if kind == "rect_prism":
        body += ['<polygon points="30,60 100,60 120,40 50,40" fill="#eaf2fb" stroke="%s" stroke-width="2"/>' % BLUE,
                  '<rect x="30" y="60" width="70" height="60" fill="#d9e8fa" stroke="%s" stroke-width="2"/>' % BLUE,
                  '<polygon points="100,60 120,40 120,100 100,120" fill="#c3ddf7" stroke="%s" stroke-width="2"/>' % BLUE]
    elif kind == "triangular_prism":
        body += ['<polygon points="30,120 90,120 130,40 70,40" fill="#eaf2fb" stroke="%s" stroke-width="2"/>' % BLUE,
                  '<polygon points="30,120 60,50 130,40 90,120" fill="none" stroke="%s" stroke-width="1.5" stroke-dasharray="3,3"/>' % BLUE,
                  '<polygon points="60,50 130,40 110,90 40,100" fill="#d9e8fa" stroke="%s" stroke-width="2"/>' % BLUE]
    elif kind == "sq_pyramid":
        body += ['<polygon points="20,120 160,120 130,100 50,100" fill="#eaf2fb" stroke="%s" stroke-width="2"/>' % AMBER,
                  '<polygon points="20,120 90,30 130,100" fill="#fdf3dd" stroke="%s" stroke-width="2"/>' % AMBER,
                  '<polygon points="160,120 90,30 130,100" fill="#fcecc4" stroke="%s" stroke-width="2"/>' % AMBER]
    elif kind == "tri_pyramid":
        body += ['<polygon points="30,120 150,120 90,40" fill="#fdf3dd" stroke="%s" stroke-width="2"/>' % AMBER,
                  '<polygon points="30,120 90,40 90,110" fill="#fcecc4" stroke="%s" stroke-width="2"/>' % AMBER]
    elif kind == "cylinder":
        body += ['<ellipse cx="90" cy="40" rx="55" ry="16" fill="#eaf2fb" stroke="%s" stroke-width="2"/>' % PURPLE,
                  '<line x1="35" y1="40" x2="35" y2="110" stroke="%s" stroke-width="2"/>' % PURPLE,
                  '<line x1="145" y1="40" x2="145" y2="110" stroke="%s" stroke-width="2"/>' % PURPLE,
                  '<ellipse cx="90" cy="110" rx="55" ry="16" fill="#efe6fb" stroke="%s" stroke-width="2"/>' % PURPLE]
    return svg(w, h, "".join(body))


# --------------------------------------------------------------- transform
def transform_grid(kind, w=260, h=210):
    gx, gy, cell = 20, 20, 24
    body = []
    for i in range(11):
        body.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="1"/>'
                     % (gx, gy + i * cell, gx + 10 * cell, gy + i * cell, GRAY))
        body.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="1"/>'
                     % (gx + i * cell, gy, gx + i * cell, gy + 8 * cell, GRAY))
    orig = [(gx + 2 * cell, gy + 5 * cell), (gx + 4 * cell, gy + 5 * cell), (gx + 2 * cell, gy + 3 * cell)]
    body.append('<polygon points="%s" fill="%s" fill-opacity="0.75" stroke="%s" stroke-width="2"/>'
                 % (" ".join("%d,%d" % p for p in orig), BLUE, BLUE))
    body.append(text(orig[2][0] - 4, orig[2][1] - 6, "original", size=10, color=BLUE, anchor="start", weight="700"))
    if kind == "translation":
        dest = [(x + 4 * cell, y - 2 * cell) for x, y in orig]
        arrow = '<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="2.5" ' \
                'marker-end="url(#tarrow)"/>' % (orig[0][0], orig[0][1] - 4, dest[0][0], dest[0][1] - 4, AMBER)
        defs = '<defs><marker id="tarrow" markerWidth="9" markerHeight="9" refX="7" refY="3" ' \
               'orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="%s"/></marker></defs>' % AMBER
        body.insert(0, defs)
        body.append(arrow)
    elif kind == "reflection":
        mx = gx + 6 * cell
        body.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="2" '
                     'stroke-dasharray="5,4"/>' % (mx, gy, mx, gy + 8 * cell, RED))
        dest = [(2 * mx - x, y) for x, y in orig]
    else:
        cxp, cyp = orig[0]
        dest = []
        for x, y in orig:
            dx, dy = x - cxp, y - cyp
            dest.append((cxp - dy, cyp + dx))
    body.append('<polygon points="%s" fill="%s" fill-opacity="0.55" stroke="%s" stroke-width="2" '
                 'stroke-dasharray="4,3"/>' % (" ".join("%d,%d" % p for p in dest), AMBER, AMBER))
    body.append(text(min(p[0] for p in dest), max(p[1] for p in dest) + 16, "image", size=10,
                      color=AMBER, anchor="start", weight="700"))
    return svg(w, h, "".join(body))
