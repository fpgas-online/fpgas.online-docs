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


def underside(name, what):
    """The whole underside with its landmarks, and one thing ringed."""
    im = Image.open(SRC / "pi5-underside.jpg").convert("RGB")
    d = ImageDraw.Draw(im)
    for xy, text in (((874, 110), "GPIO header"), ((70, 290), "USB-A"), ((871, 880), "micro-HDMI ×2"),
                     ((1215, 795), "USB-C power"), ((520, 760), "CE mark")):
        label(d, xy, text, 24)
    if what == "pads":
        ring(d, (700, 678, 812, 748))
        d.line((756, 678, 756, 610), fill=BLACK, width=12)
        d.line((756, 678, 756, 610), fill=ORANGE, width=6)
        label(d, (756, 585), "TP14 and TP1: the two FLASH WP pads", 34, ORANGE)
        label(d, (1262, 300), "microSD slot", 24)
    else:
        ring(d, (1150, 330, 1362, 540))
        d.line((1150, 435, 1020, 435), fill=BLACK, width=12)
        d.line((1150, 435, 1020, 435), fill=ORANGE, width=6)
        label(d, (1010, 435), "microSD slot: the card goes in here,", 30, ORANGE, "rm")
        label(d, (1010, 475), "contacts towards the board", 30, ORANGE, "rm")
        ring(d, (700, 678, 812, 748), 4, WHITE)
        label(d, (756, 640), "bridge still fitted", 24)
    im.save(HERE / name, quality=88)


def closeup(name, bridged):
    im = Image.open(SRC / "pi5-flash-wp-closeup.jpg").convert("RGB")
    im = im.resize((im.width * 2, im.height * 2), Image.LANCZOS)
    d = ImageDraw.Draw(im)
    tp14, tp1 = (826, 456), (1006, 456)  # pad centres, in the doubled picture
    if bridged:
        d.rounded_rectangle((tp14[0] - 34, tp14[1] - 30, tp1[0] + 34, tp1[1] + 30), radius=30,
                            fill=SILVER, outline=BLACK, width=6)
        label(d, (916, 660), "the bridge (drawn on the photo): a blob of solder, or a wire", 34, ORANGE)
        label(d, (916, 706), "or tweezers held across both pads while the Pi is powered", 34, ORANGE)
        d.line((916, 636, 916, 492), fill=BLACK, width=12)
        d.line((916, 636, 916, 492), fill=ORANGE, width=6)
    else:
        for c, text, x in ((tp14, "TP14: the flash chip's /WP", 500), (tp1, "TP1: 3.3 V", 1330)):
            ring(d, (c[0] - 84, c[1] - 84, c[0] + 84, c[1] + 84), 8)
            label(d, (x, 690), text, 38, ORANGE)
            d.line((x, 664, c[0], c[1] + 84), fill=BLACK, width=12)
            d.line((x, 664, c[0], c[1] + 84), fill=ORANGE, width=6)
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
    body.append('<text x="20" y="366" font-size="17">SRP = 1: the register itself is protected while /WP is low.</text>')
    body.append('<text x="20" y="390" font-size="17">TB = 1 with BP2 BP1 BP0 = 111: the whole chip is protected.</text>')
    body.append('<text x="20" y="414" font-size="17">WEL and BUSY are 0 at rest. Status register 2 reads 0x02 either way (QE = 1).</text>')
    (HERE / "sr1-bits.svg").write_text(SVG.format(w=910, h=430, body="\n".join(body) + "\n"))


def dip():
    """The Dev blade's three DIP switches as the maker's table gives them."""
    rows = [("1", "Write protection", "Disabled", "Enabled", "left for a bootloader upgrade"),
            ("2", "Wi-Fi", "Enabled", "Disabled", ""), ("3", "Bluetooth", "Enabled", "Disabled", "")]
    body = ['<text x="20" y="32" font-size="22" font-weight="bold">Compute Blade, Dev model: the DIP switches (from the maker\'s table)</text>',
            '<text x="330" y="70" font-size="18" font-weight="bold" text-anchor="middle">LEFT</text>',
            '<text x="530" y="70" font-size="18" font-weight="bold" text-anchor="middle">RIGHT</text>']
    for i, (n, what, left, right, note) in enumerate(rows):
        y = 90 + i * 74
        body.append(f'<text x="20" y="{y + 36}" font-size="19"><tspan font-weight="bold">{n}</tspan>  {what}</text>')
        body.append(f'<rect x="250" y="{y}" width="360" height="56" rx="10" fill="#e9ecef" stroke="#111" stroke-width="2"/>')
        knob_x = 258 if i == 0 else 258
        body.append(f'<rect x="{knob_x}" y="{y + 7}" width="150" height="42" rx="7" fill="{"#b00" if i == 0 else "#666"}"/>')
        body.append(f'<text x="330" y="{y + 35}" font-size="18" fill="#fff" text-anchor="middle" font-weight="bold">{left}</text>')
        body.append(f'<text x="530" y="{y + 35}" font-size="18" fill="#333" text-anchor="middle">{right}</text>')
        if note:
            body.append(f'<text x="630" y="{y + 35}" font-size="17" fill="#b00" font-weight="bold">{note}</text>')
    body.append('<text x="20" y="330" font-size="16">Drawn with every switch at LEFT. Which way is "left" on the board is the maker\'s wording; we have not held one.</text>')
    body.append('<text x="20" y="354" font-size="16">The maker: "Only change switch positions when the Blade is unplugged from power."</text>')
    (HERE / "blade-dip.svg").write_text(SVG.format(w=920, h=370, body="\n".join(body) + "\n"))


def blade():
    """A Dev model Compute Blade, in outline, with the three parts a USB bootloader flash needs."""
    body = ['<text x="20" y="32" font-size="22" font-weight="bold">Compute Blade, Dev model, seen from the component side (drawn from the maker\'s picture)</text>',
            '<rect x="20" y="70" width="1160" height="230" rx="14" fill="#1f4e8c" stroke="#111" stroke-width="2"/>']

    def part(x, y, w, h, text, fill="#c9d3df", size=15, colour=None):
        body.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5" fill="{fill}" stroke="{colour or "#111"}" stroke-width="{5 if colour else 1.5}"/>')
        for k, line in enumerate(text.split("\n")):
            body.append(f'<text x="{x + w / 2}" y="{y + h / 2 + 5 + (k - (text.count(chr(10))) / 2) * (size + 3)}" font-size="{size}" text-anchor="middle">{line}</text>')

    part(30, 190, 110, 100, "Ethernet\n(PoE)")
    part(150, 84, 44, 44, "DIP", "#ffe9a8", 14, "#b8860b")
    part(205, 84, 60, 90, "HDMI")
    part(275, 84, 200, 206, "Compute Module\n(underneath its\nconnectors)", "#3b6fb5")
    part(500, 84, 80, 80, "SD card")
    part(590, 118, 80, 46, "USB-A")
    part(690, 84, 44, 110, "M.2")
    part(760, 84, 400, 100, "M.2 SSD positions (2230 to 22110)", "#3b6fb5")
    part(760, 205, 110, 80, "Extension\nPort")
    part(880, 205, 46, 80, "UART")
    part(945, 215, 78, 62, "USB-C", "#d9f7d9", 16, "#22a022")
    part(1040, 196, 110, 36, "USB switch", "#f7d9f1", 14, "#c2188f")
    part(1052, 244, 50, 46, "nRPI\nBOOT", "#f7d9d9", 13, "#c81e1e")
    for x, y, tx, ty, text, colour in ((984, 277, 470, 345, "1. USB Type-C port: the cable to the computer that runs rpiboot", "#22a022"),
                                       (1095, 196, 470, 371, "2. USB switch: moved to the USB Type-C position", "#c2188f"),
                                       (1077, 290, 470, 397, "3. nRPIBOOT button: held down while the cable is connected", "#c81e1e"),
                                       (172, 128, 30, 345, "DIP: 1 write protection, 2 Wi-Fi, 3 Bluetooth", "#b8860b")):
        body.append(f'<text x="{tx}" y="{ty}" font-size="17" fill="{colour}" font-weight="bold">{text}</text>')
    body.append('<text x="30" y="371" font-size="15">A drawing from documentation, not from a board</text>')
    body.append('<text x="30" y="391" font-size="15">in hand: positions are approximate.</text>')
    body.append('<text x="30" y="411" font-size="15">Only the Dev model has these parts.</text>')
    (HERE / "blade-dev.svg").write_text(SVG.format(w=1200, h=425, body="\n".join(body) + "\n"))


underside("pi5-underside-flash-wp.jpg", "pads")
underside("pi5-underside-sd-slot.jpg", "sd")
closeup("pi5-flash-wp-closeup.jpg", False)
closeup("pi5-flash-wp-bridged.jpg", True)
sr1_bits()
dip()
blade()
print("figures written to", HERE)
