---
type: explanation
owner: documentation maintainers
reader: someone with an Acorn-family card who wants to know what is on it
review: 2026-11-10
---

# The Acorn card

**You have a SQRL Acorn CLE-215+, CLE-215 or CLE-101 (or a LiteFury or NiteFury) and want to know what the card is.**
What differs between the cards of the family is on [Acorn variants](../which-one.md); the two connectors and their wires
are on the wiring pages, [on a Raspberry Pi 5](../setup/rpi-5/wiring.md) and [on a Compute
Blade](../setup/compute-blade/wiring.md).

The SQRL Acorn CLE-215+ is an M.2 form factor PCIe FPGA accelerator card,
pin-compatible with the [NiteFury and
LiteFury](https://github.com/RHSResearchLLC/NiteFury-and-LiteFury) boards. In
the fpgas.online fleet it sits either in an M.2 HAT on a Raspberry Pi 5 or in
a Compute Blade's own M.2 slot, with JTAG and UART carried on adapted
Pico-EZmate cables to the host's GPIO header (a Pi 5) or to a Compute Blade's
Extension Port (P1) and 4-pin UART header (P2).

## The card

![The connector end of the card from the underside, in a photograph of a LiteFury (the same PCB as the Acorn): the two 6-pin sockets P1 and P2 with pin 1 of each marked, and the half-round plated mounting pad at the card's end](../generated/acorn-card-underside.png){.only-light}
![The connector end of the card from the underside, in a photograph of a LiteFury (the same PCB as the Acorn): the two 6-pin sockets P1 and P2 with pin 1 of each marked, and the half-round plated mounting pad at the card's end](../generated/acorn-card-underside-dark.png){.only-dark}

The photograph shows the connector end of the underside, which is the end the two cables plug into.

The figures and the pins of each part are on [Acorn specifications](specifications.md).
