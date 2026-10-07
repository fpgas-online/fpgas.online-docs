#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Tests for sync_mechanical.py that need no network."""

import pathlib
import re
import unittest

import sync_mechanical as m

DOCS = pathlib.Path(__file__).resolve().parent.parent / "docs"


class Mechanical(unittest.TestCase):
    def test_every_drawing_comes_light_and_dark_and_every_picture_as_png(self):
        names = [name for _, name in m.files()]
        self.assertEqual(len(names), len(set(names)))
        for stem, exts in ((s, e) for _, stems in m.DRAWINGS for s, e in stems.items()):
            self.assertIn("png", exts)
            for theme in ("light", "dark"):
                for ext in exts:
                    self.assertIn(f"{stem}-{theme}.{ext}", names)

    def test_the_copies_and_the_pinned_commit_are_here(self):
        self.assertRegex(m.pinned(), r"^[0-9a-f]{40}$")
        for _, name in m.files():
            self.assertTrue((m.DEST / name).is_file(), name)

    def test_every_page_that_shows_a_drawing_shows_it_in_both_themes(self):
        for page in DOCS.rglob("*.md"):
            text = page.read_text(encoding="utf-8")
            for stem in set(re.findall(r"_static/mechanical/([a-z0-9-]+)-(?:light|dark)\.(?:svg|png)", text)):
                self.assertIn(f"{stem}-light", text, page)
                self.assertIn(f"{stem}-dark", text, page)
                self.assertEqual(text.count(":class: only-light"), text.count(":class: only-dark"), page)


if __name__ == "__main__":
    unittest.main()
