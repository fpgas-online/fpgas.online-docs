---
type: explanation
owner: documentation maintainers
reader: someone who wants to know how the check tests an Acorn's memory
review: 2026-11-10
---

# The Acorn DDR memory test

**You have an Acorn that runs the fpgas.online design, on a Raspberry Pi 5 or in a Compute Blade, and want
to know what tests its DDR3 memory, what a pass means, and what has been measured.** The memory itself and
its pins are on [Acorn specifications](../overview/specifications.md#ddr3-sdram). Each fact here is given with its source.

## What it is

There is no separate DDR design for the Acorn: the memory test is part of the operational image of [the fpgas.online Acorn design](../overview/design.md). From the design's source
([`acorn_pcie_soc.py`](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/designs/acorn-pcie/gateware/acorn_pcie_soc.py)):

- The DDR3 controller is LiteDRAM on the 7-series PHY (`A7DDRPHY`), built for an MT41K512M16 on the CLE-215+
  and the CLE-215 and for an MT41K256M16 on the CLE-101.
- A DRAM BIST (`dram_generator`, `dram_checker`) is LiteDRAM's pattern writer and checker on ports of their
  own. A host sets `base`, `end` and `length`, starts the generator, waits for `done`, does the same with
  the checker and reads `errors`. Each one's `ticks` is the system clock cycles its pass took, which gives
  the bandwidth.
- The golden image has no DDR3 and no BIST, so nothing in it can fail calibration.

## How the check tests it

From the check's document ([what each board's check tests](../../../verify/fpgas-verify.md#what-each-boards-check-tests)):
the `ddr` test runs over BAR0. After the BIOS console is read out, the DRAM BIST makes two passes over the
whole DRAM, and the test passes with no errors and a write and a read bandwidth of at least the variant's
minimum.

From the check's expected figures
([`expected.toml`](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/docs/wiring/acorn/expected.toml)):
the minimum is 1100 MB/s for writing and for reading, on both the CLE-215+ and the CLE-101. Both run one
16-bit DDR3 at 400 MHz (DDR3-800), so the peak is 1600 MB/s.

The test reads and writes only the DRAM. The check never writes the card's flash and never reconfigures
the FPGA (from [Installing the Acorn packages](../setup/packages.md#installing-the-acorn-packages)).

To run the test alone, the same command on either carrier (`--test` is in the check's document; on a Compute
Blade it is **not yet run by us on this hardware**):

```console
$ sudo fpgas-acorn-verify --test ddr
```

## What has been measured

- **1327 MB/s write and 1350 MB/s read**, by the DRAM BIST, on a CLE-215+ on a Raspberry Pi 5 then named
  pi-sw2-p48, on 2026-10-01 (from `expected.toml`).
- **A different test, the LiteX BIOS's own memory test at start-up**: DDR3 1 GiB at 800 MT/s, read leveling clean on both modules, `Memtest OK`,
  35.1 MiB/s write, 46.8 MiB/s read, on acorn-willow, last checked 2026-09-21 (step 10 of [its
  install](../setup/install-images.md#steps)).
- **The `ddr` test passed** on acorn-holly, acorn-willow, acorn-sycamore and acorn-olive in the boot check of
  6 October 2026.
- The CLE-101 has not been measured yet (from `expected.toml`).

More: the design's own document is in fpgas.online-test-designs: [`designs/acorn-pcie`](https://github.com/fpgas-online/fpgas.online-test-designs/tree/main/designs/acorn-pcie) and [`docs/tests/ddr-memory.md`](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/docs/tests/ddr-memory.md).
