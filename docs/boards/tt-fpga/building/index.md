# Tiny Tapeout FPGA board on a Raspberry Pi: building overview

**You have a Tiny Tapeout FPGA demo board, a Raspberry Pi and a Digilent Pmod HAT, and want to join them, and
then check that the wiring is right.**

**This guide is not yet a full procedure.** It holds what is recorded about how the boards at welland are put
together; nothing in it was written from an assembly we watched. Each step that has no procedure or no
picture says so in place. Not yet run by us on this hardware as a guide.

## What you will have

Each RPi connects to a TT FPGA board via USB-C, has a Digilent
[Pmod HAT](../../pmod/rpi-hat.md) for GPIO-level control of the TT I/O pins, and an
ov5647 camera publishing a live feed of the board. RPis are powered and
networked through PoE switches at each site. The camera and the power are not in the picture below, which
shows the Pmod cables and the USB-C cable only.

[![Which Pmod header of the demo board goes to which port of the Pmod HAT](../generated/tt-fpga-pmod-cables.png)](../generated/tt-fpga-pmod-cables.svg)

Three 12-pin Pmod cables, each pin 1 to pin 1 (INPUT to JA, BIDIR to JB, OUTPUT to JC), and one USB-C cable
from the demo board to a USB port of the Raspberry Pi.

## The order of work

1. [Parts](bom.md): what is known and not known about the parts.
2. [Fitting](fitting.md): power off, the HAT on the Raspberry Pi, the three Pmod cables, the USB-C cable, the camera.
3. [Verifying 1](verifying-1.md): install the packages, run the check and read its result.
4. [Verifying 2](verifying-2.md): from a failing line of the check to the cable at fault.

## The pages of this guide

```{toctree}
:maxdepth: 1

What is known about the parts <bom>
Fitting <fitting>
Verifying 1: install and run the check <verifying-1>
Verifying 2: from a failing line to the cable <verifying-2>
```

## What is not known about the cables

What cable joins the demo board's headers to the Pmod HAT on our boards, and whether its pins 6 and 12
(3.3 V on both boards) are connected, is not recorded. The question was asked of the boards' owner on
6 October 2026 and is not yet answered: [which cable goes where](../wiring/cables.md). Until it is, this guide
names no cable to buy and gives no instruction about the 3.3 V pins.
