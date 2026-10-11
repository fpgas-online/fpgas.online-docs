---
type: reference
owner: documentation maintainers
reader: someone looking up which wire goes to which pin of a Raspberry Pi 5
review: 2026-11-10
---

# Acorn wiring on a Raspberry Pi 5

This page is for someone with an Acorn on a Raspberry Pi 5 with an M.2 HAT. It lists which wire of the card's two connectors goes to which pin of the Pi's 40-pin header. The settings the Pi needs for those wires are on [the Pi's settings](pi-settings.md). An Acorn in a Compute Blade is wired differently and has [its own page](../compute-blade/wiring.md). To build and fit the cables, follow [The two cables on a Raspberry Pi 5](cables.md).

## The wiring sheet

[![Acorn to Raspberry Pi 5 wiring sheet](../../generated/acorn-wiring-pi5.png)](../../generated/acorn-wiring-pi5.svg){.only-light}
[![Acorn to Raspberry Pi 5 wiring sheet](../../generated/acorn-wiring-pi5-dark.png)](../../generated/acorn-wiring-pi5-dark.svg){.only-dark}

The `--pins` numbers at the top right of the sheet are GPIO numbers, not header pin numbers. A dashed outline is one Dupont housing, and a red cross is a pin or a wire that nothing goes on. Select the sheet for the full-size drawing.

```{include} ../../inc/board-connectors.inc
```

## P2: serial pair and spare GPIOs

P2 goes to a 2×3 Dupont housing on header pins 5-10, and the cavity over pin 9 (GND) stays empty. The outline in the header picture is the whole housing. Each row is one wire: a P2 pin, the header pin it lands on, its GPIO and the direction.

![The Acorn's connector end from below, with socket P2 and its pin 1 marked; P1 and the pad greyed](../../views/acorn.bottom.p2.png){.only-light}

![The Acorn's connector end from below, with socket P2 and its pin 1 marked; P1 and the pad greyed](../../views/acorn.bottom.p2-dark.png){.only-dark}

![The M.2 HAT's 40-pin header from above, with pins 5 to 10 marked: where the 2×3 housing goes](../../views/pi5-hat.top.pins-5-10.png){.only-light width="400px"}

![The M.2 HAT's 40-pin header from above, with pins 5 to 10 marked: where the 2×3 housing goes](../../views/pi5-hat.top.pins-5-10-dark.png){.only-dark width="400px"}

```{include} ../../generated/acorn-pi5-p2.md
```

## P1: JTAG

P1 goes to a 2×4 Dupont housing on header pins 19-26. The cavities over pins 20 (GND), 22 (GPIO25) and 26 (GPIO7) stay empty. The outline in the header picture is the whole housing. Each row is one wire: a P1 pin, the header pin it lands on, its GPIO and the direction.

![The Acorn's connector end from below, with socket P1 and its pin 1 marked; P2 and the pad greyed](../../views/acorn.bottom.p1.png){.only-light}

![The Acorn's connector end from below, with socket P1 and its pin 1 marked; P2 and the pad greyed](../../views/acorn.bottom.p1-dark.png){.only-dark}

![The M.2 HAT's 40-pin header from above, with pins 19 to 26 marked: where the 2×4 housing goes](../../views/pi5-hat.top.pins-19-26.png){.only-light width="400px"}

![The M.2 HAT's 40-pin header from above, with pins 19 to 26 marked: where the 2×4 housing goes](../../views/pi5-hat.top.pins-19-26-dark.png){.only-dark width="400px"}

```{include} ../../generated/acorn-pi5-p1.md
```

When a wire does not answer: [Acorn wiring faults on a Raspberry Pi 5](../../troubleshooting/rpi-5-wiring.md).
