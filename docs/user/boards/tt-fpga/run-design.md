---
type: how-to
owner: documentation maintainers
reader: a visitor with a Tiny Tapeout FPGA demo board's page open
review: 2026-11-10
---

# How to run a bundled design

**You have a Tiny Tapeout FPGA demo board's page open on tinytapeout.fpgas.online. You want one of its designs to run,
and to drive it**.

## What you need

- A board's page: on [the Tiny Tapeout site](https://tinytapeout.fpgas.online/), under "FPGA emulation boards", press **Use this board**.

Everyone on the page drives the same board, so a design you run replaces the one another visitor was using.

## Steps

1. Under **Designs on this board**, choose a design. [The bundled designs](designs.md) says what each one does and
   which inputs it uses.
2. Press its **Run** button. The page shows `Loading <design>…`, then `<design> is running`.
3. In the Commander, open the **Interact** tab and tick **ui_in**. The buttons 0 to 7 are the design's inputs `ui[0]` to `ui[7]`:
   press the ones the design uses.
4. Tick **uo_out** to see the design's outputs.

:::{admonition} Figure to come
:class: placeholder

The Tiny Tapeout board page with Designs on this board and the Commander's Interact tab. Tracked in [docs issue #188](https://github.com/fpgas-online/fpgas.online-docs/issues/188).
:::

## Check

The design's button reads **Running**, and the status log shows `design <design> loaded`. The camera and the **uo_out** row show the board's
outputs change as you set the inputs.

## If it fails

| What you see | Likely cause | Fix |
|---|---|---|
| `another task is running` | the board was busy with another load | wait a moment, then press Run again |
| `board not present` | the board is not on its Pi's USB | press **Power-cycle board** ([How to reset a board](../reset.md)), then try again |
| `Pi unreachable`, or `HTTP 502 Bad Gateway` | the board's Pi is restarting or off | wait two minutes, then reload the page |
| `Could not reach the Pi` | your browser's connection to the site failed | check your connection, then reload the page |

## Next

- [How to load your own bitstream](own-bitstream.md)
