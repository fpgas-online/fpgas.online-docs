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

```{figure} ../screenshots/tt-board-page.png
:alt: The top of a Tiny Tapeout FPGA board's page. The heading reads TT FPGA emulation board 1, under the site's Under construction banner and its menu bar, with an FPGA emulation tag, a board present, 1 viewer status pill, and the Power-cycle board and Reset video buttons. Below, the camera is on the left. On the right is the Commander, with Shuttle FPGA and Firmware 3.1.0, a Reconnect button, and the Config, Interact, Pinout and REPL tabs. The Config tab shows the Project field with 7-Segment Hex Counter, Load design, Clock speed, Preset and Set, and the Project docs and Repo links, above the board's log.

The top of a Tiny Tapeout FPGA board's page, 11 Oct 2026. **Designs on this board** and its **Run** buttons are
below this part of the page.
```

## Steps

1. Under **Designs on this board**, choose a design. [The bundled designs](designs.md) says what each one does and
   which inputs it uses.
2. Press its **Run** button. The page shows `Loading <design>…`, then `<design> is running`.
3. In the Commander, open the **Interact** tab and tick **ui_in**. The buttons 0 to 7 are the design's inputs `ui[0]` to `ui[7]`:
   press the ones the design uses.

   ```{figure} ../screenshots/tt-commander-interact.png
   :alt: The Commander's Interact tab, with Shuttle FPGA, Firmware 3.1.0 and Reconnect above the tabs. The ui_in checkbox has buttons 0 to 7 and a settings gear beside it; the buttons are greyed because it is not ticked. Under it is the uo_out checkbox, also not ticked. Below are the Reset (R) and Clock once (C) buttons, then the board's log.

   The Commander's **Interact** tab as step 3 opens it, before **ui_in** and **uo_out** are ticked.
   ```

4. Tick **uo_out** to see the design's outputs.

## Check

The design's button reads **Running**, and the status log shows `design <design> loaded`. The camera and the **uo_out** row show the board's
outputs change as you set the inputs.

## If it fails

| What you see | Likely cause | Fix |
|---|---|---|
| `another task is running` | the board was busy with another load | wait a moment, then press Run again |
| `board not present` | the board is not on its Pi's USB | press **Power-cycle board** ([How to reset a board](../reset.md)), then try again |
| `Pi unreachable`, or `HTTP 502` | the board's Pi is restarting or off | wait two minutes, then reload the page |
| `Could not reach the Pi` | your browser's connection to the site failed | check your connection, then reload the page |

## Next

- [How to load your own bitstream](own-bitstream.md)
