---
type: how-to
owner: documentation maintainers
reader: someone who needs a program to use a Tiny Tapeout board's serial port on its Raspberry Pi
review: 2026-11-10
---

# How to free a Tiny Tapeout board's serial port from fpgas-tt

You have a Tiny Tapeout chip demo board on a Raspberry Pi and a program, such as `mpremote`, that needs its serial port.
The `fpgas-tt` daemon holds that port open, so the program cannot open it until the daemon stops.
This page does not cover installing the daemon: [The Tiny Tapeout stack](../../../setup/tinytapeout.md).

## What you need

- A shell on the board's Raspberry Pi, with `sudo`.
- The program that needs the port, ready to run on `/dev/ttboard`.

## Steps

1. On the Raspberry Pi, stop the daemon with `sudo systemctl stop fpgas-tt`; the port is free and the board leaves tinytapeout.fpgas.online.
2. On the Raspberry Pi, run your program on `/dev/ttboard` and close it when it is done.
3. On the Raspberry Pi, start the daemon with `sudo systemctl start fpgas-tt`; the board returns to the public site.

## Check

The daemon runs again: `systemctl is-active fpgas-tt` prints `active`.

```console
$ systemctl is-active fpgas-tt
active
```

The board's `https://tinytapeout.fpgas.online/board/<slug>/status.json` reports the daemon's `/health` plus `reachable`.

## If it fails

- **Your program cannot open the port.** The daemon still holds it. Repeat step 1.
- **The board is missing from the public site.** The daemon is stopped. Run step 3.

## Next

- [Tiny Tapeout chip demo board wiring to a Raspberry Pi](wiring.md)
- [The Tiny Tapeout chip demo boards](../overview/board.md)
- [Serial port ownership](../../tt-fpga.md#serial-port-ownership)
