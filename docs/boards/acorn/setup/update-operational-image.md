---
type: how-to
owner: documentation maintainers
reader: someone replacing the operational image in an Acorn's flash
review: 2026-11-10
---

# How to update the operational image of an Acorn

You have an Acorn that runs the fpgas.online Acorn design from flash and want to write another operational image to it. This page covers a Raspberry Pi 5. It does not cover the first install, which is [How to install the fpgas.online images on an Acorn](install-images.md).

This procedure is waiting for its run: ISSUE-04.

## What you need

- The Acorn running the fpgas.online Acorn design from flash, and the flash tool from [Installing the Acorn packages](packages.md#installing-the-acorn-packages).
- The replacement image as `sqrl_acorn_operational.bin`, and its `.bit`.
- The load and rescan commands of [How to run JTAG by hand on an Acorn](../checks/jtag-by-hand.md) and [How to check an Acorn's PCIe link by hand](../checks/pcie-by-hand.md).

## Steps

1. Test the image first: detach the endpoint, load the `.bit` into SRAM over JTAG, bring PCIe back and check it.
2. Check what is in the slot before the write with `sudo python3 spi_flash.py verify sqrl_acorn_operational.bin 0x400000`.
3. Write the image with `sudo python3 spi_flash.py write sqrl_acorn_operational.bin 0x400000 --idcode 0x3636093`.
4. Warm-boot to `0x400000` over ICAP, or PoE-cycle the host's switch port, then bring PCIe back with `echo 1 | sudo tee /sys/bus/pci/rescan`.

With the `litepcie` kernel module loaded, `litepcie_util` writes and reloads instead of steps 3 and 4:

```console
$ litepcie_util flash_write operational.bin 0x400000
$ litepcie_util flash_reload        # ICAP warm boot from flash
```

:::{warning}
**`litepcie_util` checks nothing before it writes.** `spi_flash.py` checks the image against the slot and refuses address `0x0` without `--i-know-this-writes-golden`. `litepcie_util` does neither.
:::

## Check

The PCIe endpoint `10ee:7021` is enumerated again after the rescan.

## If it fails

- **The image does not boot, or the card does not come back.** Follow [How to recover an Acorn with a bad image](../troubleshooting/recovery.md).
- **`spi_flash.py` refuses the write.** The image does not match the slot. The operational slot wants the flavour with the watchdog and the IDCODE of the part that is there.

## Next

- [How to install the fpgas.online images on an Acorn](install-images.md)
- [How to generate multiboot bitstreams by hand](multiboot-bitstreams.md)
