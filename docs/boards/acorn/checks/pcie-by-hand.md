---
type: how-to
owner: documentation maintainers
reader: someone with an Acorn in a Raspberry Pi 5 who wants to check its PCIe link
review: 2026-11-10
---

# How to check an Acorn's PCIe link by hand on a Raspberry Pi 5

**You have an Acorn on a Raspberry Pi 5 and want to load the fpgas.online design and bring the card back.**

The boot check does the reading part by itself (`pcie-link`, `pcie-bar0`): [Installing the Acorn packages](../setup/packages.md#installing-the-acorn-packages). The design is built for the CLE-215+, the CLE-215 and the CLE-101. On a Compute Blade the addresses and the way back differ: [How to check an Acorn's PCIe link by hand on a Compute Blade](pcie-by-hand-compute-blade.md).

## What you need

- An Acorn in the M.2 slot of a Pi 5 with the M.2 HAT, where the card is at `0001:01:00.0`.
- The JTAG wiring of [Acorn wiring on a Raspberry Pi 5](../setup/rpi-5/wiring.md), and `openFPGALoader` with the `libgpiod` cable.
- The fpgas.online Acorn design's `.bit` file in `SOC`:

  ```{include} ../inc/soc-file.inc
  ```

## Steps

1. On the Pi, list the card with `lspci`; it shows one line, whose ID says which image it runs.

   ```console
   $ lspci -nn -s 0001:01:00.0
   ```

   ```{include} ../inc/lspci-ids.inc
   ```

2. On the Pi, detach the card's PCIe endpoint before any JTAG load ([why](jtag-and-the-pcie-endpoint.md#why-the-endpoint-is-detached-before-a-load)); the card no longer shows in `lspci`.

   ```console
   $ echo 1 | sudo tee /sys/bus/pci/devices/0001:01:00.0/remove
   ```

3. On the Pi, link the header's GPIO chip as `gpiochip0`, because the `libgpiod` cable opens `gpiochip0` and the header is `gpiochip15`.

   ```console
   $ sudo ln -sfn /dev/gpiochip15 /dev/gpiochip0
   ```

4. On the Pi, load the design into SRAM; the load ends with the done message of openFPGALoader.

   ```console
   $ openFPGALoader --cable libgpiod --pins 10:9:11:8 $SOC
   ```

5. On the Pi, rescan the bus; the link is up the moment the load finishes, so the rescan enumerates the card.

   ```console
   $ echo 1 | sudo tee /sys/bus/pci/rescan
   ```

6. On the Pi, list the Xilinx devices; the card is back, as the LitePCIe default for one lane.

   ```console
   $ lspci -nn -d 10ee:
   ```

## Check

Step 6 shows the fpgas.online design's ID.

```text
Xilinx Corporation Device [10ee:7021]
```

## If it fails

- **The Acorn is not in step 1:** the M.2 card or the HAT's FPC cable is loose; reseat both and read `dmesg | grep -i pci`.
- **The Pi reboots or SSH drops during the load:** the endpoint was still enumerated; detach it (step 2) before every load.
- **Step 6 shows nothing:** the card did not link; re-probe the slot's root complex with the lines below, then run step 6 again.
- **`bind` fails with `No such device`, and the driver logs `link down`:** the link was down, so the root port `0001:00:00.0` is gone. Load a design that links (or `openFPGALoader --reset`), then `bind` again.
- **The card still does not link:** check that the build's I/O report has the lane on B10 and B6.

The re-probe finds the platform device behind the slot, `1000110000.pcie`, then unbinds and binds it. `lspci -nn -s 0001:01:00.0` then shows the card:

```console
$ RC=$(readlink -f /sys/bus/pci/devices/0001:00:00.0 | grep -o '[0-9a-f]*\.pcie')
$ echo $RC | sudo tee /sys/bus/platform/drivers/brcm-pcie/unbind
$ echo $RC | sudo tee /sys/bus/platform/drivers/brcm-pcie/bind
$ lspci -nn -s 0001:01:00.0
0001:01:00.0 Memory controller [0580]: Xilinx Corporation Device [10ee:7021]
```

## Next

- [How to run JTAG by hand on an Acorn on a Raspberry Pi 5](jtag-by-hand.md)
- [JTAG loads and the PCIe endpoint](jtag-and-the-pcie-endpoint.md)
- [How to recover an Acorn with a bad image](../troubleshooting/recovery.md)
