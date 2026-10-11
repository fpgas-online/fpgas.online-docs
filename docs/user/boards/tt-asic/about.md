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
shows which are connected; no page of this site lists them. Under **Tiny Tapeout ASIC boards**, a connected board's card
has **Use this board**. A card that shows "not connected", or a status and "Read about it", opens a page with no controls.

## The board's page

The page has the board's title, a tag for its kind, a link "<shuttle> chip page", and a status pill such as
"board present · 1 viewer". It has a **Power-cycle board** button, which asks "Power-cycle this board? Anyone else using
it will be interrupted.", and a **Reset video** button. The camera sits beside the Tiny Tapeout Commander. Below are
"About this board" and a "Status log".

The Commander has four tabs: **Config**, **Interact**, **Pinout** and **REPL**. Once it has connected, "Shuttle:" and
"Firmware:" appear above the tabs, with a **Reconnect** button, and a **Debug log** sits below. Everyone who opens the
page sees the same board. Other people may be driving it too.

## The safe idle state

At every start the board's SDK selects the chip's factory test, `tt_um_factory_test`. It drives pins the board's own
wiring also drives. To avoid that clash, the host puts the board into a safe state once each time the board starts up.
It does so only if nobody has connected within 30 seconds and the board is still on that start project.

The project clock is stopped, the controller's `uio` pins are released and `ui_in` is driven to 0. A project you
select stays until the board is power-cycled. Then the SDK starts again on its start project, the factory test
([fpgas.online-tt README](https://github.com/fpgas-online/fpgas.online-tt/blob/main/README.md)).

## What a visitor changes

A visitor selects a project that is already in the chip, and sets its clock. Nothing a visitor does writes, replaces or
deletes a file on the board.

## Next

The steps are in [How to select a design on a Tiny Tapeout chip demo board](select-design.md).
