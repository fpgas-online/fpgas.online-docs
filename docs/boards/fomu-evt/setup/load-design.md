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

- A Raspberry Pi with the Fomu EVT plugged into its USB port and seated on its GPIO header.
- `openFPGALoader` installed on the Pi; the [packages](packages.md) bring it.
- The Fomu's DFU bootloader running, which waits for DFU activity for about 3 minutes.

## Steps

1. On the Pi, run `lsusb` and find `1209:5bf0`; the Fomu is in its DFU bootloader.
2. On the Pi, run `openFPGALoader -b fomu design.bin`, where `design.bin` is your bitstream; the bitstream loads into the iCE40's volatile SRAM.
3. If the design has no USB core, run `lsusb` again; the Fomu is gone from USB, and the design talks over the GPIO header pins.

## Check

- `openFPGALoader` ends without an error message.
- A test bitstream such as the UART echo has no USB core, so `lsusb` no longer lists `1209:5bf0`.
- The design answers on `/dev/serial0` once the [serial login console is stopped](../checks/stop-serial-console.md).

## If it fails

| What you see | Likely cause | Fix |
|---|---|---|
| `1209:5bf0` is not in `lsusb` before the load | The bootloader timed out of DFU after about 3 minutes, or a bitstream with no USB core is running | PoE power cycle the Pi, which restarts the DFU bootloader, then load again inside the 3 minutes |
| The design you loaded earlier is gone after a power cycle | A power cycle discards the volatile SRAM load | Load it again |

More faults are on [Fomu EVT programming faults](../troubleshooting/programming-faults.md).

## Next

- [How to stop the serial login console before a Fomu UART test](../checks/stop-serial-console.md)
- [Fomu EVT checks](../checks/index.md)
