# -*- coding: utf-8 -*-
"""Builds 12 extra fill-in-the-blank questions (with a matching diagram) for
every chapter in data/seed.json, bringing each chapter to 20 questions total.
Every answer is computed in code, never typed by hand, so it is correct by
construction. Run once from the math5-platform directory:

    python scripts/gen_questions.py
"""
import json
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(__file__))
import viz  # noqa: E402

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEED_PATH = os.path.join(BASE, "data", "seed.json")

fmt_int = viz.fmt_int
fmt_dec = viz.fmt_dec
num_to_words = viz.num_to_words
expanded_form = viz.expanded_form


def mk(stem, accept, display, unit="", visual="", explanation="", skill="", diff="medium"):
    accept = [str(a) for a in accept]
    return dict(type="fill", stem=stem, options=[], answer=[], accept=accept,
                display_answer=str(display), unit=unit, visual=visual,
                explanation=explanation, skill_tag=skill, difficulty=diff)


def cycle(kinds, rng, n=12):
    out = []
    i = 0
    while len(out) < n:
        out.append(kinds[i % len(kinds)](rng))
        i += 1
    return out


def round_to(n, unit):
    r = n % unit
    base = n - r
    return base + unit if r * 2 >= unit else base


# ============================================================== Chapter 1
def ch1(rng):
    def rand6():
        return rng.randint(100000, 999999)

    PLACES = ["hundred thousands", "ten thousands", "thousands", "hundreds", "tens", "ones"]
    VALUES = [100000, 10000, 1000, 100, 10, 1]

    def k_place(rng):
        n = rand6()
        idx = rng.randrange(6)
        digit = int(str(n)[idx])
        value = digit * VALUES[idx]
        return mk("In the number %s, what is the value of the digit in the %s place?"
                   % (fmt_int(n), PLACES[idx]),
                   [value], fmt_int(value),
                   visual=viz.place_value_grid(n, highlight=idx),
                   explanation="The digit %d sits in the %s place, worth %d each, so its value is %s."
                   % (digit, PLACES[idx], VALUES[idx], fmt_int(value)),
                   skill="place-value", diff="easy")

    def k_word(rng):
        n = rand6()
        return mk("Write '%s' in standard form." % num_to_words(n),
                   [n], fmt_int(n), visual=viz.place_value_grid(n, blank=True),
                   explanation="Reading the word form place by place gives %s." % fmt_int(n),
                   skill="word-to-standard-form", diff="medium")

    def k_expanded(rng):
        n = rand6()
        return mk("Write %s as a single number." % expanded_form(n),
                   [n], fmt_int(n), visual=viz.place_value_grid(n, blank=True),
                   explanation="Adding the parts of the expanded form gives %s." % fmt_int(n),
                   skill="expanded-to-standard-form", diff="medium")

    def k_round(rng):
        n = rand6()
        unit, label = rng.choice([(1000, "nearest thousand"), (10000, "nearest ten thousand"),
                                   (100000, "nearest hundred thousand")])
        r = round_to(n, unit)
        base = n - n % unit
        return mk("Round %s to the %s." % (fmt_int(n), label),
                   [r], fmt_int(r),
                   visual=viz.number_line(base, base + unit, unit / 2,
                                          points=[(n, viz.AMBER, fmt_int(n))],
                                          below=[(r, viz.GREEN, "rounds to %s" % fmt_int(r))]),
                   explanation="%s is closer to %s than to the other %s, so it rounds to %s."
                   % (fmt_int(n), fmt_int(r), label, fmt_int(r)),
                   skill="rounding-large-numbers", diff="hard")

    return cycle([k_place, k_word, k_expanded, k_round], rng)


# ============================================================== Chapter 2
def ch2(rng):
    def rand_dec(places=3):
        whole = rng.randint(0, 9)
        frac = rng.randint(1, 10 ** places - 1)
        return round(whole + frac / 10 ** places, places)

    PLACE_NAMES = {1: "tenths", 2: "hundredths", 3: "thousandths"}

    def k_place(rng):
        n = rand_dec(3)
        s = ("%.3f" % n).split(".")[1]
        idx = rng.randrange(3)
        digit = int(s[idx])
        place = PLACE_NAMES[idx + 1]
        return mk("In the number %s, what digit is in the %s place?" % (fmt_dec(n, 3), place),
                   [digit], digit, visual=viz.place_value_grid(n, digits=4, decimals=3),
                   explanation="Counting tenths, hundredths, then thousandths after the decimal "
                               "point, the %s digit is %d." % (place, digit),
                   skill="decimal-place-value", diff="easy")

    def k_equiv(rng):
        whole = rng.randint(0, 6)
        tenths = rng.randint(1, 9)
        n = round(whole + tenths / 10, 1)
        extra_zeros = rng.choice([1, 2])
        s = "%s%s" % (fmt_dec(n, 1), "0" * extra_zeros)
        grid = viz.hundred_grid(round((n - whole) * 100)) if whole == 0 else \
            viz.place_value_grid(n, digits=2, decimals=1)
        return mk("Write %s with %d more decimal place%s, without changing its value."
                   % (fmt_dec(n, 1), extra_zeros, "s" if extra_zeros > 1 else ""),
                   [s], s,
                   visual=grid,
                   explanation="Extra zeros at the end of a decimal do not change its value, "
                               "so %s equals %s." % (fmt_dec(n, 1), s),
                   skill="equivalent-decimals", diff="easy")

    def k_compare(rng):
        a = rand_dec(rng.choice([1, 2]))
        b = rand_dec(rng.choice([1, 2]))
        while a == b:
            b = rand_dec(2)
        a_s = fmt_dec(a, 2).rstrip("0").rstrip(".")
        b_s = fmt_dec(b, 2).rstrip("0").rstrip(".")
        bigger_s = a_s if a > b else b_s
        smaller_s = b_s if a > b else a_s
        return mk("Write the greater of these two decimals: %s and %s." % (a_s, b_s),
                   [bigger_s], bigger_s,
                   visual=viz.number_line(min(a, b) - 0.2, max(a, b) + 0.2,
                                          (max(a, b) - min(a, b) + 0.4) / 4,
                                          points=[(a, viz.BLUE, a_s), (b, viz.AMBER, b_s)]),
                   explanation="Comparing place by place, %s is greater than %s." % (bigger_s, smaller_s),
                   skill="compare-decimals", diff="medium")

    def k_thousandth(rng):
        base = round(rng.randint(0, 9) + rng.randint(0, 99) / 100, 2)
        add = rng.randint(1, 9)
        n = round(base + add / 1000, 3)
        return mk("What number is %d thousandths more than %s?" % (add, fmt_dec(base, 2)),
                   [fmt_dec(n, 3)], fmt_dec(n, 3),
                   visual=viz.place_value_grid(base, digits=4, decimals=3),
                   explanation="%s + 0.%03d = %s." % (fmt_dec(base, 2), add, fmt_dec(n, 3)),
                   skill="thousandths", diff="hard")

    return cycle([k_place, k_equiv, k_compare, k_thousandth], rng)


# ============================================================== Chapter 3
def ch3(rng):
    def k_build(rng):
        d = rng.randint(2, 6)
        n = rng.randint(1, d - 1)
        m = rng.randint(2, 5)
        return mk("Multiply the numerator and denominator of %d/%d by %d. What fraction do you get?"
                   % (n, d, m),
                   ["%d/%d" % (n * m, d * m), "%d / %d" % (n * m, d * m)],
                   "%d/%d" % (n * m, d * m),
                   visual=viz.fraction_bar_pair(n, d, n * m, d * m, hide_second=True),
                   explanation="%d x %d = %d and %d x %d = %d, so the equivalent fraction is %d/%d."
                   % (n, m, n * m, d, m, d * m, n * m, d * m),
                   skill="build-equivalent-fractions", diff="easy")

    def k_simplify(rng):
        f = rng.randint(2, 6)
        n = rng.randint(1, 4)
        d = rng.randint(n + 1, 6)
        while math.gcd(n, d) != 1:
            n, d = rng.randint(1, 4), rng.randint(2, 6)
        return mk("Simplify %d/%d to simplest form." % (n * f, d * f),
                   ["%d/%d" % (n, d)], "%d/%d" % (n, d),
                   visual=viz.fraction_bar_pair(n * f, d * f, n, d, hide_second=True),
                   explanation="Dividing the top and bottom of %d/%d by their common factor %d "
                               "gives %d/%d." % (n * f, d * f, f, n, d),
                   skill="simplify-fractions", diff="medium")

    def k_whole(rng):
        d = rng.choice([2, 3, 4, 5, 6, 8, 10])
        return mk("What fraction with a denominator of %d is equal to one whole?" % d,
                   ["%d/%d" % (d, d)], "%d/%d" % (d, d),
                   visual=viz.single_fraction_svg(d, d, w=260),
                   explanation="When the numerator equals the denominator, the fraction equals "
                               "one whole, so %d/%d = 1." % (d, d),
                   skill="fractions-equal-one", diff="easy")

    def k_missing(rng):
        n = rng.randint(1, 4)
        d = rng.randint(n + 1, 6)
        while math.gcd(n, d) != 1:
            n, d = rng.randint(1, 4), rng.randint(2, 6)
        m = rng.randint(2, 6)
        new_n = n * m
        return mk("%d/%d = ___/%d. What number completes the equivalent fraction?"
                   % (n, d, d * m),
                   [new_n], new_n,
                   visual=viz.fraction_bar_pair(n, d, new_n, d * m, hide_second=True),
                   explanation="%d and %d are both multiplied by %d, so the missing numerator is %d."
                   % (n, d, m, new_n),
                   skill="missing-numerator", diff="medium")

    return cycle([k_build, k_simplify, k_whole, k_missing], rng)


# ============================================================== Chapter 4
def ch4(rng):
    def k_half(rng):
        d = rng.choice([3, 5, 6, 8, 10])
        n = rng.randint(1, d - 1)
        ans = "greater than" if n * 2 > d else ("less than" if n * 2 < d else "equal to")
        return mk("Is %d/%d greater than, less than, or equal to one half?" % (n, d),
                   [ans], ans,
                   visual=viz.single_fraction_svg(n, d, w=260),
                   explanation="Half of %d is %.1f, and the numerator is %d, so %d/%d is %s one half."
                   % (d, d / 2, n, n, d, ans),
                   skill="half-benchmark", diff="easy")

    def k_decfrac(rng):
        d = rng.choice([2, 4, 5, 10])
        n = rng.randint(1, d - 1)
        dec = round(n / d, 2)
        dec_s = fmt_dec(dec, 2)
        short_s = dec_s.rstrip("0").rstrip(".")
        return mk("Write %d/%d as a decimal." % (n, d), list({dec_s, short_s}), dec_s,
                   visual=viz.single_fraction_svg(n, d, w=260),
                   explanation="%d divided by %d is %s." % (n, d, fmt_dec(dec, 2)),
                   skill="fraction-to-decimal", diff="medium")

    def k_nearest(rng):
        d = rng.choice([5, 6, 8, 10, 12])
        n = rng.randint(1, d - 1)
        cands = {0: 0, 0.5: d / 2, 1: d}
        best = min(cands, key=lambda b: abs(n - cands[b]))
        lbl = {0: "0", 0.5: "one half", 1: "1"}[best]
        return mk("Which benchmark is %d/%d closest to: 0, one half, or 1?" % (n, d), [lbl], lbl,
                   visual=viz.number_line(0, d, d / 4, points=[(n, viz.AMBER, "%d/%d" % (n, d))]),
                   explanation="%d/%d is closest to %s on the number line." % (n, d, lbl),
                   skill="nearest-benchmark", diff="medium")

    def k_order(rng):
        vals = []
        while len(vals) < 2:
            d = rng.choice([2, 4, 5, 10])
            n = rng.randint(1, d - 1)
            v = round(n / d, 2)
            if v not in [x[0] for x in vals]:
                vals.append((v, "%d/%d" % (n, d)))
        dec = round(rng.randint(1, 9) / 10, 1)
        while dec in [x[0] for x in vals]:
            dec = round(rng.randint(1, 9) / 10, 1)
        vals.append((dec, fmt_dec(dec, 1)))
        vals.sort()
        smallest = vals[0][1]
        return mk("Which of these is the smallest: %s?" % ", ".join(v[1] for v in vals),
                   [smallest], smallest,
                   visual=viz.number_line(0, 1, 0.25,
                                          points=[(v, viz.BLUE, lbl) for v, lbl in vals]),
                   explanation="Placed on a number line from 0 to 1, %s is furthest to the left."
                   % smallest, skill="order-fractions-decimals", diff="hard")

    return cycle([k_half, k_decfrac, k_nearest, k_order], rng)


# ============================================================== Chapter 5
def ch5(rng):
    def k_add(rng):
        a = rng.randint(100000, 799999)
        b = rng.randint(50000, 199999)
        return mk("%s + %s = ___" % (fmt_int(a), fmt_int(b)), [a + b], fmt_int(a + b),
                   explanation="%s + %s = %s." % (fmt_int(a), fmt_int(b), fmt_int(a + b)),
                   skill="add-large-numbers", diff="medium")

    def k_sub(rng):
        a = rng.randint(300000, 950000)
        b = rng.randint(50000, a - 1000)
        return mk("%s - %s = ___" % (fmt_int(a), fmt_int(b)), [a - b], fmt_int(a - b),
                   explanation="%s - %s = %s." % (fmt_int(a), fmt_int(b), fmt_int(a - b)),
                   skill="subtract-large-numbers", diff="medium")

    def k_missing_part(rng):
        whole = rng.randint(200000, 900000)
        part = rng.randint(50000, whole - 50000)
        other = whole - part
        return mk("A whole of %s splits into two parts. One part is %s. What is the other part?"
                   % (fmt_int(whole), fmt_int(part)),
                   [other], fmt_int(other),
                   explanation="%s - %s = %s." % (fmt_int(whole), fmt_int(part), fmt_int(other)),
                   skill="part-part-whole", diff="hard")

    def k_estimate(rng):
        a = rng.randint(100000, 899999)
        b = rng.randint(100000, 899999)
        ra = round_to(a, 100000)
        rb = round_to(b, 100000)
        return mk("Estimate %s + %s by rounding each number to the nearest hundred thousand first."
                   % (fmt_int(a), fmt_int(b)),
                   [ra + rb], fmt_int(ra + rb),
                   explanation="%s rounds to %s and %s rounds to %s, so the estimate is %s + %s = %s."
                   % (fmt_int(a), fmt_int(ra), fmt_int(b), fmt_int(rb), fmt_int(ra), fmt_int(rb),
                      fmt_int(ra + rb)),
                   skill="estimate-sums", diff="medium")

    return cycle([k_add, k_sub, k_missing_part, k_estimate], rng)


# ============================================================== Chapter 6
def ch6(rng):
    def k_mult(rng):
        a = rng.randint(12, 96)
        b = rng.randint(3, 9)
        return mk("%d x %d = ___" % (a, b), [a * b], fmt_int(a * b),
                   visual="",
                   explanation="%d x %d = %d." % (a, b, a * b),
                   skill="multiply-2-digit", diff="medium")

    def k_div(rng):
        b = rng.randint(3, 9)
        q = rng.randint(12, 80)
        a = b * q
        return mk("%d / %d = ___" % (a, b), [q], fmt_int(q),
                   visual="",
                   explanation="%d divides evenly by %d exactly %d times, since %d x %d = %d."
                   % (a, b, q, b, q, a),
                   skill="divide-exact", diff="medium")

    def k_remainder(rng):
        b = rng.randint(3, 9)
        q = rng.randint(12, 60)
        r = rng.randint(1, b - 1)
        a = b * q + r
        return mk("%d / %d leaves a remainder. What is the remainder?" % (a, b), [r], r,
                   visual="",
                   explanation="%d x %d = %d, and %d - %d = %d, so the remainder is %d."
                   % (b, q, b * q, a, b * q, r, r),
                   skill="division-remainder", diff="hard")

    def k_word(rng):
        b = rng.randint(3, 9)
        q = rng.randint(8, 40)
        a = b * q
        return mk("A baker splits %d muffins evenly into boxes of %d. How many boxes are filled?"
                   % (a, b), [q], q,
                   visual=viz.array_grid(min(q, 8), b),
                   explanation="%d / %d = %d boxes." % (a, b, q),
                   skill="multiplication-division-word-problem", diff="medium")

    return cycle([k_mult, k_div, k_remainder, k_word], rng)


# ============================================================== Chapter 7
def ch7(rng):
    def rand_money(lo=1, hi=900):
        return round(rng.randint(lo * 100, hi * 100) / 100, 2)

    def k_add(rng):
        a, b = rand_money(1, 500), rand_money(1, 500)
        s = round(a + b, 2)
        return mk("$%s + $%s = $___" % (fmt_dec(a, 2), fmt_dec(b, 2)), [fmt_dec(s, 2)],
                   fmt_dec(s, 2),
                   visual="",
                   explanation="Lining up the decimal points, $%s + $%s = $%s."
                   % (fmt_dec(a, 2), fmt_dec(b, 2), fmt_dec(s, 2)),
                   skill="add-decimals", diff="medium")

    def k_sub(rng):
        a = rand_money(50, 900)
        b = rand_money(1, 49)
        d = round(a - b, 2)
        return mk("$%s - $%s = $___" % (fmt_dec(a, 2), fmt_dec(b, 2)), [fmt_dec(d, 2)],
                   fmt_dec(d, 2),
                   visual="",
                   explanation="Lining up the decimal points, $%s - $%s = $%s."
                   % (fmt_dec(a, 2), fmt_dec(b, 2), fmt_dec(d, 2)),
                   skill="subtract-decimals", diff="medium")

    def k_pad(rng):
        a = round(rng.randint(1, 90) + rng.choice([0.5, 0.25, 0.75, 0.1, 0.2]), 3)
        b = round(rng.randint(1, 9) / 100, 2)
        s = round(a + b, 3)
        return mk("%s + %s = ___ (pad with zeros so both numbers line up)" % (fmt_dec(a, 3), fmt_dec(b, 2)),
                   [fmt_dec(s, 3)], fmt_dec(s, 3),
                   visual="",
                   explanation="Writing %s as %s lines up every place, so %s + %s = %s."
                   % (fmt_dec(b, 2), fmt_dec(b, 3), fmt_dec(a, 3), fmt_dec(b, 3), fmt_dec(s, 3)),
                   skill="pad-decimals", diff="hard")

    def k_estimate(rng):
        a = round(rng.uniform(1, 99), 2)
        b = round(rng.uniform(1, 99), 2)
        ra, rb = round(a), round(b)
        return mk("Estimate %s + %s by rounding each to the nearest whole number first."
                   % (fmt_dec(a, 2), fmt_dec(b, 2)),
                   [ra + rb], fmt_int(ra + rb),
                   visual="",
                   explanation="%s rounds to %d and %s rounds to %d, so the estimate is %d."
                   % (fmt_dec(a, 2), ra, fmt_dec(b, 2), rb, ra + rb),
                   skill="estimate-decimal-sums", diff="medium")

    return cycle([k_add, k_sub, k_pad, k_estimate], rng)


# ============================================================== Chapter 8
def ch8(rng):
    def k_maketen(rng):
        a = rng.randint(6, 9)
        b = rng.randint(20 - a, 9) if 20 - a <= 9 else rng.randint(2, 9)
        b = rng.randint(max(2, 11 - a), 9)
        return mk("%d + %d = ___" % (a, b), [a + b], a + b,
                   visual=viz.number_line(0, 20, 1, points=[(a, viz.BLUE, str(a))],
                                          arcs=[(a, a + b, viz.AMBER, "+%d" % b)]),
                   explanation="Make ten first: %d + %d = 10, then 10 + %d = %d."
                   % (a, 10 - a, a + b - 10, a + b),
                   skill="making-ten", diff="easy")

    def k_doubles(rng):
        a = rng.randint(4, 9)
        b = a + rng.choice([-1, 1])
        b = max(1, min(9, b))
        return mk("%d + %d = ___ (use a near double)" % (a, b), [a + b], a + b,
                   visual=viz.number_line(0, 20, 1, points=[(a, viz.BLUE, str(a))],
                                          arcs=[(a, a + b, viz.GREEN, "+%d" % b)]),
                   explanation="%d + %d is double %d, %s 1, which is %d."
                   % (a, b, a, "plus" if b > a else "minus", a + b),
                   skill="near-doubles", diff="easy")

    def k_subtract(rng):
        a = rng.randint(11, 20)
        b = rng.randint(2, a - 1)
        return mk("%d - %d = ___" % (a, b), [a - b], a - b,
                   visual=viz.number_line(0, 20, 1, points=[(a, viz.AMBER, str(a))],
                                          arcs=[(b, a, viz.RED, "-%d" % b)]),
                   explanation="Counting back %d from %d lands on %d." % (b, a, a - b),
                   skill="subtraction-facts", diff="medium")

    def k_annex(rng):
        a = rng.randint(3, 9)
        b = rng.randint(2, max(2, 9 - a))
        scale = rng.choice([10, 100])
        return mk("If %d + %d = %d, what is %d + %d?" % (a, b, a + b, a * scale, b * scale),
                   [(a + b) * scale], fmt_int((a + b) * scale),
                   visual="",
                   explanation="%d + %d = %d, and annexing a zero%s gives %d + %d = %s."
                   % (a, b, a + b, "s" if scale == 100 else "", a * scale, b * scale,
                      fmt_int((a + b) * scale)),
                   skill="annexing-zeros", diff="hard")

    return cycle([k_maketen, k_doubles, k_subtract, k_annex], rng)


# ============================================================== Chapter 9
def ch9(rng):
    def k_fact(rng):
        a = rng.randint(2, 10)
        b = rng.randint(2, 10)
        return mk("%d x %d = ___" % (a, b), [a * b], a * b,
                   visual=viz.array_grid(a, b),
                   explanation="An array of %d rows and %d columns has %d dots in all."
                   % (a, b, a * b), skill="multiplication-facts", diff="easy")

    def k_divfact(rng):
        a = rng.randint(2, 10)
        b = rng.randint(2, 10)
        p = a * b
        return mk("%d / %d = ___" % (p, a), [b], b,
                   visual=viz.array_grid(a, b),
                   explanation="%d divided into groups of %d makes %d groups." % (p, a, b),
                   skill="division-facts", diff="easy")

    def k_double(rng):
        a = rng.randint(2, 6)
        b = rng.choice([2, 4])
        return mk("Use doubling to find %d x %d." % (a, b), [a * b], a * b,
                   visual=viz.array_grid(a, b),
                   explanation="Doubling %d %s gives %d." % (a, "twice" if b == 4 else "once", a * b),
                   skill="doubling-strategy", diff="medium")

    def k_skip(rng):
        step = rng.randint(2, 9)
        n = rng.randint(3, 9)
        return mk("Skip count by %ds, %d times, starting at %d. What number do you land on?"
                   % (step, n, step), [step * n], step * n,
                   visual=viz.array_grid(n, step),
                   explanation="Skip counting by %d a total of %d times reaches %d x %d = %d."
                   % (step, n, step, n, step * n),
                   skill="skip-counting", diff="medium")

    return cycle([k_fact, k_divfact, k_double, k_skip], rng)


# ============================================================= Chapter 10
def ch10(rng):
    def k_next(rng):
        start = rng.randint(1, 6)
        step = rng.randint(2, 8)
        terms = [start + step * i for i in range(4)]
        nxt = start + step * 4
        return mk("What is the next term in the pattern %s?" % ", ".join(map(str, terms)),
                   [nxt], nxt,
                   visual=viz.pattern_row(terms + [0], unknown_index=4),
                   explanation="Each term is %d more than the one before, so the next term is %d + %d = %d."
                   % (step, terms[-1], step, nxt),
                   skill="extend-pattern", diff="easy")

    def k_decrease(rng):
        start = rng.randint(40, 90)
        step = rng.randint(2, 8)
        terms = [start - step * i for i in range(4)]
        nxt = start - step * 4
        return mk("What is the next term in the decreasing pattern %s?" % ", ".join(map(str, terms)),
                   [nxt], nxt, visual="",
                   explanation="Each term is %d less than the one before, so the next term is %d - %d = %d."
                   % (step, terms[-1], step, nxt),
                   skill="decreasing-pattern", diff="medium")

    def k_rule(rng):
        step = rng.randint(2, 9)
        start = rng.randint(1, 10)
        term_n = rng.randint(5, 9)
        value = start + step * (term_n - 1)
        return mk("A pattern starts at %d and increases by %d each time. What is term %d?"
                   % (start, step, term_n), [value], value, visual="",
                   explanation="Term %d is %d + %d x %d = %d." % (term_n, start, step, term_n - 1, value),
                   skill="pattern-rule", diff="hard")

    def k_table(rng):
        step = rng.randint(2, 6)
        n1, n2 = rng.randint(1, 4), 0
        n2 = n1 + rng.randint(2, 4)
        v1 = step * n1
        v2 = step * n2
        return mk("A pattern rule is 'multiply the term number by %d'. Term %d has value %d. "
                   "What is the value of term %d?" % (step, n1, v1, n2),
                   [v2], v2, visual="",
                   explanation="Term %d = %d x %d = %d." % (n2, step, n2, v2),
                   skill="pattern-table", diff="medium")

    return cycle([k_next, k_decrease, k_rule, k_table], rng)


# ============================================================= Chapter 11
def ch11(rng):
    def k_addsub(rng):
        x = rng.randint(2, 40)
        b = rng.randint(2, 30)
        op = rng.choice(["+", "-"])
        if op == "+":
            total = x + b
            stem = "x + %d = %d. What is x?" % (b, total)
        else:
            x, b = max(x, b), min(x, b)
            total = x - b
            stem = "x - %d = %d. What is x?" % (b, total)
        return mk(stem, [x], x,
                   visual=viz.balance_scale("x %s %d" % (op, b), str(total)),
                   explanation="Using the inverse operation, x = %d." % x,
                   skill="one-step-equation-addsub", diff="easy")

    def k_muldiv(rng):
        b = rng.randint(2, 9)
        op = rng.choice(["x", "/"])
        if op == "x":
            x = rng.randint(2, 12)
            total = x * b
            # the chapter writes multiplication by juxtaposition (5x), which keeps
            # the variable apart from the x used as a multiplication sign
            stem = "%dx = %d. What is x?" % (b, total)
            beam_left = "%dx" % b
        else:
            x = rng.randint(2, 12)
            total = x
            x = x * b
            stem = "x / %d = %d. What is x?" % (b, total)
            beam_left = "x / %d" % b
        return mk(stem, [x], x,
                   visual=viz.balance_scale(beam_left, str(total)),
                   explanation="Using the inverse operation, x = %d." % x,
                   skill="one-step-equation-muldiv", diff="medium")

    def k_word(rng):
        b = rng.randint(3, 50)
        x = rng.randint(2, 40)
        total = x + b
        return mk("Yuki had some stickers. After getting %d more, she had %d. Write and solve "
                   "an equation for the stickers she started with (x)." % (b, total),
                   [x], x,
                   visual=viz.balance_scale("x + %d" % b, str(total)),
                   explanation="x + %d = %d, so x = %d - %d = %d." % (b, total, total, b, x),
                   skill="write-equation-from-words", diff="medium")

    def k_check(rng):
        x = rng.randint(2, 20)
        b = rng.randint(2, 20)
        total = x + b
        return mk("A student says x = %d is the solution to x + %d = %d. Substitute to check: "
                   "what does the left side equal?" % (x, b, total),
                   [total], total,
                   visual="",
                   explanation="%d + %d = %d, which matches the right side, so x = %d is correct."
                   % (x, b, total, x),
                   skill="check-solution", diff="hard")

    return cycle([k_addsub, k_muldiv, k_word, k_check], rng)


# ============================================================= Chapter 12
def ch12(rng):
    def k_area(rng):
        l = rng.randint(3, 12)
        w = rng.randint(3, 10)
        return mk("A rectangle is %d cm long and %d cm wide. What is its area?" % (l, w),
                   [l * w], l * w, unit="cm2",
                   visual=viz.area_grid(w, l, unit="cm"),
                   explanation="Area = length x width = %d x %d = %d cm2." % (l, w, l * w),
                   skill="rectangle-area", diff="easy")

    def k_square(rng):
        s = rng.randint(3, 14)
        return mk("A square has side length %d m. What is its area?" % s, [s * s], s * s,
                   unit="m2",
                   visual=viz.area_grid(s, s, unit="m") if s <= 10 else "",
                   explanation="Area = side x side = %d x %d = %d m2." % (s, s, s * s),
                   skill="square-area", diff="easy")

    def k_missing_side(rng):
        w = rng.randint(3, 10)
        area = w * rng.randint(3, 12)
        l = area // w
        return mk("A rectangle has an area of %d cm2 and a width of %d cm. What is its length?"
                   % (area, w), [l], l, unit="cm",
                   visual=viz.area_grid(w, l, unit="cm") if l <= 12 else "",
                   explanation="Length = area / width = %d / %d = %d cm." % (area, w, l),
                   skill="missing-side-from-area", diff="medium")

    def k_compare(rng):
        l1, w1 = rng.randint(4, 10), rng.randint(3, 8)
        l2, w2 = rng.randint(4, 10), rng.randint(3, 8)
        a1, a2 = l1 * w1, l2 * w2
        bigger = "the first rectangle" if a1 > a2 else "the second rectangle"
        if a1 == a2:
            l2 += 1
            a2 = l2 * w2
            bigger = "the second rectangle"
        return mk("Rectangle A is %d cm by %d cm. Rectangle B is %d cm by %d cm. Which has the "
                   "greater area: the first rectangle or the second rectangle?" % (l1, w1, l2, w2),
                   [bigger], bigger,
                   visual="",
                   explanation="Rectangle A has area %d cm2 and rectangle B has area %d cm2, so %s "
                               "has the greater area." % (a1, a2, bigger),
                   skill="compare-areas", diff="hard")

    return cycle([k_area, k_square, k_missing_side, k_compare], rng)


# ============================================================= Chapter 13
def ch13(rng):
    def k_both(rng):
        l = rng.randint(3, 12)
        w = rng.randint(2, 9)
        area = l * w
        perim = 2 * (l + w)
        which = rng.choice(["area", "perimeter"])
        ans = area if which == "area" else perim
        unit = "cm2" if which == "area" else "cm"
        return mk("A rectangle is %d cm by %d cm. What is its %s?" % (l, w, which), [ans], ans,
                   unit=unit, visual=viz.area_grid(w, l, unit="cm") if l <= 12 else "",
                   explanation="Area = %d x %d = %d cm2. Perimeter = 2 x (%d + %d) = %d cm."
                   % (l, w, area, l, w, perim),
                   skill="area-and-perimeter", diff="easy")

    def k_same_perim(rng):
        p = rng.choice([16, 20, 24, 28, 32])
        half = p // 2
        l = rng.randint(2, half - 2)
        w = half - l
        return mk("A rectangle has a perimeter of %d cm and a length of %d cm. What is its area?"
                   % (p, l), [l * w], l * w, unit="cm2",
                   visual=viz.area_grid(w, l, unit="cm") if l <= 12 and w <= 12 else "",
                   explanation="Width = %d / 2 - %d = %d cm, so area = %d x %d = %d cm2."
                   % (p, l, w, l, w, l * w),
                   skill="same-perimeter-different-area", diff="hard")

    def k_same_area(rng):
        area = rng.choice([12, 16, 18, 20, 24, 36])
        divisors = [d for d in range(2, area) if area % d == 0]
        l = rng.choice(divisors)
        w = area // l
        perim = 2 * (l + w)
        return mk("A rectangle has an area of %d cm2 and a length of %d cm. What is its perimeter?"
                   % (area, l), [perim], perim, unit="cm",
                   visual=viz.area_grid(w, l, unit="cm") if l <= 12 and w <= 12 else "",
                   explanation="Width = %d / %d = %d cm, so perimeter = 2 x (%d + %d) = %d cm."
                   % (area, l, w, l, w, perim),
                   skill="same-area-different-perimeter", diff="medium")

    def k_perim_only(rng):
        sides = [rng.randint(2, 15) for _ in range(4)]
        return mk("A four-sided shape has sides %s cm. What is its perimeter?"
                   % ", ".join(map(str, sides)), [sum(sides)], sum(sides), unit="cm",
                   visual="",
                   explanation="Adding every side: %s = %d cm." % (" + ".join(map(str, sides)), sum(sides)),
                   skill="perimeter-irregular", diff="medium")

    return cycle([k_both, k_same_perim, k_same_area, k_perim_only], rng)


# ============================================================= Chapter 14
def ch14(rng):
    def k_convert(rng):
        unit, factor, to = rng.choice([("hours", 60, "minutes"), ("minutes", 60, "seconds"),
                                       ("days", 24, "hours")])
        n = rng.randint(2, 9)
        return mk("How many %s are in %d %s?" % (to, n, unit), [n * factor], n * factor,
                   unit=to, visual="",
                   explanation="1 %s = %d %s, so %d %s = %d %s." % (unit[:-1], factor, to, n, unit,
                                                                    n * factor, to),
                   skill="convert-time-units", diff="easy")

    def k_elapsed(rng):
        h1 = rng.randint(1, 11)
        m1 = rng.choice([0, 15, 30, 45])
        dur_h = rng.randint(0, 3)
        dur_m = rng.choice([0, 15, 30, 45])
        while dur_h == 0 and dur_m == 0:
            dur_h, dur_m = rng.randint(0, 3), rng.choice([0, 15, 30, 45])
        total_min = h1 * 60 + m1 + dur_h * 60 + dur_m
        h2 = (total_min // 60) % 12
        h2 = 12 if h2 == 0 else h2
        m2 = total_min % 60
        if dur_h and dur_m:
            dur_s = "%d h %d min" % (dur_h, dur_m)
        elif dur_h:
            dur_s = "%d h" % dur_h
        else:
            dur_s = "%d min" % dur_m
        return mk("A movie starts at %d:%02d and runs for %s. What time does it end?"
                   % (h1, m1, dur_s),
                   ["%d:%02d" % (h2, m2)], "%d:%02d" % (h2, m2),
                   visual=viz.clock_face(h1 % 12, m1),
                   explanation="%d:%02d plus %s is %d:%02d." % (h1, m1, dur_s, h2, m2),
                   skill="find-end-time", diff="medium")

    def k_duration(rng):
        h1 = rng.randint(1, 9)
        m1 = rng.choice([0, 15, 30])
        h2 = h1 + rng.randint(1, 3)
        m2 = rng.choice([0, 15, 30, 45])
        t1 = h1 * 60 + m1
        t2 = h2 * 60 + m2
        dur = t2 - t1
        return mk("How many minutes pass between %d:%02d and %d:%02d?" % (h1, m1, h2, m2),
                   [dur], dur, unit="min",
                   visual=viz.clock_face(h1 % 12, m1),
                   explanation="From %d:%02d to %d:%02d is %d minutes." % (h1, m1, h2, m2, dur),
                   skill="elapsed-time", diff="hard")

    def k_readclock(rng):
        h = rng.randint(1, 12)
        m = rng.choice([0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55])
        return mk("What time does the clock show?", ["%d:%02d" % (h, m)], "%d:%02d" % (h, m),
                   visual=viz.clock_face(h, m),
                   explanation="The hour hand is just past %d and the minute hand points to the "
                               "%d-minute mark, so the clock reads %d:%02d." % (h, m, h, m),
                   skill="read-analog-clock", diff="easy")

    return cycle([k_convert, k_elapsed, k_duration, k_readclock], rng)


# ============================================================= Chapter 15
def ch15(rng):
    SOLIDS = [
        ("rectangular prism", "rect_prism", 6, 12, 8),
        ("triangular prism", "triangular_prism", 5, 9, 6),
        ("square pyramid", "sq_pyramid", 5, 8, 5),
        ("triangular pyramid", "tri_pyramid", 4, 6, 4),
        ("cylinder", "cylinder", 3, 2, 0),
    ]

    def k_count(rng):
        name, icon, faces, edges, verts = rng.choice(SOLIDS)
        attr, val = rng.choice([("faces", faces), ("edges", edges), ("vertices", verts)])
        return mk("How many %s does a %s have?" % (attr, name), [val], val,
                   visual=viz.prism_pyramid_icon(icon),
                   explanation="A %s has %d faces, %d edges and %d vertices." % (name, faces, edges, verts),
                   skill="count-faces-edges-vertices", diff="medium")

    def k_name(rng):
        name, icon, faces, edges, verts = rng.choice(SOLIDS)
        return mk("This solid has %d faces, %d edges and %d vertices. What is its name?"
                   % (faces, edges, verts), [name], name,
                   visual=viz.prism_pyramid_icon(icon),
                   explanation="%d faces, %d edges and %d vertices describe a %s."
                   % (faces, edges, verts, name),
                   skill="name-solid-from-attributes", diff="hard")

    def k_prism_vs_pyramid(rng):
        name, icon, faces, edges, verts = rng.choice(SOLIDS[:4])
        kind = "prism" if "prism" in name else "pyramid"
        return mk("Is a %s a prism or a pyramid?" % name, [kind], kind,
                   visual=viz.prism_pyramid_icon(icon),
                   explanation="A %s has %s, which makes it a %s."
                   % (name, "two matching parallel bases" if kind == "prism" else "one base "
                      "and triangular faces meeting at a point", kind),
                   skill="prism-or-pyramid", diff="easy")

    def k_base(rng):
        name, icon, faces, edges, verts = rng.choice(SOLIDS[:4])
        base = "triangle" if "triangular" in name else ("square" if "square" in name else "rectangle")
        return mk("What shape is the base of a %s?" % name, [base], base,
                   visual=viz.prism_pyramid_icon(icon),
                   explanation="The name '%s' tells you its base is a %s." % (name, base),
                   skill="name-base-shape", diff="easy")

    return cycle([k_count, k_name, k_prism_vs_pyramid, k_base], rng)


# ============================================================= Chapter 16
def ch16(rng):
    def k_name(rng):
        kind, word = rng.choice([("translation", "slide"), ("reflection", "flip"), ("rotation", "turn")])
        return mk("A shape is moved in a %s without changing size or shape. What is the "
                   "everyday word for this transformation?" % kind, [word], word,
                   visual=viz.transform_grid(kind),
                   explanation="A %s is also called a %s." % (kind, word),
                   skill="transformation-everyday-word", diff="easy")

    def k_everyday(rng):
        kind, word = rng.choice([("translation", "slide"), ("reflection", "flip"), ("rotation", "turn")])
        return mk("A shape is given a %s. What is the mathematical name for this transformation?"
                   % word, [kind], kind,
                   visual=viz.transform_grid(kind),
                   explanation="A %s is the mathematical name for a %s." % (kind, word),
                   skill="transformation-math-word", diff="easy")

    def k_congruent(rng):
        kind, word = rng.choice([("translation", "slide"), ("reflection", "flip"), ("rotation", "turn")])
        return mk("After a %s, is the image congruent (same size and shape) to the original: "
                   "yes or no?" % kind, ["yes"], "yes",
                   visual=viz.transform_grid(kind),
                   explanation="Every single transformation keeps the size and shape the same, "
                               "so the image is always congruent to the original.",
                   skill="transformations-preserve-congruence", diff="medium")

    def k_count(rng):
        n = rng.randint(2, 5)
        return mk("A design is made by translating one triangle %d times. How many congruent "
                   "triangles appear in the finished design, counting the original?" % n, [n + 1], n + 1,
                   visual=viz.transform_grid("translation"),
                   explanation="The original plus %d translated copies makes %d triangles in total."
                   % (n, n + 1),
                   skill="transformations-in-patterns", diff="hard")

    return cycle([k_name, k_everyday, k_congruent, k_count], rng)


# ============================================================= Chapter 17
def ch17(rng):
    DAYS = ["Mon", "Tue", "Wed", "Thu"]

    def build(rng):
        a = [rng.randint(2, 18) for _ in DAYS]
        b = [rng.randint(2, 18) for _ in DAYS]
        return a, b

    def k_read(rng):
        a, b = build(rng)
        i = rng.randrange(len(DAYS))
        return mk("The double bar graph shows Class A and Class B. How many did Class A record "
                   "on %s?" % DAYS[i], [a[i]], a[i],
                   visual=viz.double_bar_chart(DAYS, a, b, "Class A", "Class B"),
                   explanation="The blue bar for %s reaches %d." % (DAYS[i], a[i]),
                   skill="read-double-bar-graph", diff="easy")

    def k_diff(rng):
        a, b = build(rng)
        i = rng.randrange(len(DAYS))
        diff = abs(a[i] - b[i])
        return mk("On %s, how much greater is the larger class value than the smaller one?"
                   % DAYS[i], [diff], diff,
                   visual=viz.double_bar_chart(DAYS, a, b, "Class A", "Class B"),
                   explanation="Class A shows %d and Class B shows %d on %s; the difference is %d."
                   % (a[i], b[i], DAYS[i], diff),
                   skill="compare-double-bar-graph", diff="medium")

    def k_total(rng):
        a, b = build(rng)
        i = rng.randrange(len(DAYS))
        total = a[i] + b[i]
        return mk("What is the combined total for both classes on %s?" % DAYS[i], [total], total,
                   visual=viz.double_bar_chart(DAYS, a, b, "Class A", "Class B"),
                   explanation="%d + %d = %d." % (a[i], b[i], total),
                   skill="total-double-bar-graph", diff="medium")

    def k_scale(rng):
        scale = rng.choice([2, 5, 10])
        marks = rng.randint(2, 6)
        return mk("On a graph, each symbol stands for %d votes. If a bar shows %d symbols, how "
                   "many votes does it represent?" % (scale, marks), [scale * marks], scale * marks,
                   visual="",
                   explanation="%d symbols x %d votes each = %d votes." % (marks, scale, scale * marks),
                   skill="many-to-one-correspondence", diff="hard")

    return cycle([k_read, k_diff, k_total, k_scale], rng)


# ============================================================= Chapter 18
def ch18(rng):
    COLORS = {"red": viz.RED, "blue": viz.BLUE, "green": viz.GREEN, "yellow": viz.AMBER,
              "purple": viz.PURPLE}

    def build_spinner(rng, n):
        names = rng.sample(list(COLORS), n)
        weights = [rng.randint(1, 4) for _ in names]
        return names, weights

    def k_outcomes(rng):
        n = rng.randint(3, 5)
        names, weights = build_spinner(rng, n)
        return mk("A spinner has %d equal sections coloured %s. How many possible outcomes does "
                   "one spin have?" % (n, ", ".join(names)), [n], n,
                   visual=viz.spinner(list(zip(names, [1] * n, [COLORS[c] for c in names]))),
                   explanation="Each section is one possible outcome, and there are %d sections." % n,
                   skill="list-outcomes", diff="easy")

    def k_prob(rng):
        n = rng.randint(3, len(COLORS))
        names = rng.sample(list(COLORS), n)
        i = rng.randrange(n)
        return mk("A spinner has %d equal sections. What is the probability of landing on the "
                   "%s section, as a fraction?" % (n, names[i]), ["1/%d" % n], "1/%d" % n,
                   visual=viz.spinner([(c, 1, COLORS[c]) for c in names]),
                   explanation="1 out of %d equal sections is %s, so the probability is 1/%d."
                   % (n, names[i], n),
                   skill="probability-as-fraction", diff="medium")

    def k_scale(rng):
        pos = rng.choice(["impossible", "certain", "even chance"])
        val = {"impossible": "0", "certain": "1", "even chance": "1/2"}[pos]
        return mk("On the probability scale from 0 to 1, what number matches an event that is "
                   "'%s'?" % pos, [val], val, visual="",
                   explanation="An event that is %s sits at %s on the probability scale." % (pos, val),
                   skill="probability-scale", diff="easy")

    def k_weighted(rng):
        n = rng.randint(2, 4)
        names, weights = build_spinner(rng, n)
        total = sum(weights)
        i = rng.randrange(n)
        return mk("A spinner has %d sections sized %s (out of %d equal parts). What is the "
                   "probability of landing on %s, as a fraction out of %d?"
                   % (n, ", ".join(str(w) for w in weights), total, names[i], total),
                   ["%d/%d" % (weights[i], total)], "%d/%d" % (weights[i], total),
                   visual=viz.spinner(list(zip(names, weights, [COLORS[c] for c in names]))),
                   explanation="%s takes up %d of the %d equal parts, so the probability is %d/%d."
                   % (names[i], weights[i], total, weights[i], total),
                   skill="weighted-probability", diff="hard")

    return cycle([k_outcomes, k_prob, k_scale, k_weighted], rng)


# ============================================================= Chapter 19
def ch19(rng):
    def k_add(rng):
        a = round(rng.randint(100, 49900) / 100, 2)
        b = round(rng.randint(100, 49900) / 100, 2)
        s = round(a + b, 2)
        return mk("$%s + $%s = $___" % (fmt_dec(a, 2), fmt_dec(b, 2)), [fmt_dec(s, 2)],
                   fmt_dec(s, 2), visual="",
                   explanation="$%s + $%s = $%s." % (fmt_dec(a, 2), fmt_dec(b, 2), fmt_dec(s, 2)),
                   skill="add-money", diff="easy")

    def k_change(rng):
        price = round(rng.randint(150, 4500) / 100, 2)
        paid = math.ceil(price / 5) * 5 + rng.choice([0, 5, 10])
        paid = max(paid, math.ceil(price) + 5)
        change = round(paid - price, 2)
        return mk("An item costs $%s. A customer pays with $%s. How much change do they get?"
                   % (fmt_dec(price, 2), fmt_dec(paid, 2)),
                   [fmt_dec(change, 2)], fmt_dec(change, 2),
                   visual=viz.money_row(paid),
                   explanation="$%s - $%s = $%s change." % (fmt_dec(paid, 2), fmt_dec(price, 2),
                                                            fmt_dec(change, 2)),
                   skill="making-change", diff="medium")

    def k_budget(rng):
        income = rng.randint(20, 90) * 10
        expenses = [rng.randint(5, income // 3) for _ in range(3)]
        savings = income - sum(expenses)
        return mk("Monthly income is $%d. Expenses are $%s. How much is left for savings?"
                   % (income, ", $".join(map(str, expenses))),
                   [savings], fmt_int(savings), unit="$",
                   visual="",
                   explanation="$%d - (%s) = $%d." % (income, " + ".join("$%d" % e for e in expenses),
                                                       savings),
                   skill="build-a-budget", diff="hard")

    def k_savings_goal(rng):
        goal = rng.randint(4, 20) * 10
        per_week = rng.randint(2, 10)
        weeks = math.ceil(goal / per_week)
        exact = goal % per_week == 0
        return mk("Aiden saves $%d each week toward a $%d goal. How many weeks until he reaches "
                   "the goal?" % (per_week, goal), [weeks], weeks, unit="weeks",
                   visual=viz.money_row(per_week),
                   explanation=("%d saved %d times a week reaches exactly $%d in %d weeks."
                                % (per_week, weeks, goal, weeks)) if exact else
                               ("$%d / $%d a week is %d weeks with money left over, so it takes "
                                "%d whole weeks to reach the goal." % (goal, per_week,
                                                                       goal // per_week, weeks)),
                   skill="savings-goal", diff="medium")

    return cycle([k_add, k_change, k_budget, k_savings_goal], rng)


CHAPTER_FUNCS = {1: ch1, 2: ch2, 3: ch3, 4: ch4, 5: ch5, 6: ch6, 7: ch7, 8: ch8, 9: ch9, 10: ch10,
                 11: ch11, 12: ch12, 13: ch13, 14: ch14, 15: ch15, 16: ch16, 17: ch17, 18: ch18,
                 19: ch19}

HERO_VISUALS = {
    1: lambda: viz.place_value_grid(372486, highlight=2),
    2: lambda: viz.place_value_grid(3.75, digits=4, decimals=3),
    3: lambda: viz.fraction_bar_pair(1, 2, 3, 6),
    4: lambda: viz.number_line(0, 1, 0.25, points=[(0, viz.MUTE, "0"), (0.5, viz.AMBER, "1/2"),
                                                    (1, viz.MUTE, "1"), (0.7, viz.BLUE, "0.7")]),
    5: lambda: viz.number_line(0, 1000000, 250000,
                               points=[(320000, viz.BLUE, "320 000"), (480000, viz.AMBER, "480 000")]),
    6: lambda: viz.array_grid(6, 9),
    7: lambda: viz.place_value_grid(12.375, digits=5, decimals=3),
    8: lambda: viz.number_line(0, 20, 1, points=[(7, viz.BLUE, "7")],
                               arcs=[(7, 15, viz.AMBER, "+8")]),
    9: lambda: viz.array_grid(7, 8),
    10: lambda: viz.pattern_row([2, 4, 6, 8], unknown_index=None),
    11: lambda: viz.balance_scale("x + 4", "10"),
    12: lambda: viz.area_grid(5, 8, unit="cm"),
    13: lambda: viz.area_grid(4, 9, unit="cm"),
    14: lambda: viz.clock_face(3, 45),
    15: lambda: viz.prism_pyramid_icon("rect_prism"),
    16: lambda: viz.transform_grid("rotation"),
    17: lambda: viz.double_bar_chart(["Mon", "Tue", "Wed", "Thu"], [6, 9, 4, 12], [8, 5, 10, 7],
                                     "Class A", "Class B"),
    18: lambda: viz.spinner([("Red", 1, viz.RED), ("Blue", 2, viz.BLUE), ("Green", 1, viz.GREEN)]),
    19: lambda: viz.coin_bill_row([20, 10], [1, 0.25, 0.1]),
}


def main():
    with open(SEED_PATH, encoding="utf-8") as f:
        data = json.load(f)

    for c in data["chapters"]:
        num = c["number"]
        c["visual"] = HERO_VISUALS[num]()
        rng = random.Random(10000 + num * 97)
        existing = len(c["questions"])
        new_qs = CHAPTER_FUNCS[num](rng)[:20 - existing]
        pos = existing + 1
        for q in new_qs:
            q["position"] = pos
            pos += 1
        c["questions"].extend(new_qs)
        assert len(c["questions"]) == 20, (num, len(c["questions"]))
        for q in c["questions"]:
            q.setdefault("visual", "")
            assert q["type"] in ("mcq", "multi", "fill")
            if q["type"] == "fill":
                assert q["accept"], (num, q["stem"])
                assert q["display_answer"], (num, q["stem"])
            else:
                assert q["options"] and q["answer"], (num, q["stem"])

    with open(SEED_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1, ensure_ascii=False)
    total = sum(len(c["questions"]) for c in data["chapters"])
    print("done: %d chapters, %d questions total" % (len(data["chapters"]), total))


if __name__ == "__main__":
    main()
