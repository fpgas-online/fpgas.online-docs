# Acorn wiring sheets

`gen.py` draws the two sheets on [Acorn wiring](../../docs/boards/acorn/wiring.md)
from one pin table and the vendors' board photos. `GOALS.md` says what the
sheets have to show; `sheetlib.py` measures every label with the font it embeds
and fails the build if a label leaves its box or the canvas, overlaps another
label, sits on a wire, or a pad leaves its header.

The SVGs load nothing, not even a `data:` URI, so they render the same when
opened straight from `raw.githubusercontent.com` (whose
`Content-Security-Policy: default-src 'none'` blocks embedded images and
fonts). Text is drawn as glyph outlines from the Liberation fonts, and each
photo is a set of horizontal colour runs, one path per colour. That costs about
2 MB per sheet.

```console
$ cd tools/acorn_wiring
$ uv run --with pillow --with fonttools python gen.py              # searches header placements, ~15 min
$ uv run --with pillow --with fonttools python gen.py pi5=8 blade=8  # the placements it found, ~3 min
$ uv run python render.py                                          # out/*.png via headless Chromium
$ cp out/pi5.svg   ../../docs/boards/acorn/acorn-wiring-pi5.svg
$ cp out/pi5.png   ../../docs/boards/acorn/acorn-wiring-pi5.png
$ cp out/blade.svg ../../docs/boards/acorn/acorn-wiring-computeblade.svg
$ cp out/blade.png ../../docs/boards/acorn/acorn-wiring-computeblade.png
```

Change the wiring in `pi5()` (`mapping`) / `blade()` (`p1_map`, `p2_map`, the
resistor sets passed to `make_wires`, the `unused` wires) and in
`sheetlib.py` (`P1_PINS`, `P2_PINS`), never in the picture.

`photos/` holds the crops the sheets embed. `prep_photos.py` made them from the
vendors' originals, which are not in this repository: the Compute Blade top view
is Uptime Lab's (docs.computeblade.com), the HAT is Waveshare's dimension drawing
of the PoE M.2 HAT+, and the card underside is RHS Research's LiteFury photo
(the Acorn is the same PCB). They are credited on each sheet.
