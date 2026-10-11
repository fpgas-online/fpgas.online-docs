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

- A board's page: on [the Tiny Tapeout site](https://tinytapeout.fpgas.online/), a board the index shows as connected.

Everyone on the page drives the same board, so a project you select replaces the one another visitor was using.

## Steps

1. In the Commander, open the **Config** tab.
2. Click the **Project** field and choose a project from the list. Type part of a title or an author to narrow the list.
   The **Index** field shows its number, and **Clock speed (Hz)** fills in with the project's own clock.
3. To use another clock, type it in **Clock speed (Hz)**, or choose one from **Preset**, and press **Set**.
4. Press **Select**. A project marked with a warning icon has a reason on the icon: hover over it to read it. A project
   marked with a red error icon cannot be selected.
5. Open the **Interact** tab and tick **ui_in**. The buttons 0 to 7 are the project's inputs `ui_in[0]` to `ui_in[7]`:
   press the ones the project uses. The keys 0 to 7 do the same.
6. Tick **uo_out** to see the project's outputs. Press **Reset (R)** to reset the project, or **Clock once (C)** to give
   it one clock pulse.

:::{admonition} Figure to come
:class: placeholder

The Commander's Config and Interact tabs on a chip board's page. Tracked in [docs issue #188](https://github.com/fpgas-online/fpgas.online-docs/issues/188).
:::

## Check

The **Project** list shows the project you chose. With **uo_out** ticked, its row shows the project's output as a
decimal number, a hexadecimal number and eight binary digits. The row changes as you set the inputs.

## If it fails

| What you see | Likely cause | Fix |
|---|---|---|
| **Select** is greyed, with a red error icon | the project is marked as dangerous to select | choose another project |
| **Select** is greyed, with an error icon whose text starts "Subtile projects require firmware" | the board's firmware is older than the project needs | choose another project |
| **Project** reads "Loading projects..." and stays so | the project list has not loaded | wait a moment, then reload the page |
| the page shows a connection banner with a close code, and **Retry now** | the page lost its link to the board | press **Retry now** |

## Next

- [The Tiny Tapeout chip demo boards on fpgas.online](about.md)
- [How to reset a board](../reset.md)
