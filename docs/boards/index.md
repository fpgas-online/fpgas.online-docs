---
type: reference
owner: documentation maintainers
reader: someone looking for the pages of a board type
review: 2026-11-10
---

# Boards

This page lists every board type that fpgas.online puts on a Raspberry Pi, with its page. It is for someone
looking for a board's pages. It does not say which boards a site has: that is on the site's page, under
[Sites](../sites/index.md).

Board names the board and links its maker's page. Page is its page here. FPGA is the device on it. Features is
what the board carries. Interface is how the board reaches its Raspberry Pi.

| Board | Page | FPGA | Features | Interface |
|---|---|---|---|---|
| [Digilent Arty A7-35T](https://digilent.com/shop/arty-a7-artix-7-fpga-development-board/) | [Digilent Arty A7](arty-a7/index.md) | Xilinx XC7A35T | DDR3, Ethernet, PMOD, USB JTAG and UART | USB to an FTDI FT2232: JTAG on `ttyUSB0`, a 115200 baud UART on `ttyUSB1`; PMOD HAT |
| [Kosagi NeTV2](https://www.crowdsupply.com/alphamax/netv2) | [Kosagi NeTV2](netv2/index.md) | Xilinx XC7A35T | DDR3, Ethernet, PCIe, HDMI | GPIO JTAG; GPIO UART; on a Raspberry Pi 5 also PCIe Gen2 x1 and a second UART on the PCIe "hax" pins |
| [SQRL Acorn CLE-215+](https://github.com/enjoy-digital/litex/wiki/Use-LiteX-on-the-Acorn-CLE-215) | [SQRL Acorn and LiteFury](acorn/index.md) | Xilinx XC7A200T | DDR3, PCIe, SPI flash | GPIO JTAG (P1); GPIO UART (P2) on `/dev/ttyAMA0`; PCIe through an M.2 slot |
| [LiteFury](https://github.com/RHSResearchLLC/NiteFury-and-LiteFury) and Acorn CLE-101 | [SQRL Acorn and LiteFury](acorn/index.md) | Xilinx XC7A100T | DDR3, PCIe, SPI flash | GPIO JTAG (P1); GPIO UART (P2) on `/dev/ttyAMA0`; PCIe through an M.2 slot |
| [Fomu EVT](https://www.crowdsupply.com/sutajio-kosagi/fomu) | [Fomu EVT](fomu-evt/index.md) | Lattice iCE40UP5K | USB 1.1, SPI flash, PMOD, I2C | native USB, programmed over DFU; the Pi's GPIO UART at 115200 on `/dev/serial0` (iCE40 pins 13 and 21 to GPIO14 and GPIO15) |
| [Tiny Tapeout FPGA demo board](https://tinytapeout.com/guides/fpga-breakout/) | [Tiny Tapeout FPGA demo board](tt-fpga.md) | Lattice iCE40UP5K | PMOD, USB (RP2350) | USB-C to the RP2350 as `/dev/ttboard`; PMOD HAT |
| [Tiny Tapeout chip demo boards](https://tinytapeout.com/chips/) | [Tiny Tapeout ASIC demo boards](tt-asic/index.md) | a manufactured Tiny Tapeout chip | PMOD, USB (RP2040 or RP2350) | USB to the controller as `/dev/ttboard`; PMOD HAT |

```{toctree}
:hidden:

arty-a7/index
acorn/index
netv2/index
fomu-evt/index
tt-fpga
tt-asic/index
```
