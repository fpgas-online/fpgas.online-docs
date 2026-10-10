---
type: explanation
owner: documentation maintainers
reader: someone asking how the flash tool reaches an Acorn's flash
review: 2026-11-10
---

# Reaching an Acorn's flash through PCIe

This page explains how the flash tool `spi_flash.py` reads and writes an Acorn's flash. It also says what the tool checks first and which two hardware properties it handles. It is for someone following [How to install the fpgas.online images on an Acorn](install-images.md) or writing their own reader. It does not give the install steps.

## What the tool does

The tool drives the SoC's flash core through PCIe BAR0 from Python, with no kernel module. It is read-only unless told otherwise, and before anything is erased it checks the image against the slot. The golden slot wants the flavour that chain-loads `0x400000`, and the operational slot the one with the watchdog. Both want the IDCODE of the part that is there. It refuses the golden slot without `--i-know-this-writes-golden`.

## Two properties of the hardware

The first SPI transfer after every configuration is lost. `STARTUPE2` does not pass the first three `USRCCLKO` edges to the flash clock pin. The first command therefore arrives three clocks short and reads back as all ones. The tool spends those clocks with the flash deselected.

BAR0 answers only aligned 32-bit reads. Through `/sys/bus/pci/devices/<bdf>/resource0`, a 4-byte slice of the `mmap` returns the register, and a byte-wise slice of the same window returns `0xff` for every byte. Memory decoding must be enabled first.

## Why a PoE cycle

After a `sudo reboot` the FPGA can keep its configuration, because a reboot need not drop the M.2 rail. The reliable power cycle is a PoE cycle of the host's switch port. A Pi 5 takes more than 90 s to come back from it.
