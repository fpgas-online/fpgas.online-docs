---
type: explanation
owner: documentation maintainers
reader: someone with an Acorn-family card who wants to know what is on it
review: 2026-11-10
---

# The Acorn card

This page shows the Acorn as a whole and says what each part of the card is for. It is for someone holding an
SQRL Acorn CLE-215+, CLE-215 or CLE-101, or a LiteFury or NiteFury. What differs between the cards is on
[Acorn variants](../which-one.md); the figures and pins of each part are on [Acorn specifications](specifications.md).

:::{admonition} Figure to come
:class: placeholder

The whole Acorn, top and bottom, with numbered callouts that match the sections of this page. Tracked in ISSUE-01.
:::

## The connector end

![The connector end of a LiteFury (the Acorn PCB), underside: sockets P1 and P2, pin 1 marked, and the half-round pad.](../generated/acorn-card-underside.png){.only-light}

![The connector end of a LiteFury (the Acorn PCB), underside: sockets P1 and P2, pin 1 marked, and the half-round pad.](../generated/acorn-card-underside-dark.png){.only-dark}

The two 6-pin sockets P1 and P2 sit at the end of the card that the two cables plug into. P1 carries JTAG and P2 carries
the serial pair and spare pins. The card has no USB serial adapter of its own. P2 is therefore wired to the host's own
GPIO UART with an adapted Pico-EZmate cable. The wiring is on the pages for [a Raspberry Pi 5](../setup/rpi-5/wiring.md)
and for [a Compute Blade](../setup/compute-blade/wiring.md).

## The FPGA and its memory

The card carries a Xilinx Artix-7 FPGA, DDR3 SDRAM, and a quad-SPI flash chip. The flash holds the images that
configure the FPGA when the card powers on. How an image reaches the FPGA is on [Programming an Acorn](programming.md).

## The PCIe edge and the LEDs

The card plugs into an M.2 M-key slot, which gives it PCIe and its power. The card also has four user LEDs and a 200 MHz system clock. The
pins of each are in [Acorn specifications](specifications.md).
