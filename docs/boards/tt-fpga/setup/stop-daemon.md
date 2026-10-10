---
type: how-to
owner: documentation maintainers
reader: someone using a demo board's serial port with their own tool
review: 2026-11-10
---

# How to stop the fpgas-tt daemon and start it again

**You want to run a tool on the serial port of a Tiny Tapeout FPGA demo board, and the `fpgas-tt` daemon holds that port.**

The board drops off the public site until the daemon is started again. Why the daemon owns the port is on [Serial port ownership on a Tiny Tapeout FPGA demo board](../overview/serial-port.md). A tool can also drive the board through the daemon's `/serial` socket, which needs no stop.

## What you need

- A shell on the Raspberry Pi that has the board, with `sudo`. A Pi that is not routable from your machine is reached through its site's gateway, as [The welland gateway](../../../sites/welland-gateway.md#reaching-a-pi) shows.
- The tool you want to run, one that opens `/dev/ttyACM0` itself.

## Steps

1. On the Pi, run `sudo systemctl stop fpgas-tt` to stop the daemon, which releases `/dev/ttyACM0`.
2. On the Pi, run your tool on `/dev/ttyACM0`, and wait until it has closed the port.
3. On the Pi, run `sudo systemctl start fpgas-tt` to start the daemon again, whether or not step 2 succeeded, which puts the board back on the public site.

## Check

After step 3, `fuser /dev/ttyACM0` shows the daemon's python3 process again. The board's `status.json`, whose address is on [The Tiny Tapeout stack](../../../setup/tinytapeout.md), reports the daemon's `/health` and `reachable`.

## If it fails

| What you see | Likely cause | Fix |
|---|---|---|
| Your tool cannot open `/dev/ttyACM0` | The daemon holds the port | Stop the daemon first, as in step 1 |
| The board is missing from the public site after your tool ended | The daemon was not started again | Run step 3 |

## Next

- [Serial port ownership on a Tiny Tapeout FPGA demo board](../overview/serial-port.md)
- [The Tiny Tapeout stack](../../../setup/tinytapeout.md)
- [Tiny Tapeout FPGA demo board checks](../checks/index.md)
