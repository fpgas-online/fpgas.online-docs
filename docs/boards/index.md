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

Board names the board and links its maker's page. Page is its page here. FPGA is the device on it. Interface is
how the board reaches its Raspberry Pi.

| Board | Page | FPGA | Interface |
|---|---|---|---|
| [Digilent Arty A7-35T](https://digilent.com/shop/arty-a7-artix-7-fpga-development-board/) | [Digilent Arty A7](arty-a7.md) | Xilinx XC7A35T | USB to an FTDI FT2232 (JTAG and UART); PMOD HAT |
| [Kosagi NeTV2](https://www.crowdsupply.com/alphamax/netv2) | [Kosagi NeTV2](netv2.md) | Xilinx XC7A35T | GPIO JTAG; GPIO UART; PCIe on a Raspberry Pi 5 |
| [SQRL Acorn CLE-215+](https://github.com/enjoy-digital/litex/wiki/Use-LiteX-on-the-Acorn-CLE-215) | [SQRL Acorn and LiteFury](acorn/index.md) | Xilinx XC7A200T | GPIO JTAG (P1); GPIO UART (P2); PCIe through an M.2 slot |
| [LiteFury](https://github.com/RHSResearchLLC/NiteFury-and-LiteFury) and Acorn CLE-101 | [SQRL Acorn and LiteFury](acorn/index.md) | Xilinx XC7A100T | GPIO JTAG (P1); GPIO UART (P2); PCIe through an M.2 slot |
| [Fomu EVT](https://www.crowdsupply.com/sutajio-kosagi/fomu) | [Fomu EVT](fomu-evt.md) | Lattice iCE40UP5K | native USB (DFU); GPIO UART |
| [Tiny Tapeout FPGA demo board](https://tinytapeout.com/guides/fpga-breakout/) | [Tiny Tapeout FPGA demo board](tt-fpga.md) | Lattice iCE40UP5K | USB-C to the RP2350; PMOD HAT |
| [Tiny Tapeout chip demo boards](https://tinytapeout.com/chips/) | [Tiny Tapeout ASIC demo boards](tt-asic.md) | a manufactured Tiny Tapeout chip | USB to the RP2040 or RP2350; PMOD HAT |

```{toctree}
:hidden:

arty-a7
acorn/index
netv2
fomu-evt
tt-fpga
tt-asic
pin-id
butterstick
ulx3s
```
