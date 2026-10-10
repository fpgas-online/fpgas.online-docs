---
type: how-to
owner: documentation maintainers
reader: someone using a demo board's serial port with their own tool
review: 2026-11-10
---

# How to stop the fpgas-tt daemon and start it again

**You want to run a tool of your own on the serial port of a Tiny Tapeout FPGA demo board.**

The `fpgas-tt` daemon holds that port open, so the tool needs the daemon stopped. The board drops off the public site until the daemon is started again. Why the daemon owns the port is on [Serial port ownership on a Tiny Tapeout FPGA demo board](../overview/serial-port.md).

## What you need

- A shell on the Raspberry Pi that has the board, with `sudo`. A Pi that is not routable from your machine is reached through its site's gateway, as [The welland gateway](../../../sites/welland-gateway.md#reaching-a-pi) shows.
- A tool that reads from the board or streams a bitstream to the FPGA. The tool must not write, replace or delete a file on the board.

## Steps

1. On the Pi, run `sudo systemctl stop fpgas-tt` to stop the daemon, which releases `/dev/ttyACM0`.
2. On the Pi, run your tool on `/dev/ttyACM0` and wait for it to finish.
3. On the Pi, run `sudo systemctl start fpgas-tt` to start the daemon again, which puts the board back on the public site.

## Check

With the daemon running, `fuser /dev/ttyACM0` shows the daemon's python3 process. After step 1 it prints nothing. After step 3 the board's `status.json` on the [Tiny Tapeout site](https://tinytapeout.fpgas.online) reports the daemon's `/health` and `reachable` again.

## If it fails

| What you see | Likely cause | Fix |
|---|---|---|
| Your tool cannot open `/dev/ttyACM0` | The daemon still holds the port | Run step 1 again, and check with `fuser /dev/ttyACM0` |
| The board is missing from the public site after your tool ended | The daemon was not started again | Run step 3 |
| You cannot stop the daemon | The tool must share the port | Drive the board through the daemon's `/serial` socket instead |

## Next

- [Serial port ownership on a Tiny Tapeout FPGA demo board](../overview/serial-port.md)
- [The Tiny Tapeout stack](../../../setup/tinytapeout.md)
- [Tiny Tapeout FPGA demo board checks](../checks/index.md)
