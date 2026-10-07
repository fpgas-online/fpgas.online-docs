# SPDX-License-Identifier: Apache-2.0
"""Lets the code in a table's message column wrap at its spaces: a column whose header is one of
MESSAGE_HEADERS holds what a check prints (a failure message, a log line), and every code span in its cells
with a space in it gets the class `message-code` (docs/_static/custom.css, "Tables").

Every other code span in a table (a command, an address, a DNA, a pin list, a label) is kept on one line, so
wrapping is opt-in by column, never guessed from the code. A failing line on "verifying 2" is a whole message
in code, up to a hundred characters and more, and kept on one line it took the whole width of the page and
crushed the column beside it to a word per line.

The headers are matched exactly. tools/test_table_code.py checks that each is still a header on the site, so
a renamed column fails the tests instead of quietly going back to one line."""

from docutils import nodes

# A column with one of these headers holds messages that a check prints, and nothing else in code that must
# stay whole. "The failing line": verifying 2 (generated in fpgas.online-test-designs). "It says": verifying 2b
# and the common failures page. "What the check does": the Tiny Tapeout check's variants.
MESSAGE_HEADERS = frozenset({"The failing line", "It says", "What the check does"})


def message_columns(table: nodes.table) -> set[int]:
    """The indexes of the table's columns whose header is one of MESSAGE_HEADERS."""
    head = next(table.findall(nodes.thead), None)
    if head is None:
        return set()
    columns = set()
    for row in head.findall(nodes.row):
        for index, entry in enumerate(c for c in row.children if isinstance(c, nodes.entry)):
            if entry.astext().strip() in MESSAGE_HEADERS:
                columns.add(index)
    return columns


def mark_message_code(table: nodes.table) -> None:
    """Mark each code span with a space in it in the table's message columns as message-code."""
    if "nowrap" in table["classes"]:
        return
    columns = message_columns(table)
    if not columns:
        return
    for entry in table.findall(nodes.entry):
        if entry.get("morecols") or entry.get("morerows"):
            # a spanned cell shifts every column after it: the index would name the wrong column
            raise ValueError(f"a table with a message column has a spanned cell: {entry.astext()[:60]!r}")
    for body in table.findall(nodes.tbody):
        for row in body.findall(nodes.row):
            cells = [c for c in row.children if isinstance(c, nodes.entry)]
            for index in columns:
                for literal in cells[index].findall(nodes.literal):
                    if any(c.isspace() for c in literal.astext()):
                        literal["classes"].append("message-code")


def _mark(app, doctree, docname):
    for table in doctree.findall(nodes.table):
        mark_message_code(table)


def setup(app):
    app.connect("doctree-resolved", _mark)
    return {"parallel_read_safe": True, "parallel_write_safe": True}
