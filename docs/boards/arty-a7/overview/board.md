---
type: explanation
owner: documentation maintainers
reader: someone with a Digilent Arty A7 who wants to know what it is
review: 2026-11-10
---

# The Arty A7 board

**You have a Digilent Arty A7 and want to know what is on it and how it reaches its Pi.**

[Arty A7 specifications](specifications.md) has its figures and pins. [Arty A7 wiring to a Raspberry Pi](../setup/wiring.md) has the wires.

:::{admonition} Figure to come
:class: placeholder

The whole Arty A7 from above, with the USB connector, the four PMOD connectors, the RJ45 jack and the FPGA numbered. Tracked in ISSUE-01.
:::

The Digilent Arty A7 is a Xilinx Artix-7 development board. It carries 256 MB of DDR3 SDRAM, a TI DP83848J Ethernet PHY and a quad SPI flash. It also has four PMOD connectors (JA, JB, JC and JD), and LEDs, switches and buttons. A single FTDI FT2232HQ chip gives it a USB connection for both programming and a serial console.

## How it sits on its Raspberry Pi

Each Arty reaches its Raspberry Pi host in two independent ways. One USB cable carries both JTAG and the console, because the on-board FTDI FT2232HQ gives the host one channel for each. A board whose FTDI is disconnected can be neither programmed nor reached on its console.

On hosts fitted with a [PMOD HAT](../../pmod/rpi-hat.md), three PMOD ribbon cables also carry FPGA signals straight to the Raspberry Pi's GPIO header. They run from the HAT's ports JA, JB and JC to the Arty's own JA, JB and JC. The HAT has only three ports, so the Arty's JD is not connected.

A third path is separate from both. A USB Ethernet adapter on the Raspberry Pi is cabled to the Arty's RJ45 jack. It is independent of the PMOD HAT and of the Pi's own Ethernet. It carries the Ethernet test.

## What the PMOD cables are for

The PMOD cables let the Raspberry Pi drive signals through the HAT to the Arty's PMOD connectors and check that they arrive. That is the PMOD loopback test, and the pin identification scan reads the same cables. Which cable carries which pin is on [Arty A7 wiring to a Raspberry Pi](../setup/wiring.md#pmod-cables).
