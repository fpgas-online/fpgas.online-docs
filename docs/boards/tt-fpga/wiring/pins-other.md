# Tiny Tapeout FPGA board wiring: the loading pins, display, clock, reset and LED

**You have a Tiny Tapeout FPGA demo board on a Raspberry Pi with a Digilent Pmod HAT, and want the pins that
are not one of the 24 cabled signals: the pins that load the FPGA, the seven-segment display, the clock, the
reset and the LED.**

The RP2350 GPIO numbers on this page follow Tiny Tapeout's specification for the version 3 demo board, as [Tiny Tapeout PMOD layouts](../../pmod/tinytapeout.md#rp2350-gpio-mapping-demo-board-v3-tt09) gives it.

## The pins no cable carries, and the display

```{include} ../generated/tt-fpga-pins-other.md
:relative-images:
:relative-docs: tt-fpga-
:start-after: "the clock, the reset and the LED."
:end-before: "**Finding the headers.**"
```

Which header goes to which port, with the picture, pin 1 and how to find the headers: [which cable goes where](cables.md).

```{include} ../generated/tt-fpga-pins-other.md
:relative-images:
:relative-docs: tt-fpga-
:start-after: "How the sockets and cables are made, and what is not yet known about the cables: see [the cables page](/boards/tt-fpga/wiring/cables.md)."
```
