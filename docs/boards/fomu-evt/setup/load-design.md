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
`fpgas-fomu-debug program` and `test` load are such designs.

To put foboot back, run `sudo fpgas-fomu-debug reset` from the
`fpgas-online-fomu-debug` package. It resets the Fomu through the header and waits up to 10 s for foboot (`1209:5bf0`) on USB. The Fomu is then in its
bootloader, and its 3-minute window to load starts again. A power cycle by the site operator does the same.

```console
$ sudo fpgas-fomu-debug reset
```

## If it fails

| What you see | Likely cause | Fix |
|---|---|---|
| `fpgas-fomu-debug reset: fail: foboot (1209:5bf0) did not come back on USB within 10 s` | The reset through the header did not restart foboot | Ask the site operator, then power-cycle the Fomu's host. Then check that `lsusb` lists `1209:5bf0` |
| `fpgas-fomu-debug reset: error: the closing reset could not be done` | The Pi could not drive the Fomu's header: the host is not a Raspberry Pi, the header read failed, or a header line was left an output | Ask the site operator, then power-cycle the Fomu's host. Then check that `lsusb` lists `1209:5bf0` |
| `1209:5bf0` is not in `lsusb` before the load | The bootloader timed out of DFU after about 3 minutes, or a bitstream with no USB core is running | Run `sudo fpgas-fomu-debug reset`, which restarts the DFU bootloader. If it fails, ask the site operator, then PoE power cycle the Pi. Then load again inside the 3 minutes |

More faults are on [Fomu EVT programming faults](../troubleshooting/programming-faults.md).

## Next

- [How to stop the serial login console before a Fomu UART test](../checks/stop-serial-console.md)
- [Fomu EVT checks](../checks/index.md)
