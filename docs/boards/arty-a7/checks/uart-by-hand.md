---
type: how-to
owner: documentation maintainers
reader: someone with an Arty A7 on its Raspberry Pi who wants to test its serial channel
review: 2026-11-10
---

# How to run the Arty A7 UART test by hand

**You have an Arty A7 on its Raspberry Pi and want to run the UART test by hand.**

The UART reaches the Pi through channel B of the FTDI chip, as `/dev/ttyUSB1` at 115200 baud with no flow control. The test passes when the LiteX BIOS banner arrives and printable ASCII echoes back.

## What you need

- The Arty A7 joined to the Raspberry Pi by its USB cable ([Arty A7 wiring to a Raspberry Pi](../setup/wiring.md#the-uart-channel)).
- `fpgas-arty-debug` on the Raspberry Pi, from the `fpgas-online-arty-debug` package ([How to install the Arty A7 packages](../setup/packages.md)).

## Steps

1. On the Raspberry Pi, run the test with `sudo fpgas-arty-debug test uart`, which loads the UART design and runs its host script.
2. If the board's UART is not the default, name it with `--port /dev/ttyUSB1` before `test`, and the script reads that port.

```console
$ sudo fpgas-arty-debug test uart
$ sudo fpgas-arty-debug --port /dev/ttyUSB1 test uart
```

## Check

- The test passes when its host script exits 0, so `echo $?` prints `0`.

## If it fails

- You see no `/dev/ttyUSB1`. The Arty's FTDI is disconnected, and a board in that state cannot be reached on its console. Reconnect the USB cable.
- The test talks to the wrong device. `/dev/ttyUSB0` is the JTAG channel and `/dev/ttyUSB1` is the UART channel. Pass `--port /dev/ttyUSB1`.

## Next

- [How to run the Arty A7 GPIO loopback test by hand](gpio-loopback-by-hand.md)
- [How to load a design onto an Arty A7](../setup/load-design.md)
