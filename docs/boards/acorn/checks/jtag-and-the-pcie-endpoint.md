---
type: explanation
owner: documentation maintainers
reader: someone who wants the reasons behind the by-hand JTAG and PCIe pages
review: 2026-11-10
---

# JTAG loads and the PCIe endpoint

**This page explains what a JTAG load does to an Acorn's PCIe endpoint, and why a Compute Blade needs its serial port off for JTAG.**

It is for someone who wants the reasons behind the by-hand pages. It gives no steps: those are on [the by-hand pages](by-hand.md).

## Why the endpoint is detached before a load

Reconfiguring the FPGA over JTAG while its endpoint is enumerated is a PCIe surprise removal. The BCM2712 root complex, in a Pi 5 and in a CM5, does not survive it. The host drops its SSH session and reboots. With the endpoint removed first, the load completes and the host is unaffected.

The rule belongs to the root complex, not to the Acorn. It applies to any PCIe FPGA on a Pi 5, the NeTV2 included ([PCIe detection](../../netv2.md#pcie-detection-rpi5-netv2)). Every by-hand page that loads a bitstream detaches the endpoint first, on every carrier.

Read-only operations (`--detect`, `--read-dna`, `--read-xadc`) do not reconfigure the device. They are safe on a live endpoint.

## What coming back looks like

After a load the endpoint has to come back. The first way is a bus rescan. Where the rescan finds nothing, the second way is a re-probe of the slot's root complex. What works depends on the carrier and on the design that was loaded:

- **A CM5 blade, kernel 6.12, the vendor XDMA image reloaded from flash with `openFPGALoader --reset`:** the rescan re-links at 5 GT/s x1 and enumerates. The re-probe works too.
- **A CM5 blade, kernel 6.12, the LiteX `acorn-pcie` SoC:** the rescan finds nothing. The core's LTSSM sits at `0x2d`, and a root-port retrain or secondary-bus reset changes nothing. The re-probe links at 5 GT/s x1 and enumerates as `10ee:7021`.
- **A Pi 5 with an M.2 HAT, kernel 6.12, the LiteX SoC on a CLE-215+:** the rescan is enough. The link is up (LTSSM `0x16`, L0, 5 GT/s x1) the moment the load finishes, so no re-probe is needed.

So try the rescan first, and re-probe only when `lspci` still shows nothing. The re-probe toggles PERST# by unbinding and rebinding the slot's root complex. That touches only the FPGA's PCI domain, because the RP1 southbridge (Ethernet, USB, GPIO) hangs off a different platform device. The platform device behind the slot is `1000110000.pcie` on a Pi 5 and on a CM5 blade.

## Why a blade needs its serial port off for JTAG

On a blade the JTAG pin TMS is GPIO14, which is also the serial port's TX pin. The J2 wire of the serial pair shares that line through a 470 Ω resistor ([the shared line](../setup/compute-blade/shared-line.md)). With `enable_uart=1` the kernel's serial driver holds GPIO14, whether or not a console or a getty uses the port.

Kernel 6.18 refuses a request for a pin that a driver holds. openFPGALoader does not check the refusal, so it stops with `gpiod_line_request_set_values_subset: Assertion 'request' failed`. Under kernel 6.12 JTAG also answers with the serial port on.

A test of the serial pair (`p2-uart`, `p2-serial`) needs the opposite: the port on, with a design already running that was loaded from flash. Under kernel 6.18 the two cannot share a boot. The loads over JTAG run in a boot with the port off: the JTAG page, pin ID and the PCIe design. The pair test runs in a boot with it on.

openFPGALoader also leaves its pins as outputs when it exits: GPIO2 and GPIO4 were seen driving low, and it drives TMS on GPIO14 too. The blade pages put the pins back with `pinctrl` before anything else uses the lines.
