# Tiny Tapeout FPGA board on a Raspberry Pi: fitting

**You have a Tiny Tapeout FPGA demo board, a Raspberry Pi, a Digilent Pmod HAT, three Pmod cables, a USB-C
cable and a camera, and want to join them.**

**Not yet run by us on this hardware as a procedure.** Only the cabling (step 3) is recorded in any detail.
The other steps say what is recorded and what is not.

## 1. Power off

```{include} ../power-off.inc
```

## 2. The Pmod HAT on the Raspberry Pi

**Not yet written, and no picture yet.** The record says only that the HAT goes on the Raspberry Pi's 40-pin
header. What the HAT is and which GPIO each of its pins is: [Raspberry Pi PMOD HAT](../../pmod/rpi-hat.md).

## 3. The three Pmod cables and the USB-C cable

**Before a cable goes in, find pin 1 on both connectors** (the paragraph "Pin 1 on the picture" below): a
2x6 cable turned round puts 3.3 V on signal pins. What cable to use, and whether its 3.3 V pins may be
connected, is not recorded (the list "The cables" below): nothing here tells you which to choose.

Where the text below says `tt-fpga-sources.md`, that is the [sources page](../wiring/sources.md).

```{include} ../generated/tt-fpga-cables.md
:relative-images:
:relative-docs: tt-fpga-
```

With the USB-C cable in and the demo board running its firmware, the Raspberry Pi sees the board's
microcontroller as a USB serial device:

**USB device:** `/dev/ttyACM0` (VID:PID `2e8a:0005` — MicroPython Board in FS
mode), with a udev symlink **`/dev/ttboard`** that the Pi daemon opens (the symlink comes with the
`fpgas-online-tt` package: [Serial consoles](../../../setup/pi.md#serial-consoles)).

## 4. The camera

**Not yet written, and no picture yet.** The record says only that each host has an ov5647 camera publishing
a live feed of the board. How it is mounted, cabled and aimed is not recorded. The software that publishes the
feed: [Camera](../../../setup/pi.md#camera).

## Next

Check the result: [verifying 1](verifying-1.md).
