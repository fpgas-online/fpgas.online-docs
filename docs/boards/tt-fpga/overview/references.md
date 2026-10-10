---
type: reference
owner: documentation maintainers
reader: someone looking for the documents behind the board pages
review: 2026-11-10
---

# Tiny Tapeout FPGA demo board references

**You want the outside documents, repositories and LiteX files behind the Tiny Tapeout FPGA demo board pages.**

The pages of this site that these documents feed are listed on [Tiny Tapeout FPGA demo board overview](index.md).

## Tiny Tapeout documents

- Tiny Tapeout demo PCB design: <https://github.com/TinyTapeout/tt-demo-pcb>
- Tiny Tapeout PCB specifications: <https://tinytapeout.com/specs/pcb/>
- Tiny Tapeout FPGA Breakout Guide: <https://tinytapeout.com/guides/fpga-breakout/>
- Tiny Tapeout FPGA Demo repository: <https://github.com/efabless/tt-fpga-demo>
- Tiny Tapeout main site: <https://tinytapeout.com>

## LiteX support

The board does not have a dedicated LiteX platform file in litex-boards. Designs target the iCE40UP5K with a custom pin constraint file matching the Tiny Tapeout I/O interface. The iCE40UP5K is the same FPGA as on the Fomu.

- The LiteX platform definition of the board: [`tt_fpga_platform.py`](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/designs/_shared/tt_fpga_platform.py)
- The clock and reset generator: [`tt_fpga_crg.py`](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/designs/_shared/tt_fpga_crg.py)

## PMOD pages

- PMOD Interface Specification: [PMOD interface](../../pmod/index.md)
- Tiny Tapeout PMOD connector standards: [Tiny Tapeout PMOD layouts](../../pmod/tinytapeout.md)
- PMOD HAT adapter for the Raspberry Pi: [Raspberry Pi PMOD HAT](../../pmod/rpi-hat.md)
