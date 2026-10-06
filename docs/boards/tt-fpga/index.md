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

```{include} generated/tt-fpga-pins-other.md
:start-after: "### Loading the FPGA: its configuration pins"
:end-before: "The FPGA breakout has no SPI flash"
```

## Overview

What the board is, its variants, its signals and how a design is loaded, and the documents behind these
pages:

```{toctree}
:maxdepth: 1

overview/device-info
overview/variants
overview/functionality
overview/resources
```

## Wiring Overview

Which cable goes where between the demo board and a Raspberry Pi with a Pmod HAT, then every wire by signal
group, and where each fact comes from:

```{toctree}
:maxdepth: 1

wiring/cables
wiring/pins-ui-uo
wiring/pins-uio-uart
wiring/pins-other
wiring/sources
```

## Building Guide

Putting a demo board on a Raspberry Pi with a Pmod HAT: parts, fitting, and checking the result:

```{toctree}
:maxdepth: 2
:titlesonly:

building/index
```

## Test Designs

The designs loaded into the FPGA, one page for each, then what the public site loads and the demo board's
own firmware:

```{toctree}
:maxdepth: 1

designs/pmod-pin-id
designs/pmod-loopback
designs/uart
designs/spi-flash-id
designs/demos
designs/firmware
```

## Installations

Where the boards are, by site: each board by its microcontroller's USB serial number, its state and what it
still needs:

```{toctree}
:maxdepth: 1

installations/welland
installations/ps1
```

This board's page used to be one page, [at its old address](../tt-fpga.md): each of its headings is listed
there with the page that holds it now.
