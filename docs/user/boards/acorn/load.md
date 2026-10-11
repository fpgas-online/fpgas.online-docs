---
type: how-to
owner: documentation maintainers
reader: a visitor with an Acorn's page open on welland.fpgas.online
review: 2026-11-10
---

# How to load a design onto an Acorn from its board page

**You have an Acorn's page open on welland.fpgas.online and a bitstream for it. You want the design to run, and to
see it**. The load goes into the FPGA's SRAM, so a reset brings back the image in the card's flash. A reset or a reboot also empties `/home/pi`, uploads included.

## What you need

- An Acorn's page, from [the welland list](https://welland.fpgas.online/fpgas/): a board whose label says Acorn.
- A `.bit` file for the card on that page, for example built for the CLE-215+.

## Steps

1. Upload the file with the page's **upload** button. It goes into `/home/pi/Uploads/` on the host.
2. In the page's terminal, list the card; it shows one line, at `0001:01:00.0`.

   ```console
   $ lspci -nn -s 0001:01:00.0
   ```

3. Detach the card from the PCIe bus. The card no longer shows in `lspci`. The host's PCIe controller does not survive a
   load while the card is on the bus: the host drops your terminal and reboots.

   ```console
   $ echo 1 | sudo tee /sys/bus/pci/devices/0001:01:00.0/remove
   ```

4. Make sure `gpiochip0` is the header's GPIO chip, because the loader's cable opens `gpiochip0`.

   ```{include} ../../../boards/acorn/inc/gpiochip0.inc
   ```

5. Load the design into SRAM. Put your file's name in place of `design.bit`.

   ```console
   $ openFPGALoader --cable libgpiod --pins 10:9:11:8 Uploads/design.bit
   ```

6. Rescan the bus and list the card again. A design with a PCIe endpoint shows one line. A design without one shows none,
   and the card stays off the bus until a Reset loads its flash image again.

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
| The terminal drops during the load, and the host reboots | the card was still on the PCIe bus | wait for the host to come back (press Reset, as on [How to reset a board](../reset.md), if it does not), then follow the steps again from step 1: the reboot emptied `Uploads` |
| `done 0` | the FPGA did not configure | read the STAT register printed under it, and check that the file was built for the card the page names |

More causes are on [How to check an Acorn's PCIe link by hand on a Raspberry Pi 5](../../../boards/acorn/checks/pcie-by-hand.md#if-it-fails).

## Next

- [An Acorn on fpgas.online](about.md)
- [The camera on a board](../camera.md)
