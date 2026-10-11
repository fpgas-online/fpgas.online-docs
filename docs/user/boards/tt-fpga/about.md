---
type: explanation
owner: documentation maintainers
reader: a visitor choosing a board on tinytapeout.fpgas.online
review: 2026-11-10
---

# A Tiny Tapeout FPGA demo board on fpgas.online

This page explains what a Tiny Tapeout FPGA demo board is and what its page offers a visitor on
tinytapeout.fpgas.online. It does not cover setting one up, which is
[Tiny Tapeout FPGA demo board](../../../boards/tt-fpga/index.md) under Admin documentation.

## The board

The board is a Tiny Tapeout demo board with an FPGA breakout in place of a chip. Its iCE40UP5K runs a Tiny Tapeout
design as the chip would, and the demo board's RP2350 drives the design's clock and pins. A Raspberry Pi holds the
board's USB port. Each board has a camera.

## The board's page

The page has a status pill, the camera, the Tiny Tapeout Commander and a status log. The button Power-cycle board
restarts the board and its Pi ([How to reset a board](../reset.md)). Under the Commander, **Designs on this board** lists the
bundled designs and your uploads, each with a **Run** button. An upload form takes your own bitstream.

Everyone who opens the page drives the same board. A design one visitor runs is the design every visitor sees.

## How a design reaches the FPGA

A design is a file on the Pi, never on the board. Run sends the file's bytes through the board's MicroPython console
into the RP2350's memory, and the board's own loader clocks them into the iCE40. Nothing is written to the board's
files. Your uploads stay on the Pi until its next reboot.

When nobody has used a board for a minute, its Pi loads a design that keeps the display moving. A design a visitor
loaded is not replaced.
