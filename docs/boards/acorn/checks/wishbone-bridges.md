---
type: explanation
owner: documentation maintainers
reader: someone who wants to know how the check reaches the design's registers
review: 2026-11-10
---

# The Acorn Wishbone bridges test

**You have an Acorn that runs the fpgas.online design, on a Raspberry Pi 5 or in a Compute Blade, and want
to know the two ways a host reaches the design's registers, what tests each, and what has been measured.**
Each fact here is given with its source.

## What it is

The bridges are part of [the fpgas.online LiteX SoC](../overview/design.md), in both its images. From the
design's source
([`acorn_pcie_soc.py`](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/designs/acorn-pcie/gateware/acorn_pcie_soc.py)),
the design is reachable two ways, with the same registers behind both:

- **PCIe BAR0 to Wishbone**: PCIe Gen2 x1, with one DMA channel beside it (`ndmas=1` in the design's source).
- **UARTBone on the P2 serial pair**, K2 (FPGA TX) and J2 (FPGA RX). The link comes out of reset at 1200
  baud; the host writes the PHY's `tuning_word` register to move it to 921600; a UART break (J2 low for
  50 ms) resets the PHY and the bridge, which puts it back. A command has 1 s to complete, so that
  transfers of several words work at 1200 baud.
- The BIOS console is on the crossover UART, so it can be read through either bridge.

How BAR0 has to be read from a host (aligned 32-bit reads only, memory decoding enabled first) is under
[Installing the fpgas.online images](../setup/install-images.md#installing-the-fpgasonline-images). Where the
P2 pair lands on each carrier is on the wiring pages: [Raspberry Pi 5](../setup/rpi-5/wiring.md), [Compute
Blade](../setup/compute-blade/wiring.md).

## How the check tests it

From the check's document ([what each board's check tests](../../../verify/fpgas-verify.md#what-each-boards-check-tests)):

| Test | Over | Passes when |
|---|---|---|
| `pcie-bar0` | BAR0 | the operational build runs, the flash identifies itself, the device DNA is neither all zeros nor all ones, and the XADC temperature and voltages are in range |
| `p2-uart` | P2 | the UARTBone identifier at 1200 baud is BAR0's; at 921600 baud the identifier, DNA and XADC readings are right and the DNA is BAR0's. The link is left at 1200 baud |
| `scratch` | BAR0 and P2 | the `ctrl` scratch register holds two patterns written over each bridge; its value is put back |

**On a Raspberry Pi 5, before a `p2-uart` test:** the header's serial port must be on (`/dev/ttyAMA0`) and the
kernel console off it: [the Pi's settings](../setup/rpi-5/pi-settings.md#the-serial-port).

To run these tests alone, the same command on either carrier (`--test` is in the check's document; on a
Compute Blade it is **not yet run by us on this hardware**, and there the P2 tests need a boot with the
header's serial port on: [JTAG on a blade](compute-blade-jtag-by-hand.md#jtag-on-a-blade)):

```console
$ sudo fpgas-acorn-verify --test pcie-bar0 --test p2-uart --test scratch
```

## What has been measured

- **Both bridges on acorn-willow**, on a Raspberry Pi 5, last checked 2026-09-21: after a PoE power cycle
  the UART, PCIe, P2 GPIO and flash checks passed, and the BIOS log was read from the crossover UART through
  BAR0 (steps 9 and 10 of [its install](../setup/install-images.md#installing-the-fpgasonline-images)).
- **Both bridges on a Compute Blade**, on pi20 at ps1 (a CM5) on 2026-09-20, with the design loaded into SRAM: the
  same identifier and device DNA over PCIe and over the UART bridge. That blade's P2 pair is wired straight to GPIO14 and GPIO15, not by the
  guide's cable; which header pins its wires sit on is not recorded by us.
- **The `pcie-bar0`, `p2-uart` and `scratch` tests passed** on acorn-holly, acorn-willow, acorn-sycamore and
  acorn-olive in the boot check of 6 October 2026.

More: the design's own document is in fpgas.online-test-designs: [`designs/acorn-pcie`](https://github.com/fpgas-online/fpgas.online-test-designs/tree/main/designs/acorn-pcie).
