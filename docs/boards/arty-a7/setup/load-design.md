---
type: how-to
owner: documentation maintainers
reader: someone with an Arty A7 on its Raspberry Pi who wants to run a design on it
review: 2026-11-10
---

# How to load a design onto an Arty A7

**You have an Arty A7 and a bitstream, and want to run the design on the board.**

This is a volatile load: the design is lost at the next power cycle. To keep a design, use [How to write a design into an Arty A7's flash](write-flash.md).

## What you need

- The Arty A7 joined to the Raspberry Pi by its USB cable ([Arty A7 wiring to a Raspberry Pi](wiring.md#the-usb-cable)).
- `openFPGALoader` on the Raspberry Pi ([How to install the Arty A7 packages](packages.md)).
- A bitstream, a `.bit` file, called `design.bit` below.

## Steps

1. On the Raspberry Pi, list the USB serial devices with `ls /dev/ttyUSB*`, and two appear: the JTAG channel and the UART channel.
2. On the Raspberry Pi, load the design with `openFPGALoader -b arty design.bit`, and the FPGA runs it from SRAM.

```console
$ ls /dev/ttyUSB*
$ openFPGALoader -b arty design.bit
```

## Check

- `ls /dev/ttyUSB*` prints `/dev/ttyUSB0  /dev/ttyUSB1`.
- `openFPGALoader` ends without an error and the shell prompt returns.

## If it fails

- You see no `/dev/ttyUSB*` devices at all. The Arty's FTDI is disconnected, and a board in that state cannot be programmed or reached on its console. Reconnect the USB cable and list the devices again.

## Next

- [How to write a design into an Arty A7's flash](write-flash.md)
- [How to run the Arty A7 UART test by hand](../checks/uart-by-hand.md)
