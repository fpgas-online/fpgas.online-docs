---
type: how-to
owner: documentation maintainers
reader: someone who needs a program to use a Tiny Tapeout board's serial port on its Raspberry Pi
review: 2026-11-10
---

# How to free a Tiny Tapeout board's serial port from fpgas-tt

**You want to run a program on the serial port of a Tiny Tapeout chip demo board, and the `fpgas-tt` daemon holds that port.**

The program cannot open the port until the daemon stops, and the board drops off the public site until the daemon starts again.
This page does not cover installing the daemon: [The Tiny Tapeout stack](../../../setup/tinytapeout.md).

## What you need

- A shell on the board's Raspberry Pi, with `sudo`.
- The program that needs the port, ready to run on `/dev/ttboard`, the udev link to the board's USB serial port.
- A program that copies, replaces or deletes no file on the board ([The Tiny Tapeout stack](../../../setup/tinytapeout.md)).

## Steps

1. On the Raspberry Pi, stop the daemon with `sudo systemctl stop fpgas-tt`; the port is free and the board leaves tinytapeout.fpgas.online.
2. On the Raspberry Pi, run your program on `/dev/ttboard` and close it when it is done.
3. On the Raspberry Pi, start the daemon with `sudo systemctl start fpgas-tt`; the board returns to the public site.

## Check

The daemon runs again: `systemctl is-active fpgas-tt` prints `active`, and `sudo fuser /dev/ttboard` shows its python3 process.

```console
$ systemctl is-active fpgas-tt
active
```

The board's `https://tinytapeout.fpgas.online/board/<slug>/status.json` reports the daemon's `/health` plus `reachable`.

## If it fails

| What you see | Likely cause | Fix |
|---|---|---|
| Your program cannot open `/dev/ttboard` | The daemon holds the port | Stop the daemon first, as in step 1 |
| The board is missing from the public site after your program ended | The daemon was not started again | Run step 3 |

## Next

- [Tiny Tapeout chip demo board wiring to a Raspberry Pi](wiring.md)
- [The Tiny Tapeout chip demo boards](../overview/board.md)
- [Serial port ownership on a Tiny Tapeout FPGA demo board](../../tt-fpga/overview/serial-port.md)
