---
type: how-to
owner: documentation maintainers
reader: a visitor with an Acorn's page open on welland.fpgas.online
review: 2026-11-10
---

# How to load a design onto an Acorn from its board page

**You have an Acorn's page open on welland.fpgas.online and a bitstream for it. You want the design to run, and to
see it**. The load goes into the FPGA's SRAM, so a reset brings back the image in the card's flash.

## What you need

- An Acorn's page, from [the welland list](https://welland.fpgas.online/fpgas/): a board whose label says Acorn.
- A `.bit` file for the card on that page, for example built for the CLE-215+.

## Steps

1. Upload the file with the page's **upload** button. It goes into `/home/pi/Uploads/` on the host.
2. In the page's terminal, list the card; it shows one line, at `0001:01:00.0`.

   ```console
   $ lspci -nn -s 0001:01:00.0
   ```

3. Detach the card from the PCIe bus. The card no longer shows in `lspci`. Loading a design while the card is on the
   bus crashes the host's PCIe controller, and the host then needs a Reset.

   ```console
   $ echo 1 | sudo tee /sys/bus/pci/devices/0001:01:00.0/remove
   ```

4. Link the header's GPIO chip as `gpiochip0`, because the loader's cable opens `gpiochip0` and the header is
   `gpiochip15`.

   ```console
   $ sudo ln -sfn /dev/gpiochip15 /dev/gpiochip0
   ```

5. Load the design into SRAM. Put your file's name in place of `design.bit`.

   ```console
   $ openFPGALoader --cable libgpiod --pins 10:9:11:8 Uploads/design.bit
   ```

6. If your design has a PCIe endpoint, rescan the bus and list the card again.

   ```console
   $ echo 1 | sudo tee /sys/bus/pci/rescan
   $ lspci -nn -s 0001:01:00.0
   ```

## Check

The load's last line ends with `done 1`. With `done 0` the FPGA is not configured, whatever the exit status; the
STAT register printed under it says why. Then watch the card's LEDs on the page's camera.

## If it fails

| What you see | Likely cause | Fix |
|---|---|---|
| The terminal stops answering during the load | the card was still on the PCIe bus | press Reset ([How to reset a board](../reset.md)), then follow the steps again from step 2 |
| `done 0` | the file is not for this card, or not a 7-series bitstream | check that the file was built for the card the page names |

More causes are on [How to check an Acorn's PCIe link by hand on a Raspberry Pi 5](../../../boards/acorn/checks/pcie-by-hand.md#if-it-fails).

## Next

- [An Acorn on fpgas.online](about.md)
- [The camera on a board](../camera.md)
