# Tiny Tapeout FPGA board: resources and links

**You want the documents, repositories and sources behind the Tiny Tapeout FPGA board pages: Tiny Tapeout's
own documents, our repositories, and where the generated wiring comes from.**

## Where the wiring comes from

The wiring has one source: the table `wiring.toml` in `docs/wiring/tt-fpga/` of
[fpgas.online-test-designs](https://github.com/fpgas-online/fpgas.online-test-designs) (added by
[its pull request 153](https://github.com/fpgas-online/fpgas.online-test-designs/pull/153)). The cable
picture and the pin tables on the [wiring pages](../wiring/cables.md) are generated from it, and a test there
holds the test code's own numbers to it. Where each fact in it comes from, and what nobody has checked:
[sources](../wiring/sources.md).

## LiteX Integration

| Property | Value |
|----------|-------|
| FPGA | iCE40UP5K (same as Fomu) |
| Toolchain | Yosys + nextpnr-ice40 (open source, IceStorm flow) |

The TT FPGA board does not have a dedicated LiteX platform file in litex-boards.
Designs target the iCE40UP5K with a custom pin constraint file matching the
TinyTapeout I/O interface.

## References

- TinyTapeout Demo PCB design: <https://github.com/TinyTapeout/tt-demo-pcb>
- TinyTapeout PCB specifications: <https://tinytapeout.com/specs/pcb/>
- TinyTapeout FPGA Breakout Guide: <https://tinytapeout.com/guides/fpga-breakout/>
- TT FPGA Demo repository: <https://github.com/efabless/tt-fpga-demo>
- TinyTapeout main site: <https://tinytapeout.com>
- [TT FPGA LiteX platform definition](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/designs/_shared/tt_fpga_platform.py)
- PMOD Interface Specification: [PMOD interface](../../pmod/index.md)
- TinyTapeout PMOD Connector Standards:
  [Tiny Tapeout PMOD layouts](../../pmod/tinytapeout.md)
- PMOD HAT Adapter (RPi): [Raspberry Pi PMOD HAT](../../pmod/rpi-hat.md)
- The board's page in fpgas.online-test-designs:
  [`docs/hardware/tt-fpga.md`](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/docs/hardware/tt-fpga.md)
- `fpgas-tt`, the daemon on the Pi that the public site uses: <https://github.com/fpgas-online/fpgas.online-tt>;
  how it is installed: [The Tiny Tapeout stack](../../../setup/tinytapeout.md)
- The board with a chip in place of the FPGA: [Tiny Tapeout ASIC demo boards](../../tt-asic.md)
