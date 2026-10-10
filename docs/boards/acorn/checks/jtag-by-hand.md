---
type: how-to
owner: documentation maintainers
reader: someone with an Acorn on a Raspberry Pi 5 who wants to run JTAG by hand
review: 2026-11-10
---

# How to run JTAG by hand on an Acorn on a Raspberry Pi 5

**You have an Acorn wired to a Raspberry Pi 5 and want to see its JTAG answer, then load a design over it.**

The boot check reads the IDCODE and the device DNA over P1 by itself (`jtag`): [Installing the Acorn packages](../setup/packages.md#installing-the-acorn-packages). On a Compute Blade the commands differ: [How to run JTAG by hand on an Acorn on a Compute Blade](compute-blade-jtag-by-hand.md).

## What you need

- An Acorn wired as on [Acorn wiring on a Raspberry Pi 5](../setup/rpi-5/wiring.md), in the M.2 HAT slot, where the card is at `0001:01:00.0`.
- `openFPGALoader` on the Pi, with the `libgpiod` cable.
- The pin order `10:9:11:8` (TDI:TDO:TCK:TMS) for the `--pins` option.
- The fpgas.online Acorn design's `.bit` file in `SOC`:

  ```{include} ../inc/soc-file.inc
  ```

## Steps

1. On the Pi, detach the card's PCIe endpoint, so that the load cannot remove it under the host ([why](jtag-and-the-pcie-endpoint.md#why-the-endpoint-is-detached-before-a-load)); `lspci` no longer lists the card.

   ```console
   $ echo 1 | sudo tee /sys/bus/pci/devices/0001:01:00.0/remove
   ```

2. On the Pi, link the header's GPIO chip as `gpiochip0`, because the `libgpiod` cable opens `/dev/gpiochip0` and the header is `gpiochip15` under kernel 6.12.

   ```console
   $ sudo ln -sfn /dev/gpiochip15 /dev/gpiochip0
   ```

3. On the Pi, read the IDCODE with a read-only `--detect`, which is safe without step 1; it prints the IDCODE of the chip.

   ```console
   $ openFPGALoader --cable libgpiod --pins 10:9:11:8 --detect
   ```

4. On the Pi, load the design into SRAM, which takes about 16 s for a 1.6 MB XC7A200T bitstream over `libgpiod`.

   ```console
   $ openFPGALoader --cable libgpiod --pins 10:9:11:8 $SOC
   ```

5. On the Pi, bring the endpoint back with `echo 1 | sudo tee /sys/bus/pci/rescan`, or reboot; the card is enumerated again.

## Check

The IDCODE from step 3 tells the chip: `0x3636093` for an XC7A200T (CLE-215+, CLE-215, NiteFury) and `0x3631093` for an XC7A100T (CLE-101, LiteFury).

```text
idcode 0x3636093 (XC7A200T)
```

A load over JTAG lands in SRAM and works on every variant. An SRAM load is lost at power-off, so a reboot restores whatever is in flash. Never pass `--write-flash` here: [How to install the fpgas.online images on an Acorn](../setup/install-images.md) writes the flash.

## If it fails

- **`JTAG init failed with: Unable to open gpio chip`:** the `gpiochip0` link of step 2 is missing; link the chip again.
- **`--detect` says `found 0 devices` but PCIe enumerates:** the P1 cable is unmated or miswired; check TCK for the Acorn's pull-up and reseat P1.
- **`Open file … FAIL` in under 0.1 s:** the bitstream is gone, because `/home/pi` is a memory overlay that loses its files at reboot; copy it again.
- **The Pi drops SSH and reboots during the load:** the endpoint was still enumerated; detach it (step 1) before every load.
- **JTAG programming fails:** the pin order is wrong; use `--pins 10:9:11:8`.

## Next

- [How to check an Acorn's PCIe link by hand on a Raspberry Pi 5](pcie-by-hand.md)
- [JTAG loads and the PCIe endpoint](jtag-and-the-pcie-endpoint.md)
- [Acorn wiring faults on a Raspberry Pi 5](../troubleshooting/rpi-5-wiring.md)
