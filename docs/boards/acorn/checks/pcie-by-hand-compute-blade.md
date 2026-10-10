---
type: how-to
owner: documentation maintainers
reader: someone with an Acorn in a Compute Blade who wants to check its PCIe link
review: 2026-11-10
---

# How to check an Acorn's PCIe link by hand on a Compute Blade

**You have an Acorn in a Compute Blade and want to load the fpgas.online design and bring the card back on the PCIe bus.**

The boot check does the reading part by itself (`pcie-link`, `pcie-bar0`): [Installing the Acorn packages](../setup/packages.md#installing-the-acorn-packages). The design is built for the CLE-215+, the CLE-215 and the CLE-101. On a Raspberry Pi 5 the addresses and the way back differ. That page is [How to check an Acorn's PCIe link by hand on a Raspberry Pi 5](pcie-by-hand.md).

This procedure is waiting for its run: [test-designs issue #237](https://github.com/fpgas-online/fpgas.online-test-designs/issues/237).

## What you need

- An Acorn in the M.2 slot of a Compute Blade with a CM4 or a CM5.
- The JTAG wiring of [Acorn wiring on a Compute Blade](../setup/compute-blade/wiring.md), and `openFPGALoader` with the `libgpiod` cable.
- The header's chip as `gpiochip0`, as in [How to run JTAG by hand on an Acorn on a Compute Blade](compute-blade-jtag-by-hand.md).
- The header's serial port off in this boot:

  ```{include} ../inc/blade-jtag-serial-off.inc
  ```

- The card's PCI address in `BDF`:

  ```{include} ../inc/blade-first.inc
  ```

- The fpgas.online Acorn design's `.bit` file in `SOC`:

  ```{include} ../inc/soc-file.inc
  ```

## Steps

1. On the blade, list the card with `lspci`; it shows one line, whose ID says which image it runs.

   ```console
   $ lspci -nn -s $BDF
   ```

   ```{include} ../inc/lspci-ids.inc
   ```

2. On the blade, detach the card's PCIe endpoint before any JTAG load ([why](jtag-and-the-pcie-endpoint.md#why-the-endpoint-is-detached-before-a-load)); the card no longer shows in `lspci`.

   ```{include} ../inc/blade-detach.inc
   ```

3. On the blade, load the design into SRAM and put the pins back; the load ends with the done message of openFPGALoader.

   ```console
   $ openFPGALoader --cable libgpiod --pins 2:3:4:14 $SOC
   $ pinctrl set 2,4 no pu
   ```

4. On the blade, rescan the bus and list the Xilinx devices; with the LiteX design on a CM5 the list is empty ([why](jtag-and-the-pcie-endpoint.md#what-coming-back-looks-like)).

   ```console
   $ echo 1 | sudo tee /sys/bus/pci/rescan
   $ lspci -nn -d 10ee:
   ```

5. On the blade, find the root complex of the slot and print its name, which is `1000110000.pcie` on a CM5.

   ```console
   $ RC=$(readlink -f /sys/bus/pci/devices/${BDF%%:*}:00:00.0 | grep -o '[0-9a-f]*\.pcie')
   $ echo $RC
   ```

6. On the blade, unbind and bind the root complex to re-probe the slot; the link comes up at 5 GT/s x1.

   ```console
   $ echo $RC | sudo tee /sys/bus/platform/drivers/brcm-pcie/unbind
   $ echo $RC | sudo tee /sys/bus/platform/drivers/brcm-pcie/bind
   ```

7. On the blade, list the Xilinx devices again; the card is back, as the LitePCIe default for one lane.

   ```console
   $ lspci -nn -d 10ee:
   ```

## Check

Step 7 shows the fpgas.online design's ID.

```text
Xilinx Corporation Device [10ee:7021]
```

## If it fails

- **The Acorn does not appear in step 1:** the M.2 card is not seated; reseat it and read `dmesg | grep -i pci`.
- **The blade reboots or SSH drops during the load:** the endpoint was still enumerated; detach it (step 2) before every load.
- **`gpiod_line_request_set_values_subset: Assertion 'request' failed` in step 3:** the serial port was on; boot with it off.
- **`bind` fails with `No such device`:** the link was down, so the root port is gone. Load a design that links (or `openFPGALoader --reset`), then `bind` again.
- **The card still does not link:** check that the build's I/O report has the lane on B10 and B6.

## Next

- [How to run JTAG by hand on an Acorn on a Compute Blade](compute-blade-jtag-by-hand.md)
- [JTAG loads and the PCIe endpoint](jtag-and-the-pcie-endpoint.md)
- [How to recover an Acorn with a bad image](../troubleshooting/recovery.md)
