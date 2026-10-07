# Tiny Tapeout FPGA board on a Raspberry Pi: fitting 2, the cables, power on and the camera

**You have fitted the demo board on its plate and the HAT on the Raspberry Pi ([fitting 1](fitting.md)), and
now join them with the cables, power the Pi on and fit the camera.** Not yet run by us on this hardware as a
procedure; each step says where it comes from.

## 4. The three Pmod cables and the USB-C cable

**Before a cable goes in, find pin 1 on both connectors** (the paragraph "Pin 1 on the picture" below): a
cable turned round puts ground on signal pins. The cable's 3.3 V pins are expected not to be connected, so the
two boards' 3.3 V supplies are not joined; whether it has 10 or 12 wires is not known: [the
cables](index.md#the-cables-33-v-not-connected).

**Pin 1 on the demo board** (from Tiny Tapeout's KiCad files: the square pad under i0, b0 or o0; the small L
mark on each socket's outline is beside pin 6, not pin 1):

```{image} /_static/mechanical/tt-demoboard-v3.2-pmods-light.svg
:alt: The demo board's three Pmod sockets from above, board edge at the bottom: pin 1 is the square pad under i0, b0 or o0; the L corner mark beside pin 6 is labelled not pin 1; the 3.3 V and ground columns named
:class: only-light
```

```{image} /_static/mechanical/tt-demoboard-v3.2-pmods-dark.svg
:alt: The demo board's three Pmod sockets from above, board edge at the bottom: pin 1 is the square pad under i0, b0 or o0; the L corner mark beside pin 6 is labelled not pin 1; the 3.3 V and ground columns named
:class: only-dark
```

**Pin 1 on the Pmod HAT** (from Digilent's photograph and manual: the square pad with a printed 1):

```{image} /_static/mechanical/digilent-pmod-hat-ports-light.svg
:alt: The Digilent Pmod HAT from above, its 40-pin header at the top: JA, JB and JC each with pin 1, the square pad with the printed 1, and the 3V3 and GND end
:class: only-light
```

```{image} /_static/mechanical/digilent-pmod-hat-ports-dark.svg
:alt: The Digilent Pmod HAT from above, its 40-pin header at the top: JA, JB and JC each with pin 1, the square pad with the printed 1, and the 3V3 and GND end
:class: only-dark
```

**Pin 1 on the cable itself.** A ribbon cable's IDC housing usually has a small triangle moulded on it at
pin 1's end, and wire 1 is the marked one: a coloured stripe on a grey cable, usually the brown wire on a
rainbow one. These are the common marks, not checked on our cables. Put wire 1 on pin 1 at both ends. Seen from the front of a
right-angle socket, where the cable goes in, pins 1 to 6 are the upper row of openings: the row wired to the
square-pad row (from how a right-angle socket is built and the makers' drawings; not checked on our boards). A
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
