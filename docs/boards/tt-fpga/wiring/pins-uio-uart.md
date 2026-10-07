# Tiny Tapeout FPGA board wiring: uio and the serial port

**You have a Tiny Tapeout FPGA demo board cabled to a Raspberry Pi with a Digilent Pmod HAT, and want to
follow one of the eight `uio` signals, or the design's serial port, from the FPGA pin to the Raspberry Pi.**

Where the text below says `tt-fpga-cables.md`, that is [which cable goes where](cables.md); where it says
`tt-fpga-sources.md`, that is the [sources page](sources.md).

The RP2350 GPIO numbers on this page follow Tiny Tapeout's specification for the version 3 demo board, as [Tiny Tapeout PMOD layouts](../../pmod/tinytapeout.md#rp2350-gpio-mapping-demo-board-v3-tt09) gives it.

## The BIDIR header and the serial port

```{include} ../generated/tt-fpga-pins-uio-uart.md
:relative-images:
:relative-docs: tt-fpga-
```
