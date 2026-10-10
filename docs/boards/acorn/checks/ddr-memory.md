---
type: explanation
owner: documentation maintainers
reader: someone who wants to know how the check tests an Acorn's memory
review: 2026-11-10
---

# The Acorn DDR memory test

**This page explains what tests an Acorn's DDR3 memory, what a pass means, and what speeds to expect.**

It is for someone who wants to know what the check does to the memory, on a Raspberry Pi 5 or in a Compute Blade. The memory itself and its pins are on [Acorn specifications](../overview/specifications.md#ddr3-sdram). The page gives no steps.

## What it is

There is no separate DDR design for the Acorn: the memory test is part of the operational image of [the fpgas.online Acorn design](../overview/design.md). From the design's source
([`acorn_pcie_soc.py`](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/designs/acorn-pcie/gateware/acorn_pcie_soc.py)):

- The DDR3 controller is LiteDRAM on the 7-series PHY (`A7DDRPHY`). It is built for an MT41K512M16 on the CLE-215+
  and the CLE-215, and for an MT41K256M16 on the CLE-101.
- A DRAM BIST (`dram_generator`, `dram_checker`) is LiteDRAM's pattern writer and checker on ports of their
  own. A host sets `base`, `end` and `length`, starts the generator, waits for `done`, does the same with
  the checker and reads `errors`. Each one's `ticks` is the system clock cycles its pass took, which gives
  the bandwidth.
- The golden image has no DDR3 and no BIST, so nothing in it can fail calibration.

## How the check tests it

From the check's document ([what each board's check tests](../../../verify/fpgas-verify.md#what-each-boards-check-tests)):
the `ddr` test runs over BAR0. After the BIOS console is read out, the DRAM BIST makes two passes over the
whole DRAM. The test passes with no errors and a write and a read bandwidth of at least the variant's
minimum.

From the check's expected figures
([`expected.toml`](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/docs/wiring/acorn/expected.toml)):
the minimum is 1100 MB/s for writing and for reading, on both the CLE-215+ and the CLE-101. Both run one
16-bit DDR3 at 400 MHz (DDR3-800), so the peak is 1600 MB/s.

The test reads and writes only the DRAM. The check never writes the card's flash and never reconfigures
the FPGA (from [Installing the Acorn packages](../setup/packages.md#installing-the-acorn-packages)).

The check runs the `ddr` test alone as `sudo fpgas-acorn-verify --test ddr`, on either carrier: [on a Raspberry Pi 5](rpi-5.md), [on a Compute Blade](compute-blade.md).

## What to expect

A CLE-215+ on a Raspberry Pi 5 measures 1327 MB/s for writing and 1350 MB/s for reading with the DRAM BIST. That is above the 1100 MB/s minimum and below the 1600 MB/s peak.

The LiteX BIOS runs its own memory test at start-up, which is a different test. It reports DDR3 1 GiB at 800 MT/s and clean read leveling on both modules. It ends with `Memtest OK`, 35.1 MiB/s for writing and 46.8 MiB/s for reading.

More: the design's own document is in fpgas.online-test-designs: [`designs/acorn-pcie`](https://github.com/fpgas-online/fpgas.online-test-designs/tree/main/designs/acorn-pcie) and [`docs/tests/ddr-memory.md`](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/docs/tests/ddr-memory.md).
