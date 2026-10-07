#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Only the code in a table's message column (its header one of MESSAGE_HEADERS) is marked message-code and may
wrap at its spaces; every other code span in a table, however long, stays on one line (docs/_ext/table_code.py).

Run: python -m unittest discover -s tools -p 'test_*.py'
"""

import re
import sys
import unittest
from pathlib import Path

try:
    from docutils import nodes
except ImportError:  # the extension runs inside Sphinx: without docutils (pip install -r docs/requirements.txt)
    raise unittest.SkipTest("needs docutils, from docs/requirements.txt")

DOCS = Path(__file__).resolve().parent.parent / "docs"
sys.path.insert(0, str(DOCS / "_ext"))
import table_code  # noqa: E402

MESSAGE = "jtag fail: device DNA over P1 JTAG reads 0x0: the DNA port is not being read"
COMMAND = "sudo fpgas-acorn-verify --no-publish --test p2-serial"


def code(text: str) -> nodes.literal:
    return nodes.literal(text, text)


def cell(*children: nodes.Node) -> nodes.entry:
    return nodes.entry("", nodes.paragraph("", "", *children))


def table(header: list[nodes.entry], *rows: list[nodes.entry], classes: tuple[str, ...] = ()) -> nodes.table:
    head = nodes.thead("", nodes.row("", *header))
    body = nodes.tbody("", *(nodes.row("", *row) for row in rows))
    return nodes.table("", nodes.tgroup("", head, body), classes=list(classes))


def marked(node: nodes.Node) -> list[str]:
    return [lit.astext() for lit in node.findall(nodes.literal) if "message-code" in lit["classes"]]


class MessageColumn(unittest.TestCase):
    def test_the_message_column_is_marked_and_the_other_is_not(self):
        t = table([cell(nodes.Text("The failing line")), cell(nodes.Text("Look at"))],
                  [cell(code(MESSAGE)), cell(code(COMMAND))])
        table_code.mark_message_code(t)
        self.assertEqual(marked(t), [MESSAGE])

    def test_a_word_without_a_space_is_not_marked(self):
        t = table([cell(nodes.Text("It says")), cell(nodes.Text("Meaning"))],
                  [cell(code("0x1ffffffffffffff"), nodes.Text(" or "), code("no device found")), cell()])
        table_code.mark_message_code(t)
        self.assertEqual(marked(t), ["no device found"])

    def test_code_inside_a_link_is_marked(self):
        link = nodes.reference("", "", code(MESSAGE), refuri="#x")
        t = table([cell(nodes.Text("It says")), cell(nodes.Text("Meaning"))], [cell(link), cell()])
        table_code.mark_message_code(t)
        self.assertEqual(marked(t), [MESSAGE])

    def test_code_in_a_header_cell_is_not_marked(self):
        t = table([cell(nodes.Text("It says")), cell(code("rpi-hwid labels --this-host"))], [cell(), cell()])
        table_code.mark_message_code(t)
        self.assertEqual(marked(t), [])

    def test_a_nowrap_table_is_not_marked(self):
        t = table([cell(nodes.Text("It says"))], [cell(code(MESSAGE))], classes=("nowrap",))
        table_code.mark_message_code(t)
        self.assertEqual(marked(t), [])

    def test_a_long_command_is_not_marked_unless_its_table_opts_in(self):
        t = table([cell(nodes.Text("Command")), cell(nodes.Text("Does"))], [cell(code(COMMAND)), cell(code(MESSAGE))])
        table_code.mark_message_code(t)
        self.assertEqual(marked(t), [])

    def test_a_table_without_a_header_is_not_marked(self):
        t = nodes.table("", nodes.tgroup("", nodes.tbody("", nodes.row("", cell(code(MESSAGE))))))
        table_code.mark_message_code(t)
        self.assertEqual(marked(t), [])

    def test_a_spanned_cell_in_a_message_table_is_refused(self):
        spanned = cell(code(MESSAGE))
        spanned["morecols"] = 1
        t = table([cell(nodes.Text("It says")), cell(nodes.Text("Meaning"))], [spanned])
        with self.assertRaises(ValueError):
            table_code.mark_message_code(t)


class HeadersAreStillOnTheSite(unittest.TestCase):
    """A renamed column would quietly go back to one line: each header must still head a Markdown table."""

    def test_each_message_header_heads_a_table(self):
        headers = set()
        for page in DOCS.rglob("*.md"):
            if "superpowers" in page.parts or "_build" in page.parts:
                continue
            lines = page.read_text(encoding="utf-8").splitlines()
            for line, below in zip(lines, lines[1:]):
                if line.startswith("|") and re.fullmatch(r"\|(\s*:?-+:?\s*\|)+", below.strip()):
                    headers.update(h.strip() for h in line.strip().strip("|").split("|"))
        self.assertEqual(table_code.MESSAGE_HEADERS - headers, set())


if __name__ == "__main__":
    unittest.main()
