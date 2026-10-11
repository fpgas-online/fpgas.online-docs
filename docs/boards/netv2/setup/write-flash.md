---
type: how-to
owner: documentation maintainers
reader: someone who wants a bitstream to stay on a NeTV2
review: 2026-11-10
---

# How to write a design into a NeTV2's flash

**You want a bitstream written to a NeTV2's SPI flash, so that it survives a power cycle.**

The write overwrites whatever bitstream the flash holds, and this page does not save it first. Loading into SRAM only is on [the Raspberry Pi 3B+ page](load-pi-3b-plus.md) and [the Raspberry Pi 5 page](load-pi-5.md).

This procedure is waiting for its run: [test-designs issue #249](https://github.com/fpgas-online/fpgas.online-test-designs/issues/249).

## What you need

- A NeTV2 wired as on [NeTV2 wiring to a Raspberry Pi](wiring.md#jtag), with openFPGALoader on the Pi.
- A bitstream, here `design.bit`.

## Steps

1. On a Raspberry Pi 5, run `lspci -d 10ee:7011` to find the NeTV2's PCIe address, `0001:01:00.0` on a Pi 5.
   If it printed nothing, there is nothing to detach: go to step 3.
2. On a Raspberry Pi 5, detach the endpoint: `echo 1 | sudo tee /sys/bus/pci/devices/0001:01:00.0/remove`, with the address from step 1.
3. On the Pi, run `sudo openFPGALoader --cable libgpiod --pins 27:22:4:17 --write-flash design.bit` to write the bitstream to the flash over GPIO bit-banged JTAG. On a Raspberry Pi 3B+ this is the only step.

The pin order is `TDI:TDO:TCK:TMS`.

## Check

Step 3's command ends without an error. On a Raspberry Pi 5 the endpoint stays detached until the FPGA next runs a design with a PCIe endpoint. That the FPGA then starts the design from flash at power-up waits for this page's run ([test-designs issue #249](https://github.com/fpgas-online/fpgas.online-test-designs/issues/249)).

## If it fails

| What you see | Likely cause | Fix |
|---|---|---|
| The Pi crashes or drops off during the write | On a Raspberry Pi 5, the PCIe endpoint was still enumerated | Detach it as in steps 1 and 2, then write again |

## Next

- [How to load a design into a NeTV2 on a Raspberry Pi 3B+](load-pi-3b-plus.md)
- [How to load a design into a NeTV2 on a Raspberry Pi 5](load-pi-5.md)
- [Programming a NeTV2](../overview/programming.md)
