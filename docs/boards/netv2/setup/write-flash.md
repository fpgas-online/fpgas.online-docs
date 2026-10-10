---
type: how-to
owner: documentation maintainers
reader: someone who wants a bitstream to stay on a NeTV2
review: 2026-11-10
---

# How to write a design into a NeTV2's flash

**You want a bitstream written to a NeTV2's SPI flash, so that it survives a power cycle.**

The write overwrites whatever bitstream the flash holds. Loading into SRAM only is on [the Raspberry Pi 3B+ page](load-pi-3b-plus.md) and [the Raspberry Pi 5 page](load-pi-5.md).

## What you need

- A NeTV2 wired as on [NeTV2 wiring to a Raspberry Pi](wiring.md#jtag), with openFPGALoader on the Pi.
- A bitstream, here `design.bit`.
- A copy of the bitstream the flash holds before the write.

## Steps

1. On a Raspberry Pi 5, detach the PCIe endpoint as in steps 1 and 2 of [the Raspberry Pi 5 page](load-pi-5.md#steps).
2. On the Pi, run `sudo openFPGALoader --cable libgpiod --pins 27:22:4:17 --write-flash design.bit` to write the bitstream to the flash over GPIO bit-banged JTAG. On a Raspberry Pi 3B+ this is the only step.

The pin order is `TDI:TDO:TCK:TMS`.

## Check

The command ends without an error, and the design is running after the next power cycle.

## If it fails

| What you see | Likely cause | Fix |
|---|---|---|
| The Pi crashes or drops off during the write | On a Raspberry Pi 5, the PCIe endpoint was still enumerated | Detach it as in step 1, then write again |

## Next

- [How to load a design into a NeTV2 on a Raspberry Pi 3B+](load-pi-3b-plus.md)
- [How to load a design into a NeTV2 on a Raspberry Pi 5](load-pi-5.md)
- [Programming a NeTV2](../overview/programming.md)
