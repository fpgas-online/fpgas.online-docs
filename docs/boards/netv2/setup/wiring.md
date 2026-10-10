---
type: reference
owner: documentation maintainers
reader: someone wiring or debugging a NeTV2 on a Pi
review: 2026-11-10
---

# NeTV2 wiring to a Raspberry Pi

**You want to know which NeTV2 signal goes to which Raspberry Pi pin.**

The NeTV2 stacks on the Pi's 40-pin header, so these connections are direct GPIO wires. The board's own pins are on [NeTV2 specifications](../overview/specifications.md).

## JTAG

JTAG signal is the NeTV2's signal, RPi GPIO and RPi header pin are where it lands, and Direction is seen from the Pi. The mapping comes from the NeTV2 MVP scripts' [alphamax-rpi OpenOCD configuration](https://github.com/alphamaxmedia/netv2mvp-scripts/blob/master/alphamax-rpi.cfg). openFPGALoader's `--pins` order is TDI:TDO:TCK:TMS, so these pins are `--pins 27:22:4:17`.

| JTAG Signal | RPi GPIO | RPi Header Pin | Direction (from RPi) |
| ----------- | -------- | -------------- | -------------------- |
| TCK         | GPIO4    | Pin 7          | Output               |
| TMS         | GPIO17   | Pin 11         | Output               |
| TDI         | GPIO27   | Pin 13         | Output               |
| TDO         | GPIO22   | Pin 15         | Input                |
| SRST        | GPIO24   | Pin 18         | Output               |

## Primary UART

Signal is the NeTV2's serial signal, FPGA pin its ball, and RPi GPIO and RPi header pin the Pi's side. Both FPGA pins are LVCMOS33. The FPGA's TX connects to the Pi's RX (GPIO15) and the FPGA's RX to the Pi's TX (GPIO14). The Pi's device for this port is in [Serial device by Raspberry Pi model](../overview/specifications.md#serial-device-by-raspberry-pi-model).

| Board | Signal  | FPGA Pin | RPi GPIO     | RPi Header Pin |
| ----- | ------- | -------- | ------------ | -------------- |
| NeTV2 | FPGA TX | E14      | GPIO15 (RXD) | Pin 10         |
| NeTV2 | FPGA RX | E13      | GPIO14 (TXD) | Pin 8          |

## Secondary UART on the PCIe hax pins

Signal is the serial signal, FPGA pin its ball, and PCIe hax pin the auxiliary pin on the PCIe connector that carries it. Both FPGA pins are LVCMOS33. These pins give a second serial channel and are reachable only over the PCIe connector, so only on a Raspberry Pi 5.

| Signal | FPGA Pin | PCIe Hax Pin |
| ------ | -------- | ------------ |
| TX     | B17      | hax7         |
| RX     | A18      | hax8         |

## GPIO loopback

Drive RPi GPIO is the Pi pin that drives the FPGA input, and Read RPi GPIO is the Pi pin that reads the FPGA output. The loopback uses the same FPGA pins as the primary UART: a 1-bit loopback through GPIO14 and GPIO15.

| Drive RPi GPIO | FPGA Pin (Input) | Read RPi GPIO | FPGA Pin (Output) |
| -------------- | ---------------- | ------------- | ----------------- |
| GPIO14         | E13              | GPIO15        | E14               |
