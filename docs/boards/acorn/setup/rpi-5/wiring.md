---
type: reference
owner: documentation maintainers
reader: someone looking up which wire goes to which pin of a Raspberry Pi 5
review: 2026-11-10
---

# Acorn wiring on a Raspberry Pi 5

**You have an Acorn on a Raspberry Pi 5 with an M.2 HAT and want to know which wire of the card's two
connectors goes to which pin of the Pi's 40-pin header.** What the Pi must have set for those wires (the
serial port, the GPIO chip for JTAG, the kernel console) is on [the Pi's settings](pi-settings.md).
An Acorn in a Compute Blade is wired differently and has [its own page](../compute-blade/wiring.md). To build
and fit the cables, follow the [Raspberry Pi 5 building guide](cables.md).

## The wiring sheet

[![Acorn to Raspberry Pi 5 wiring sheet](../../generated/acorn-wiring-pi5.png)](../../generated/acorn-wiring-pi5.svg){.only-light}
[![Acorn to Raspberry Pi 5 wiring sheet](../../generated/acorn-wiring-pi5-dark.png)](../../generated/acorn-wiring-pi5-dark.svg){.only-dark}

Read it from the right: the card's two connectors (P2 above, P1 below, pin 1 at the end nearest the M.2
edge), each wire, and the 40-pin header pin it lands on. A dashed outline is one Dupont housing and a red
cross is a pin or a wire that nothing goes on. The `--pins` numbers at the top right are GPIO numbers, not
header pin numbers. Select the sheet for the full-size drawing.

```{include} ../../inc/board-connectors.inc
```

## P2: serial pair and spare GPIOs

P2 goes to a 2×3 Dupont housing on header pins 5-10. The cavity over pin 9
(GND) stays empty.

```{include} ../../generated/acorn-pi5-p2.md
```

## P1: JTAG

P1 goes to a 2×4 Dupont housing on header pins 19-26. The cavities over pins 20
(GND), 22 (GPIO25) and 26 (GPIO7) stay empty.

```{include} ../../generated/acorn-pi5-p1.md
```

When a wire does not answer: [Acorn wiring faults on a Raspberry Pi 5](../../troubleshooting/rpi-5-wiring.md).
