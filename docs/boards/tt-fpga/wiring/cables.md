# Tiny Tapeout FPGA board wiring: which cable goes where

**You have a Tiny Tapeout FPGA demo board and a Raspberry Pi with a Digilent Pmod HAT, and want to know which
header of the demo board is cabled to which port of the HAT.** Each wire is on the three pages after this
one: [`ui_in` and `uo_out`](pins-ui-uo.md), [`uio` and the serial port](pins-uio-uart.md), [the other
pins](pins-other.md). To fit the cables, follow the [building guide](../building/index.md).

```{include} ../power-off.inc
```

```{include} ../generated/tt-fpga-cables.md
:relative-images:
:relative-docs: tt-fpga-
:start-after: "This part shows which cable goes where."
:end-before: "**The cables**"
```

```{include} ../pin1-measured.inc
```

**The cables** on our boards are 10-pin ribbon cables with the 3.3 V pin left out (Tim Ansell, 7 October
2026); as we read Tim Ansell's answer of 7 October 2026, each cable sits on pins 1 to 5 and 7 to 11 and leaves the 3.3 V column (pins 6 and 12) free; not checked by us on a board. What is known about them is in one place, at the
top of the [building overview](../building/index.md#the-cables-10-pin-ribbon-no-33-v-wire).

```{include} ../generated/tt-fpga-cables.md
:start-after: "Neither the wires nor any pin 1 mark can be made out."
```
