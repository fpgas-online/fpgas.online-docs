# SPDX-License-Identifier: Apache-2.0
"""Draw the figures of the bootloader EEPROM page.

    uv run --no-project --with pillow docs/setup/bootloader-eeprom/make_figures.py
    uv run --no-project docs/setup/bootloader-eeprom/make_figures.py --no-photos    # the diagrams only

Every figure is written twice, <name> for the light theme and the printed booklet and <name>-dark for the
dark theme; the page shows each in its theme (only-light / only-dark). A diagram is one drawing resolved with
the colours of PALETTE; an annotated photograph (PHOTOS) gets its caption band and words in the dark page's
colours, the photograph itself unchanged. tools/test_dark_twins.py checks that the diagrams are what this
writes and that every figure has its twin on the page.

The two photographs (`source/pi5-underside.jpg`, `source/pi5-flash-wp-closeup.jpg`) are crops of
"Raspberry Pi5 8GB Bottom View (1).jpg" by Suyash Dwivedi, Wikimedia Commons, CC BY-SA 4.0
(https://commons.wikimedia.org/wiki/File:Raspberry_Pi5_8GB_Bottom_View_(1).jpg). The annotated versions
written here are under the same licence; each one's caption on the page says so.

The three diagrams are SVG text written from the numbers in this file: the status-register bits from the
Winbond W25Q16JV datasheet, the DIP switch from the Compute Blade maker's table, and the outline of a Dev
model Compute Blade from the maker's own picture (docs.computeblade.com, getting-started/image). That last
one is a drawing from documentation, not from a board in hand, and says so in the figure.
"""
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).parent
SRC = HERE / "source"
THEMES = ("light", "dark")
ORANGE, WHITE, BLACK, SILVER = (232, 112, 42), (255, 255, 255), (0, 0, 0), (214, 218, 222)
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
GREEN, RED = (30, 140, 60), (200, 30, 30)

# The annotated photographs, each written twice: <name>.jpg with its caption band in white for the light theme and
# the printed booklet, and <name>-dark.jpg for the dark theme, its band in the dark page's colour and its words in
# the dark palette. The photograph (its own background too) and what is drawn on it (rings, leaders, solder,
# labels in white with a black edge) are the same on both.
# file name: (picture, what it shows)
PHOTOS = {
    "pi5-underside-flash-wp.jpg": ("underside", "pads"),
    "pi5-underside-sd-slot.jpg": ("underside", "sd"),
    "pi5-flash-wp-closeup.jpg": ("closeup", "pads"),
    "pi5-flash-wp-bridged.jpg": ("closeup", "bridged"),
    "pi5-flash-wp-wrong.jpg": ("closeup", "wrong"),
    "pi5-flash-wp-tweezers.jpg": ("closeup", "tweezers"),
    "pi5-flash-wp-clear.jpg": ("closeup", "clear"),
}
# The words under a photograph, and what they stand on: (light, dark). The dark values are PALETTE's below.
BAND = {
    "band": (WHITE, (0x13, 0x14, 0x16)),
    "words": (BLACK, (0xE3, 0xE6, 0xEA)),
    "orange": (ORANGE, (0xFF, 0xA0, 0x60)),
    "good": (GREEN, (0x5F, 0xD2, 0x7A)),
    "bad": (RED, (0xFF, 0x7B, 0x7B)),
}
def font(size):
    from PIL import ImageFont  # here, not at the top: the diagrams and their tests need no Pillow

    return ImageFont.truetype(FONT, size)


def label(d, xy, text, size=26, fill=WHITE, anchor="mm"):
    d.text(xy, text, font=font(size), fill=fill, anchor=anchor, stroke_width=4, stroke_fill=BLACK)


def ring(d, box, width=7, colour=ORANGE):
    d.ellipse(box, outline=BLACK, width=width + 6)
    d.ellipse(box, outline=colour, width=width)


def band(im, height, theme):
    """The picture with a band under it for the words, in the page's colour, and a draw handle."""
    from PIL import Image, ImageDraw

    out = Image.new("RGB", (im.width, im.height + height), BAND["band"][THEMES.index(theme)])
    out.paste(im, (0, 0))
    return out, ImageDraw.Draw(out)


def words(theme, role="words"):
    return BAND[role][THEMES.index(theme)]


def note(d, xy, text, size, fill, anchor="mm"):
    d.text(xy, text, font=font(size), fill=fill, anchor=anchor)


def leader(d, start, end, colour=ORANGE):
    d.line((start, end), fill=BLACK, width=11)
    d.line((start, end), fill=colour, width=6)


def underside(what, theme):
    """The whole underside with its landmarks, and one thing ringed."""
    from PIL import Image

    photo = Image.open(SRC / "pi5-underside.jpg").convert("RGB")
    im, d = band(photo, 150, theme)
    for xy, text in (((874, 110), "GPIO header"), ((70, 290), "USB-A"), ((871, 880), "micro-HDMI ×2"),
                     ((1215, 795), "USB-C power"), ((520, 770), "CE mark")):
        label(d, xy, text, 24)
    if what == "pads":
        ring(d, (690, 664, 824, 760), 9)
        leader(d, (757, 760), (757, 935))
        note(d, (700, 975), "TP14 and TP1: the two pads marked FLASH WP", 40, words(theme, "orange"))
        note(d, (700, 1030), "right of the CE mark, above the two micro-HDMI sockets", 30, words(theme))
    else:
        ring(d, (1150, 330, 1362, 540), 9)
        # a microSD card, drawn, on its way into the slot from the board's edge
        d.rounded_rectangle((1372, 372, 1398, 498), radius=6, fill=(40, 40, 40), outline=WHITE, width=3)
        leader(d, (1256, 540), (1256, 935))
        note(d, (700, 975), "microSD slot: push the card in from the edge of the board,", 38, words(theme, "orange"))
        note(d, (700, 1030), "gold contacts facing the board, until it stops", 38, words(theme, "orange"))
        d.rounded_rectangle((722, 696, 792, 728), radius=16, fill=SILVER, outline=BLACK, width=3)
        ring(d, (690, 664, 824, 760), 6, WHITE)
        leader(d, (690, 712), (560, 712), WHITE)
        label(d, (555, 712), "the bridge stays on (drawn)", 26, WHITE, "rm")
    return im


def closeup(what, theme):
    from PIL import Image

    photo = Image.open(SRC / "pi5-flash-wp-closeup.jpg").convert("RGB")
    photo = photo.resize((photo.width * 2, photo.height * 2), Image.LANCZOS)
    im, d = band(photo, 190, theme)
    tp14, tp1, tp17 = (826, 456), (1006, 456), (650, 356)  # pad centres, in the doubled picture
    y0 = photo.height
    good, bad, plain = words(theme, "good"), words(theme, "bad"), words(theme)

    def blob(points, colour):
        """Solder, drawn: a rounded shape through the given pad centres."""
        xs, ys = [q[0] for q in points], [q[1] for q in points]
        for q in points:
            d.ellipse((q[0] - 78, q[1] - 70, q[0] + 78, q[1] + 70), fill=SILVER)
        d.line(points, fill=SILVER, width=110)
        for q in points:
            d.ellipse((q[0] - 78, q[1] - 70, q[0] + 78, q[1] + 70), outline=colour, width=7)
        d.line(points, fill=SILVER, width=96)
        d.ellipse((min(xs) + 20, min(ys) - 40, min(xs) + 70, min(ys) - 10), fill=WHITE)  # a highlight

    if what == "pads":
        for c, text, x in ((tp14, "TP14 (left): the flash chip's write-protect line", 480),
                           (tp1, "TP1 (right): power", 1400)):
            ring(d, (c[0] - 84, c[1] - 84, c[0] + 84, c[1] + 84), 8)
            leader(d, (c[0], c[1] + 84), (c[0], y0 + 30))
            note(d, (x, y0 + 70), text, 36, words(theme, "orange"))
        note(d, (900, y0 + 140), "The board prints TP14 TP1 above the pads and FLASH WP below them.", 32, plain)
    elif what == "bridged":
        blob([tp14, tp1], GREEN)
        note(d, (900, y0 + 60), "RIGHT: one blob of solder over TP14 and TP1, touching nothing else", 38, good)
        note(d, (900, y0 + 120), "(Without an iron: a wire or tweezers held on both pads.)", 30, plain)
        note(d, (900, y0 + 164), "A drawing on the photo.", 30, plain)
    elif what == "wrong":
        blob([tp17, tp14, tp1], RED)
        ring(d, (tp17[0] - 100, tp17[1] - 100, tp17[0] + 100, tp17[1] + 100), 10, RED)
        leader(d, (tp17[0] - 100, tp17[1]), (330, 120), RED)
        label(d, (330, 90), "TP17 is touched too", 40, RED)
        note(d, (900, y0 + 60), "WRONG: the solder also reaches TP17", 38, bad)
        note(d, (900, y0 + 120), "Take it off and make it again before any power goes on.", 30, plain)
        note(d, (900, y0 + 164), "A drawing on the photo.", 30, plain)
    elif what == "tweezers":
        for q in (tp14, tp1):  # two tips, one on each pad, meeting above the picture
            d.polygon([(q[0] - 16, q[1] + 10), (q[0] + 16, q[1] + 10), (916 + (q[0] - 916) // 6 + 26, 0),
                       (916 + (q[0] - 916) // 6 - 26, 0)], fill=SILVER, outline=BLACK)
        note(d, (900, y0 + 60), "Without an iron: one tip of the tweezers on each pad", 38, good)
        note(d, (900, y0 + 120), "Hold them there until the network cable comes out (step 5).", 30, plain)
        note(d, (900, y0 + 164), "A drawing on the photo.", 30, plain)
    else:  # clear: the pads separate again
        for c in (tp14, tp1):
            ring(d, (c[0] - 84, c[1] - 84, c[0] + 84, c[1] + 84), 8, GREEN)
        note(d, (900, y0 + 70), "Bridge off: TP14 and TP1 are two separate pads again,", 38, good)
        note(d, (900, y0 + 130), "and no solder went anywhere else.", 38, good)
    return im


def photos():
    """Write every annotated photograph and its dark twin."""
    for name, (picture, what) in PHOTOS.items():
        for theme in THEMES:
            im = {"underside": underside, "closeup": closeup}[picture](what, theme)
            im.save(HERE / (name if theme == "light" else dark_name(name)), quality=88)


# ----------------------------------------------------------------------------------------------------------------
# The diagrams, each written twice: <name>.svg on white for the light theme and the printed booklet, and
# <name>-dark.svg on the dark theme's background (Furo's #131416). A diagram is drawn once with its colours as
# @@role@@ tokens; resolve() makes the two files from PALETTE, which differ only in their colours.
# ----------------------------------------------------------------------------------------------------------------
# role: (light, dark). The light values are the colours the diagrams were drawn in before there was a dark one.
PALETTE = {
    # the page, and what stands straight on it
    "paper": ("#ffffff", "#131416"),
    "ink": ("#111", "#e3e6ea"),
    "leader": ("#555", "#9aa1aa"),  # the dashed lines from the board to its enlarged corner
    "good": ("#1e8c3c", "#5fd27a"),  # DONE, RIGHT, plug in
    "bad": ("#c81e1e", "#ff7b7b"),  # NOT DONE, STOP, pull out
    "warn": ("#b8860b", "#e0b040"),  # the edge of a "do this first" box
    "warn-text": ("#8a6500", "#f0c45c"),
    "alert": ("#b00", "#ff7b7b"),  # the red words under the DIP switches
    "note-text": ("#7a5a00", "#e8c66a"),
    "callout-1": ("#22a022", "#6fdc6f"),  # the words naming part 1, 2, 3 of the blade, in the parts' colours
    "callout-2": ("#c2188f", "#ff6fd0"),
    "callout-3": ("#c81e1e", "#ff7b7b"),
    # boxes on the page: pale on white, dark tints of the same colour on the dark page
    "box": ("#ffffff", "#202328"),
    "surface": ("#f4f4f4", "#24272c"),
    "surface-plain": ("#eef3f8", "#1c2631"),
    "good-fill": ("#e2f3e2", "#15301b"),
    "bad-fill": ("#fde3e3", "#3d1c1c"),
    "warn-fill": ("#fff3d6", "#382c10"),
    "note-fill": ("#fffbe6", "#2b2714"),
    "switch": ("#e9ecef", "#2c3036"),  # the DIP switch's body, the network cable's plug
    "switch-text": ("#333", "#c4c9d0"),
    # the boards, drawn: they keep their colours on both pages, and so does what is on them
    "board": ("#1f4e8c", "#1f4e8c"),
    "pi-board": ("#2e7d32", "#2e7d32"),
    "part": ("#c9d3df", "#c9d3df"),
    "part-wp": ("#dfe9f5", "#dfe9f5"),
    "part-module": ("#3b6fb5", "#3b6fb5"),
    "part-dip": ("#ffe9a8", "#ffe9a8"),
    "part-dip-edge": ("#b8860b", "#b8860b"),
    "part-1": ("#d9f7d9", "#d9f7d9"),
    "part-1-edge": ("#22a022", "#22a022"),
    "part-2": ("#f7d9f1", "#f7d9f1"),
    "part-2-edge": ("#c2188f", "#c2188f"),
    "part-3": ("#f7d9d9", "#f7d9d9"),
    "part-3-edge": ("#c81e1e", "#c81e1e"),
    "part-edge": ("#111", "#111"),
    "on-part": ("#111", "#111"),
    "on-board": ("#fff", "#fff"),  # white on a board or on the module
    "board-mark": ("#fff", "#fff"),  # the dashed box round the enlarged corner, on the board
    "lever-on": ("#b00", "#b00"),  # the DIP lever of switch 1, and of the others
    "lever": ("#666", "#666"),
    "on-lever": ("#fff", "#fff"),
}
TOKEN = re.compile(r"@@([a-z0-9-]+)@@")
PAINT = re.compile(r'\b(?:fill|stroke)="(?!none"|@@[a-z0-9-]+@@")([^"]*)"')
TEXT_ON_PAPER, TEXT_SMALL = 7.0, 4.5  # the contrast text must reach on the dark page, on the page and on a box
SVG = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
       'font-family="DejaVu Sans, Arial, sans-serif">\n<rect width="{w}" height="{h}" fill="@@paper@@"/>\n{body}</svg>\n')
DRAWINGS = {}  # name: the diagram, with its colours as tokens
TEXTS = []  # (diagram, words, colour role, role of what they stand on): checked for contrast


def c(name):
    """The token of a colour role."""
    if name not in PALETTE:
        raise KeyError(f"no colour role {name!r} in PALETTE")
    return f"@@{name}@@"


def resolve(svg, theme):
    """The diagram's SVG for theme "light" or "dark". Any colour that is not a token stops it."""
    stray = PAINT.findall(svg)
    if stray:
        raise SystemExit(f"make_figures: colours outside PALETTE: {sorted(set(stray))}")
    if re.search(r"<text(?![^>]*\bfill=)", svg):
        raise SystemExit("make_figures: a <text> with no fill would be black on the dark page")
    k = ("light", "dark").index(theme)
    return TOKEN.sub(lambda m: PALETTE[m.group(1)][k], svg)


def luminance(colour):
    h = colour.lstrip("#")
    h = "".join(ch * 2 for ch in h) if len(h) == 3 else h
    lin = [(v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4) for v in (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contrast(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def contrast_errors(theme="dark"):
    """Text short of TEXT_ON_PAPER straight on the page, or of TEXT_SMALL on a box, on the page of theme."""
    k = ("light", "dark").index(theme)
    errors = []
    for name, words, fill, on in TEXTS:
        ratio = contrast(PALETTE[fill][k], PALETTE[on][k])
        need = TEXT_ON_PAPER if on == "paper" else TEXT_SMALL
        if ratio < need:
            errors.append(f"{name} ({theme}): {words!r}, {fill} on {on}: {ratio:.2f}, under {need}")
    return errors


def dark_name(name):
    """kit.svg -> kit-dark.svg, pi5-flash-wp-clear.jpg -> pi5-flash-wp-clear-dark.jpg."""
    stem, _, ext = name.rpartition(".")
    return f"{stem}-dark.{ext}"


def box(body, x, y, w, h, fill="surface", stroke="ink", width=2, rx=8):
    body.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{c(fill)}" stroke="{c(stroke)}" stroke-width="{width}"/>')


def text(body, x, y, t, size=20, weight="normal", fill="ink", anchor="start", mono=False, on="paper", space=False):
    """Words at (x, y). on: the colour role of what they stand on, for the contrast check."""
    family = ' font-family="DejaVu Sans Mono, monospace"' if mono else ""
    keep = ' xml:space="preserve"' if space else ""
    body.append(f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{c(fill)}" text-anchor="{anchor}"{family}{keep}>{t}</text>')
    TEXTS.append((None, t, fill, on))


def write(name, w, h, body):
    for i, (who, *rest) in enumerate(TEXTS):
        if who is None:
            TEXTS[i] = (name, *rest)
    DRAWINGS[name] = SVG.format(w=w, h=h, body="\n".join(body) + "\n")


def sr1_bits():
    """Status register 1 of the boot flash, bit 7 on the left, locked (0xbc) above unlocked (0x00)."""
    names = ["SRP", "SEC", "TB", "BP2", "BP1", "BP0", "WEL", "BUSY"]
    body = []
    text(body, 20, 34, "Status register 1 of the boot flash (Winbond W25Q16)", 22, "bold")
    for row, (value, title, colour) in enumerate(((0xBC, "locked: reads 0xbc", "bad-fill"),
                                                  (0x00, "not locked: reads 0x00", "good-fill"))):
        y = 70 + row * 150
        text(body, 20, y + 20, title, 20, "bold")
        for i, name in enumerate(names):
            bit = (value >> (7 - i)) & 1
            x = 20 + i * 110
            fill = colour if bit else "surface"
            box(body, x, y + 32, 104, 70, fill, "ink", 1, 0)
            text(body, x + 52, y + 60, f"bit {7 - i}: {name}", 17, anchor="middle", on=fill)
            text(body, x + 52, y + 92, bit, 26, "bold", anchor="middle", on=fill)
    text(body, 20, 366, "SRP = 1: the register itself is protected while /WP is low.", 19)
    text(body, 20, 390, "TB = 1 with BP2 BP1 BP0 = 111: the whole chip is protected.", 19)
    write("sr1-bits.svg", 910, 430, body)


def dip():
    """The Dev blade's three DIP switches as the maker's table gives them."""
    rows = [("1", "Write protection", "Disabled", "Enabled"), ("2", "Wi-Fi", "Enabled", "Disabled"),
            ("3", "Bluetooth", "Enabled", "Disabled")]
    body = []
    text(body, 20, 34, "Dev model Compute Blade: the DIP switches", 24, "bold")
    text(body, 420, 76, "LEFT", 20, "bold", "ink", "middle")
    text(body, 660, 76, "RIGHT", 20, "bold", "ink", "middle")
    for i, (n, what, left, right) in enumerate(rows):
        y = 92 + i * 74
        text(body, 20, y + 36, f"{n}  {what}", 21, "bold")
        box(body, 300, y, 480, 56, "switch", "ink", 2, 10)
        lever = "lever-on" if i == 0 else "lever"
        box(body, 308, y + 7, 224, 42, lever, "ink", 0, 7)
        text(body, 420, y + 35, left, 20, "bold", "on-lever", "middle", on=lever)
        text(body, 660, y + 35, right, 20, "normal", "switch-text", "middle", on="switch")
    text(body, 20, 338, "Switch 1 at LEFT for a bootloader upgrade: that is our reading of the", 19, "bold", "alert")
    text(body, 20, 364, "two makers' documents. Untested by us.", 19, "bold", "alert")
    text(body, 20, 400, "Drawn with every switch at LEFT. Which way is left on the board is the", 18)
    text(body, 20, 424, "maker's wording; we have not held one. The maker: change switch", 18)
    text(body, 20, 448, "positions only when the blade is unplugged from power.", 18)
    write("blade-dip.svg", 800, 470, body)


def blade():
    """A Dev model Compute Blade, in outline, with the three parts a USB bootloader flash needs."""
    body = []
    text(body, 20, 32, "Compute Blade, Dev model, component side (drawn from the maker's picture)", 24, "bold")
    box(body, 20, 70, 1160, 230, "board", "ink", 2, 14)

    def part(x, y, w, h, words, fill="part", size=15, edge=None, on="on-part"):
        box(body, x, y, w, h, fill, edge or "part-edge", 5 if edge else 1.5, 5)
        lines = words.split("\n")
        for k, line in enumerate(lines):
            text(body, x + w / 2, y + h / 2 + size * 0.35 + (k - (len(lines) - 1) / 2) * (size + 4), line, size,
                 fill=on, anchor="middle", on=fill)

    part(30, 190, 110, 100, "Ethernet\n(PoE)", size=17)
    part(150, 84, 44, 44, "DIP", "part-dip", 15, "part-dip-edge")
    part(205, 84, 60, 90, "HDMI", size=17)
    part(150, 232, 110, 58, "WP WL BT\n(printed)", "part-wp", 13)
    part(275, 84, 200, 206, "Compute Module\n(under its\nconnectors)", "part-module", 17, on="on-board")
    part(500, 84, 80, 80, "SD card", size=17)
    part(590, 118, 80, 46, "USB-A", size=17)
    part(690, 84, 44, 110, "M.2", size=17)
    part(760, 84, 400, 100, "M.2 SSD positions", "part-module", 17, on="on-board")
    part(760, 205, 110, 80, "Extension\nPort", size=17)
    part(880, 205, 46, 80, "UART", size=14)
    part(945, 215, 78, 62, "1", "part-1", 26, "part-1-edge")
    part(1040, 196, 110, 36, "2", "part-2", 24, "part-2-edge")
    part(1052, 240, 62, 52, "3", "part-3", 24, "part-3-edge")
    # the corner with the three parts, enlarged
    body.append(f'<rect x="932" y="186" width="232" height="112" fill="none" stroke="{c("board-mark")}" stroke-width="3" stroke-dasharray="8 6"/>')
    body.append(f'<path d="M932 298 L30 350 M1164 298 L650 350" stroke="{c("leader")}" stroke-width="2" stroke-dasharray="6 6" fill="none"/>')
    box(body, 30, 350, 620, 290, "board", "ink", 2, 10)
    part(60, 420, 210, 170, "1\nUSB Type-C\nport", "part-1", 26, "part-1-edge")
    part(320, 372, 300, 96, "2\nUSB switch", "part-2", 26, "part-2-edge")
    part(350, 496, 170, 130, "3\nnRPIBOOT\nbutton", "part-3", 26, "part-3-edge")
    for y, words, colour in ((385, "1  USB Type-C port: the cable to the", "callout-1"),
                             (411, "    computer that runs rpiboot", "callout-1"),
                             (455, "2  USB switch: moved to the", "callout-2"), (481, "    USB Type-C position", "callout-2"),
                             (525, "3  nRPIBOOT button: held down while", "callout-3"),
                             (551, "    the cable is connected", "callout-3"),
                             (600, "DIP (top left, beside HDMI): 1 write", "warn-text"),
                             (626, "    protection, 2 Wi-Fi, 3 Bluetooth", "warn-text")):
        text(body, 680, y, words, 22, "bold", colour, space=True)
    text(body, 30, 682, "How to tell a Dev model: it has the USB Type-C socket and, beside it,", 22, "bold")
    text(body, 30, 710, "the small nRPIBOOT button.", 22, "bold")
    text(body, 30, 744, "A drawing from documentation, not from a board in hand: positions are approximate.", 19)
    write("blade-dev.svg", 1200, 764, body)


def check_card(name, verdicts):
    """The three things to read, each with the wanted value beside what is not wanted."""
    body = []
    text(body, 20, 36, "Is this Pi 5 done? Three reads, three answers", 26, "bold")
    text(body, 500, 80, "DONE", 22, "bold", "good", "middle")
    text(body, 800, 80, "NOT DONE", 22, "bold", "bad", "middle")
    rows = [("1  bootloader date", "first line of", "vcgencmd bootloader_version", "2026/09/25 ...", "an older date"),
            ("2  boot order", "the BOOT_ORDER line of", "vcgencmd bootloader_config", "BOOT_ORDER=0xf2", "anything else"),
            ("3  flash lock", "the SR1 line of the script", "sudo python3 read_flash_status.py", "SR1 0xbc", "SR1 0x0")]
    for i, (title, where, cmd, good, bad) in enumerate(rows):
        y = 100 + i * 110
        text(body, 20, y + 36, title, 22, "bold")
        text(body, 20, y + 62, where, 16)
        text(body, 20, y + 84, cmd, 15, mono=True)
        box(body, 370, y + 12, 260, 76, "good-fill", "good", 3)
        text(body, 500, y + 58, good, 22, "bold", "ink", "middle", True, on="good-fill")
        box(body, 670, y + 12, 260, 76, "bad-fill", "bad", 3)
        text(body, 800, y + 58, bad, 22, "bold", "ink", "middle", True, on="bad-fill")
    y = 458
    for line, weight, colour in verdicts:
        text(body, 20, y, line, 19, weight, colour)
        y += 27
    write(name, 950, y + 4, body)


def boot_order(name, rows, title):
    """BOOT_ORDER read from its last digit."""
    body = []
    text(body, 20, 36, title, 26, "bold")
    names = {"1": "SD card", "2": "network", "4": "USB", "6": "NVMe", "f": "start again"}
    nth = {1: "tried 1st", 2: "tried 2nd", 3: "tried 3rd", 4: "tried 4th"}
    for row, (value, caption, colour) in enumerate(rows):
        y = 70 + row * 150
        text(body, 20, y + 22, caption, 21, "bold")
        n = len(value)
        for i, digit in enumerate(value):
            x = 20 + i * 184
            box(body, x, y + 36, 174, 84, colour)
            text(body, x + 87, y + 72, digit, 30, "bold", "ink", "middle", True, on=colour)
            text(body, x + 87, y + 104, names[digit] + (": then" if digit == "f" else ": " + nth[n - i]),
                 17, "normal", "ink", "middle", on=colour)
    write(name, 950, 80 + len(rows) * 150, body)


def kit():
    body = []
    text(body, 20, 36, "What you need on the bench", 26, "bold")
    items = [("1  The Pi 5", "out of its case, underside reachable"),
             ("2  A microSD card", "any size; everything on it is erased"),
             ("3  A Linux computer", "card reader, internet, git, python3, sha256sum"),
             ("4  A soldering iron and solder", "OR fine tweezers or a short wire to hold"),
             ("5  Desoldering braid", "if you solder: to take the bridge off again"),
             ("6  The Pi's own network cable", "on its switch port; it also powers the Pi"),
             ("7  A multimeter", "optional: to check the bridge")]
    for i, (title, what) in enumerate(items):
        y = 60 + i * 62
        box(body, 20, y, 910, 52, "surface-plain")
        text(body, 36, y + 33, title, 21, "bold", on="surface-plain")
        text(body, 420, y + 33, what, 18, on="surface-plain")
    write("kit.svg", 950, 504, body)


def card_files():
    body = []
    text(body, 20, 36, "The finished card: these four files at the top level, nothing else", 26, "bold")
    box(body, 20, 60, 910, 250, "note-fill", "warn", 3)
    text(body, 40, 92, "microSD card (one FAT32 partition)", 18, "bold", "note-text", on="note-fill")
    files = [("recovery.bin", "104314 bytes", "the program the Pi runs from the card"),
             ("pieeprom.bin", "2097152 bytes", "the 2026/09/25 bootloader with the fleet's settings"),
             ("pieeprom.sig", "80 bytes", "the checksum of pieeprom.bin"),
             ("config.txt", "23 bytes", "one line: eeprom_write_protect=0")]
    for i, (name, size, what) in enumerate(files):
        y = 112 + i * 48
        box(body, 40, y, 870, 40, "box", "ink", 1.5, 5)
        text(body, 56, y + 27, name, 19, "bold", mono=True, on="box")
        text(body, 250, y + 27, size, 17, mono=True, on="box")
        text(body, 430, y + 27, what, 17, on="box")
    write("card-files.svg", 950, 330, body)


def cable(name, title, plug_in, lines):
    """A Pi 5 from above, in outline, with its network cable going in or coming out."""
    body = []
    text(body, 20, 36, title, 26, "bold")
    box(body, 60, 70, 420, 270, "pi-board", "ink", 3, 14)
    text(body, 225, 190, "Raspberry Pi 5", 19, "bold", "on-board", "middle", on="pi-board")
    text(body, 225, 216, "top side up (the side with", 15, "normal", "on-board", "middle", on="pi-board")
    text(body, 225, 236, "the sockets and the header)", 15, "normal", "on-board", "middle", on="pi-board")
    box(body, 390, 250, 110, 76, "part", "part-edge")
    text(body, 445, 294, "Ethernet", 16, "bold", "on-part", "middle", on="part")
    for y in (90, 168):
        box(body, 400, y, 100, 64, "part", "part-edge")
        text(body, 450, y + 38, "USB", 15, "normal", "on-part", "middle", on="part")
    box(body, 70, 300, 70, 34, "part", "part-edge")
    text(body, 105, 322, "USB-C", 13, "normal", "on-part", "middle", on="part")
    colour = "good" if plug_in else "bad"
    x0 = 520 if plug_in else 600
    box(body, x0, 264, 150, 48, "switch", colour, 4)
    text(body, x0 + 75, 295, "network cable", 16, "bold", "ink", "middle", on="switch")
    arrow = f"M{x0 + 150 + 120} 288 L{x0 + 150 + 20} 288" if plug_in else f"M{x0 + 150 + 20} 288 L{x0 + 150 + 120} 288"
    tip = x0 + 150 + 20 if plug_in else x0 + 150 + 120
    d = -1 if plug_in else 1
    body.append(f'<path d="{arrow}" stroke="{c(colour)}" stroke-width="8" fill="none"/>')
    body.append(f'<path d="M{tip} 288 l{-d * 22} -14 l0 28 z" fill="{c(colour)}"/>')
    for k, line in enumerate(lines):
        text(body, 520, 100 + k * 30, line, 19, "bold" if k == 0 else "normal", colour if k == 0 else "ink")
    write(name, 950, 360, body)


def outcomes():
    """What step 6 can read, and what to do for each."""
    body = []
    text(body, 20, 36, "Step 6: your result. Take the FIRST row that fits.", 26, "bold")
    rows = [("good-fill", "good", ["2026/09/25, BOOT_ORDER=0xf2", "and SR1 0xbc"],
             ["DONE. The Pi is back in service.", "Keep the card for the next Pi."]),
            ("bad-fill", "bad", ["an older date", "(whatever the rest says)"],
             ["Nothing was written. Go back to step 2. Check that the", "bridge is on both pads and the card holds the four files."]),
            ("bad-fill", "bad", ["2026/09/25, but BOOT_ORDER", "is not 0xf2"],
             ["The card's boot.conf was wrong. Make the card again", "(step 1, and check what it prints), then from step 2."]),
            ("warn-fill", "warn", ["2026/09/25 and 0xf2,", "but SR1 0x0"],
             ["Not locked. Pull the network cable, plug it in again on", "the Pi's normal port, wait 2 minutes, read again.", "Still 0x0: unplug the Pi and tell whoever runs the site."]),
            ("bad-fill", "bad", ["no answer: the Pi is not back", "on the network after 5 minutes"],
             ["Go back to step 2, with a card whose pieeprom.bin you", "have checked prints BOOT_ORDER=0xf2 (step 1)."])]
    for i, (fill, stroke, read, do) in enumerate(rows):
        y = 60 + i * 114
        box(body, 20, y, 340, 100, fill, stroke, 3)
        for k, line in enumerate(read):
            text(body, 190, y + 43 + k * 28, line, 19, "bold", "ink", "middle", on=fill)
        body.append(f'<path d="M364 {y + 50} L396 {y + 50}" stroke="{c("ink")}" stroke-width="4"/>')
        body.append(f'<path d="M408 {y + 50} l-16 -10 l0 20 z" fill="{c("ink")}"/>')
        box(body, 412, y, 568, 100, "box", "ink", 2)
        top = y + (43 if len(do) == 2 else 32)
        for k, line in enumerate(do):
            text(body, 426, top + k * 27, line, 19, on="box")
    write("outcomes.svg", 1000, 640, body)


def diagrams():
    """{file name: diagram with tokens} for every diagram; fails if any text is short of its contrast."""
    DRAWINGS.clear()
    TEXTS.clear()
    sr1_bits()
    dip()
    blade()
    stop = [("A NEWER date, another SR1 value, or a jedec line that is not ef4015:", "bold", "bad"),
            ("STOP. This page does not cover that Pi; change nothing on it.", "bold", "bad")]
    check_card("check-card.svg", [
        ("All three DONE: nothing to do.", "bold", "good"),
        ("Date or boot order NOT DONE: upgrade it (next part).", "bold", "ink"),
        ("ONLY the lock NOT DONE (SR1 0x0): do NOT upgrade. Pull the network cable,", "bold", "warn-text"),
        ("plug it in again on the Pi's normal port, wait 2 minutes, read again.", "bold", "warn-text"),
        ("Still 0x0: unplug the Pi and tell whoever runs the site.", "bold", "warn-text")] + stop)
    check_card("check-card-after.svg", [
        ("All three DONE: finished.", "bold", "good"),
        ("Anything else: the chart at the end of this step.", "bold", "ink")] + stop)
    boot_order("boot-order.svg", (("f2", "0xf2: the fleet's Pi 5 setting. Network only.", "good-fill"),
                                  ("f12", "0xf12: network, then an SD card. Not the fleet's.", "bad-fill"),
                                  ("f2461", "0xf2461: SD card, NVMe, USB, then network. Not the fleet's.", "bad-fill")),
               "Reading BOOT_ORDER: start at the LAST digit and go left")
    boot_order("boot-order-blade.svg",
               (("f2461", "0xf2461: SD card, NVMe, USB, then the network (the 2), then round again.", "surface-plain"),),
               "This blade's BOOT_ORDER, read from the LAST digit")
    kit()
    card_files()
    cable("cable-out.svg", "Pull the network cable: the Pi is now off", False,
          ["Network cable OUT", "The Pi gets its power over this", "cable from the switch (PoE).", "If a USB-C supply is fitted,",
           "pull that too."])
    cable("cable-in.svg", "Plug the network cable in: the Pi is now on", True,
          ["Network cable IN", "Same switch port as before.", "The Pi starts by itself."])
    outcomes()
    errors = contrast_errors()
    if errors:
        raise SystemExit("make_figures: text without enough contrast on the dark page:\n  " + "\n  ".join(errors))
    return dict(DRAWINGS)


def files():
    """{file name: contents} of every diagram, light and dark."""
    out = {}
    for name, svg in diagrams().items():
        out[name] = resolve(svg, "light")
        out[dark_name(name)] = resolve(svg, "dark")
    return out


def main(argv):
    if "--no-photos" not in argv:  # the annotated photographs, light and dark
        photos()
    for name, svg in files().items():
        (HERE / name).write_text(svg)
    print("figures written to", HERE)


if __name__ == "__main__":
    main(sys.argv[1:])
