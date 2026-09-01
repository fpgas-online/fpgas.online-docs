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

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "requirements.txt"]

# Warn about references that do not resolve. Combined with fail_on_warning in
# .readthedocs.yaml this turns a broken cross-reference into a failed build
# rather than a silently dead link.
nitpicky = False

todo_include_todos = True

# -- MyST -------------------------------------------------------------------

myst_enable_extensions = [
    "colon_fence",       # ::: fences, so admonitions work without indentation
    "deflist",           # definition lists, useful for pin/option tables
    "fieldlist",
    "linkify",           # bare URLs become links
    "substitution",
    "tasklist",          # - [ ] checkboxes, used in the runbooks
]

# Give every heading an anchor so other pages (and external links) can target
# sections directly, e.g. `hardware.md#jtag`.
myst_heading_anchors = 3

# -- HTML -------------------------------------------------------------------

html_theme = "furo"
html_title = "fpgas.online"

html_theme_options = {
    "source_repository": "https://github.com/fpgas-online/fpgas.online-docs/",
    "source_branch": "main",
    "source_directory": "docs/",
}

# -- Intersphinx ------------------------------------------------------------

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}
