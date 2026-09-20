"""SVG canvas for the Acorn wiring sheets: measures its own text and checks the layout.

check() FAILS the build if any text leaves its box or the canvas, overlaps other text, sits on a wire
or on a keep-out shape, or if one rectangle that must contain another does not.
"""

import base64
import io
import itertools
import pathlib
import random

from fontTools import subset
from fontTools.ttLib import TTFont
from PIL import Image, ImageFont

HERE = pathlib.Path(__file__).parent
OUT = HERE / "out"
W, H = 1600, 900

FONT_FILES = {
    "regular": "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "bold": "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "mono": "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf",
}

INK, MUTED, FAINT, PAPER = "#15181d", "#5b6470", "#c9ced6", "#fbfaf7"
RED, GOLD, BODY = "#c62828", "#e2b33c", "#1d1f23"

SIGNALS = {  # name: (colour, who drives it, what it is)
    "K2": ("#0f766e", "fpga", "serial TX, FPGA output"),
    "J2": ("#b4491f", "pi", "serial RX, FPGA input"),
    "J5": ("#6b4aa0", "both", "spare GPIO"),
    "H5": ("#1d6fb8", "both", "spare GPIO"),
    "TDI": ("#d97706", "pi", "JTAG data in"),
    "TDO": ("#2e7d32", "fpga", "JTAG data out"),
    "TCK": ("#546e7a", "pi", "JTAG clock"),
    "TMS": ("#d81b60", "pi", "JTAG mode select"),
    "GND1": ("#15181d", None, "ground"),
    "GND2": ("#15181d", None, "ground"),
}
P1_PINS = ["GND1", "TCK", "TDO", "TMS", "TDI", "VCC"]  # pin 1 .. pin 6, physical order
P2_PINS = ["GND2", "J2", "K2", "J5", "H5", "VCC"]


def label_of(sig):
    return "GND" if sig.startswith("GND") else sig


# ----------------------------------------------------------------------------------------------
# SVG canvas that knows how wide its text is
# ----------------------------------------------------------------------------------------------
class Sheet:
    def __init__(self):
        self.parts = []
        self.texts = []  # (bbox, string, may_touch_wire)
        self.wire_segments = []  # (x0, y0, x1, y1)
        self.contain = []  # (inner, outer, what)
        self.keepouts = []  # (bbox, what): shapes no text may touch
        self.boxes = []  # (bbox, label): filled labels, which may not overlap each other
        self.used = {k: set() for k in FONT_FILES}
        self._fonts = {}

    def font(self, face, size):
        key = (face, size)
        if key not in self._fonts:
            self._fonts[key] = ImageFont.truetype(FONT_FILES[face], size)
        return self._fonts[key]

    def width(self, s, size, face="regular"):
        return self.font(face, size * 4).getlength(s) / 4

    def add(self, s):
        self.parts.append(s)

    def rect(self, x, y, w, h, fill="none", stroke="none", sw=1, rx=0, extra=""):
        self.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}" '
                 f'stroke="{stroke}" stroke-width="{sw}" {extra}/>')

    def text(self, x, y, s, size=13, face="regular", fill=INK, anchor="start", box=None, on_wire=False, rotate=None):
        """Draw text with its baseline at y. `box` = (x0, y0, x1, y1) the text must stay inside."""
        w = self.width(s, size, face)
        x0 = {"start": x, "middle": x - w / 2, "end": x - w}[anchor]
        bbox = (x0, y - size * 0.76, x0 + w, y + size * 0.24)
        if rotate is None:
            self.texts.append((bbox, s, on_wire))
            if box is not None:
                self.contain.append((bbox, box, f"text {s!r}"))
        self.used[face].update(s)
        esc = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        tr = f' transform="rotate({rotate} {x:.1f} {y:.1f})"' if rotate is not None else ""
        self.add(f'<text x="{x:.1f}" y="{y:.1f}" class="f-{face}" font-size="{size}" fill="{fill}" '
                 f'text-anchor="{anchor}"{tr}>{esc}</text>')
        return w

    def tag(self, x, y, s, fill, size=12, h=20, anchor="start", pad=7, on_wire=False, fg="#fff", stroke="none"):
        """A filled label whose box is sized FROM the text. (x, y) = left/right/centre edge, vertical centre."""
        w = self.width(s, size, "bold") + 2 * pad
        x0 = {"start": x, "middle": x - w / 2, "end": x - w}[anchor]
        self.rect(x0, y - h / 2, w, h, fill=fill, rx=4, stroke=stroke)
        self.boxes.append(((x0, y - h / 2, x0 + w, y + h / 2), s))
        self.text(x0 + w / 2, y + size * 0.35, s, size, "bold", fg, "middle", box=(x0, y - h / 2, x0 + w, y + h / 2),
                  on_wire=on_wire)
        return x0, x0 + w

    def photo(self, name, x, y, w):
        im = Image.open(HERE / "photos" / name)
        h = w * im.height / im.width
        small = im.resize((round(w * 2), round(h * 2)), Image.LANCZOS)
        buf = io.BytesIO()
        small.save(buf, "JPEG", quality=84)
        data = base64.b64encode(buf.getvalue()).decode()
        self.add(f'<image x="{x}" y="{y}" width="{w:.1f}" height="{h:.1f}" href="data:image/jpeg;base64,{data}"/>')
        return (x, y, w, h), w / im.width

    # ---- checks ------------------------------------------------------------------------------
    def check(self, name):
        errors = []
        for inner, outer, what in self.contain:
            if inner[0] < outer[0] - 0.5 or inner[1] < outer[1] - 0.5 or inner[2] > outer[2] + 0.5 or inner[3] > outer[3] + 0.5:
                errors.append(f"{what} leaves its box: {tuple(round(v) for v in inner)} vs {tuple(round(v) for v in outer)}")
        for bbox, s, _ in self.texts:
            if bbox[0] < 8 or bbox[1] < 8 or bbox[2] > W - 8 or bbox[3] > H - 8:
                errors.append(f"text {s!r} leaves the canvas")
        for (a, sa, _), (b, sb, _) in itertools.combinations(self.texts, 2):
            if a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]:
                errors.append(f"text {sa!r} overlaps text {sb!r}")
        for bbox, s, on_wire in self.texts:
            if on_wire:
                continue
            for x0, y0, x1, y1 in self.wire_segments:
                lo_x, hi_x, lo_y, hi_y = min(x0, x1) - 4, max(x0, x1) + 4, min(y0, y1) - 4, max(y0, y1) + 4
                if bbox[0] < hi_x and lo_x < bbox[2] and bbox[1] < hi_y and lo_y < bbox[3]:
                    errors.append(f"text {s!r} at {tuple(round(v) for v in bbox)} sits on the wire run {(x0, y0, x1, y1)}")
                    break
        for (a, sa), (b, sb) in itertools.combinations(self.boxes, 2):
            if a[0] < b[2] - 0.5 and b[0] < a[2] - 0.5 and a[1] < b[3] - 0.5 and b[1] < a[3] - 0.5:
                errors.append(f"label {sa!r} at {tuple(round(v) for v in a)} overlaps label {sb!r} at {tuple(round(v) for v in b)}")
        for bbox, s, _ in self.texts:
            for k, what in self.keepouts:
                if bbox[0] < k[2] and k[0] < bbox[2] and bbox[1] < k[3] and k[1] < bbox[3]:
                    errors.append(f"text {s!r} touches {what}")
        if errors:
            raise SystemExit(f"{name}: {len(errors)} layout errors\n  " + "\n  ".join(errors))

    def font_css(self):
        css = []
        for face, path in FONT_FILES.items():
            chars = "".join(sorted(self.used[face])) or " "
            opts = subset.Options()
            opts.layout_features = []
            opts.notdef_outline = True
            sub = subset.Subsetter(opts)
            font = TTFont(path)
            sub.populate(text=chars)
            sub.subset(font)
            buf = io.BytesIO()
            font.save(buf)
            data = base64.b64encode(buf.getvalue()).decode()
            css.append(f"@font-face{{font-family:'sheet-{face}';src:url(data:font/ttf;base64,{data}) format('truetype');}}"
                       f".f-{face}{{font-family:'sheet-{face}','Liberation Sans',Arial,sans-serif;}}")
        return "".join(css)

    def svg(self):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
                f"<style>{self.font_css()}</style>"
                f'<rect width="{W}" height="{H}" fill="{PAPER}"/>' + "".join(self.parts) + "</svg>")


