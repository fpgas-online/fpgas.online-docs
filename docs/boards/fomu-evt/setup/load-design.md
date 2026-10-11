---
type: how-to
owner: documentation maintainers
reader: someone with a Fomu EVT on its Raspberry Pi who wants to load a design into it
review: 2026-11-10
---

# How to load a design onto a Fomu EVT with openFPGALoader

**You have a Fomu EVT on a Pi and a `.bin` bitstream, and want it running.**

Why the board leaves USB afterwards is on [Programming a Fomu EVT](../overview/programming.md).

## What you need

- A Raspberry Pi 3B+ with the Fomu EVT plugged into its USB port and seated on its GPIO header.
- `openFPGALoader` installed on the Pi; the [packages](packages.md) bring it.
- The Fomu's DFU bootloader running, which waits for DFU activity for about 3 minutes.

## Steps

1. On the Pi, run `lsusb` and find `1209:5bf0`; the Fomu is in its DFU bootloader.
2. On the Pi, run `openFPGALoader -b fomu design.bin`, where `design.bin` is your bitstream; the bootloader writes the bitstream to the flash's user image and starts it.

## Check

- `openFPGALoader` ends without an error message.
- A design with no USB core, such as the UART echo, leaves USB: `lsusb` no longer lists `1209:5bf0`. It talks over the GPIO header pins.
- The design answers on `/dev/serial0` once the [serial login console is stopped](../checks/stop-serial-console.md).

A design with no USB core keeps the Fomu off USB, so no other design can be loaded over DFU. The test designs that
`fpgas-fomu-debug program` and `test` load are such designs. To put foboot back, run `sudo fpgas-fomu-debug reset` from the
`fpgas-online-fomu-debug` package. It resets the Fomu through the header and waits for foboot (`1209:5bf0`) on USB. A
power cycle does the same.

```console
$ sudo fpgas-fomu-debug reset
```

## If it fails

| What you see | Likely cause | Fix |
|---|---|---|
| `fpgas-fomu-debug reset` says foboot did not come back on USB | the reset through the header did not restart foboot | ask the site operator, then power-cycle the Fomu's host, and check `lsusb` again |
| `1209:5bf0` is not in `lsusb` before the load | The bootloader timed out of DFU after about 3 minutes, or a bitstream with no USB core is running | run `sudo fpgas-fomu-debug reset`, or PoE power cycle the Pi; either restarts the DFU bootloader. Then load again inside the 3 minutes |

More faults are on [Fomu EVT programming faults](../troubleshooting/programming-faults.md).

## Next

- [How to stop the serial login console before a Fomu UART test](../checks/stop-serial-console.md)
- [Fomu EVT checks](../checks/index.md)
