# Arty A7: serial (UART)

**You want to talk to a design on the Arty over its USB serial port.**

## Serial (UART)

The primary serial port uses the FTDI FT2232HQ USB-to-UART bridge. This is
**not** a GPIO connection — it goes through USB, so the FPGA's TX and RX pins
face the on-board FTDI chip rather than the Raspberry Pi header.

| Signal | FPGA Pin | Direction | IO Standard |
| --------------- | -------- | --------- | ----------- |
| TX (FPGA → RPi) | D10      | Output    | LVCMOS33    |
| RX (RPi → FPGA) | A9       | Input     | LVCMOS33    |

The FTDI chip provides two channels: Channel A for JTAG and Channel B for UART.
The UART typically appears as `/dev/ttyUSB1` on Linux (the second of two USB
serial devices created by the FT2232HQ). The host-side settings are under
[UART Interface](wiring.md#uart-interface).
