# SPDX-License-Identifier: Apache-2.0
"""{open-items}: one line for each {todo} box on the site, the page's title and the box's first sentence,
linked to the box itself. A Sphinx extension of its own, not code in conf.py, because Sphinx pickles each
page's document and a node class defined in conf.py cannot be pickled."""

import re

from docutils import nodes
from sphinx.util.docutils import SphinxDirective


class open_items(nodes.General, nodes.Element):
    """Where {open-items} puts its list, once every page has been read."""


class OpenItems(SphinxDirective):
    def run(self):
        return [open_items()]


def first_sentence(todo, limit=160):
    """The first sentence of a todo box's text (its "Todo" title left out), cut at `limit` characters."""
    text = " ".join(p.astext() for p in todo.findall(nodes.paragraph))
    text = " ".join(text.split())
    if not text:
        raise ValueError("a {todo} box with no text")
    sentence = re.split(r"(?<=[.!?:])\s", text, maxsplit=1)[0]
    if sentence.endswith(":"):  # it leads into a list or a note: say there is more
        sentence = sentence[:-1].rstrip() + " …"
    return sentence if len(sentence) <= limit else sentence[: limit - 1].rstrip() + "…"


def _fill_open_items(app, doctree, docname):
    found = list(doctree.findall(open_items))
    if not found:
        return
    todos = app.env.get_domain("todo").todos
    items = nodes.bullet_list()
    for where in sorted(todos):
        for todo in todos[where]:
            if not todo["ids"]:
                raise ValueError(f"a {{todo}} box on {where} has no id to link to")
            uri = app.builder.get_relative_uri(docname, where) + "#" + todo["ids"][0]
            line = nodes.paragraph()
            line += nodes.reference("", app.env.titles[where].astext(), internal=True, refuri=uri)
            line += nodes.Text(": " + first_sentence(todo))
            items += nodes.list_item("", line)
    for node in found:
        node.replace_self(items.deepcopy())


def setup(app):
    app.add_node(open_items)
    app.add_directive("open-items", OpenItems)
    app.connect("doctree-resolved", _fill_open_items)
    return {"parallel_read_safe": True, "parallel_write_safe": True}
