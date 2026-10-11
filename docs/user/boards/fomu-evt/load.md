---
type: how-to
owner: documentation maintainers
reader: a visitor with a Fomu EVT's page open on welland.fpgas.online
review: 2026-11-10
---

# How to load a design onto a Fomu EVT from its board page

**You have a Fomu EVT's page open on welland.fpgas.online and a `.bin` bitstream for it. You want the design to
run**. The Fomu's bootloader waits for a load for about 3 minutes after the host starts. A reset or a reboot empties
`/home/pi`, uploads included.

## What you need

- A Fomu EVT's page, from [the welland list](https://welland.fpgas.online/fpgas/): a board whose label says Fomu.
- A `.bin` file for the Fomu, here `design.bin`.

## Steps

1. Upload the file with the page's **upload** button. It goes into `/home/pi/Uploads/` on the host.
2. In the page's terminal, find `1209:5bf0` in the list. The Fomu is then in its DFU bootloader.

   ```console
   $ lsusb
   ```

3. Load the design. The bootloader writes it to the flash's user image and starts it. Do this inside the 3 minutes.

   ```console
   $ openFPGALoader -b fomu Uploads/design.bin
   ```

## Check

`openFPGALoader` ends without an error message. A design with no USB core, such as the UART echo, leaves USB, so
`lsusb` no longer lists `1209:5bf0`. That is expected. Such a design talks over the Pi's header pins, opened as
`/dev/serial0`.

## If it fails

| What you see | Likely cause | Fix |
|---|---|---|
| `1209:5bf0` is not in `lsusb` before the load | the bootloader timed out of DFU after about 3 minutes, or a bitstream with no USB core is running | press Reset, as on [How to reset a board](../reset.md): the Reset is a PoE power cycle, which restarts the DFU bootloader. Wait about two minutes, upload `design.bin` again, because the reset emptied `Uploads`, and load inside the 3 minutes |

More faults are on [Fomu EVT programming faults](../../../boards/fomu-evt/troubleshooting/programming-faults.md).

## Next

- [A Fomu EVT on fpgas.online](about.md)
- [How to reset a board](../reset.md)
