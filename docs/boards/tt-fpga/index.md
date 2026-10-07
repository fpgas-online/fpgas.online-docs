# Tiny Tapeout FPGA demo board

The Tiny Tapeout (TT) FPGA demo board is a Lattice iCE40UP5K "FabricFox" FPGA
breakout plugged into a Tiny Tapeout demo PCB, in place of the Tiny Tapeout ASIC
the demo PCB was designed for. The FPGA presents the same `ui_in` / `uo_out` /
`uio` interface as a real Tiny Tapeout chip, so a design can be emulated on real
hardware before — or instead of — silicon. In the fpgas.online fleet each board is joined to a Raspberry Pi
carrying a Digilent Pmod HAT: a USB-C cable to the demo board's microcontroller and three Pmod cables to the
HAT.

**You have a Tiny Tapeout FPGA demo board and a Raspberry Pi with a Pmod HAT:** start at [which cable goes
where](wiring/cables.md), then the [building guide](building/index.md).

Before running anything against a board that is on the public site, read
[Serial port ownership](../../setup/tinytapeout.md#serial-port-ownership): a daemon holds the port open
and the board is on a public web site while you work.

```{include} streaming-rule.inc
```

## Overview

What the board is, its variants, its signals and how a design is loaded, and the documents behind these
pages:

```{toctree}
:maxdepth: 1
:caption: Overview

Device info: what is on the board <overview/device-info>
Variants: demo board version 3 against 2, the FPGA against a chip <overview/variants>
Functionality: the signals, the serial port, loading a design <overview/functionality>
Resources and links <overview/resources>
Mechanical: the demo board on its mounting plate <overview/mechanical>
Mechanical: the mounting plate <overview/plate>
Mechanical: the camera over the plate <overview/camera>
```

**Load a bitstream by hand:** [functionality, by hand](overview/functionality.md#by-hand).

## Wiring Overview

Which cable goes where between the demo board and a Raspberry Pi with a Pmod HAT, then every wire by signal
group, and where each fact comes from:

```{toctree}
:maxdepth: 1
:caption: Wiring Overview

Which cable goes where <wiring/cables>
ui_in and uo_out, wire by wire <wiring/pins-ui-uo>
uio and the serial port <wiring/pins-uio-uart>
The loading pins, display, clock, reset and LED <wiring/pins-other>
Sources of the wiring facts <wiring/sources>
```

## Building Guide

Putting a demo board on a Raspberry Pi with a Pmod HAT: parts, fitting, and checking the result:

```{toctree}
:maxdepth: 2
:titlesonly:
:caption: Building Guide

Building overview <building/index>
```

## Test Designs

The designs loaded into the FPGA, one page for each, then what the public site loads and the demo board's
own firmware. Running the whole check, which loads the pin-ID and UART designs itself, is [verifying
1](building/verifying-1.md) of the building guide.

```{toctree}
:maxdepth: 1
:caption: Test Designs

Pmod pin ID <designs/pmod-pin-id>
Pmod loopback <designs/pmod-loopback>
UART <designs/uart>
What the public site loads <designs/demos>
Firmware and known workarounds <designs/firmware>
```

## Installations

Where the boards are, by site: each board by its microcontroller's USB serial number, its state and what it
still needs:

```{toctree}
:maxdepth: 1
:caption: Installations

At welland <installations/welland>
At ps1 <installations/ps1>
```

:::{note}
This board's page used to be one page, [at its old address](../tt-fpga.md): each of its headings is listed
there with the page that holds it now.
:::
