---
type: explanation
owner: documentation maintainers
reader: someone with a Kosagi NeTV2 who wants to know what is on it
review: 2026-11-10
---

# The NeTV2 board

**You have a Kosagi NeTV2 and want to know what the board is and what it carries.**

Its pins and figures are on [NeTV2 specifications](specifications.md). Its wires are on [NeTV2 wiring to a Raspberry Pi](../setup/wiring.md). How a design reaches it is on [Programming a NeTV2](programming.md).

The NeTV2 is a Xilinx Artix-7 video overlay and processing board produced by Alphamax (Kosagi). It stacks on a Raspberry Pi's 40-pin header. These pages cover it on a Raspberry Pi 3B+ and on a Raspberry Pi 5.

:::{admonition} Figure to come
:class: placeholder

The whole NeTV2 from above and from below, with each part named on the page numbered on the board. Tracked in [test-designs issue #244](https://github.com/fpgas-online/fpgas.online-test-designs/issues/244).
:::

## What is on the board

The board carries these parts, each with its pins on [NeTV2 specifications](specifications.md):

- An Artix-7 FPGA, an XC7A35T by default or an XC7A100T on the large variant.
- 512 MB of DDR3 SDRAM on a 32-bit bus.
- An Ethernet PHY with an RMII interface, for 100Base-T.
- Two HDMI inputs and two HDMI outputs.
- A full-size SD slot and a quad SPI flash.
- Six user LEDs.
- A PCIe connector for x1, x2 or x4.

## How it sits on its Raspberry Pi

The NeTV2 connects to the Raspberry Pi through the 40-pin GPIO header, and optionally through a PCIe link. JTAG and the serial port are direct GPIO connections, with no USB serial adapter anywhere in the path.

A Raspberry Pi 3B+ has no PCIe interface, so a NeTV2 on one is driven entirely over GPIO JTAG and a GPIO UART. A Raspberry Pi 5 adds a PCIe Gen2 x1 link through its PCIe connector, and a second UART on the PCIe "hax" pins. The board's Ethernet PHY has its own network connection, independent of the Raspberry Pi's network.
