---
type: explanation
owner: documentation maintainers
reader: someone with a Tiny Tapeout FPGA demo board
review: 2026-11-10
---

# The Tiny Tapeout FPGA demo board

**You have a Tiny Tapeout FPGA demo board and want to know what it is and how it sits on its Raspberry Pi.**

Its figures are on [Tiny Tapeout FPGA demo board specifications](specifications.md), and its pins are on [Tiny Tapeout FPGA demo board pin mapping](pin-mapping.md). The board with a manufactured chip instead of an FPGA is on [Tiny Tapeout ASIC demo boards](../../tt-asic.md).

The Tiny Tapeout (TT) FPGA demo board is a Lattice iCE40UP5K "FabricFox" FPGA breakout. It plugs into a Tiny Tapeout demo PCB, in place of the Tiny Tapeout ASIC the demo PCB was designed for. The FPGA presents the same `ui_in` / `uo_out` / `uio` interface as a real Tiny Tapeout chip. A design can therefore be emulated on real hardware before, or instead of, silicon. The demo PCB is the demo board v3 (TTDBv3), with an RP2350B controller.

:::{admonition} Figure to come
:class: placeholder

The whole board, with the FPGA breakout in the demo PCB and each named part numbered. Tracked in [test-designs issue #255](https://github.com/fpgas-online/fpgas.online-test-designs/issues/255).
:::

## The two boards

The demo board consists of two PCBs.

1. **The Tiny Tapeout demo PCB** carries the RP2350B microcontroller, the USB-C connector, the 7-segment display, the DIP switches and the PMOD headers. It is designed to interface with Tiny Tapeout ASICs and also accepts the FPGA breakout board.
2. **The FPGA breakout board** carries the iCE40UP5K FPGA, the SPI flash and the clock oscillator. It plugs into the chip socket of the demo PCB and presents the same interface as a Tiny Tapeout ASIC.

The microcontroller programs the iCE40 over SPI and provides its 50 MHz clock. After programming it releases its GPIO pins to high impedance. The Raspberry Pi can then talk to the FPGA directly through the PMOD HAT. The controller and the PMOD headers share the same physical traces. The order of those steps is on [Programming a Tiny Tapeout FPGA demo board](programming.md).

## How it sits on its Raspberry Pi

Each Raspberry Pi connects to the board with a USB-C cable. It has a Digilent [PMOD HAT](../../pmod/rpi-hat.md) for GPIO-level control of the Tiny Tapeout I/O pins. An ov5647 camera publishes a live feed of the board. The Raspberry Pis are powered and networked through PoE switches.

A daemon on the Raspberry Pi owns the board's serial port and shares it. [Serial port ownership on a Tiny Tapeout FPGA demo board](serial-port.md) explains it.

The board is on the public [Tiny Tapeout site](https://tinytapeout.fpgas.online). The site's software is on [The Tiny Tapeout stack](../../../setup/tinytapeout.md), and what it offers is on [The welland site](../../../sites/welland.md). Each board's `status.json` on the site reports the Pi daemon's `/health` plus `reachable`. It is the quickest liveness check.
