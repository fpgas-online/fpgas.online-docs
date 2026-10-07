# SPDX-License-Identifier: Apache-2.0
"""Marks a long code span in a table cell, one that is a sentence rather than a name, with the class
`long-code`, so that the stylesheet (docs/_static/custom.css, "Tables") lets it wrap at its spaces.

Every other code span in a cell (an address, a DNA, a pin list, a short command) is kept on one line there. A
failing line on "verifying 2" is a whole message in code, up to a hundred characters and more, and kept on
one line it took the whole width of the page and crushed the column beside it to a word per line."""

from docutils import nodes

# A code span longer than this, with a space in it, may wrap at its spaces. The same limit as WHOLE_CODE in
# tools/print_pages.py. At 40, on a phone (390 px) a 39-character failing line ("pcie-link fail: link is x2,
# expected x1") still took the width and left the column beside it a word wide.
LONG_CODE = 24


def is_long_code(text: str) -> bool:
    """Whether a code span in a table cell may wrap at its spaces."""
    return len(text) > LONG_CODE and any(c.isspace() for c in text)


def _mark_long_code(app, doctree, docname):
    for entry in doctree.findall(nodes.entry):
        for literal in entry.findall(nodes.literal):
            if is_long_code(literal.astext()):
                literal["classes"].append("long-code")


def setup(app):
    app.connect("doctree-resolved", _mark_long_code)
    return {"parallel_read_safe": True, "parallel_write_safe": True}
