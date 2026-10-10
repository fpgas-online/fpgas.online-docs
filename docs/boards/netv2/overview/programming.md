---
type: explanation
owner: documentation maintainers
reader: someone who wants to know how a design reaches a NeTV2's FPGA
review: 2026-11-10
---

# Programming a NeTV2

**You want to know how a bitstream gets from a Raspberry Pi into a NeTV2's FPGA.**

This page keeps the protocol, the connection and the tool apart. The commands are on [How to load a design into a NeTV2 on a Raspberry Pi 3B+](../setup/load-pi-3b-plus.md) and [on a Raspberry Pi 5](../setup/load-pi-5.md).

:::{admonition} Figure to come
:class: placeholder

The three layers of programming a NeTV2: JTAG as the protocol, the Pi's GPIO header as the connection, openFPGALoader as the tool. Tracked in ISSUE-03.
:::

## The protocol

The NeTV2 is configured over JTAG. Its JTAG interface has the signals TCK, TMS, TDI and TDO, and a reset line, SRST. A load over JTAG lands in the FPGA's SRAM. With `--write-flash` the same protocol writes the on-board SPI flash, so that the bitstream survives a power cycle.

## The connection

JTAG is wired directly to Raspberry Pi GPIO pins on the 40-pin header. TCK is on GPIO4, TMS on GPIO17, TDI on GPIO27, TDO on GPIO22 and SRST on GPIO24. The pins and their header positions are on [NeTV2 wiring to a Raspberry Pi](../setup/wiring.md#jtag). PCIe plays no part in programming.

On a Raspberry Pi 5 the PCIe link matters for another reason. Reconfiguring the FPGA over JTAG while its PCIe endpoint is enumerated is a surprise removal, and it crashes the BCM2712 root complex. The endpoint is detached first.

## The tool

openFPGALoader drives the JTAG signals, and its `--pins` order is `TDI:TDO:TCK:TMS`. On a Raspberry Pi 3B+ it uses the `libgpiod` cable, which drives the pins through the Linux GPIO subsystem. That is bit-banging, and its effective JTAG clock is about 5 MHz.

On a Raspberry Pi 5 the same `libgpiod` cable works but is slower, because the RP1 I/O controller adds latency to GPIO access. The `rp1pio` cable drives JTAG through the RP1's PIO peripheral instead, which is much faster. It is not in upstream openFPGALoader. It is installed from the `openfpgaloader-rp1pio` package, which brings the `librp1jtag0` shared library with it, and [the NeTV2 packages](../setup/packages.md) say where the package comes from.

The sources behind the package are [mithro/openFPGALoader (feature/rp1-jtag-netv2)](https://github.com/mithro/openFPGALoader/tree/feature/rp1-jtag-netv2), which has the RP1 PIO JTAG support, and the RP1 JTAG shared library [mithro/rp1-jtag](https://github.com/mithro/rp1-jtag).
