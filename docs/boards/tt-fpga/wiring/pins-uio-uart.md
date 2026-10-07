# Tiny Tapeout FPGA board wiring: uio and the serial port

**You have a Tiny Tapeout FPGA demo board cabled to a Raspberry Pi with a Digilent Pmod HAT, and want to
follow one of the eight `uio` signals, or the design's serial port, from the FPGA pin to the Raspberry Pi.**

The RP2350 GPIO numbers on this page follow Tiny Tapeout's specification for the version 3 demo board, as [Tiny Tapeout PMOD layouts](../../pmod/tinytapeout.md#rp2350-gpio-mapping-demo-board-v3-tt09) gives it.

## The BIDIR header and the serial port

Which header goes to which port, with the picture, pin 1 and how to find the headers: [which cable goes where](cables.md).

```{include} ../generated/tt-fpga-pins-uio-uart.md
:relative-images:
:relative-docs: tt-fpga-
:start-after: "How the sockets and cables are made, and what is not yet known about the cables: see [the cables page](/boards/tt-fpga/wiring/cables.md)."
```
