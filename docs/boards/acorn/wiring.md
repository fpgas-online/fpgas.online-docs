---
orphan: true
type: landing
owner: documentation maintainers
reader: someone following an old link to the Acorn wiring page
review: 2026-11-10
---

# Acorn wiring

This page has been split, by carrier and by task. Each part of it is now on the page named here; the
whole tree is on [SQRL Acorn and LiteFury](index.md).

(raspberry-pi-5)=
(p2-serial-pair-and-spare-gpios)=
(p1-jtag)=
**On a Raspberry Pi 5** (the wiring sheet, P2, P1, the serial port overlay, `gpiochip15`): [Acorn wiring on a Raspberry Pi 5](setup/rpi-5/wiring.md) and [the Pi's settings](setup/rpi-5/pi-settings.md).

(compute-blade)=
(pin-numbering)=
(p1-jtag-on-the-extension-port)=
(p2-serial-pair-on-the-uart-header)=
(housings)=
(jtag-on-a-blade)=
**On a Compute Blade** (the wiring sheet, pin numbering, P1, P2, housings, the shared line and the 470 Ω resistor, JTAG on a blade): [Acorn wiring on a Compute Blade](setup/compute-blade/wiring.md) and [the blade's pins, shared line and settings](setup/compute-blade/blade-settings.md) and [JTAG on a Compute Blade](checks/compute-blade-jtag-by-hand.md).

(board-connectors)=
**The card's two connectors, P1 and P2**: on both wiring pages, [Raspberry Pi 5](setup/rpi-5/wiring.md#board-connectors) and [Compute Blade](setup/compute-blade/wiring.md#board-connectors).

(bill-of-materials)=
(building-the-cables)=
(assembly)=
**Parts, building the cables and fitting them**: the building guides, [for a Raspberry Pi 5](setup/rpi-5/cables.md) ([parts](setup/rpi-5/parts.md), [fitting](setup/rpi-5/fitting.md)) and [for a Compute Blade](setup/compute-blade/cables.md) ([parts](setup/compute-blade/parts.md), [fitting](setup/compute-blade/fitting.md)).

(verification)=
(the-designs-these-steps-load)=
(step-1-pcie)=
(step-2-jtag)=
(step-3-uart-and-gpio-loopback)=
(step-4-pin-id)=
(step-5-pcie-design)=
**Verification by hand**: one page for each step, each with a block for each carrier: [PCIe](checks/pcie-by-hand.md) (steps 1 and 5), [JTAG](checks/jtag-by-hand.md) (step 2), [UART and GPIO loopback](checks/uart-gpio-loopback.md) (step 3), [pin ID](checks/pin-id.md) (step 4). The check that needs none of this is in the building guides: [verifying on a Raspberry Pi 5](checks/rpi-5.md), [verifying on a Compute Blade](checks/compute-blade.md).

(kernel-console-on-the-fpga-uart)=
**Kernel console on the FPGA UART**: for each carrier, [Raspberry Pi 5](setup/rpi-5/pi-settings.md#kernel-console-on-the-fpga-uart) and [Compute Blade](setup/compute-blade/blade-settings.md#kernel-console-on-the-fpga-uart).

(troubleshooting)=
**Troubleshooting**: each row is on the page of the thing it is about: the wiring pages, [the Pi's settings](troubleshooting/rpi-5-wiring.md), [the blade's settings](troubleshooting/compute-blade-wiring.md), and [PCIe](checks/pcie-by-hand.md#if-it-goes-wrong), [JTAG](checks/jtag-by-hand.md#if-it-goes-wrong), [UART and GPIO loopback](checks/uart-gpio-loopback.md#if-it-goes-wrong) and [pin ID](checks/pin-id.md#if-it-goes-wrong).

(compatible-boards)=
**Compatible boards**: [Acorn variants](which-one.md). **References**: [Acorn references](overview/references.md).
