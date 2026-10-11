---
type: explanation
owner: documentation maintainers
reader: a visitor choosing a board on welland.fpgas.online
review: 2026-11-10
---

# An Arty A7 on fpgas.online

This page explains what an Arty A7 is and what a visitor can do with one on welland.fpgas.online or ps1.fpgas.online. It does not cover
setting one up, which is [Digilent Arty A7](../../../boards/arty-a7/index.md) under Admin documentation.

:::{admonition} No Arty A7 was in service when this was checked
:class: warning

On 26 September 2026 no Arty A7 was online at welland.fpgas.online. The recorded ports were down, and none of the
reachable hosts showed the board's USB chip
([infra issue #125](https://github.com/fpgas-online/fpgas.online-infra/issues/125)). At ps1.fpgas.online, seven of eight
Arty A7 hosts did not answer the gateway on 6 October 2026
([infra issue #272](https://github.com/fpgas-online/fpgas.online-infra/issues/272)). Both issues are open.

The board type on each site's list says whether one is back. Read the pages below as what a visitor will find then.
:::

## The board

The Digilent Arty A7 is a Xilinx Artix-7 development board. It has DDR3 memory, an Ethernet jack, a quad SPI flash,
four PMOD connectors, and LEDs, switches and buttons. One FTDI chip gives it a single USB cable for both programming
and a serial console ([The Arty A7 board](../../../boards/arty-a7/overview/board.md)).

## The host

Each Arty A7 is joined to a Raspberry Pi by that USB cable. The Pi sees the board as two `/dev/ttyUSB*` devices: the
JTAG channel and the UART channel. A board whose USB chip is not on the Pi's USB cannot be programmed or reached on
its console.

## What the board page offers

An Arty's page is the page every board has: a terminal, an upload, the camera and a Reset
([the board page](../board-page.md)). The page's Demo buttons and its Useful links are written for the Arty A7, and
only for it ([site issue #104](https://github.com/fpgas-online/fpgas.online-site/issues/104),
[site issue #105](https://github.com/fpgas-online/fpgas.online-site/issues/105)).

## Loading a design

A visitor loads a design with one command in the page's terminal. The load goes into the FPGA's SRAM, so the design is
gone at the next power cycle: a Reset ends it. The steps are in
[How to load a design onto an Arty A7 from its board page](load.md).
