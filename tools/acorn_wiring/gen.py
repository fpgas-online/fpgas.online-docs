"""Acorn wiring sheets: real board photos, one drawn header per sheet, two-bend wires.

Run:  uv run --with pillow --with fonttools python gen.py
Writes out/pi5.svg and out/blade.svg. See GOALS.md for what the sheets have to show, and
sheetlib.py for the layout checks that fail the build.

Wires whose pad is in the header column AWAY from the plugs reach it through the gap between two
rows of pins, the way a trace escapes a connector. That keeps every wire to two bends outside the
header and removes the long loops around it.
"""

import itertools
import random
import sys

from sheetlib import BODY, FAINT, GOLD, H, INK, MUTED, OUT, P1_PINS, P2_PINS, PAPER, RED, SIGNALS, W, Sheet, label_of

MARK = "#ffd60a"  # highlight on photos: not a wire colour
LANE = 22
WIRE, HALO = 4.5, 9
CLEAR = 18  # a crossing stays this far from any corner; parallel runs stay this far apart


# ----------------------------------------------------------------------------------------------
# Routing
# ----------------------------------------------------------------------------------------------
def segments(path):
    return list(zip(path, path[1:], strict=False))


def crossings(paths):
    """(crossings, tracks two wires share, crossings too near a corner or runs too close) over every pair of wires."""
    cross = shared = tight = 0
    for a, b in itertools.combinations(paths, 2):
        for (p0, p1), (q0, q1) in itertools.product(segments(a), segments(b)):
            p_h, q_h = p0[1] == p1[1], q0[1] == q1[1]
            if p_h != q_h:
                (h0, h1), (v0, v1) = ((p0, p1), (q0, q1)) if p_h else ((q0, q1), (p0, p1))
                if min(h0[0], h1[0]) < v0[0] < max(h0[0], h1[0]) and min(v0[1], v1[1]) < h0[1] < max(v0[1], v1[1]):
                    cross += 1
                    # a crossing has to be two straight runs: not inside either wire's corner
                    clear = min(v0[0] - min(h0[0], h1[0]), max(h0[0], h1[0]) - v0[0],
                                h0[1] - min(v0[1], v1[1]), max(v0[1], v1[1]) - h0[1])
                    if clear < CLEAR:
                        tight += 1
                continue
            axis, other = (0, 1) if p_h else (1, 0)
            apart = abs(p0[other] - q0[other])
            if apart < CLEAR:
                lo = max(min(p0[axis], p1[axis]), min(q0[axis], q1[axis]))
                hi = min(max(p0[axis], p1[axis]), max(q0[axis], q1[axis]))
                if hi - lo > -14:  # overlapping, or end to end with less than 14 px between them
                    if apart < HALO:
                        shared += 1
                    else:
                        tight += 1
    return cross, shared, tight


def route(wires, lanes):
    """Two bends per wire: out of the plug, along a lane of its own, into the header. Returns (paths, stats)."""

    def build(order):
        return [[w["start"], (lane, w["start"][1]), (lane, w["end"][1]), w["end"]] for w, lane in zip(wires, order, strict=True)]

    def cost(order):
        paths = build(order)
        c, s, t = crossings(paths)
        return s * 1000 + t * 40 + c * 10 + sum(abs(p[1][0] - p[0][0]) for p in paths) / 5000

    rng = random.Random(1)
    best = None
    for _ in range(80):
        order = list(lanes)
        rng.shuffle(order)
        order = order[: len(wires)]
        spare = [x for x in lanes if x not in order]
        score, improved = cost(order), True
        while improved:
            improved = False
            for i, j in itertools.combinations(range(len(order)), 2):
                order[i], order[j] = order[j], order[i]
                s2 = cost(order)
                if s2 < score - 1e-9:
                    score, improved = s2, True
                else:
                    order[i], order[j] = order[j], order[i]
            for i in range(len(order)):
                for k, x in enumerate(spare):
                    old = order[i]
                    order[i] = x
                    s2 = cost(order)
                    if s2 < score - 1e-9:
                        score, improved, spare[k] = s2, True, old
                    else:
                        order[i] = old
        if best is None or score < best[0]:
            best = (score, list(order))
    paths = build(best[1])
    return paths, crossings(paths)


def rounded(path, r=9):
    d = [f"M{path[0][0]:.1f},{path[0][1]:.1f}"]
    for prev, cur, nxt in zip(path, path[1:], path[2:], strict=False):
        def toward(a, b, dist):
            length = abs(b[0] - a[0]) + abs(b[1] - a[1])
            t = min(dist, length / 2) / length if length else 0
            return a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
        a, b = toward(cur, prev, r), toward(cur, nxt, r)
        d.append(f"L{a[0]:.1f},{a[1]:.1f} Q{cur[0]:.1f},{cur[1]:.1f} {b[0]:.1f},{b[1]:.1f}")
    d.append(f"L{path[-1][0]:.1f},{path[-1][1]:.1f}")
    return " ".join(d)


def draw_wires(sh, wires, paths):
    """Every wire, then every VERTICAL run again over a paper-coloured gap: verticals always pass over horizontals."""
    for p in paths:
        sh.wire_segments += [(a[0], a[1], b[0], b[1]) for a, b in segments(p)]
    for w, p in zip(wires, paths, strict=True):
        sh.add(f'<path d="{rounded(p)}" fill="none" stroke="{w["colour"]}" stroke-width="{WIRE}" stroke-linejoin="round" stroke-linecap="round"/>')
    for w, p in zip(wires, paths, strict=True):
        (x, y0), (_, y1) = p[1], p[2]
        if abs(y1 - y0) < 40:
            continue
        lo, hi = min(y0, y1) + 11, max(y0, y1) - 11
        sh.add(f'<line x1="{x}" y1="{lo}" x2="{x}" y2="{hi}" stroke="{PAPER}" stroke-width="{HALO}"/>')
        sh.add(f'<line x1="{x}" y1="{lo - 2}" x2="{x}" y2="{hi + 2}" stroke="{w["colour"]}" stroke-width="{WIRE}"/>')


def arrow(sh, x, y, colour, direction):
    s = 7 * direction
    sh.add(f'<polygon points="{x - s:.1f},{y - 6} {x + s:.1f},{y} {x - s:.1f},{y + 6}" fill="{colour}" stroke="{PAPER}" stroke-width="1.5"/>')


# ----------------------------------------------------------------------------------------------
# Pieces
# ----------------------------------------------------------------------------------------------
def title_block(sh, kicker, title, subtitle, pins, numbering):
    sh.text(30, 34, kicker, 12, "bold", "#0f766e")
    sh.text(30, 66, title, 30, "bold")
    sh.text(30, 88, subtitle, 13, "regular", MUTED)
    w = sh.width(pins, 19, "mono") + 36
    sh.rect(W - 30 - w, 22, w, 38, fill=BODY, rx=7)
    sh.text(W - 30 - w / 2, 48, pins, 19, "mono", "#fff", "middle", box=(W - 30 - w, 22, W - 30, 60))
    sh.text(W - 30, 76, numbering, 12, "bold", INK, "end")
    sh.text(W - 30, 92, "openFPGALoader --cable libgpiod, in the order TDI : TDO : TCK : TMS", 11.5, "regular", MUTED, "end")
    sh.add(f'<line x1="30" y1="102" x2="{W - 30}" y2="102" stroke="{INK}" stroke-width="1.5"/>')


def footer(sh, credit):
    msg = "Cut the VCC wire (pin 6) of BOTH cables. 3.3 V from the Acorn into the header can destroy the host."
    w = sh.width(msg, 14, "bold") + 40
    sh.rect(30, H - 52, w, 30, fill="#fdecea", stroke=RED, sw=1.5, rx=6)
    sh.text(50, H - 32, msg, 14, "bold", RED, box=(30, H - 52, 30 + w, H - 22))
    sh.text(W - 30, H - 38, "Every wire in the Molex cables is black: count from pin 1.", 12, "bold", INK, "end")
    sh.text(W - 30, H - 22, credit, 10, "regular", MUTED, "end")


def highlight(sh, rect):
    x, y, w, h = rect[0], rect[1], rect[2] - rect[0], rect[3] - rect[1]
    sh.rect(x, y, w, h, stroke=INK, sw=5.5, rx=4)
    sh.rect(x, y, w, h, stroke=MARK, sw=3, rx=4)


def wedge(sh, a, b, down=False):
    """Zoom cone from rect a to rect b, kept faint so nothing oblique competes with the wires."""
    ax0, ay0, ax1, ay1 = a
    bx0, by0, bx1, by1 = b
    if down:
        pts = [(ax0, ay1), (bx0, by0), (bx1, by0), (ax1, ay1)]
    elif bx0 >= ax1:
        pts = [(ax1, ay0), (bx0, by0), (bx0, by1), (ax1, ay1)]
    elif bx1 <= ax0:
        pts = [(ax0, ay0), (bx1, by0), (bx1, by1), (ax0, ay1)]
    elif by0 >= ay1:
        pts = [(ax0, ay1), (bx0, by0), (bx1, by0), (ax1, ay1)]
    else:
        pts = [(ax0, ay0), (bx0, by1), (bx1, by1), (ax1, ay0)]
    poly = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    sh.add(f'<polygon points="{poly}" fill="{INK}" opacity="0.07"/>')
    sh.add(f'<path d="M{pts[0][0]:.1f},{pts[0][1]:.1f} L{pts[1][0]:.1f},{pts[1][1]:.1f} M{pts[3][0]:.1f},{pts[3][1]:.1f} '
           f'L{pts[2][0]:.1f},{pts[2][1]:.1f}" stroke="{INK}" stroke-width="1" opacity="0.3"/>')


def plug_box(sh, x, y, w, name, what, pins, wire_side, pin1_at_top, note, row=31, head=50):
    """Pico-EZmate plug, pins in physical order. Returns ({signal: attach point}, box rect)."""
    h = head + 6 * row + 10
    sh.rect(x, y, w, h, fill="#fff", stroke=FAINT, sw=1.5, rx=8)
    sh.text(x + 14, y + 22, name, 15, "bold", box=(x, y, x + w, y + head))
    sh.text(x + 14 + sh.width(name, 15, "bold") + 8, y + 22, what, 13, "regular", MUTED, box=(x, y, x + w, y + head))
    sh.text(x + w - 14, y + 22, "pin 1 = the end nearest the M.2 edge", 11, "regular", MUTED, "end", box=(x, y, x + w, y + head))
    sh.text(x + 14, y + 40, note, 11.5, "regular", MUTED, box=(x, y, x + w, y + head))
    order = pins if pin1_at_top else pins[::-1]
    shell_x = x + 8 if wire_side == "left" else x + w - 8 - 40
    sh.rect(shell_x, y + head - 2, 40, 6 * row + 4, fill=BODY, rx=4)
    attach = {}
    for i, sig in enumerate(order):
        cy = y + head + row * i + row / 2
        n = pins.index(sig) + 1
        sh.rect(shell_x + 6, cy - 9, 28, 18, fill=GOLD, rx=2)
        sh.text(shell_x + 20, cy + 4.5, str(n), 12.5, "bold", BODY, "middle", box=(shell_x + 6, cy - 9, shell_x + 34, cy + 9))
        edge = x if wire_side == "left" else x + w
        inner = shell_x + 50 if wire_side == "left" else shell_x - 10
        anchor = "start" if wire_side == "left" else "end"
        rowbox = (x, cy - row / 2, x + w, cy + row / 2)
        if sig == "VCC":
            a, b = sh.tag(inner, cy, "VCC", RED, anchor=anchor)
            sh.text(b + 8 if wire_side == "left" else a - 8, cy + 4, "3.3 V: cut this wire", 12, "bold", RED, anchor, box=rowbox)
            stub = edge - 26 if wire_side == "left" else edge + 26
            sh.add(f'<line x1="{edge}" y1="{cy}" x2="{stub}" y2="{cy}" stroke="{RED}" stroke-width="4"/>')
            sh.add(f'<path d="M{stub - 7},{cy - 7} L{stub + 7},{cy + 7} M{stub - 7},{cy + 7} L{stub + 7},{cy - 7}" stroke="{RED}" stroke-width="3"/>')
            continue
        colour, _, desc = SIGNALS[sig]
        a, b = sh.tag(inner, cy, label_of(sig), colour, anchor=anchor)
        sh.text(b + 8 if wire_side == "left" else a - 8, cy + 4, desc, 12, "regular", INK, anchor, box=rowbox)
        attach[sig] = (edge, cy)
    return attach, (x, y, x + w, y + h)


class Header:
    """A two-column pin header, drawn once. `numbers[row]` = (left, right) as printed on, or counted from, the board."""

    def __init__(self, sh, x, y, numbers, pitch, pad, plugs_side):
        self.sh, self.x, self.y, self.pitch, self.pad, self.numbers = sh, x, y, pitch, pad, numbers
        self.body = (x, y, x + 2 * pitch, y + len(numbers) * pitch)
        self.near_col = 0 if plugs_side == "left" else 1
        self.near_x = self.body[0] if plugs_side == "left" else self.body[2]
        self.far_x = self.body[2] if plugs_side == "left" else self.body[0]
        self.out = -1 if plugs_side == "left" else 1  # x direction pointing away from the header on the plug side
        self.where = {n: (r, c) for r, row in enumerate(numbers) for c, n in enumerate(row)}

    def centre(self, n):
        r, c = self.where[n]
        return self.x + self.pitch * c + self.pitch / 2, self.y + self.pitch * r + self.pitch / 2

    def is_near(self, n):
        return self.where[n][1] == self.near_col

    def draw_body(self, used, danger, housings):
        sh, pad = self.sh, self.pad
        sh.rect(self.body[0], self.body[1], self.body[2] - self.body[0], self.body[3] - self.body[1], fill=BODY, rx=6)
        for n in self.where:
            cx, cy = self.centre(n)
            rect = (cx - pad / 2, cy - pad / 2, cx + pad / 2, cy + pad / 2)
            sh.contain.append((rect, self.body, f"pad {n}"))
            fill = GOLD if n in used else ("#ef9a9a" if n in danger else "#6d6a5f")
            sh.rect(rect[0], rect[1], pad, pad, fill=fill, rx=3, stroke=RED if n in danger else "none", sw=2)
            sh.text(cx, cy + pad * 0.17, str(n), pad * 0.5, "bold", BODY if n in used or n in danger else "#d8d5cb", "middle", box=rect)
        for r0, r1 in housings:
            x0, y0 = self.body[0] - 7, self.y + self.pitch * r0 + 7
            w, h = 2 * self.pitch + 14, self.pitch * (r1 - r0 + 1) - 14
            sh.rect(x0, y0, w, h, stroke=PAPER, sw=5, rx=9)
            sh.rect(x0, y0, w, h, stroke=INK, sw=2.5, rx=9, extra='stroke-dasharray="8 5"')

    def side_x(self, n, gap=13):
        """x just outside the body on pin n's own side, and the text anchor to use there."""
        left = self.where[n][1] == 0
        return (self.body[0] - gap, "end") if left else (self.body[2] + gap, "start")

    def empty_mark(self, n):
        x, _ = self.side_x(n, 22)
        _, cy = self.centre(n)
        k = 6
        self.sh.add(f'<path d="M{x - k},{cy - k} L{x + k},{cy + k} M{x - k},{cy + k} L{x + k},{cy - k}" stroke="{RED}" stroke-width="2.6"/>')
        self.sh.keepouts.append(((x - k, cy - k, x + k, cy + k), f"the empty mark on pin {n}"))
        return x

    def note(self, n, text, colour=MUTED, face="regular", after_mark=False):
        x, anchor = self.side_x(n, 36 if after_mark else 13)
        _, cy = self.centre(n)
        self.sh.text(x, cy + 4, text, 11.5, face, colour, anchor)


def terminate(sh, hdr, wires):
    """Give every wire its end point on the header's plug side, and draw the run inside the header to the pad."""
    by_pin = {}
    for w in wires:
        by_pin.setdefault(w["pin"], []).append(w)
    inside = []
    for pin, group in by_pin.items():
        group.sort(key=lambda w: w["start"][1])
        cx, cy = hdr.centre(pin)
        offs = [0] if len(group) == 1 else [-1, 1]
        for w, o in zip(group, offs, strict=True):
            if hdr.is_near(pin):
                y = cy + o * 11
                w["end"] = (hdr.near_x, y)
                pad_edge = cx + hdr.out * hdr.pad / 2
                inside.append((w, [(hdr.near_x, y), (pad_edge + hdr.out * 6, y), (pad_edge, cy + o * 6)]))
            else:
                gy = cy - hdr.pitch / 2 + o * 11
                w["end"] = (hdr.near_x, gy)
                xm = (hdr.body[0] + hdr.body[2]) / 2 + o * hdr.out * 7  # the upper wire turns down nearer its pad
                pad_edge = cx + hdr.out * hdr.pad / 2
                inside.append((w, [(hdr.near_x, gy), (xm, gy), (xm, cy + o * 6), (pad_edge, cy + o * 6)]))
    return inside


def draw_inside(sh, inside):
    for w, pts in inside:
        d = rounded(pts, r=5)
        sh.add(f'<path d="{d}" fill="none" stroke="#f1f3f5" stroke-width="{WIRE + 4}" stroke-linejoin="round"/>')
        sh.add(f'<path d="{d}" fill="none" stroke="{w["colour"]}" stroke-width="{WIRE}" stroke-linejoin="round"/>')


def wire_ends(sh, hdr, wires, names, plugs_side):  # names: {signal: what the host calls that pin}
    """On every wire: signal tag at the header, the host's name for that pin, the resistor, the direction arrow."""
    for w in wires:
        ex, ey = w["end"]
        side = hdr.out
        anchor = "end" if side < 0 else "start"
        a, b = sh.tag(ex + side * 13, ey, label_of(w["sig"]), w["colour"], anchor=anchor, on_wire=True, h=18, size=11.5)
        edge = a if side < 0 else b
        if names.get(w["sig"]):
            a, b = sh.tag(edge + side * 5, ey, names[w["sig"]], "#fff", anchor=anchor, on_wire=True, h=18, size=10.5, fg=INK,
                          stroke="#9aa0a8", pad=5)
            edge = a if side < 0 else b
        if w["resistor"]:
            rw = sh.width("470 Ω", 11, "bold") + 14
            rx0 = edge - 12 - rw if side < 0 else edge + 12
            sh.rect(rx0, ey - 9, rw, 18, fill="#fff", stroke=w["colour"], sw=2.5, rx=3)
            sh.text(rx0 + rw / 2, ey + 4, "470 Ω", 11, "bold", w["colour"], "middle", box=(rx0, ey - 9, rx0 + rw, ey + 9), on_wire=True)
        sx, sy = w["start"]
        step = 1 if plugs_side == "left" else -1
        ax = sx + step * 22
        if w["drive"] == "fpga":
            arrow(sh, ax, sy, w["colour"], step)
        elif w["drive"] == "pi":
            arrow(sh, ax, sy, w["colour"], -step)
        elif w["drive"] == "both":
            arrow(sh, ax - 7, sy, w["colour"], -1)
            arrow(sh, ax + 7, sy, w["colour"], 1)


def make_wires(plug_attach, mapping, resistors):
    return [{"sig": sig, "pin": pin, "colour": SIGNALS[sig][0], "drive": SIGNALS[sig][1], "start": plug_attach[sig],
             "resistor": sig in resistors} for sig, pin in mapping.items()]


def legend(sh, x, y, with_resistor):
    sh.text(x, y, "Reading the wires", 13, "bold")
    grey = "#5b6470"
    yy = y + 24
    sh.add(f'<line x1="{x}" y1="{yy}" x2="{x + 64}" y2="{yy}" stroke="{grey}" stroke-width="{WIRE}"/>')
    arrow(sh, x + 32, yy, grey, 1)
    sh.text(x + 76, yy + 4, "signal travels this way", 12)
    yy += 24
    sh.add(f'<line x1="{x}" y1="{yy}" x2="{x + 64}" y2="{yy}" stroke="{grey}" stroke-width="{WIRE}"/>')
    arrow(sh, x + 25, yy, grey, -1)
    arrow(sh, x + 39, yy, grey, 1)
    sh.text(x + 76, yy + 4, "either end may drive it", 12)
    yy += 24
    sh.add(f'<path d="M{x + 26},{yy - 6} L{x + 38},{yy + 6} M{x + 26},{yy + 6} L{x + 38},{yy - 6}" stroke="{RED}" stroke-width="2.6"/>')
    sh.text(x + 76, yy + 4, "nothing goes on this pin", 12)
    yy += 24
    sh.add(f'<rect x="{x + 4}" y="{yy - 9}" width="56" height="18" rx="7" fill="none" stroke="{INK}" stroke-width="2.5" stroke-dasharray="8 5"/>')
    sh.text(x + 76, yy + 4, "one Dupont housing", 12)
    if with_resistor:
        yy += 24
        rw = sh.width("470 Ω", 11, "bold") + 14
        sh.rect(x + 32 - rw / 2, yy - 9, rw, 18, fill="#fff", stroke=grey, sw=2.5, rx=3)
        sh.text(x + 32, yy + 4, "470 Ω", 11, "bold", grey, "middle")
        sh.text(x + 76, yy + 4, "resistor in that wire,", 12)
        sh.text(x + 76, yy + 19, "at the housing end", 12)


def acorn_photo(sh, x, y, w, rotation):
    """The connector end of the card, connectors facing the plugs. Returns the two highlight rects (P1, P2)."""
    (ax, ay, aw, ah), k = sh.photo(f"acorn-{rotation}.jpg", x, y, w)
    if rotation == "cw":  # connectors on the left edge, P2 on top, pin 1 at the bottom, M.2 edge below
        p2 = (ax + 10 * k, ay + 94 * k, ax + 128 * k, ay + 304 * k)
        p1 = (ax + 6 * k, ay + 336 * k, ax + 128 * k, ay + 550 * k)
        sh.text(x + w / 2, ay - 10, "Acorn underside, fan end", 12.5, "bold", INK, "middle")
        sh.text(x + w / 2, ay + ah + 17, "M.2 edge connector this way", 11.5, "bold", MUTED, "middle")
        sh.add(f'<path d="M{x + w / 2 - 7},{ay + ah + 24} l14,0 l-7,10 z" fill="{MUTED}"/>')
    else:  # connectors on the right edge, P1 on top, pin 1 at the top, M.2 edge above
        p1 = (ax + 394 * k, ay + 550 * k, ax + 516 * k, ay + 764 * k)
        p2 = (ax + 394 * k, ay + 796 * k, ax + 512 * k, ay + 1006 * k)
        sh.text(x + w / 2, ay + ah + 17, "Acorn underside, fan end", 12.5, "bold", INK, "middle")
        sh.text(x + w / 2, ay - 10, "M.2 edge connector this way", 11.5, "bold", MUTED, "middle")
        sh.add(f'<path d="M{x + w / 2 - 7},{ay - 26} l14,0 l-7,-10 z" fill="{MUTED}"/>')
    for rect, name in ((p1, "P1"), (p2, "P2")):
        highlight(sh, rect)
        inward = rect[2] + 5 if rotation == "cw" else rect[0] - 5
        anchor = "start" if rotation == "cw" else "end"
        sh.tag(inward, (rect[1] + rect[3]) / 2, name, MARK, size=12, h=19, anchor=anchor, fg=INK, stroke=INK)
        pin1_y = rect[3] - 9 if rotation == "cw" else rect[1] + 9
        sh.tag(inward, pin1_y, "1", "#fff", size=10, h=15, anchor=anchor, fg=INK, stroke=INK, pad=4)
    return p1, p2


# ----------------------------------------------------------------------------------------------
# The two sheets
# ----------------------------------------------------------------------------------------------
def pi5(nudge=0):
    sh = Sheet()
    title_block(sh, "CARRIER A  ·  WELLAND.FPGAS.ONLINE", "SQRL Acorn CLE-215+ to Raspberry Pi 5",
                "Waveshare PoE M.2 HAT+ on a Pi 5. A Pi 4 or Pi 3B has the same 40-pin header and takes the same cable.",
                "--pins 10:9:11:8", "These are GPIO numbers, not header pin numbers")

    (px, py, pw, ph), k = sh.photo("hat-ccw.jpg", 30, 150, 380)
    sh.text(30, 138, "Pi 5 with the PoE M.2 HAT+, from above", 12.5, "bold")
    sh.text(30, py + ph + 18, "The header pins come up through the HAT along this edge", 11.5, "regular", MUTED)
    sh.text(30, py + ph + 33, "(shown here without the stacking header fitted).", 11.5, "regular", MUTED)
    hl = (px + 436 * k, py + 64 * k, px + 487 * k, py + 355 * k)
    highlight(sh, hl)
    sh.tag(hl[0] - 5, hl[1] + 10, "pin 1", "#fff", size=10, h=15, anchor="end", fg=INK, stroke=INK, pad=4)

    pitch, pad, rows = 48, 26, 13
    numbers = [(2 * r + 1, 2 * r + 2) for r in range(rows)]
    mapping = {"K2": 10, "J2": 8, "J5": 5, "H5": 7, "GND2": 6, "TDI": 19, "TDO": 21, "TCK": 23, "TMS": 24, "GND1": 25}
    hdr = Header(sh, 556, 170 + nudge, numbers, pitch, pad, "right")
    wedge(sh, hl, hdr.body)
    hdr.draw_body(set(mapping.values()), {2, 4}, [(2, 4), (9, 12)])
    sh.text(hdr.x + pitch, hdr.y - 12, "40-pin header, pins 1 to 26", 12, "bold", INK, "middle")
    sh.text(hdr.x + pitch, hdr.body[3] + 18, "pins 27 to 40: not used", 11, "regular", MUTED, "middle")
    for n in (9, 20, 22, 26):
        hdr.empty_mark(n)
    for n in (2, 4):
        hdr.empty_mark(n)
        hdr.note(n, "5 V", RED, "bold", after_mark=True)
    hdr.note(1, "3.3 V")
    hdr.note(17, "3.3 V")

    p1_hl, p2_hl = acorn_photo(sh, 1400, 196, 172, "cw")
    p2_at, p2_box = plug_box(sh, 1076, 176, 300, "P2", "I/O", P2_PINS, "left", False, "to a 2×3 Dupont housing on header pins 5 to 10")
    p1_at, p1_box = plug_box(sh, 1076, 470, 300, "P1", "JTAG", P1_PINS, "left", False, "to a 2×4 Dupont housing on header pins 19 to 26")
    wedge(sh, p2_hl, p2_box)
    wedge(sh, p1_hl, p1_box)

    wires = make_wires({**p2_at, **p1_at}, mapping, set())
    inside = terminate(sh, hdr, wires)
    lanes = [hdr.body[2] + 164 + 18 * i for i in range(12)]
    paths, (cross, shared, tight) = route(wires, lanes)
    assert shared == 0, f"pi5: {shared} shared tracks"
    draw_wires(sh, wires, paths)
    draw_inside(sh, inside)
    names = {"J5": "GPIO3", "H5": "GPIO4", "J2": "GPIO14 TXD", "K2": "GPIO15 RXD", "TDI": "GPIO10", "TDO": "GPIO9",
             "TCK": "GPIO11", "TMS": "GPIO8"}
    wire_ends(sh, hdr, wires, names, "right")

    legend(sh, 40, 700, False)
    footer(sh, "Photos: Waveshare (PoE M.2 HAT+), RHS Research (LiteFury underside; the Acorn is the same PCB)")
    sh.check("pi5")
    return sh.svg(), cross + 3 * tight


def blade(nudge=0):
    sh = Sheet()
    title_block(sh, "CARRIER B  ·  PS1.FPGAS.ONLINE", "SQRL Acorn CLE-101 (LiteFury) to Compute Blade",
                "CM4 or CM5. Header pins carry the numbers printed on the blade: 1 to 5 down the left, 6 to 10 down the right.",
                "--pins 2:3:4:14", "These are GPIO (IO) numbers, not the printed pin numbers")

    (px, py, pw, ph), k = sh.photo("blade.jpg", 30, 132, 930)
    sh.text(30, 124, "Compute Blade, from above", 12.5, "bold")
    strip_hl = (px + 2378 * k, py + 336 * k, px + 2484 * k, py + 496 * k)
    highlight(sh, strip_hl)
    (ix, iy, iw, ih), ki = sh.photo("blade-port.jpg", 1000, 118, 570)
    port_hl = (ix + 1228 * ki, iy + 100 * ki, ix + 1466 * ki, iy + 488 * ki)
    highlight(sh, port_hl)
    sh.tag(ix + iw, iy + ih + 12, "the 4-pin header beside it is the UART: not that one", "#fff", size=10.5, h=17, anchor="end",
           fg=INK, stroke=INK, pad=6)
    wedge(sh, strip_hl, (ix, iy, ix + iw, iy + ih))

    pitch, pad, rows = 88, 38, 5
    numbers = [(r + 1, r + 6) for r in range(rows)]
    mapping = {"TDI": 2, "TDO": 3, "J5": 3, "TCK": 4, "H5": 4, "GND2": 5, "GND1": 8, "TMS": 9, "J2": 9, "K2": 10}
    hdr = Header(sh, 1180, 340 + nudge, numbers, pitch, pad, "left")
    wedge(sh, port_hl, hdr.body, down=True)
    hdr.draw_body(set(mapping.values()), {6, 7}, [(1, 4)])
    for n in (6, 7):
        hdr.empty_mark(n)
    hdr.note(7, "5 V: nothing goes here", RED, "bold", after_mark=True)
    hdr.note(6, "5 V", RED, "bold", after_mark=True)
    hdr.note(1, "3.3 V")

    p1_hl, p2_hl = acorn_photo(sh, 30, 410, 172, "ccw")
    p1_at, p1_box = plug_box(sh, 290, 330, 330, "P1", "JTAG", P1_PINS, "right", True, "to the shared 2×4 Dupont housing", row=29, head=48)
    p2_at, p2_box = plug_box(sh, 290, 580, 330, "P2", "I/O", P2_PINS, "right", True, "to the shared 2×4 Dupont housing", row=29, head=48)
    wedge(sh, p1_hl, p1_box)
    wedge(sh, p2_hl, p2_box)

    wires = make_wires({**p1_at, **p2_at}, mapping, {"J2", "J5", "H5"})
    inside = terminate(sh, hdr, wires)
    lanes = [hdr.body[0] - 236 - LANE * i for i in range(12)]
    paths, (cross, shared, tight) = route(wires, lanes)
    assert shared == 0, f"blade: {shared} shared tracks"
    draw_wires(sh, wires, paths)
    draw_inside(sh, inside)
    names = {"TDI": "IO2", "TDO": "IO3", "TCK": "IO4", "TMS": "IO14", "J2": "TXD", "K2": "IO15 RXD"}
    wire_ends(sh, hdr, wires, names, "left")

    sh.text(1376, 596, "Pins 3, 4 and 9 take two wires", 12.5, "bold")
    sh.text(1376, 613, "in one crimp.", 12.5, "bold")
    legend(sh, 1376, 656, True)
    footer(sh, "Photos: Uptime Lab (Compute Blade), RHS Research (LiteFury underside; the Acorn is the same PCB)")
    sh.check("blade")
    return sh.svg(), cross + 3 * tight


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for name, fn in (("pi5", pi5), ("blade", blade)):
        # A plug row and a header row at nearly the same height would share a track. Nudge the header
        # down a few pixels at a time and keep the placement with the fewest crossings.
        best = None
        fixed = dict(a.split("=") for a in sys.argv[1:])  # e.g. "pi5=8 blade=0" skips the search
        for nudge in ([int(fixed[name])] if name in fixed else range(0, 24, 2)):
            try:
                svg, cross = fn(nudge)
            except AssertionError as e:
                print(f"  {name} nudge {nudge}: {e}")
                continue
            print(f"  {name} nudge {nudge}: score {cross} (crossings + 3 x tight spots)")
            if best is None or cross < best[1]:
                best = (svg, cross, nudge)
        svg, cross, nudge = best
        (OUT / f"{name}.svg").write_text(svg)
        print(f"{name}: {len(svg) // 1024} KiB, routing score {cross} (header nudged {nudge} px), layout checks passed")
