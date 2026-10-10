---
type: reference
owner: documentation maintainers
reader: someone wiring or checking a Fomu EVT on a Raspberry Pi
review: 2026-11-10
---

# Fomu EVT wiring to a Raspberry Pi

**You want to know which Fomu EVT signals reach the Raspberry Pi.** The board's pins are on [Fomu EVT specifications](../overview/specifications.md). Why the board leaves USB is on [Programming a Fomu EVT](../overview/programming.md).

## Connections to the Pi

The Fomu connects to the Pi in two ways.

- **GPIO header**: the Fomu sits directly on the Pi's GPIO header as a standard HAT, and connects UART and GPIO signals.
- **USB**: the Fomu's USB-A connector plugs into the Pi's USB port, through an inline [USB analyser](../overview/usb-analysers.md) when one is fitted.

## Serial (UART) on the GPIO header

The FPGA's serial pins connect to the Pi's GPIO UART through the GPIO header. This is a direct connection, not through USB. Each row of the first table gives a signal, its iCE40 pin, its direction and its I/O standard.

| Signal          | iCE40 Pin | Direction | I/O Standard      |
| --------------- | --------- | --------- | ----------------- |
| TX (FPGA → RPi) | 13        | Output    | LVCMOS33 (PULLUP) |
| RX (RPi → FPGA) | 21        | Input     | LVCMOS33          |

Each row of the second table gives a parameter of the Pi's side and its value.

| Parameter  | Value                                            |
| ---------- | ------------------------------------------------ |
| RPi device | `/dev/serial0` → `/dev/ttyAMA0`                  |
| Baud rate  | 115200                                           |
| Test args  | `--port /dev/serial0 --board fomu --skip-banner` |

The model-agnostic form to use is `--port /dev/serial0`. The device `/dev/serial0` is the symlink the Pi points at whichever UART is on GPIO14/GPIO15. It is right on every host, whichever kernel device that turns out to be. Each row of the third table gives a Pi UART, the kernel device it is and when the GPIO header uses it.

| Pi UART   | Kernel device    | When it is the GPIO UART                                        |
| --------- | ---------------- | --------------------------------------------------------------- |
| PL011     | `/dev/ttyAMA0`   | `hciuart` is inactive, so the PL011 is free for the FPGA UART   |
| Mini UART | `/dev/ttyS0`     | a stock Raspberry Pi 3B+, where Bluetooth holds the PL011       |

The login console on the port is stopped by [How to stop the serial login console before a Fomu UART test](../checks/stop-serial-console.md).

## PMOD / GPIO loopback

The loopback gateware uses `pmoda_n` as input and `pmodb_n` as output. Their pins are under PMODA_N and PMODB_N on [Fomu EVT specifications](../overview/specifications.md#pmod-connectors). Each row of the first table gives a connector and its loopback role.

| Connector | Role            | Note                                             |
| --------- | --------------- | ------------------------------------------------ |
| `pmoda_n` | loopback input  |                                                  |
| `pmodb_n` | loopback output | shares pins with `touch_pins`, the touch pads    |

### Confirmed loopback pair

Only 1 of the 4 loopback pairs connects to a Pi GPIO through the GPIO header. Each row gives the Pi GPIO driven, the Pi GPIO read and the status of the pair.

| Drive RPi GPIO | Read RPi GPIO | Status    |
| -------------- | ------------- | --------- |
| GPIO27         | GPIO9         | Confirmed |

GPIO9 is SPI0_MISO, so the SPI0 drivers must be removed first: [How to free the Pi's SPI0 bus for the Fomu PMOD loopback test](../checks/loopback-spi-bus.md). The Fomu GPIO output has slow propagation, roughly 5 ms of settle time. The test polls until the value is stable rather than reading once.
