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

A Fomu's page is the page every board has: a terminal, an upload, the camera and a Reset
([the board page](../board-page.md)).

## Loading a design: not possible today

A visitor cannot load a design into the Fomu today. The only way in is the Fomu's DFU bootloader, which waits about 3
minutes after the host powers up.

At every boot the host's own check takes that window first. It loads its test design
by DFU, and the Fomu leaves USB about 36 seconds into the boot. Your terminal connects after about two minutes, when the
bootloader is gone. A Reset only repeats this
([test-designs issue #135](https://github.com/fpgas-online/fpgas.online-test-designs/issues/135),
[docs issue #203](https://github.com/fpgas-online/fpgas.online-docs/issues/203)).

Once a visitor can load, a load writes the design into the Fomu's user image in its flash: the slot made for user
designs. The next load replaces it, and the bootloader itself is untouched.

## The design running now

The host's check leaves its UART test design running. A design with no USB core, such as that one, is off USB, which is
expected, not a fault. It talks over two pins on the Pi's header, which the Pi opens as `/dev/serial0`
([Programming a Fomu EVT](../../../boards/fomu-evt/overview/programming.md)).

## Designs on the host

Where the Fomu packages are installed, the host carries the test bitstreams in
`/usr/share/fpgas-online/fomu/bitstreams/` ([fpgas-verify: installing it](../../../verify/installing.md)).
