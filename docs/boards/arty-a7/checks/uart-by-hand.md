---
type: how-to
owner: documentation maintainers
reader: someone with an Arty A7 on its Raspberry Pi who wants to test its serial channel
review: 2026-11-10
---

# How to run the Arty A7 UART test by hand

**You have an Arty A7 on its Raspberry Pi and want to run the UART test by hand.**

The UART reaches the Pi through channel B of the FTDI chip, as `/dev/ttyUSB1` at 115200 baud with no flow control. The test passes when the LiteX BIOS banner arrives and printable ASCII echoes back.

This procedure is waiting for its run: [test-designs issue #248](https://github.com/fpgas-online/fpgas.online-test-designs/issues/248).

## What you need

- The Arty A7 joined to the Raspberry Pi by its USB cable ([Arty A7 wiring to a Raspberry Pi](../setup/wiring.md#the-uart-channel)).
- The fpgas.online apt repository on the Raspberry Pi: [How to install the Arty A7 packages](../setup/packages.md). Step 1 installs the debug tool, which `fpgas-online-arty` does not bring.

## Steps

1. On the Raspberry Pi, install the debug tool, `fpgas-arty-debug`.

   ```console
   $ sudo apt install fpgas-online-arty-debug
   ```

2. On the Raspberry Pi, run the test, which loads the UART design and runs its host script.

   ```console
   $ sudo fpgas-arty-debug test uart
   ```

## Check

- The test passes when its host script exits 0, so `echo $?` prints `0`.

## If it fails

| What you see | Likely cause | Fix |
|---|---|---|
| no `/dev/ttyUSB1` | the Arty's FTDI is not on USB; a board in that state cannot be programmed or reached on its console | run `lsusb`. If it does not list the FT2232H, `0403:6010`, check the USB cable between the board and the Pi |
| the test talks to the wrong device | the tool uses `/dev/ttyUSB1`, and another USB serial device on the Pi has taken that name | find the UART channel's own port: in `ls -l /dev/serial/by-id/`, the Arty's entry ending in `-if01-port0` points at it. Name that port before `test`, for example `sudo fpgas-arty-debug --port /dev/ttyUSB2 test uart` |

## Next

- [How to run the Arty A7 GPIO loopback test by hand](gpio-loopback-by-hand.md)
- [How to load a design onto an Arty A7](../setup/load-design.md)
