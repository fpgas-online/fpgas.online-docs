---
type: explanation
owner: documentation maintainers
reader: someone who wants to know how the check reaches the design's registers
review: 2026-11-10
---

# The Acorn Wishbone bridges test

**This page explains the two ways a host reaches the registers of an Acorn that runs the fpgas.online design, and what tests each.**

It is for someone who wants to know what the check does over each bridge, on a Raspberry Pi 5 or in a Compute Blade. The page gives no steps.

## What it is

The bridges are part of [the fpgas.online Acorn design](../overview/design.md), in both its images. From the
design's source
([`acorn_pcie_soc.py`](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/designs/acorn-pcie/gateware/acorn_pcie_soc.py)),
the design is reachable two ways, with the same registers behind both:

- **PCIe BAR0 to Wishbone**: PCIe Gen2 x1, with one DMA channel beside it (`ndmas=1` in the design's source).
- **UARTBone on the P2 serial pair**, K2 (FPGA TX) and J2 (FPGA RX). The link comes out of reset at 1200
  baud. The host writes the PHY's `tuning_word` register to move it to 921600. A UART break (J2 low for
  50 ms) resets the PHY and the bridge, which puts it back. A command has 1 s to complete, so that
  transfers of several words work at 1200 baud.
- The BIOS console is on the crossover UART, so it can be read through either bridge.

BAR0 is read from a host with aligned 32-bit reads only, after memory decoding is enabled. The steps are in
[How to install the fpgas.online images on an Acorn](../setup/install-images.md). Where the
P2 pair lands on each carrier is on the wiring pages: [Raspberry Pi 5](../setup/rpi-5/wiring.md), [Compute
Blade](../setup/compute-blade/wiring.md).

## How the check tests it

From the check's document ([what each board's check tests](../../../verify/tests.md#what-the-check-tests-on-each-board)):

| Test | Over | Passes when |
|---|---|---|
| `pcie-bar0` | BAR0 | the operational build runs, the flash identifies itself, the device DNA is neither all zeros nor all ones, and the XADC temperature and voltages are in range |
| `p2-uart` | P2 | the UARTBone identifier at 1200 baud is BAR0's; at 921600 baud the identifier, DNA and XADC readings are right and the DNA is BAR0's. The link is left at 1200 baud |
| `scratch` | BAR0 and P2 | the `ctrl` scratch register holds two patterns written over each bridge; its value is put back |

On a Raspberry Pi 5, a `p2-uart` test needs the header's serial port on (`/dev/ttyAMA0`) and the kernel console off it:
[the Pi's settings](../setup/rpi-5/pi-settings.md#the-serial-port).

The check runs these tests alone as `sudo fpgas-acorn-verify --test pcie-bar0 --test p2-uart --test scratch`, on either carrier: [on a Raspberry Pi 5](rpi-5.md), [on a Compute Blade](compute-blade.md). On a Compute Blade the P2 tests need a boot with the header's serial port on ([why](jtag-and-the-pcie-endpoint.md#why-a-blade-needs-its-serial-port-off-for-jtag)).

More: the design's own document is in fpgas.online-test-designs: [`designs/acorn-pcie`](https://github.com/fpgas-online/fpgas.online-test-designs/tree/main/designs/acorn-pcie).
