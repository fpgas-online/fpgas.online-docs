---
orphan: true
---

# Acorn wiring

This page has been split, by carrier and by task. Each part of it is now on the page named here; the
whole tree is on [SQRL Acorn and LiteFury](index.md).

(raspberry-pi-5)=
(p2-serial-pair-and-spare-gpios)=
(p1-jtag)=
**On a Raspberry Pi 5** (the wiring sheet, P2, P1, the serial port overlay, `gpiochip15`): [Acorn wiring on a Raspberry Pi 5](wiring/rpi-5.md) and [the Pi's settings](wiring/rpi-5-host.md).

(compute-blade)=
(pin-numbering)=
(p1-jtag-on-the-extension-port)=
(p2-serial-pair-on-the-uart-header)=
(housings)=
(jtag-on-a-blade)=
**On a Compute Blade** (the wiring sheet, pin numbering, P1, P2, housings, the shared line and the 470 Ω resistor, JTAG on a blade): [Acorn wiring on a Compute Blade](wiring/compute-blade.md) and [the blade's pins, shared line and settings](wiring/compute-blade-host.md) and [JTAG on a Compute Blade](wiring/compute-blade-jtag.md).

(board-connectors)=
**The card's two connectors, P1 and P2**: on both wiring pages, [Raspberry Pi 5](wiring/rpi-5.md#board-connectors) and [Compute Blade](wiring/compute-blade.md#board-connectors).

(bill-of-materials)=
(building-the-cables)=
(assembly)=
**Parts, building the cables and fitting them**: the building guides, [for a Raspberry Pi 5](building/rpi-5/index.md) ([parts](building/rpi-5/bom.md), [fitting](building/rpi-5/fitting.md)) and [for a Compute Blade](building/compute-blade/index.md) ([parts](building/compute-blade/bom.md), [fitting](building/compute-blade/fitting.md)).

(verification)=
(the-designs-these-steps-load)=
(step-1-pcie)=
(step-2-jtag)=
(step-3-uart-and-gpio-loopback)=
(step-4-pin-id)=
(step-5-pcie-design)=
**Verification by hand**: one page for each step, each with a block for each carrier: [PCIe](designs/pcie.md) (steps 1 and 5), [JTAG](designs/jtag.md) (step 2), [UART and GPIO loopback](designs/uart-gpio-loopback.md) (step 3), [pin ID](designs/pin-id.md) (step 4). The check that needs none of this is in the building guides: [verifying on a Raspberry Pi 5](building/rpi-5/verifying-1.md), [verifying on a Compute Blade](building/compute-blade/verifying-1.md).

(kernel-console-on-the-fpga-uart)=
**Kernel console on the FPGA UART**: for each carrier, [Raspberry Pi 5](wiring/rpi-5-host.md#kernel-console-on-the-fpga-uart) and [Compute Blade](wiring/compute-blade-host.md#kernel-console-on-the-fpga-uart).

(troubleshooting)=
**Troubleshooting**: each row is on the page of the thing it is about: the wiring pages, [the Pi's settings](wiring/rpi-5-host.md#troubleshooting), [the blade's settings](wiring/compute-blade-host.md#troubleshooting), and [PCIe](designs/pcie.md#if-it-goes-wrong), [JTAG](designs/jtag.md#if-it-goes-wrong), [UART and GPIO loopback](designs/uart-gpio-loopback.md#if-it-goes-wrong) and [pin ID](designs/pin-id.md#if-it-goes-wrong).

(compatible-boards)=
**Compatible boards**: [Acorn variants](overview/variants.md). **References**: [Acorn resources and links](overview/resources.md).
