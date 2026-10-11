---
type: how-to
owner: documentation maintainers
reader: a visitor with a Tiny Tapeout chip demo board's page open
review: 2026-11-10
---

# How to select a design on a Tiny Tapeout chip demo board

**You have a Tiny Tapeout chip demo board's page open on tinytapeout.fpgas.online. You want a project in the chip to
run, and to drive it**.

## What you need

- The index of [tinytapeout.fpgas.online](https://tinytapeout.fpgas.online/), and a board on it that is connected.

Everyone on the page drives the same board, so a project you select replaces the one another visitor was using.

## Steps

1. On the index, under **Tiny Tapeout ASIC boards**, press **Use this board** on the board's card. A card that shows
   "not connected", or a status and "Read about it", has no controls: choose another card.
2. In the Commander, open the **Config** tab.
3. Click the **Project** field and choose a project from the list. Type part of a title or an author to narrow the list.
   The **Index** field shows its number, and **Clock speed (Hz)** fills in with the project's own clock.
4. Press **Select**. A project marked with a warning icon has a reason on the icon: hover over it to read it. A project
   marked with a red error icon cannot be selected. **Select** also unticks any **ui_in** buttons you had set.
5. To use another clock, do it after **Select**. Type it in **Clock speed (Hz)**, or choose a **Preset**. Then press
   **Set**. **Select** sends the project's own clock, so a clock set before it is not used.
6. Open the **Interact** tab and tick **ui_in**. The buttons 0 to 7 are the project's inputs `ui_in[0]` to `ui_in[7]`:
   press the ones the project uses. The keys 0 to 7 do the same.
7. Tick **uo_out** to see the project's outputs. Press **Reset (R)** to reset the project, or **Clock once (C)** to give
   it one clock pulse.

:::{admonition} Figure to come
:class: placeholder

The Commander's Config and Interact tabs on a chip board's page. Tracked in [docs issue #188](https://github.com/fpgas-online/fpgas.online-docs/issues/188).
:::

## Check

At the bottom of the Commander, the **Debug log** shows a line that starts `> select_design(`, with the project's
number in it. The **Index** field then shows that number. With **uo_out** ticked, its row shows the project's output as
a decimal number, a hexadecimal number and eight binary digits. The row changes as you set the inputs.

## If it fails

| What you see | Likely cause | Fix |
|---|---|---|
| a card with "not connected", or the board page's banner "This board is not connected" | no board's boot check reports it | choose a connected board on the index |
| the board page says "This page offers no controls for the board until its Raspberry Pi's boot check has read it and passed" | the board's boot check has not passed | choose another board, or come back later |
| the status pill reads "Pi offline" | the board's Pi is off or restarting | wait two minutes, then reload; if it stays, press **Power-cycle board** and confirm ([How to reset a board](../reset.md)) |
| the status pill reads "board not detected", or the Commander shows "The Pi is reachable but no Tiny Tapeout board is detected on it. Try "Power-cycle board" on the page." | the Pi cannot see the board | press **Power-cycle board** and confirm ([How to reset a board](../reset.md)) |
| "Connecting to the board…" stays on screen | the page has not reached the board yet | wait; if it stays, reload the page |
| "Disconnected (…). Retrying in N s", with **Retry now** | the page lost its link to the board | press **Retry now**, or wait: the page retries by itself |
| a banner that starts "This board runs demo-board firmware" | the firmware is older than the Commander expects | some features may not work; the maintainers upgrade it, and a visitor cannot |
| **Select** is greyed, with a red error icon | the project is marked as dangerous to select | choose another project |
| **Select** is greyed, with an error icon whose text starts "Subtile projects require firmware" | the board's firmware is older than the project needs | choose another project |
| **Project** reads "Loading projects..." and stays so | the project list has not loaded | wait a moment, then reload the page |

## Next

- [The Tiny Tapeout chip demo boards on fpgas.online](about.md)
- [How to reset a board](../reset.md)
