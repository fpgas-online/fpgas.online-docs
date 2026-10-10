---
type: explanation
owner: documentation maintainers
reader: someone with a Fomu EVT who wants to know what it is
review: 2026-11-10
---

# The Fomu EVT board

**You have a Fomu EVT and want to know what the board is.** Its pins are on [Fomu EVT specifications](specifications.md). How a design reaches it is on [Programming a Fomu EVT](programming.md). Its wires to the Pi are on [Fomu EVT wiring to a Raspberry Pi](../setup/wiring.md).

The Fomu is a tiny FPGA board that fits inside a USB Type-A port, designed by the Fomu project. The EVT (Engineering Validation Test) revision is the one used in the fpgas.online test infrastructure. It is built around a Lattice iCE40UP5K with native USB. The FPGA has dedicated USB I/O pins, so there is no external PHY and no FTDI. The board therefore enumerates as a USB device by itself, and it is programmed over USB DFU rather than over JTAG.

:::{admonition} Figure to come
:class: placeholder

The whole Fomu EVT, top and bottom, with the USB contacts, the RGB LED, the touch pads, the PMOD pads and the debug header marked. Tracked in ISSUE-02.
:::

## How it sits on its Raspberry Pi

The Fomu EVT connects to the Pi in two ways. The first is the GPIO header: the Fomu sits directly on the Pi's GPIO header as a standard HAT, and carries UART and GPIO signals. The second is USB: the Fomu's USB-A connector plugs into the Pi's USB port, through an inline [USB analyser](usb-analysers.md) when one is fitted.

The USB interface is live only when the DFU bootloader or a USB-enabled bitstream is loaded. The custom test bitstreams (UART echo, GPIO loopback) do not include USB, so the Fomu disappears from USB after programming. That is expected, not a fault. The board then has no USB serial device. It does have a serial port: two pins on the GPIO header, opened as `/dev/serial0` on the Pi.

The board documentation treats the serial port as a debugging extra, on the grounds that USB (CDC-ACM or DFU) is the Fomu's primary channel. That is not how fpgas.online uses it. The reasons are on [Programming a Fomu EVT](programming.md).
