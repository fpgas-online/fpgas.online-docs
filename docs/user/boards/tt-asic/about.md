---
type: explanation
owner: documentation maintainers
reader: a visitor choosing a board on tinytapeout.fpgas.online
review: 2026-11-10
---

# The Tiny Tapeout chip demo boards on fpgas.online

This page explains what a Tiny Tapeout chip demo board is and what its page offers a visitor on
tinytapeout.fpgas.online. It does not cover setting one up, which is
[Tiny Tapeout chip demo boards](../../../boards/tt-asic/index.md) under Admin documentation.

## The board

A chip demo board is a Tiny Tapeout demo board with a manufactured shuttle chip on it, real silicon. The board carries a
microcontroller that runs the Tiny Tapeout MicroPython SDK. The SDK selects the project inside the chip and drives its
clock and reset. The controller is an RP2040 on a TT06 to TT08 board and an RP2350 on a TT09 board
([Tiny Tapeout shuttles and their demo boards](../../../boards/tt-asic/overview/shuttles.md)).

## Which boards you can use

Only boards that are connected can be used. The index of [tinytapeout.fpgas.online](https://tinytapeout.fpgas.online/)
shows which are connected; no page of this site lists them. Each board's page shows its shuttle and its firmware
version above the tabs.

## The board's page

The page has the Tiny Tapeout Commander, with four tabs: **Config**, **Interact**, **Pinout** and **REPL**. The Commander
reaches the board over the host's serial bridge, and everyone who opens the page sees the same board. A design one
visitor selects is the design every visitor sees. Other people may be driving the board too.

## The safe idle state

At every start the board's SDK selects the chip's factory test, which drives pins the board's own wiring also drives. To
avoid that clash, the host puts an unused chip board into a safe state. The project clock is stopped, the controller's
`uio` pins are released and `ui_in` is driven to 0. It does this after 30 quiet seconds, and only when nobody is using the
board. The state lasts until the board's SDK starts again.

A visitor who selects a design finds the board as the
design leaves it ([fpgas.online-tt README](https://github.com/fpgas-online/fpgas.online-tt/blob/main/README.md)).

## What a visitor changes

A visitor selects a project that is already in the chip, and sets its clock. Nothing a visitor does writes, replaces or
deletes a file on the board.

## Next

The steps are in [How to select a design on a Tiny Tapeout chip demo board](select-design.md).
