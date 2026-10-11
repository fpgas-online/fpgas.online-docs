---
type: explanation
owner: documentation maintainers
reader: a visitor choosing a board on welland.fpgas.online
review: 2026-11-10
---

# A Fomu EVT on fpgas.online

This page explains what a Fomu EVT is and what a visitor can do with one on welland.fpgas.online. It does not cover
setting one up, which is [Fomu EVT](../../../boards/fomu-evt/index.md) under Admin documentation.

## The board

The Fomu is a tiny FPGA board that fits inside a USB Type-A port. The EVT revision is built around a Lattice iCE40UP5K
with native USB. The board enumerates as a USB device by itself, and it is programmed over USB DFU, not over JTAG
([The Fomu EVT board](../../../boards/fomu-evt/overview/board.md)).

## The host

At welland the Fomu EVT is on a Raspberry Pi, with a USB analyser between the board and its host
([welland](../../../sites/welland.md)). It sits on the Pi's 40-pin header and plugs into the Pi's USB port.

## What the board page offers

A Fomu's page is the page every board has, with a terminal, an upload, the camera and a Reset
([the board page](../board-page.md)). The page does not load a design for you. You load it from the terminal, as on
[How to load a design onto a Fomu EVT from its board page](load.md).

The Fomu's bootloader waits for a load for about 3 minutes after it starts. After that the board runs the design in its
flash. A Reset restarts the host, and with it the bootloader's window.

## After a load

A design with no USB core, such as the UART echo, leaves USB once it loads. That is expected, not a fault. It talks
over two pins on the Pi's header, which the Pi opens as `/dev/serial0`
([Programming a Fomu EVT](../../../boards/fomu-evt/overview/programming.md)).

## Designs on the host

Where the Fomu packages are installed, the host carries the test bitstreams in
`/usr/share/fpgas-online/fomu/bitstreams/` ([fpgas-verify: installing it](../../../verify/installing.md)).
