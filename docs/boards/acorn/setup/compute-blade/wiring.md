---
type: reference
owner: documentation maintainers
reader: someone looking up which wire goes to which pin of a Compute Blade
review: 2026-11-10
---

# Acorn wiring on a Compute Blade

**You have an Acorn in a Compute Blade with a CM4 or CM5 and want to know which wire of the card's two
connectors goes to which pin of the blade's Extension Port and UART header.** What follows from the line
the two cables share, and what the blade must have set for JTAG and for the serial pair, is on [the
blade's pins, shared line and settings](blade-settings.md) and [JTAG on a Compute Blade](../../checks/compute-blade-jtag-by-hand.md). An Acorn on a Raspberry Pi 5 is
wired differently and has [its own page](../rpi-5/wiring.md). To build and fit the cables, follow the
[Compute Blade building guide](cables.md).

## The wiring sheet

The [Compute Blade](https://computeblade.com/) for a CM4 or CM5 does not have
the 40-pin header.

[![Acorn to Compute Blade wiring sheet](../../generated/acorn-wiring-computeblade.png)](../../generated/acorn-wiring-computeblade.svg){.only-light}
[![Acorn to Compute Blade wiring sheet](../../generated/acorn-wiring-computeblade-dark.png)](../../generated/acorn-wiring-computeblade-dark.svg){.only-dark}

Read the sheet from the card's two connectors (P2 and P1, pin 1 at the end nearest the M.2 edge) along each
wire to the blade pin it lands on. The `--pins` numbers on the sheet are GPIO numbers, not printed pin
numbers. Select the sheet for the full-size drawing.

```{include} ../../inc/board-connectors.inc
```

## Pin numbering

The blade prints its own numbers: **1 to 5 down the left column of the Extension
Port, 6 to 10 down the right**, and 1 to 4 from the top on the UART header (the
vendor's "UART Back"). They are not Raspberry Pi header numbers, although the
Extension Port's ten pins are electrically RPi header pins 1-10 in the same
arrangement. This page uses the printed numbers, because those are the ones in
front of you at the bench. The legend above the Extension Port is spelled
"Extention Port" on the board. TX and RX on the UART header are named from the
blade's side.

Every pin of the two headers, by its printed number, is listed under [the blade's connectors and their
GPIOs](blade-settings.md#the-blades-connectors-and-their-gpios).

## P1: JTAG, on the Extension Port

```{include} ../../generated/acorn-blade-p1.md
```

## P2: serial pair, on the UART header

```{include} ../../generated/acorn-blade-p2.md
```

**The J2 wire carries a 470 Ω resistor**, soldered into the wire near its housing end. Why: [the shared line
and the 470 Ω resistor](blade-settings.md#the-shared-line-and-the-470-ω-resistor). Fitting it: [UART
connector 1](uart-wires.md) of the building guide.

Cut the J5 and H5 wires back and insulate them like VCC: the blade's five GPIOs
are JTAG's four plus the serial pair's second line, so none is left for them.
The fpgas.online Acorn design resets J5 and H5 to inputs, so the open ends do no
harm.

## Housings

P1 goes to a 2×5 Dupont housing over the whole Extension Port, and P2 to a 1×4
over the whole UART header. The unused cavities stay empty: Extension Port 1, 5,
6, 7 and 10, and UART 1. No cavity holds two wires.

Use full-length housings, not the shortest that holds the wires. A 2×3 on
Extension Port rows 2-4 also fits one row toward pin 1, which puts the GND wire
on pin 7 (5 V); a 1×3 on UART pins 2-4 also fits one pin toward pin 1, which
puts GND on
UART pin 1 (5 V). Either shorts the blade's 5 V rail, because the Acorn's ground
is the blade's ground through the M.2 slot. A full-length housing has only one
position, but it can still go on turned round — the 2×5 then puts TCK on pin 7,
the 1×4 puts K2 on pin 1, both 5 V — so **mark pin 1 on each housing** and
match it to printed pin 1.

:::{warning}
**Extension Port pins 6 and 7 and UART pin 1 are 5 V and sit inside a housing.
Their cavities must stay empty.**
:::

When a wire does not answer: [Acorn wiring faults on a Compute Blade](../../troubleshooting/compute-blade-wiring.md).
