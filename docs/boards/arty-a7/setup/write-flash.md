---
type: how-to
owner: documentation maintainers
reader: someone with an Arty A7 on its Raspberry Pi who wants a design to stay on it
review: 2026-11-10
---

# How to write a design into an Arty A7's flash

**You have an Arty A7 and a bitstream, and want the design to survive power cycles.**

The write replaces whatever the on-board SPI flash held. A load that is only run is on [How to load a design onto an Arty A7](load-design.md).

What a correct run prints is waiting for a run: [test-designs issue #248](https://github.com/fpgas-online/fpgas.online-test-designs/issues/248).

## What you need

- The Arty A7 joined to the Raspberry Pi by its USB cable ([Arty A7 wiring to a Raspberry Pi](wiring.md#the-usb-cable)).
- `openFPGALoader` on the Raspberry Pi ([How to install the Arty A7 packages](packages.md)).
- A bitstream, a `.bit` file, called `design.bit` below.

## Steps

1. On the Raspberry Pi, write the flash with `openFPGALoader -b arty --write-flash design.bit`, and the on-board SPI flash holds the design in place of what was there.

```console
$ openFPGALoader -b arty --write-flash design.bit
```

## Check

- The board appears on the Raspberry Pi as two `/dev/ttyUSB*` devices, the JTAG channel and the UART channel.
- `openFPGALoader` ends without an error.

## If it fails

- You see no `/dev/ttyUSB*` devices at all. The Arty's FTDI is disconnected, and a board in that state cannot be programmed or reached on its console. 

## Next

- [How to load a design onto an Arty A7](load-design.md)
- [Programming an Arty A7](../overview/programming.md)
