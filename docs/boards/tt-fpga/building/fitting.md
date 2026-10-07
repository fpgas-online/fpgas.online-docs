# Tiny Tapeout FPGA board on a Raspberry Pi: fitting 1, the plate and the HAT

**You have a Tiny Tapeout FPGA demo board, a Raspberry Pi, a Digilent Pmod HAT, three Pmod cables, a USB-C
cable and a camera, and want to join them.** This page: power off, the board onto its mounting plate, the HAT
onto the Pi (steps 1 to 3); then [fitting 2](fitting-2.md): the cables, power on, the camera (steps 4 to 6).

**Not yet run by us on this hardware as a procedure.** The plate and the HAT (steps 2 and 3) are written from
the makers' drawings and manuals. Each step says where it comes from.

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

## Next

The cables, power on and the camera: [fitting 2](fitting-2.md).
