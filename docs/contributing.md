# Contributing to these docs

Pages are Markdown, parsed by [MyST](https://myst-parser.readthedocs.io/), so
ordinary Markdown works and the Sphinx-specific pieces are available when you
want them.

## Build locally

```console
$ python3 -m venv .venv && . .venv/bin/activate
$ pip install -r docs/requirements.txt
$ sphinx-build -b html docs docs/_build/html
$ python3 -m http.server -d docs/_build/html
```

Read the Docs builds with `fail_on_warning: true`, so a warning locally is a
failed build there. The usual causes are a page missing from a `toctree` and a
link to a file that has moved.

## The MyST bits worth knowing

Admonitions use colon fences, so they need no indentation:

```markdown
:::{warning}
Reconfiguring the FPGA while its PCIe endpoint is enumerated crashes the host.
:::
```

Directives that take content use the same form with backticks:

````markdown
```{toctree}
:maxdepth: 2

sites/index
```
````

Headings get anchors down to three levels, so you can link to a section of
another page directly:

```markdown
See [the Compute Blade wiring](boards/acorn/wiring.md#compute-blade).
```

Wide tables scroll sideways rather than being split. A table of dense
identifier data — MAC addresses, device DNAs, serial numbers, board models —
should also be told not to wrap, or the browser shreds every column to a few
characters wide and each row becomes several lines tall:

````markdown
```{rst-class} nowrap
```

| Host | RPi MAC | RPi Model |
|---|---|---|
````

Leave the class off tables whose cells hold prose; those should wrap normally.

## What belongs here

This site is for things that outlive a single change: how the hardware is
wired, why a setting is the way it is, and what to do when something breaks.

Things that do **not** belong here:

- Anything the code already states plainly. Document the surprise, not the
  syntax.
- Per-host inventory that a tool generates. Link to the generator instead.
- Secrets, or anything that is only true until the next deploy.

When a page records a measurement — a pinout, a device ID, a fault — say when
it was taken and on which host. A pinout with no date is impossible to trust
later.

## Printing pages

`tools/print_pages.py` renders published pages to one PDF, on A4 or US Letter,
for the bench or for someone who needs it on paper. It fetches the pages from
the live site, so the paper says what the site says: to change the print, change
the page and publish it.

```console
$ uv run tools/print_pages.py --paper A4 --title "Wiring an Acorn to a Raspberry Pi 5" \
    --output acorn-pi5.pdf "boards/acorn/wiring#bill-of-materials,raspberry-pi-5,assembly"
```

A page is given by its path, and may be cut down to sections named by their
anchors. Chapters are numbered; each carries its source URL and the commit the
site was built from, the cover lists the sheet each starts on, and every sheet's
foot carries the commit and a page number. Links are numbered, with their
addresses listed at the end of each chapter. An image drawn at least 1200 px wide (a
wiring sheet; for a PNG, which the site renders at double size, 2400 px) stays
in the text at the column's width as an overview, and is printed once at full
size on a landscape sheet of its own at the end of its chapter; the line under
each small copy names that sheet. A paragraph that holds only a picture is kept
whole, and on the sheet of the paragraph before it, so a step and its picture
are not parted. `--help` lists the rest:
boxes of notes on the cover (several in one file, separated by a line of
dashes), a last sheet, PDFs to append. Appended PDFs are not renumbered and must
already be on the chosen paper, or the run stops. The tool needs
`google-chrome-stable` and `pdftotext` (poppler-utils, for the cover's sheet
numbers), `pdfinfo` (also poppler-utils) to find a wide picture's sheet, and
`pdfunite` and `pdfinfo` for `--append`.

## Open items

Every unresolved question found while writing these pages is a `{todo}` on
the page it belongs to. They are collected here:

```{todolist}
```
