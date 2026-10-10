---
type: how-to
owner: documentation maintainers
reader: someone with an Arty A7 on its Raspberry Pi who wants a design to stay on it
review: 2026-11-10
---

# How to write a design into an Arty A7's flash

**You have an Arty A7 and a bitstream, and want the design to survive power cycles.**

The write replaces whatever the on-board SPI flash held. A load that is only run is on [How to load a design onto an Arty A7](load-design.md).

## What you need

- The Arty A7 joined to the Raspberry Pi by its USB cable ([Arty A7 wiring to a Raspberry Pi](wiring.md#the-usb-cable)).
- `openFPGALoader` on the Raspberry Pi ([How to install the Arty A7 packages](packages.md)).
- A bitstream, a `.bit` file, called `design.bit` below.

## Steps

1. On the Raspberry Pi, list the USB serial devices with `ls /dev/ttyUSB*`, and two appear: the JTAG channel and the UART channel.
2. On the Raspberry Pi, write the flash with `openFPGALoader -b arty --write-flash design.bit`, and the on-board SPI flash holds the design in place of what was there.

```console
$ ls /dev/ttyUSB*
$ openFPGALoader -b arty --write-flash design.bit
```

## Check

- `ls /dev/ttyUSB*` prints `/dev/ttyUSB0  /dev/ttyUSB1`.
- `openFPGALoader` ends without an error and the shell prompt returns.

## If it fails

- You see no `/dev/ttyUSB*` devices at all. The Arty's FTDI is disconnected, and a board in that state cannot be programmed or reached on its console. Reconnect the USB cable and list the devices again.

## Next

- [How to load a design onto an Arty A7](load-design.md)
- [Programming an Arty A7](../overview/programming.md)
