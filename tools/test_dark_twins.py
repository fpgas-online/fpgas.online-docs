#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Every drawing on the site has a dark twin, and every page shows the light one in the light theme and the
dark one in the dark theme (Furo's only-light / only-dark classes). Photographs (JPEG) are the same in both.

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
# ![alt](src){attrs}, and the image directive with its options
MARKDOWN_IMAGE = re.compile(r"!\[([^\]]*)\]\(([^)\s]+)\)(\{[^}]*\})?")
DIRECTIVE = re.compile(r"```\{(?:image|figure)\} (\S+)\n((?::[^\n]*\n)*)")
# An example written out in a page (a block fenced with four backticks, around the directive's own three).
EXAMPLE = re.compile(r"^````.*?^````\n", re.M | re.S)


def dark(name):
    stem, _, ext = name.rpartition(".")
    return f"{stem}-dark.{ext}"


def pages():
    for path in sorted(DOCS.rglob("*")):
        if path.suffix in (".md", ".inc") and "_build" not in path.parts and "superpowers" not in path.parts:
            yield path


def load_figures():
    spec = importlib.util.spec_from_file_location("make_figures", FIGURES / "make_figures.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class EveryPicture(unittest.TestCase):
    def test_every_drawing_in_markdown_is_a_light_and_dark_pair(self):
        checked = 0
        for page in pages():
            text = EXAMPLE.sub("", page.read_text())
            found = MARKDOWN_IMAGE.findall(text)
            drawings = [f for f in found if f[1].endswith(DRAWING)]
            for alt, src, attrs in drawings:
                if src.removesuffix(Path(src).suffix).endswith("-dark"):
                    self.assertEqual(attrs, "{.only-dark}", f"{page}: {src}")
                    continue
                checked += 1
                self.assertEqual(attrs, "{.only-light}", f"{page}: {src} is shown in both themes")
                self.assertIn((alt, dark(src), "{.only-dark}"), drawings, f"{page}: {src} has no dark twin shown")
                self.assertTrue((page.parent / dark(src)).exists(), f"{page}: {dark(src)} is missing")
        self.assertGreater(checked, 20)

    def test_every_drawing_in_an_image_directive_is_a_light_and_dark_pair(self):
        checked = 0
        for page in pages():
            blocks = DIRECTIVE.findall(EXAMPLE.sub("", page.read_text()))
            for src, options in blocks:
                if not src.endswith(DRAWING):
                    self.assertNotIn(":class: only-", options, f"{page}: {src} is a photograph, the same in both")
                    continue
                if src.removesuffix(Path(src).suffix).endswith("-dark"):
                    self.assertIn(":class: only-dark\n", options, f"{page}: {src}")
                    continue
                checked += 1
                self.assertIn(":class: only-light\n", options, f"{page}: {src} is shown in both themes")
                twin = [o for s, o in blocks if s == dark(src)]
                self.assertTrue(twin, f"{page}: {src} has no dark twin shown")
                self.assertEqual(twin[0].replace("only-dark", "only-light"), options, f"{page}: {src}: options differ")
                self.assertTrue((page.parent / dark(src)).exists(), f"{page}: {dark(src)} is missing")
        self.assertGreater(checked, 10)


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
                    for _alt, src, _attrs in MARKDOWN_IMAGE.findall(text):
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
