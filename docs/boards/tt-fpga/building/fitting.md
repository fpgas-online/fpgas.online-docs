# Tiny Tapeout FPGA board on a Raspberry Pi: fitting

**You have a Tiny Tapeout FPGA demo board, a Raspberry Pi, a Digilent Pmod HAT, three Pmod cables, a USB-C
cable and a camera, and want to join them.**

**Not yet run by us on this hardware as a procedure.** Only the cabling (step 3) is recorded in any detail.
The other steps say what is recorded and what is not. If the demo board goes on the fpgas.online mounting
plate, which holes it uses is on [the mechanical page](../overview/mechanical.md).

## 1. Power off

```{include} ../power-off.inc
```

## 2. The Pmod HAT on the Raspberry Pi

**Not yet written, and no picture yet.** The record says only that the HAT goes on the Raspberry Pi's 40-pin
header. Which Raspberry Pi GPIO each pin of the HAT's three ports is, and what each port's pins are for, is on
[Raspberry Pi PMOD HAT](../../pmod/rpi-hat.md), another page, not in this set; it has no fitting steps
either. Every wire this board uses is on the wiring pages of this set.

## 3. The three Pmod cables and the USB-C cable

**Before a cable goes in, find pin 1 on both connectors** (the paragraph "Pin 1 on the picture" below): a
cable turned round puts ground on signal pins. The cable's 3.3 V pins are expected not to be connected, so the
two boards' 3.3 V supplies are not joined; whether it has 10 or 12 wires is not known: [the
cables](index.md#the-cables-33-v-not-connected).

```{include} ../generated/tt-fpga-cables.md
:relative-images:
:relative-docs: tt-fpga-
:start-after: "This part shows which cable goes where."
:end-before: "**Not checked by us on a board:**"
```

```{include} ../pin1-measured.inc
```

How the sockets on both boards are made, from the makers' documents: [which cable goes
where](../wiring/cables.md).

```{include} ../generated/tt-fpga-cables.md
:start-after: "Neither the wires nor any pin 1 mark can be made out."
:end-before: "The USB-C cable carries"
```

With the USB-C cable in and the demo board running its firmware, the Raspberry Pi sees the board's
microcontroller as a USB serial device: `/dev/serial/by-id/usb-MicroPython_Board_in_FS_mode_<serial>-if00`,
where `<serial>` is its USB serial number, and `/dev/ttboard` on a Pi with the `fpgas-online-tt` package (its
udev rule: [Serial consoles](../../../setup/pi.md#serial-consoles), another page, not in this set). The boards
at welland were seen as `/dev/ttyACM0` (3 September 2026); that name is only what the kernel gave them, not
the board's name.

```{include} ../usb-ids.inc
```

## 4. Power on, and the first check

Plug the demo board's USB-C cable into the Raspberry Pi, then power the Raspberry Pi. When it is up, log in
and look for the demo board's serial port:

```console
$ ls /dev/serial/by-id/
$ ls /dev/ttyACM*
```

What to expect, from the records (the boards at welland, 3 September 2026, and [Tiny Tapeout ASIC demo
boards](../../tt-asic.md#connection-to-the-pi)): in `/dev/serial/by-id/` a name of the form
`usb-MicroPython_Board_in_FS_mode_<serial>-if00`, where `<serial>` is the microcontroller's USB serial
number, and a `/dev/ttyACM` device (`/dev/ttyACM0` on those boards). `/dev/ttboard` appears only on a Pi with the `fpgas-online-tt` package. What a board in its boot
loader shows here is not recorded (the check reports it as `2e8a:0003`).

## 5. The camera

**Not yet written, and no picture yet.** The record says only that each host has an ov5647 camera publishing
a live feed of the board. How it is mounted, cabled and aimed is not recorded. The software that publishes the
feed: [Camera](../../../setup/pi.md#camera).

## Next

Check the result: [verifying 1](verifying-1.md).
