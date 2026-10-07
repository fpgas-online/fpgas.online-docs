"""Sphinx configuration for the fpgas.online documentation.

Markdown-first: pages are written in Markdown and parsed by MyST. reStructuredText
still works if a page ever needs it, but nothing here requires it.
"""

from datetime import date

# -- Project ----------------------------------------------------------------

project = "fpgas.online"
author = "Tim 'mithro' Ansell"
copyright = f"{date.today().year}, {author}"

# The docs describe live infrastructure rather than a released artefact, so
# there is no version to pin: every build documents the current state.
release = ""
version = ""

# -- General ----------------------------------------------------------------

extensions = [
    "myst_parser",              # Markdown
    "sphinx_copybutton",        # copy button on code blocks -- these docs are
                                # full of commands meant to be pasted
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
]

source_suffix = {
    ".md": "markdown",
    ".rst": "restructuredtext",
}

# superpowers/ holds the design specs and implementation plans for this site,
# which are working documents for contributors rather than published pages.
exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    "requirements.txt",
    "superpowers",
    # Tables copied from fpgas.online-test-designs by tools/sync_test_designs.py. They are pulled into
    # pages with {include}, not built as pages of their own.
    "boards/acorn/generated/*.md",
    "boards/generated/*.md",
]

# MyST already warns (myst.xref_missing) on a Markdown link to a page or
# heading that does not exist, and fail_on_warning in .readthedocs.yaml turns
# that into a failed build. nitpicky would additionally warn on every
# unresolved Sphinx role, which the code-reference-free pages here do not use.
nitpicky = False

todo_include_todos = True

# -- MyST -------------------------------------------------------------------

myst_enable_extensions = [
    "colon_fence",       # ::: fences, so admonitions work without indentation
    "attrs_inline",      # {.class} after an image: only-light / only-dark pictures for the two themes
    "deflist",           # definition lists, useful for pin/option tables
    "fieldlist",
    "linkify",           # bare URLs become links
    "substitution",
    "tasklist",          # - [ ] checkboxes, used in the runbooks
]

# Give every heading an anchor so other pages (and external links) can target
# sections directly, e.g. `hardware.md#jtag`.
# 4, because the pulled fpgas-verify page links to its own fourth-level headings.
myst_heading_anchors = 4

# Only text that is written as a URL (with its scheme) becomes a link. With fuzzy matching on, a bare file
# name such as "verify-goals.md" is read as a host name under the .md top-level domain and linked to
# http://verify-goals.md.
myst_linkify_fuzzy_links = False

# -- HTML -------------------------------------------------------------------

html_theme = "furo"
html_title = "fpgas.online"

html_theme_options = {
    "source_repository": "https://github.com/fpgas-online/fpgas.online-docs/",
    "source_branch": "main",
    "source_directory": "docs/",
}

# Furo does not wrap Markdown tables in a scrolling container, and the site
# pages carry host inventory tables up to nine columns wide.
html_static_path = ["_static"]
html_css_files = ["custom.css"]

# -- Intersphinx ------------------------------------------------------------

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

# -- link check -------------------------------------------------------------
# GitHub builds a document's heading anchors in the browser, so the link check
# cannot see them and reports every `blob/main/x.md#heading` as broken. The
# page itself is still checked. tools/check_links.py then fails the build for a
# broken link into our own repositories and sites.
linkcheck_anchors_ignore_for_url = [r"https://github\.com/.*"]

# -- todo boxes on the contributing page --------------------------------------
# {todolist} copies every {todo} box into docs/contributing.md and re-resolves
# its cross-references from there. But sphinx.ext.todo stores the box nodes
# themselves, not copies, and Sphinx keeps the read documents in memory when it
# writes. So a page written before contributing.md (everything under boards/)
# has already resolved its boxes' links relative to itself, and the copy on the
# contributing page inherits links such as "pin-id.html" or a bare "#anchor".
# Storing a copy leaves the page's own document alone and the list's copy
# unresolved, so its links are resolved from contributing.md.


def _copy_todos_for_the_list(app, doctree):
    todos = app.env.get_domain("todo").todos
    docname = app.env.docname
    todos[docname] = [todo.deepcopy() for todo in todos.get(docname, [])]


def setup(app):
    app.connect("doctree-read", _copy_todos_for_the_list)
