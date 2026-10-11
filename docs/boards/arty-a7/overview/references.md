---
type: reference
owner: documentation maintainers
reader: someone looking for the documents behind the Arty A7 pages
review: 2026-11-10
---

# Arty A7 references

**You want the documents and LiteX files behind the Arty A7 pages.**

## LiteX integration

Property names a part of the LiteX support and Value gives it. The values are from the [LiteX platform file](https://github.com/litex-hub/litex-boards/blob/master/litex_boards/platforms/digilent_arty.py).

| Property | Value |
|----------|-------|
| Platform module | `litex_boards.platforms.digilent_arty` |
| Target module | `litex_boards.targets.digilent_arty` |
| Default clock | `clk100` (100 MHz, pin E3) |
| Toolchain | Vivado (proprietary) or openXC7 (open source) |

## Outside documents

- [Digilent Arty A7 reference manual](https://digilent.com/reference/programmable-logic/arty-a7/reference-manual): the board's own manual.
- [Digilent's Arty A7 reference page](https://digilent.com/reference/programmable-logic/arty-a7/start): the documents for both the A7-35T and the A7-100T.
- [LiteX platform file for the Arty A7](https://github.com/litex-hub/litex-boards/blob/master/litex_boards/platforms/digilent_arty.py): the board's pins and resources.

## On this site

- [PMOD interface](../../pmod/index.md): the PMOD types the board's connectors follow.
- [Raspberry Pi PMOD HAT](../../pmod/rpi-hat.md): the adapter between the board's PMOD cables and the Pi.
