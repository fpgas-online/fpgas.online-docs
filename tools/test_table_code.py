#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""A long code span with spaces in a table cell is marked long-code and may wrap at its spaces; every other one
(an address, a DNA, a pin list, a short command) stays on one line (docs/_ext/table_code.py).

Run: python -m unittest discover -s tools -p 'test_*.py'
"""

import sys
import unittest
from pathlib import Path

try:
    from docutils import nodes
except ImportError:  # the extension runs inside Sphinx: without docutils (pip install -r docs/requirements.txt)
    raise unittest.SkipTest("needs docutils, from docs/requirements.txt")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "docs" / "_ext"))
import table_code  # noqa: E402


def table(*cells: str) -> nodes.document:
    """A document with one table row, one code span in each cell, and one code span outside the table."""
    doc = nodes.document(None, None)
    row = nodes.row()
    for text in cells:
        row += nodes.entry("", nodes.paragraph("", "", nodes.literal(text, text)))
    doc += nodes.table("", nodes.tgroup("", nodes.tbody("", row)))
    outside = "a long code span outside any table, which is left alone"
    doc += nodes.paragraph("", "", nodes.literal(outside, outside))
    return doc


def marked(doc: nodes.document) -> list[str]:
    return [lit.astext() for lit in doc.findall(nodes.literal) if "long-code" in lit["classes"]]


class LongCode(unittest.TestCase):
    def test_a_failing_line_is_marked(self):
        line = "jtag fail: device DNA over P1 JTAG reads 0x0: the DNA port is not being read"
        doc = table(line, "0x00200c8664b04854")
        table_code._mark_long_code(None, doc, "page")
        self.assertEqual(marked(doc), [line])

    def test_short_code_with_spaces_is_kept_whole(self):
        doc = table("sudo -n", "fpgas-acorn-debug identify"[: table_code.LONG_CODE])
        table_code._mark_long_code(None, doc, "page")
        self.assertEqual(marked(doc), [])

    def test_long_code_without_a_space_is_kept_whole(self):
        doc = table("/usr/share/fpgas-online/arty/bitstreams/")
        table_code._mark_long_code(None, doc, "page")
        self.assertEqual(marked(doc), [])

    def test_the_limit(self):
        self.assertFalse(table_code.is_long_code("a" * (table_code.LONG_CODE - 2) + " b"))
        self.assertTrue(table_code.is_long_code("a" * (table_code.LONG_CODE - 1) + " b"))


if __name__ == "__main__":
    unittest.main()
