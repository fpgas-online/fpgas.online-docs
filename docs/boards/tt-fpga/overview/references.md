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

- [Tiny Tapeout demo PCB design](https://github.com/TinyTapeout/tt-demo-pcb): the demo board's hardware repository.
- [Tiny Tapeout PCB specifications](https://tinytapeout.com/specs/pcb/): the demo board's connectors and signals, for the TT04 to TT08 boards.
- [Tiny Tapeout FPGA breakout guide](https://tinytapeout.com/guides/fpga-breakout/): the guide to the FPGA breakout.
- [Tiny Tapeout FPGA demo repository](https://github.com/efabless/tt-fpga-demo): a template that builds an FPGA bitstream from a Wokwi design.
- [Tiny Tapeout](https://tinytapeout.com): the project's own site.

## LiteX support

The board does not have a dedicated LiteX platform file in litex-boards. Designs target the iCE40UP5K with a custom pin constraint file matching the Tiny Tapeout I/O interface. The iCE40UP5K is the same FPGA as on the Fomu.

- The LiteX platform definition of the board: [`tt_fpga_platform.py`](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/designs/_shared/tt_fpga_platform.py)
- The clock and reset generator: [`tt_fpga_crg.py`](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/designs/_shared/tt_fpga_crg.py)

## On this site

- [PMOD interface](../../pmod/index.md): the PMOD types.
- [Tiny Tapeout PMOD layouts](../../pmod/tinytapeout.md): the Tiny Tapeout PMOD connector layouts.
- [Raspberry Pi PMOD HAT](../../pmod/rpi-hat.md): the adapter between the board's PMOD connectors and the Pi.
