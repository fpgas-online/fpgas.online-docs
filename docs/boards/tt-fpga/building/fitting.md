# Tiny Tapeout FPGA board on a Raspberry Pi: fitting

**You have a Tiny Tapeout FPGA demo board, a Raspberry Pi, a Digilent Pmod HAT, three Pmod cables, a USB-C
cable and a camera, and want to join them.**

**Not yet run by us on this hardware as a procedure.** The plate, the HAT and the camera (steps 2, 3 and 6)
are written from the makers' drawings and manuals; the cabling (step 4) is also measured on the boards at
welland. Each step says where it comes from.

## 1. Power off

```{include} ../power-off.inc
```

## 2. The demo board on its mounting plate

The demo board stands on the fpgas.online Tiny Tapeout mounting plate. The boards at welland do not yet;
they move onto it soon, and these pages are written for the plate (Tim Ansell, 7 October 2026). Not yet run by
us as a procedure; every figure is from the drawings on [the fitting guide](../overview/mechanical.md) and [the
plate](../overview/plate.md) pages.

```{image} /_static/mechanical/tt-generic-mounting-plate-fitting-guide-v3-light.svg
:alt: The version 3 demo boards, DB ETR v3.2 and v3.3, on the mounting plate: the holes each uses in red (A1 and D1; D1 and E1), its outline, its USB-C connector in amber, the Pmod fields and the plate fixings
:class: only-light
```

```{image} /_static/mechanical/tt-generic-mounting-plate-fitting-guide-v3-dark.svg
:alt: The version 3 demo boards, DB ETR v3.2 and v3.3, on the mounting plate: the holes each uses in red (A1 and D1; D1 and E1), its outline, its USB-C connector in amber, the Pmod fields and the plate fixings
:class: only-dark
```

1. **Fit the plate to its chassis first**, by the plate's own fixings P1 to P6 (4.3 mm holes, for M4): the
   board overhangs them once it is on.
2. **Find your board in the picture** (the version 3 boards; every revision is on [the fitting
   guide](../overview/mechanical.md)) by its board revision (DB ETR v3.2 for the version 3 board that has
   reported itself, `TTDBv3 [3.2]`) and **put an M3 × 8 mm standoff in each hole it uses** (red in the
   picture): on DB ETR v3.2, holes A1 and D1; on DB ETR v3.3, D1 and E1.
3. **Put the board on the standoffs** with its three Pmod sockets along the plate's front (lower) edge, as
   drawn, and fix it with M3 screws through its 3.4 mm holes. **Keep that edge clear**: the sockets' bodies
   overhang it by 2.78 mm.

## 3. The Pmod HAT on the Raspberry Pi

1. **Find pin 1 on the Raspberry Pi's 40-pin header**: its solder pad on the underside of the board is the
   square one.
2. **Press the HAT's 2x20 socket (J1, on its underside) onto the Pi's 40 pins, pin 1 to pin 1**, so that the
   HAT lies over the Pi. Its J1 pin 1 is at the corner on the JA side.
3. **Fix it with its four corner standoffs and screws.**

From Digilent's Pmod HAT Adapter Reference Manual, Rev. B, and its photographs; not yet done by us at a
bench. Which Raspberry Pi GPIO each pin of the HAT's three ports is: [Raspberry Pi PMOD
HAT](../../pmod/rpi-hat.md), another page, not in this set. A drawing of the HAT's ports with pin 1 marked is
being made from the manual.

## 4. The three Pmod cables and the USB-C cable

**Before a cable goes in, find pin 1 on both connectors** (the paragraph "Pin 1 on the picture" below): a
cable turned round puts ground on signal pins. The cable's 3.3 V pins are expected not to be connected, so the
two boards' 3.3 V supplies are not joined; whether it has 10 or 12 wires is not known: [the
cables](index.md#the-cables-33-v-not-connected).

**Pin 1 on the cable itself.** A ribbon cable's IDC housing usually has a small triangle moulded on it at
pin 1's end, and wire 1 is the marked one: a coloured stripe on a grey cable, usually the brown wire on a
rainbow one. These are the common marks, not checked on our cables. Put wire 1 on pin 1 at both ends. A
10-wire cable goes on pins 1 to 5 and 7 to 11, the pin 1 end, and leaves the 3.3 V column (pins 6 and 12)
free.

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

## 5. Power on, and the first check

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

## 6. The camera

The camera is a Raspberry Pi Camera Module v1.3 with its stock 65 degree lens. It hangs lens down over the
board from a printed holder, `TT-MP-CAM65`, which bolts onto the mounting plate. Where the lens goes, the drawing and
the holder's open item: [the camera over the mounting plate](../overview/camera.md). The holder is a design in
[fpgas.online-mechanical](https://github.com/fpgas-online/fpgas.online-mechanical/tree/main/tinytapeout/camera_holder); it has not yet been built or used by us. In this order:

1. **The holder onto the plate.** Its two feet sit over the plate's own M4 fixings along its left and right
   edges and are clamped by the same screws: on a plate bolted to a chassis, the plate's own screws, 5 mm
   longer. It goes on no other way.
2. **The camera's flat cable into the camera first.** The connector's latch is out of reach once the camera
   is on its carrier.
3. **The camera onto its carrier**, with four M2 × 10 screws, heads on the lens side, into nuts in the
   carrier's hex pockets. The camera's holes may need opening with a 2.0 mm drill for an M2 to pass.
4. **The carrier onto the holder's beam**, on its four M3 fixings, with the camera's long side along the
   plate's left-to-right. Which way the sensor's rows run is not published, so look at the first picture: if
   the board does not fill it side to side, turn the carrier a quarter turn. The lens does not move.
5. **The cable up and back over the beam**, so that it does not hang into the picture.

The software that publishes the camera's feed: [Camera](../../../setup/pi.md#camera).


## Next

Check the result: [verifying 1](verifying-1.md).
