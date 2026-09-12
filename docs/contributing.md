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
See [the Compute Blade wiring](boards/acorn/wiring.md#compute-blade-wiring-variant).
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

## Open items

Every unresolved question found while writing these pages is a `{todo}` on
the page it belongs to. They are collected here:

```{todolist}
```
