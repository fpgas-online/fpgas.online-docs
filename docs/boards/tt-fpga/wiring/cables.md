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

**The cables** themselves are the open question of this board: which cable is fitted, and whether its 3.3 V
pins are connected, is not recorded (asked on 6 October 2026, not yet answered). What is known about them is
in one place, at the top of the [building overview](../building/index.md#the-open-question-which-cable-and-its-33-v-pins).

```{include} ../generated/tt-fpga-cables.md
:start-after: "Neither the wires nor any pin 1 mark can be made out."
```
