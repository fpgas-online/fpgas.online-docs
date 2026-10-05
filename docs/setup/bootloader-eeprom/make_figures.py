# SPDX-License-Identifier: Apache-2.0
"""Draw the figures of the bootloader EEPROM page.

    uv run --no-project --with pillow docs/setup/bootloader-eeprom/make_figures.py

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

from PIL import Image, ImageDraw, ImageFont

HERE = pathlib.Path(__file__).parent
SRC = HERE / "source"
ORANGE, WHITE, BLACK, SILVER = (232, 112, 42), (255, 255, 255), (0, 0, 0), (214, 218, 222)
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(size):
    return ImageFont.truetype(FONT, size)


def label(d, xy, text, size=26, fill=WHITE, anchor="mm"):
    d.text(xy, text, font=font(size), fill=fill, anchor=anchor, stroke_width=4, stroke_fill=BLACK)


def ring(d, box, width=7, colour=ORANGE):
    d.ellipse(box, outline=BLACK, width=width + 6)
    d.ellipse(box, outline=colour, width=width)


def band(im, height):
    """The picture with a white band under it for the labels, and a draw handle."""
    out = Image.new("RGB", (im.width, im.height + height), WHITE)
    out.paste(im, (0, 0))
    return out, ImageDraw.Draw(out)


def note(d, xy, text, size=30, fill=BLACK, anchor="mm"):
    d.text(xy, text, font=font(size), fill=fill, anchor=anchor)


def leader(d, start, end, colour=ORANGE):
    d.line((start, end), fill=BLACK, width=11)
    d.line((start, end), fill=colour, width=6)


GREEN, RED = (30, 140, 60), (200, 30, 30)


def underside(name, what):
    """The whole underside with its landmarks, and one thing ringed."""
    photo = Image.open(SRC / "pi5-underside.jpg").convert("RGB")
    im, d = band(photo, 150)
    for xy, text in (((874, 110), "GPIO header"), ((70, 290), "USB-A"), ((871, 880), "micro-HDMI ×2"),
                     ((1215, 795), "USB-C power"), ((520, 770), "CE mark")):
        label(d, xy, text, 24)
    if what == "pads":
        ring(d, (690, 664, 824, 760), 9)
        leader(d, (757, 760), (757, 935))
        note(d, (700, 975), "TP14 and TP1: the two pads marked FLASH WP", 40, ORANGE)
        note(d, (700, 1030), "right of the CE mark, above the two micro-HDMI sockets", 30)
    else:
        ring(d, (1150, 330, 1362, 540), 9)
        # a microSD card, drawn, on its way into the slot from the board's edge
        d.rounded_rectangle((1372, 372, 1398, 498), radius=6, fill=(40, 40, 40), outline=WHITE, width=3)
        leader(d, (1256, 540), (1256, 935))
        note(d, (700, 975), "microSD slot: push the card in from the edge of the board,", 38, ORANGE)
        note(d, (700, 1030), "gold contacts facing the board, until it stops", 38, ORANGE)
        d.rounded_rectangle((722, 696, 792, 728), radius=16, fill=SILVER, outline=BLACK, width=3)
        ring(d, (690, 664, 824, 760), 6, WHITE)
        leader(d, (690, 712), (560, 712), WHITE)
        label(d, (555, 712), "the bridge stays on (drawn)", 26, WHITE, "rm")
    im.save(HERE / name, quality=88)


def closeup(name, what):
    photo = Image.open(SRC / "pi5-flash-wp-closeup.jpg").convert("RGB")
    photo = photo.resize((photo.width * 2, photo.height * 2), Image.LANCZOS)
    im, d = band(photo, 190)
    tp14, tp1, tp17 = (826, 456), (1006, 456), (650, 356)  # pad centres, in the doubled picture
    y0 = photo.height

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
            note(d, (x, y0 + 70), text, 36, ORANGE)
        note(d, (900, y0 + 140), "The board prints TP14 TP1 above the pads and FLASH WP below them.", 32)
    elif what == "bridged":
        blob([tp14, tp1], GREEN)
        note(d, (900, y0 + 60), "RIGHT: one blob of solder over TP14 and TP1, touching nothing else", 38, GREEN)
        note(d, (900, y0 + 120), "(Without an iron: a wire or tweezers held on both pads.)", 30)
        note(d, (900, y0 + 164), "A drawing on the photo.", 30)
    elif what == "wrong":
        blob([tp17, tp14, tp1], RED)
        ring(d, (tp17[0] - 100, tp17[1] - 100, tp17[0] + 100, tp17[1] + 100), 10, RED)
        leader(d, (tp17[0] - 100, tp17[1]), (330, 120), RED)
        label(d, (330, 90), "TP17 is touched too", 40, RED)
        note(d, (900, y0 + 60), "WRONG: the solder also reaches TP17", 38, RED)
        note(d, (900, y0 + 120), "Take it off and make it again before any power goes on.", 30)
        note(d, (900, y0 + 164), "A drawing on the photo.", 30)
    elif what == "tweezers":
        for q in (tp14, tp1):  # two tips, one on each pad, meeting above the picture
            d.polygon([(q[0] - 16, q[1] + 10), (q[0] + 16, q[1] + 10), (916 + (q[0] - 916) // 6 + 26, 0),
                       (916 + (q[0] - 916) // 6 - 26, 0)], fill=SILVER, outline=BLACK)
        note(d, (900, y0 + 60), "Without an iron: one tip of the tweezers on each pad", 38, GREEN)
        note(d, (900, y0 + 120), "Hold them there for the whole 60 seconds of step 4.", 30)
        note(d, (900, y0 + 164), "A drawing on the photo.", 30)
    else:  # clear: the pads separate again
        for c in (tp14, tp1):
            ring(d, (c[0] - 84, c[1] - 84, c[0] + 84, c[1] + 84), 8, GREEN)
        note(d, (900, y0 + 70), "Bridge off: TP14 and TP1 are two separate pads again,", 38, GREEN)
        note(d, (900, y0 + 130), "and no solder went anywhere else.", 38, GREEN)
    im.save(HERE / name, quality=88)


SVG = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
       'font-family="DejaVu Sans, Arial, sans-serif">\n<rect width="{w}" height="{h}" fill="#ffffff"/>\n{body}</svg>\n')


def sr1_bits():
    """Status register 1 of the boot flash, bit 7 on the left, locked (0xbc) above unlocked (0x00)."""
    names = ["SRP", "SEC", "TB", "BP2", "BP1", "BP0", "WEL", "BUSY"]
    body = ['<text x="20" y="34" font-size="22" font-weight="bold">Status register 1 of the boot flash (Winbond W25Q16)</text>']
    for row, (value, title, colour) in enumerate(((0xBC, "locked: reads 0xbc", "#fde3e3"),
                                                  (0x00, "not locked: reads 0x00", "#e2f3e2"))):
        y = 70 + row * 150
        body.append(f'<text x="20" y="{y + 20}" font-size="20" font-weight="bold">{title}</text>')
        for i, name in enumerate(names):
            bit = (value >> (7 - i)) & 1
            x = 20 + i * 110
            body.append(f'<rect x="{x}" y="{y + 32}" width="104" height="70" fill="{colour if bit else "#f4f4f4"}" stroke="#111"/>')
            body.append(f'<text x="{x + 52}" y="{y + 60}" font-size="17" text-anchor="middle">bit {7 - i}: {name}</text>')
            body.append(f'<text x="{x + 52}" y="{y + 92}" font-size="26" font-weight="bold" text-anchor="middle">{bit}</text>')
    body.append('<text x="20" y="366" font-size="19">SRP = 1: the register itself is protected while /WP is low.</text>')
    body.append('<text x="20" y="390" font-size="19">TB = 1 with BP2 BP1 BP0 = 111: the whole chip is protected.</text>')
    (HERE / "sr1-bits.svg").write_text(SVG.format(w=910, h=430, body="\n".join(body) + "\n"))


def dip():
    """The Dev blade's three DIP switches as the maker's table gives them."""
    rows = [("1", "Write protection", "Disabled", "Enabled"), ("2", "Wi-Fi", "Enabled", "Disabled"),
            ("3", "Bluetooth", "Enabled", "Disabled")]
    body = []
    text(body, 20, 34, "Dev model Compute Blade: the DIP switches", 24, "bold")
    text(body, 420, 76, "LEFT", 20, "bold", "#111", "middle")
    text(body, 660, 76, "RIGHT", 20, "bold", "#111", "middle")
    for i, (n, what, left, right) in enumerate(rows):
        y = 92 + i * 74
        text(body, 20, y + 36, f"{n}  {what}", 21, "bold")
        box(body, 300, y, 480, 56, "#e9ecef", "#111", 2, 10)
        box(body, 308, y + 7, 224, 42, "#b00" if i == 0 else "#666", "#111", 0, 7)
        text(body, 420, y + 35, left, 20, "bold", "#fff", "middle")
        text(body, 660, y + 35, right, 20, "normal", "#333", "middle")
    text(body, 20, 338, "Switch 1 at LEFT for a bootloader upgrade: that is our reading of the", 19, "bold", "#b00")
    text(body, 20, 364, "two makers' documents. Untested by us.", 19, "bold", "#b00")
    text(body, 20, 400, "Drawn with every switch at LEFT. Which way is left on the board is the", 18)
    text(body, 20, 424, "maker's wording; we have not held one. The maker: change switch", 18)
    text(body, 20, 448, "positions only when the blade is unplugged from power.", 18)
    write("blade-dip.svg", 800, 470, body)


def blade():
    """A Dev model Compute Blade, in outline, with the three parts a USB bootloader flash needs."""
    body = ['<text x="20" y="32" font-size="24" font-weight="bold">Compute Blade, Dev model, component side (drawn from the maker\'s picture)</text>',
            '<rect x="20" y="70" width="1160" height="230" rx="14" fill="#1f4e8c" stroke="#111" stroke-width="2"/>']

    def part(x, y, w, h, text, fill="#c9d3df", size=15, colour=None):
        body.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5" fill="{fill}" stroke="{colour or "#111"}" stroke-width="{5 if colour else 1.5}"/>')
        lines = text.split("\n")
        for k, line in enumerate(lines):
            body.append(f'<text x="{x + w / 2}" y="{y + h / 2 + size * 0.35 + (k - (len(lines) - 1) / 2) * (size + 4)}" font-size="{size}" text-anchor="middle">{line}</text>')

    part(30, 190, 110, 100, "Ethernet\n(PoE)", size=17)
    part(150, 84, 44, 44, "DIP", "#ffe9a8", 15, "#b8860b")
    part(205, 84, 60, 90, "HDMI", size=17)
    part(150, 232, 110, 58, "WP WL BT\n(printed)", "#dfe9f5", 13)
    part(275, 84, 200, 206, "Compute Module\n(under its\nconnectors)", "#3b6fb5", 17)
    part(500, 84, 80, 80, "SD card", size=17)
    part(590, 118, 80, 46, "USB-A", size=17)
    part(690, 84, 44, 110, "M.2", size=17)
    part(760, 84, 400, 100, "M.2 SSD positions", "#3b6fb5", 17)
    part(760, 205, 110, 80, "Extension\nPort", size=17)
    part(880, 205, 46, 80, "UART", size=14)
    part(945, 215, 78, 62, "1", "#d9f7d9", 26, "#22a022")
    part(1040, 196, 110, 36, "2", "#f7d9f1", 24, "#c2188f")
    part(1052, 240, 62, 52, "3", "#f7d9d9", 24, "#c81e1e")
    # the corner with the three parts, enlarged
    body.append('<rect x="932" y="186" width="232" height="112" fill="none" stroke="#fff" stroke-width="3" stroke-dasharray="8 6"/>')
    body.append('<path d="M932 298 L30 350 M1164 298 L650 350" stroke="#555" stroke-width="2" stroke-dasharray="6 6" fill="none"/>')
    body.append('<rect x="30" y="350" width="620" height="290" rx="10" fill="#1f4e8c" stroke="#111" stroke-width="2"/>')
    part(60, 420, 210, 170, "1\nUSB Type-C\nport", "#d9f7d9", 26, "#22a022")
    part(320, 372, 300, 96, "2\nUSB switch", "#f7d9f1", 26, "#c2188f")
    part(350, 496, 170, 130, "3\nnRPIBOOT\nbutton", "#f7d9d9", 26, "#c81e1e")
    for y, text, colour in ((385, "1  USB Type-C port: the cable to the", "#22a022"), (411, "    computer that runs rpiboot", "#22a022"),
                            (455, "2  USB switch: moved to the", "#c2188f"), (481, "    USB Type-C position", "#c2188f"),
                            (525, "3  nRPIBOOT button: held down while", "#c81e1e"), (551, "    the cable is connected", "#c81e1e"),
                            (600, "DIP (top left, beside HDMI): 1 write", "#8a6500"), (626, "    protection, 2 Wi-Fi, 3 Bluetooth", "#8a6500")):
        body.append(f'<text x="680" y="{y}" font-size="22" fill="{colour}" font-weight="bold" xml:space="preserve">{text}</text>')
    body.append('<text x="30" y="682" font-size="22" font-weight="bold">How to tell a Dev model: it has the USB Type-C socket and, beside it,</text>')
    body.append('<text x="30" y="710" font-size="22" font-weight="bold">the small nRPIBOOT button.</text>')
    body.append('<text x="30" y="744" font-size="19">A drawing from documentation, not from a board in hand: positions are approximate.</text>')
    (HERE / "blade-dev.svg").write_text(SVG.format(w=1200, h=764, body="\n".join(body) + "\n"))


def box(body, x, y, w, h, fill="#f4f4f4", stroke="#111", width=2, rx=8):
    body.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"/>')


def text(body, x, y, t, size=20, weight="normal", fill="#111", anchor="start", mono=False):
    family = ' font-family="DejaVu Sans Mono, monospace"' if mono else ""
    body.append(f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}"{family}>{t}</text>')


def write(name, w, h, body):
    (HERE / name).write_text(SVG.format(w=w, h=h, body="\n".join(body) + "\n"))


def check_card(name, verdict):
    """The three things to read, each with the wanted value beside what is not wanted."""
    body = []
    text(body, 20, 36, "Is this Pi 5 done? Three reads, three answers", 26, "bold")
    text(body, 500, 80, "DONE", 22, "bold", "#1e8c3c", "middle")
    text(body, 800, 80, "NOT DONE", 22, "bold", "#c81e1e", "middle")
    rows = [("1  bootloader date", "first line of", "vcgencmd bootloader_version", "2026/09/25 ...", "an older date"),
            ("2  boot order", "the BOOT_ORDER line of", "vcgencmd bootloader_config", "BOOT_ORDER=0xf2", "anything else"),
            ("3  flash lock", "the SR1 line of", "sudo python3 read_flash_status.py", "SR1 0xbc", "SR1 0x0")]
    for i, (title, where, cmd, good, bad) in enumerate(rows):
        y = 100 + i * 110
        text(body, 20, y + 36, title, 22, "bold")
        text(body, 20, y + 62, where, 16)
        text(body, 20, y + 84, cmd, 15, mono=True)
        box(body, 370, y + 12, 260, 76, "#e2f3e2", "#1e8c3c", 3)
        text(body, 500, y + 58, good, 22, "bold", "#111", "middle", True)
        box(body, 670, y + 12, 260, 76, "#fde3e3", "#c81e1e", 3)
        text(body, 800, y + 58, bad, 22, "bold", "#111", "middle", True)
    text(body, 20, 456, verdict, 20, "bold")
    text(body, 20, 492, "A NEWER date, another SR1 value, or a jedec line that is not ef4015:", 18, "bold", "#c81e1e")
    text(body, 20, 518, "STOP. This page does not cover that Pi; change nothing on it.", 18, "bold", "#c81e1e")
    write(name, 950, 540, body)


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
            text(body, x + 87, y + 72, digit, 30, "bold", "#111", "middle", True)
            text(body, x + 87, y + 104, names[digit] + (": then" if digit == "f" else ": " + nth[n - i]),
                 17, "normal", "#111", "middle")
    write(name, 950, 80 + len(rows) * 150, body)


def kit():
    body = []
    text(body, 20, 36, "What you need on the bench", 26, "bold")
    items = [("1  The Pi 5", "out of its case, underside reachable"),
             ("2  A microSD card", "any size; everything on it is erased"),
             ("3  A Linux computer", "with a card reader, git, python3 and sha256sum"),
             ("4  A soldering iron and solder", "OR fine tweezers or a short wire to hold"),
             ("5  Desoldering braid", "if you solder: to take the bridge off again"),
             ("6  The Pi's own network cable", "on its switch port; it also powers the Pi"),
             ("7  A multimeter", "optional: to check the bridge")]
    for i, (title, what) in enumerate(items):
        y = 60 + i * 62
        box(body, 20, y, 910, 52, "#eef3f8")
        text(body, 36, y + 33, title, 21, "bold")
        text(body, 420, y + 33, what, 18)
    write("kit.svg", 950, 504, body)


def card_files():
    body = []
    text(body, 20, 36, "The finished card: these four files at the top level, nothing else", 26, "bold")
    box(body, 20, 60, 910, 250, "#fffbe6", "#b8860b", 3)
    text(body, 40, 92, "microSD card (one FAT32 partition)", 18, "bold", "#7a5a00")
    files = [("recovery.bin", "104314 bytes", "the program the Pi runs from the card"),
             ("pieeprom.bin", "2097152 bytes", "the 2026/09/25 bootloader with the fleet's settings"),
             ("pieeprom.sig", "80 bytes", "the checksum of pieeprom.bin"),
             ("config.txt", "23 bytes", "one line: eeprom_write_protect=0")]
    for i, (name, size, what) in enumerate(files):
        y = 112 + i * 48
        box(body, 40, y, 870, 40, "#ffffff", "#111", 1.5, 5)
        text(body, 56, y + 27, name, 19, "bold", mono=True)
        text(body, 250, y + 27, size, 17, mono=True)
        text(body, 430, y + 27, what, 17)
    write("card-files.svg", 950, 330, body)


def cable(name, title, plug_in, lines):
    """A Pi 5 from above, in outline, with its network cable going in or coming out."""
    body = []
    text(body, 20, 36, title, 26, "bold")
    box(body, 60, 70, 420, 270, "#2e7d32", "#111", 3, 14)
    text(body, 225, 190, "Raspberry Pi 5", 19, "bold", "#fff", "middle")
    text(body, 225, 216, "top side up (the side with", 15, "normal", "#fff", "middle")
    text(body, 225, 236, "the sockets and the header)", 15, "normal", "#fff", "middle")
    box(body, 390, 250, 110, 76, "#c9d3df")
    text(body, 445, 294, "Ethernet", 16, "bold", "#111", "middle")
    for k, y in enumerate((90, 168)):
        box(body, 400, y, 100, 64, "#c9d3df")
        text(body, 450, y + 38, "USB", 15, "normal", "#111", "middle")
    box(body, 70, 300, 70, 34, "#c9d3df")
    text(body, 105, 322, "USB-C", 13, "normal", "#111", "middle")
    colour = "#1e8c3c" if plug_in else "#c81e1e"
    x0 = 520 if plug_in else 600
    box(body, x0, 264, 150, 48, "#e9ecef", colour, 4)
    text(body, x0 + 75, 295, "network cable", 16, "bold", "#111", "middle")
    arrow = f"M{x0 + 150 + 120} 288 L{x0 + 150 + 20} 288" if plug_in else f"M{x0 + 150 + 20} 288 L{x0 + 150 + 120} 288"
    tip = x0 + 150 + 20 if plug_in else x0 + 150 + 120
    d = -1 if plug_in else 1
    body.append(f'<path d="{arrow}" stroke="{colour}" stroke-width="8" fill="none"/>')
    body.append(f'<path d="M{tip} 288 l{-d * 22} -14 l0 28 z" fill="{colour}"/>')
    for k, line in enumerate(lines):
        text(body, 520, 100 + k * 30, line, 19, "bold" if k == 0 else "normal", colour if k == 0 else "#111")
    write(name, 950, 360, body)


def outcomes():
    """What step 6 can read, and what to do for each."""
    body = []
    text(body, 20, 36, "Step 6: what you read, and what to do", 26, "bold")
    rows = [("#e2f3e2", "#1e8c3c", ["2026/09/25, BOOT_ORDER=0xf2", "and SR1 0xbc"],
             ["DONE. The Pi is back in service.", "Keep the card for the next Pi."]),
            ("#fde3e3", "#c81e1e", ["the old date", "and the old settings"],
             ["Nothing was written. Go back to step 2. Check that the", "bridge is on both pads and the card holds the four files."]),
            ("#fde3e3", "#c81e1e", ["2026/09/25, but BOOT_ORDER", "is not 0xf2"],
             ["The card's boot.conf was wrong. Make the card again", "(step 1, and check what it prints), then from step 2."]),
            ("#fff3d6", "#b8860b", ["2026/09/25 and 0xf2,", "but SR1 0x0"],
             ["Not locked. On a normal port, not an EEPROM service port?", "Cable out and in, 2 min, read again. Still 0x0: tell the operator."]),
            ("#fde3e3", "#c81e1e", ["no answer: the Pi is not back", "on the network after 5 minutes"],
             ["Go back to step 2, with a card whose pieeprom.bin you", "have checked prints BOOT_ORDER=0xf2 (step 1)."])]
    for i, (fill, stroke, read, do) in enumerate(rows):
        y = 60 + i * 104
        box(body, 20, y, 340, 90, fill, stroke, 3)
        for k, line in enumerate(read):
            text(body, 190, y + 38 + k * 28, line, 19, "bold", "#111", "middle")
        body.append(f'<path d="M364 {y + 45} L396 {y + 45}" stroke="#111" stroke-width="4"/>')
        body.append(f'<path d="M408 {y + 45} l-16 -10 l0 20 z" fill="#111"/>')
        box(body, 412, y, 548, 90, "#ffffff", "#111", 2)
        for k, line in enumerate(do):
            text(body, 426, y + 38 + k * 28, line, 19)
    write("outcomes.svg", 980, 600, body)


underside("pi5-underside-flash-wp.jpg", "pads")
underside("pi5-underside-sd-slot.jpg", "sd")
closeup("pi5-flash-wp-closeup.jpg", "pads")
closeup("pi5-flash-wp-bridged.jpg", "bridged")
closeup("pi5-flash-wp-wrong.jpg", "wrong")
closeup("pi5-flash-wp-tweezers.jpg", "tweezers")
closeup("pi5-flash-wp-clear.jpg", "clear")
sr1_bits()
dip()
blade()
check_card("check-card.svg", "All three DONE: nothing to do. Any NOT DONE: upgrade it (next part).")
check_card("check-card-after.svg", "All three DONE: finished. Anything else: the chart at the end of this step.")
FLEET, OTHER, PLAIN = "#e2f3e2", "#fde3e3", "#eef3f8"
boot_order("boot-order.svg", (("f2", "0xf2: the fleet's Pi 5 setting. Network only.", FLEET),
                              ("f12", "0xf12: network, then an SD card. Not the fleet's.", OTHER),
                              ("f2461", "0xf2461: SD card, NVMe, USB, then network. Not the fleet's.", OTHER)),
           "Reading BOOT_ORDER: start at the LAST digit and go left")
boot_order("boot-order-blade.svg", (("f2461", "0xf2461: SD card, NVMe, USB, then the network (the 2), then round again.", PLAIN),),
           "This blade's BOOT_ORDER, read from the LAST digit")
kit()
card_files()
cable("cable-out.svg", "Pull the network cable: the Pi is now off", False,
      ["Network cable OUT", "The Pi gets its power over this", "cable from the switch (PoE).", "If a USB-C supply is fitted,", "pull that too."])
cable("cable-in.svg", "Plug the network cable in: the Pi is now on", True,
      ["Network cable IN", "Same switch port as before.", "The Pi starts by itself."])
outcomes()
print("figures written to", HERE)
