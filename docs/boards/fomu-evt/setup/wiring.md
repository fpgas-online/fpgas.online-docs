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
| RPi device | `/dev/serial0`, which is `/dev/ttyAMA0` or `/dev/ttyS0` (the third table) |
| Baud rate  | 115200                                           |
| Test args  | `--port /dev/serial0 --board fomu --skip-banner` |

The model-agnostic form to use is `--port /dev/serial0`. The device `/dev/serial0` is the symlink the Pi points at whichever UART is on GPIO14/GPIO15. It is right on every host, whichever kernel device that turns out to be. Which one a Fomu's Raspberry Pi has is [test-designs issue #252](https://github.com/fpgas-online/fpgas.online-test-designs/issues/252). Each row of the third table gives a Pi UART, the kernel device it is and when the GPIO header uses it.

| Pi UART   | Kernel device    | When it is the GPIO UART                                        |
| --------- | ---------------- | --------------------------------------------------------------- |
| PL011     | `/dev/ttyAMA0`   | `hciuart` is inactive, so the PL011 is free for the FPGA UART   |
| Mini UART | `/dev/ttyS0`     | a stock Raspberry Pi 3B+, where Bluetooth holds the PL011       |

The login console on the port is stopped by [How to stop the serial login console before a Fomu UART test](../checks/stop-serial-console.md).

## PMOD / GPIO loopback

The loopback gateware uses `pmoda_n` as input and `pmodb_n` as output. Their pins are under PMODA_N and PMODB_N on [Fomu EVT specifications](../overview/specifications.md#pmod-connectors). Each row of the table gives a connector and its loopback role.

| Connector | Role            | Note                                             |
| --------- | --------------- | ------------------------------------------------ |
| `pmoda_n` | loopback input  |                                                  |
| `pmodb_n` | loopback output | shares pins with `touch_pins`, the touch pads    |

Neither connector reaches a pin of the Raspberry Pi's header on an EVT.

### Not a loopback on the EVT

"Drive GPIO27, read GPIO9" is not a loopback pair on an EVT that sits on the Raspberry Pi's header. Each row gives a Pi GPIO and the net of the EVT it is on.

| Pi GPIO | Net on the EVT |
| ------- | -------------- |
| GPIO27  | the iCE40's CRESET, a dedicated reset input |
| GPIO9   | the flash's MISO |

No net joins the two. The check's `pmod` and `pin-id` tests assume the PMOD HAT's wiring, which an EVT on the header does not have. What those tests become is [test-designs issue #202](https://github.com/fpgas-online/fpgas.online-test-designs/issues/202).

The Pi lines that an iCE40 design can drive on this board are:

- the six `dbg` pins, on GPIO 2, 3, 4, 18, 22 and 7;
- the UART, on GPIO 14 and 15;
- the SPI pins it shares with its flash, on GPIO 8-11, 24 and 25.

A design can drive the SPI pins only once it has loaded. It never can while the Pi reads the flash with the iCE40 held in reset.
