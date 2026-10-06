# SQRL Acorn and LiteFury

The SQRL Acorn CLE-215+ is an M.2 form factor PCIe FPGA accelerator card,
pin-compatible with the [NiteFury and
LiteFury](https://github.com/RHSResearchLLC/NiteFury-and-LiteFury) boards. In
the fpgas.online fleet it sits either in an M.2 HAT on a Raspberry Pi 5 or in
a Compute Blade's own M.2 slot, with JTAG and UART carried on adapted
Pico-EZmate cables to the host's GPIO header (a Pi 5) or to a Compute Blade's
Extension Port (P1) and 4-pin UART header (P2).

**An Acorn on a Raspberry Pi 5:** start at [Acorn wiring on a Raspberry Pi 5](wiring/rpi-5.md), then the
[Raspberry Pi 5 building guide](building/rpi-5/index.md).

**An Acorn on a Compute Blade:** start at [Acorn wiring on a Compute Blade](wiring/compute-blade.md), then the
[Compute Blade building guide](building/compute-blade/index.md).

## Overview

What the card is, its variants, what works on fpgas.online today, and the documents behind these pages:

```{toctree}
:maxdepth: 1

overview/device-info
overview/variants
overview/functionality
overview/resources
```

## Wiring Overview

Which wire goes where between the card and its host, and what the host must have set for those wires. Two pages for a Raspberry Pi 5, three for a Compute Blade:

```{toctree}
:maxdepth: 1

wiring/rpi-5
wiring/rpi-5-host
wiring/compute-blade
wiring/compute-blade-host
wiring/compute-blade-jtag
```

## Building Guide

The two cables between an Acorn and its host: parts, one page for each connector, fitting, and checking the result. One guide for each carrier:

```{toctree}
:maxdepth: 2

building/rpi-5/index
building/compute-blade/index
```

## Test Designs

The designs loaded into the card, one page for each: what it is, how to load it and what a good result looks like on each carrier:

```{toctree}
:maxdepth: 1

designs/litex-soc
designs/ddr-memory
designs/pcie
designs/wishbone-bridge
packages
designs/install-images
designs/recovery
designs/jtag
designs/uart-gpio-loopback
designs/pin-id
```

## Installations

Where the cards are, by site: which card is on which host, its state, what it still needs, and its labels.

```{toctree}
:maxdepth: 1

installations/welland
installations/ps1
installations/ps1-reads
```

## Installing the Acorn Packages

Moved to [Acorn packages and the boot check](packages.md#installing-the-acorn-packages).
