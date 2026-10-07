# Tiny Tapeout FPGA board wiring: ui_in and uo_out, wire by wire

**You have a Tiny Tapeout FPGA demo board cabled to a Raspberry Pi with a Digilent Pmod HAT, and want to
follow one of the design's eight inputs or eight outputs from the FPGA pin to the Raspberry Pi's GPIO.**

The demo board's microcontroller is on these same signals; its GPIO numbers for them are on [the loading
pins, display, clock, reset and LED](pins-other.md#the-same-24-signals-at-the-microcontroller), from Tiny
Tapeout's specification as [Tiny Tapeout PMOD
layouts](../../pmod/tinytapeout.md#rp2350-gpio-mapping-demo-board-v3-tt09) gives it.

## The INPUT and OUTPUT headers

```{include} ../generated/tt-fpga-pins-ui-uo.md
:relative-images:
:relative-docs: tt-fpga-
```
