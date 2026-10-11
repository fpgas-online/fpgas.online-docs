---
type: how-to
owner: documentation maintainers
reader: someone with an Arty A7 on its Raspberry Pi who wants a design to stay on it
review: 2026-11-10
---

# How to write a design into an Arty A7's flash

**You have an Arty A7 and a bitstream, and want the design to survive power cycles.**

The write changes the on-board SPI flash, so step 1 keeps a copy of the bitstream region first. A load that is only run is on [How to load a design onto an Arty A7](load-design.md).

What a correct run prints is waiting for a run: [test-designs issue #248](https://github.com/fpgas-online/fpgas.online-test-designs/issues/248).

## What you need

- The Arty A7 joined to the Raspberry Pi by its USB cable ([Arty A7 wiring to a Raspberry Pi](wiring.md#the-usb-cable)).
- `openFPGALoader` on the Raspberry Pi ([How to install the Arty A7 packages](packages.md)).
- A bitstream, a `.bit` file, called `design.bit` below.

## Steps

1. On the Raspberry Pi, keep a copy of the bitstream region. That is the first 2228224 bytes of the flash, which the Arty's check reads. `ls -l backup.bin` shows 2228224 bytes. Copy `backup.bin` to your own machine: a netbooted Pi loses it at its next reboot.

   ```console
   $ openFPGALoader -b arty --dump-flash --file-size 2228224 backup.bin
   ```

2. On the Raspberry Pi, write the design to the flash and read it back.

   ```console
   $ openFPGALoader -b arty --write-flash --verify design.bit
   ```

To put the old bitstream back, run step 2 with `backup.bin` in place of `design.bit`.

## Check

- The board appears on the Raspberry Pi as two `/dev/ttyUSB*` devices, the JTAG channel and the UART channel.
- `openFPGALoader` ends without an error.

## If it fails

| What you see | Likely cause | Fix |
|---|---|---|
| no `/dev/ttyUSB*` device at all | the Arty's FTDI is not on USB; a board in that state cannot be programmed or reached on its console | run `lsusb`. If it does not list the FT2232H, `0403:6010`, check the USB cable between the board and the Pi |

## Next

- [How to load a design onto an Arty A7](load-design.md)
- [Programming an Arty A7](../overview/programming.md)
