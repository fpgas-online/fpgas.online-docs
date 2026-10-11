---
type: explanation
owner: documentation maintainers
reader: a visitor choosing a board on welland.fpgas.online
review: 2026-11-10
---

# An Acorn on fpgas.online

This page explains what an Acorn is and what a visitor can do with one on welland.fpgas.online. It does not cover
setting one up, which is [SQRL Acorn and LiteFury](../../../boards/acorn/index.md) under Admin documentation.

## The card

The SQRL Acorn CLE-215+ is an M.2 PCIe card with a Xilinx Artix-7 FPGA, DDR3 memory and a quad-SPI flash. At welland
each card sits in an M.2 HAT on a Raspberry Pi 5. The Pi reaches its FPGA over JTAG on the Pi's header and over PCIe.
The card's four user LEDs are what the camera shows ([The camera over an Acorn](../../../boards/acorn/overview/camera.md)).

## What the board page offers

An Acorn's page is the page every board has, with a terminal, an upload, the camera and a Reset
([the board page](../board-page.md)). The page does not load a design for you. You load it from
the terminal, as on [How to load a design onto an Acorn from its board page](load.md).

A load goes into the FPGA's SRAM. The card's flash keeps the fpgas.online design, which runs again after a Reset.

## Designs on the host

The host carries the fpgas.online Acorn design, in `/usr/share/fpgas-online/acorn-pcie/images/`: for each card the
flash images, the operational `.bit` and the register maps. What the design holds is on
[The fpgas.online Acorn design](../../../boards/acorn/overview/design.md).
