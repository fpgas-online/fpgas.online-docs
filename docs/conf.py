"""Sphinx configuration for the fpgas.online documentation.

Markdown-first: pages are written in Markdown and parsed by MyST. reStructuredText
still works if a page ever needs it, but nothing here requires it.
"""

import json
import pathlib
import posixpath
import sys
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

# docs/_ext: this site's own Sphinx extensions
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / "_ext"))

extensions = [
    "open_items",               # {open-items}: the open items page, one line per {todo} box
    "table_code",               # the code in a message column of a table may wrap at its spaces
    "myst_parser",              # Markdown
    "sphinx_copybutton",        # copy button on code blocks -- these docs are
                                # full of commands meant to be pasted
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
    "sphinx_reredirects",       # a page at each old address that sends the reader to the new one
]

# docs/redirects.json holds every page that moved: {old page: new page}, as document names. An entry with a
# "#fragment" in its key is a section that left its page; tools/sync_repos.py reads those, a browser cannot.
_moved = json.loads((pathlib.Path(__file__).resolve().parent / "redirects.json").read_text())
redirects = {
    old: posixpath.relpath(new.partition("#")[0], posixpath.dirname(old)) + ".html" + "".join(new.partition("#")[1:])
    for old, new in _moved.items() if "#" not in old
}

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
    "redirects.json",
    "superpowers",
    # Tables copied from fpgas.online-test-designs by tools/sync_repos.py. They are pulled into
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

# -- the open items page ------------------------------------------------------
# docs/open-items.md lists every {todo} box with {open-items} (docs/_ext/open_items.py): one line
# for each, not Sphinx's {todolist}, which copies every box whole and printed 11 A4 sheets.


# -- old anchors kept on a landing page ---------------------------------------
# When a page is split, its landing page keeps each old heading's anchor as a
# MyST target, `(old-heading-slug)=`, so that links from elsewhere still land.
# A Markdown link `page.md#anchor` is resolved by MyST against the page's heading
# slugs only (myst_slugs), not its targets, so such a link to a kept anchor would
# warn. Every explicit target of a page is added to its slugs here, once all
# pages are read and before any link is resolved.


def _targets_as_slugs(app, env):
    for label, (docname, labelid) in env.get_domain("std").anonlabels.items():
        slugs = env.metadata.get(docname, {}).get("myst_slugs")
        if slugs is not None and label not in slugs:
            slugs[label] = (0, labelid, env.titles[docname].astext())


def setup(app):
    app.connect("env-check-consistency", _targets_as_slugs)
    # The environment is saved before the consistency check, so a rebuild that reads no page would load it
    # without these slugs and skip that check: add them again on every build. Doing it twice is harmless.
    app.connect("env-updated", lambda app, env: _targets_as_slugs(app, env) or [])
