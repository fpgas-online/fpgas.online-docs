# Fomu EVT: USB and serial (UART)

**You want the Fomu's native USB pins and how a design talks over its serial port.**

## USB Interface

The Fomu connects directly to a USB port and implements a full USB 1.1 Full
Speed device using the ValentyUSB soft core on the iCE40UP5K. No external USB
PHY is needed — the iCE40UP5K has dedicated USB I/O pins.

| Signal    | iCE40 Pin | I/O Standard | Description                             |
| --------- | --------- | ------------ | --------------------------------------- |
| D+        | 34        | LVCMOS33     | USB data positive                       |
| D-        | 37        | LVCMOS33     | USB data negative                       |
| Pull-up   | 35        | LVCMOS33     | 1.5K pullup for Full Speed identification |
| Pull-down | 36        | LVCMOS33     | Pulldown resistor control               |

All USB pins use the LVCMOS33 I/O standard.

The USB interface supports DFU (Device Firmware Upgrade) for bitstream loading,
as well as acting as a CDC-ACM serial port or a custom USB device depending on
the loaded design. When this interface is live on a fleet host, and what happens
to it once a test bitstream is loaded, is under
[USB connection to the Pi](wiring.md#usb-connection-to-the-pi).

Source: [LiteX platform file for the Fomu EVT](https://github.com/litex-hub/litex-boards/blob/master/litex_boards/platforms/kosagi_fomu_evt.py)

## Serial (UART)

The EVT board has a serial port on two iCE40 pins. The board documentation
treats it as a debugging extra, on the grounds that USB (CDC-ACM or DFU) is the
Fomu's primary channel — but that is not how the fleet uses it. The test
bitstreams contain no USB core, so the Fomu leaves USB the moment one is loaded,
and the harness talks to the design over these two pins, wired to the Pi's own
GPIO UART and opened as `/dev/serial0`. This reconciles the two statements in the
[Interfaces to the Raspberry Pi](../index.md#interfaces-to-the-raspberry-pi) table
and in the Welland Fomu host notes: the Fomu has no USB serial device, and it
does have a serial port — on the GPIO header. How the pins reach the Pi is covered under
[UART interface](wiring.md#uart-interface).

| Signal | FPGA Pin | I/O Standard | Notes       |
| ------ | -------- | ------------ | ----------- |
| RX     | 21       | LVCMOS33     |             |
| TX     | 13       | LVCMOS33     | Has PULLUP  |

Source: [LiteX platform file for the Fomu EVT](https://github.com/litex-hub/litex-boards/blob/master/litex_boards/platforms/kosagi_fomu_evt.py)
