#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Every drawing and every annotated photograph on the site has a dark twin, and every page shows the light one in
the light theme and the dark one in the dark theme (Furo's only-light / only-dark classes). A plain photograph is
the same in both.

Run: python -m unittest discover -s tools -p 'test_*.py'
"""

import importlib.util
import re
import unittest
from pathlib import Path

import sync_test_designs as sync

DOCS = Path(__file__).resolve().parent.parent / "docs"
FIGURES = DOCS / "setup" / "bootloader-eeprom"
DRAWING = (".png", ".svg")
# ![alt](src){attrs}, or the same image inside a link: [![alt](src)](target){attrs}
MARKDOWN_IMAGE = re.compile(
    r"(?P<link>\[)?!\[(?P<alt>[^\]]*)\]\((?P<src>[^)\s]+)\)(?P<attrs>\{[^}]*\})?"
    r"(?(link)\]\((?P<target>[^)\s]+)\)(?P<link_attrs>\{[^}]*\})?)"
)
# the image or figure directive, with its options; the class of a figure is its figclass
DIRECTIVE = re.compile(r"^ *```\{(?P<kind>image|figure)\} (?P<src>\S+)\n(?P<options>(?: *:[^\n]*\n)*)", re.M)
THEME_OPTION = re.compile(r"^ *:(?:fig)?class: (only-light|only-dark)\n", re.M)
# An example written out in a page (a block fenced with four backticks, around the directive's own three).
EXAMPLE = re.compile(r"^````.*?^````\n", re.M | re.S)
# A picture written in prose as code, to show how it is done.
CODE_SPAN = re.compile(r"`[^`\n]+`")


def dark(name):
    """The dark twin's name: x.svg -> x-dark.svg; a drawing copied in as x-light.svg -> x-dark.svg."""
    stem, _, ext = name.rpartition(".")
    return f"{stem.removesuffix('-light')}-dark.{ext}"


def is_dark(name):
    return name.rpartition(".")[0].endswith("-dark")


def pages():
    for path in sorted(DOCS.rglob("*")):
        if path.suffix in (".md", ".inc") and "_build" not in path.parts and "superpowers" not in path.parts:
            yield path


def load_figures():
    spec = importlib.util.spec_from_file_location("make_figures", FIGURES / "make_figures.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def annotated():
    """The annotated photographs make_figures.py writes: each has a dark twin, as a drawing does."""
    return set(load_figures().PHOTOS)


def needs_twin(src):
    return src.endswith(DRAWING) or Path(src).name in annotated()


def shown(page):
    """(src, theme class or None, where) of every picture on a page; a linked picture's class is its link's."""
    text = CODE_SPAN.sub("", EXAMPLE.sub("", page.read_text()))
    out = []
    for m in MARKDOWN_IMAGE.finditer(text):
        if m["link"] and m["attrs"]:
            out.append((m["src"], "on the image, not its link", m))  # the hidden link would stay focusable
            continue
        attrs = m["link_attrs"] if m["link"] else m["attrs"]
        out.append((m["src"], (attrs or "").strip("{}.") or None, m))
    for m in DIRECTIVE.finditer(text):
        theme = THEME_OPTION.search(m["options"])
        if m["kind"] == "figure" and re.search(r":class: only-", m["options"]):
            out.append((m["src"], "class on a figure's image, not :figclass:", m))
            continue
        out.append((m["src"], theme[1] if theme else None, m))
    return out


class EveryPicture(unittest.TestCase):
    def test_every_drawing_and_annotated_photo_is_shown_as_a_light_and_dark_pair(self):
        checked = 0
        for page in pages():
            pictures = shown(page)
            for src, theme, m in pictures:
                if not needs_twin(src.replace("-dark.", ".")):
                    self.assertIsNone(theme, f"{page}: {src} is a photograph, the same in both themes")
                    continue
                if is_dark(src):
                    self.assertEqual(theme, "only-dark", f"{page}: {src}")
                    continue
                checked += 1
                self.assertEqual(theme, "only-light", f"{page}: {src} is shown in both themes")
                # its twin: the next picture of that name after it
                twins = sorted((t for t in pictures if t[0] == dark(src) and t[2].start() > m.start()), key=lambda t: t[2].start())
                self.assertTrue(twins, f"{page}: {src} has no dark twin shown")
                where = DOCS / dark(src).lstrip("/") if src.startswith("/") else page.parent / dark(src)
                self.assertTrue(where.exists(), f"{page}: {dark(src)} is missing")
                twin = twins[0][2]
                if "kind" in m.groupdict():  # a directive: the same options but the class
                    same = twin["options"].replace("only-dark", "only-light")
                    if "-light." in src:  # a pair named -light / -dark: its target is the matching twin
                        same = same.replace("-dark.", "-light.")
                    self.assertEqual(same, m["options"], f"{page}: {src}")
                else:  # Markdown: the same words, a linked picture links its own twin
                    self.assertEqual(twin["alt"], m["alt"], f"{page}: {src}")
                    if m["link"]:
                        self.assertEqual(twin["target"], dark(m["target"]), f"{page}: {src}")
        self.assertGreater(checked, 40)

    def test_every_figure_make_figures_writes_has_its_twin_and_is_shown_with_it(self):
        figures = load_figures()
        written = [*figures.PHOTOS, *(n for n in figures.files() if not is_dark(n))]
        on_pages = "".join(page.read_text() for page in pages())
        for name in written:
            self.assertTrue((FIGURES / dark(name)).exists(), f"{dark(name)}: run make_figures.py")
            if f"bootloader-eeprom/{name}" in on_pages:
                self.assertIn(f"bootloader-eeprom/{dark(name)}", on_pages, f"{name} is shown without its twin")


class SyncedDrawings(unittest.TestCase):
    def test_every_drawing_taken_from_test_designs_comes_with_its_dark_twin(self):
        for dest, (_src, names) in sync.FILES.items():
            for name in names:
                if name.endswith(DRAWING) and not name.removesuffix(name[-4:]).endswith("-dark"):
                    self.assertIn(dark(name), names, f"{dest}: {name}")

    def test_every_picture_a_taken_page_shows_is_taken_too(self):
        for dest, (_src, names) in sync.FILES.items():
            for name in names:
                if name.endswith(".md"):
                    text = (DOCS.parent / dest / name).read_text()
                    for src in (m["src"] for m in MARKDOWN_IMAGE.finditer(text)):
                        self.assertIn(src, names, f"{dest}/{name} shows {src}, which the sync does not take")


class BootloaderFigures(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.figures = load_figures()
        cls.files = cls.figures.files()

    def test_the_committed_figures_are_what_make_figures_writes(self):
        for name, svg in self.files.items():
            self.assertEqual((FIGURES / name).read_text(), svg, f"{name}: run make_figures.py --no-photos")

    def test_every_diagram_has_a_dark_twin_on_the_dark_background(self):
        light = [n for n in self.files if not n.endswith("-dark.svg")]
        self.assertEqual(len(light), 12)
        for name in light:
            twin = self.files[dark(name)]
            self.assertIn('fill="#131416"/>', twin.split("\n")[1], name)  # the page: Furo's dark background
            # the same drawing: only the colours differ
            paint = re.compile(r'\b(fill|stroke)="[^"]*"')
            self.assertEqual(paint.sub("", self.files[name]), paint.sub("", twin), name)

    def test_text_reaches_its_contrast_on_the_dark_page(self):
        self.assertEqual(self.figures.contrast_errors("dark"), [])
        for role in ("ink", "good", "bad", "warn-text", "alert", "note-text", "callout-1", "callout-2", "callout-3"):
            ratio = self.figures.contrast(self.figures.PALETTE[role][1], self.figures.PALETTE["paper"][1])
            self.assertGreaterEqual(ratio, self.figures.TEXT_ON_PAPER, role)

    def test_a_colour_outside_the_palette_stops_it(self):
        with self.assertRaises(SystemExit):
            self.figures.resolve('<rect fill="#123456"/>', "dark")
        with self.assertRaises(SystemExit):
            self.figures.resolve('<text x="1" y="1">no fill</text>', "dark")
        with self.assertRaises(KeyError):
            self.figures.c("no-such-role")


if __name__ == "__main__":
    unittest.main()
