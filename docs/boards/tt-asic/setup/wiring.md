---
type: reference
owner: documentation maintainers
reader: someone wiring a Tiny Tapeout chip demo board
review: 2026-11-10
---

# Tiny Tapeout chip demo board wiring to a Raspberry Pi

This page lists the two links between a Tiny Tapeout chip demo board and its Raspberry Pi: USB and the PMOD HAT ribbon.
What the board is, is on [The Tiny Tapeout chip demo boards](../overview/board.md).
It holds no per-signal table of the ribbon.

## The USB link

Item names a property of the link; Value is what the Raspberry Pi sees.

| Item | Value |
| ---- | ----- |
| Carries | the controller's USB CDC serial console, the MicroPython REPL |
| USB name | "MicroPython Board in FS mode" |
| VID:PID | `2e8a:0005` |
| Device | `/dev/serial/by-id/usb-MicroPython_Board_in_FS_mode_<serial>-if00` |
| udev symlink | `/dev/ttboard` to `/dev/ttyACM0` |
| Owner of the port | the `fpgas-tt` daemon, which republishes it as a WebSocket on port 8765 |
| Liveness | `https://tinytapeout.fpgas.online/board/<slug>/status.json`, the daemon's `/health` plus `reachable` |

The daemon's endpoints are on [Serial port ownership on a Tiny Tapeout FPGA demo board](../../tt-fpga/overview/serial-port.md).
The steps to stop and start it are in [How to free a Tiny Tapeout board's serial port from fpgas-tt](free-the-serial-port.md).

## The PMOD HAT ribbon

A Digilent Pmod HAT ribbon brings the demo board's PMOD connectors onto the Raspberry Pi's GPIO header.
The adapter is the [Raspberry Pi PMOD HAT](../../pmod/rpi-hat.md); the connectors are on [Tiny Tapeout PMOD layouts](../../pmod/tinytapeout.md).
The cabling the `wiring` test expects is under [The wiring test](../../../verify/tt-fpga.md#the-wiring-test).
