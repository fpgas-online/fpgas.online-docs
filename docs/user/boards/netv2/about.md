---
type: explanation
owner: documentation maintainers
reader: a visitor choosing a board on welland.fpgas.online
review: 2026-11-10
---

# A NeTV2 on fpgas.online

This page explains what a NeTV2 is and what a visitor can do with one on welland.fpgas.online. It does not cover
setting one up, which is [Kosagi NeTV2](../../../boards/netv2/index.md) under Admin documentation.

## The board

The Kosagi NeTV2 is a Xilinx Artix-7 video overlay and processing board. It stacks on a Raspberry Pi's 40-pin header.
The FPGA is an XC7A35T, or an XC7A100T on the large variant. It also carries 512 MB of DDR3 memory, two HDMI inputs and
two HDMI outputs. It has a quad SPI flash and six user LEDs ([The NeTV2 board](../../../boards/netv2/overview/board.md)).

## The host

At welland each NeTV2 sits on a Raspberry Pi ([welland](../../../sites/welland.md)). The Pi may be a Pi 5 or a Pi 3B+,
and the load steps differ between them. A Pi 5 also has a PCIe link to the board. A Pi 3B+ has none, so it drives the
board only over its GPIO header.

## What the board page offers

A NeTV2's page is the page every board has, with a terminal, an upload, the camera and a Reset
([the board page](../board-page.md)). The page does not load a design for you. You load it from the terminal, as on
[How to load a design onto a NeTV2 from its board page](load.md).

A host with a USB HDMI grabber sends the picture of the board's HDMI output as its camera feed. It is not a view of
the board ([The camera on a board](../camera.md)).

A load goes into the FPGA's SRAM and is lost at power-off. A visitor never writes the board's flash.

## Designs on the host

Where the NeTV2 packages are installed, the host carries the XC7A35T and XC7A100T test bitstreams in
`/usr/share/fpgas-online/netv2/bitstreams/` ([fpgas-verify: installing it](../../../verify/installing.md)).
