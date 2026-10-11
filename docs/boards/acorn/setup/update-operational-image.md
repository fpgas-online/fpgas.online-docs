---
type: how-to
owner: documentation maintainers
reader: someone replacing the operational image in an Acorn's flash
review: 2026-11-10
---

# How to update the operational image of an Acorn

You have an Acorn that runs the fpgas.online Acorn design from flash and want to write another operational image to it. This page covers a Raspberry Pi 5. It does not cover the first install, which is [How to install the fpgas.online images on an Acorn](install-images.md).

This procedure is waiting for its run: [test-designs issue #223](https://github.com/fpgas-online/fpgas.online-test-designs/issues/223).

## What you need

- The Acorn running the fpgas.online Acorn design from flash, and the flash tool `fpgas-acorn-flash` from [How to install the Acorn packages](packages.md).
- The replacement image as `sqrl_acorn_operational.bin`, and its `.bit`.
- The load command of [How to run JTAG by hand on an Acorn on a Raspberry Pi 5](../checks/jtag-by-hand.md).
- The rescan command of [How to check an Acorn's PCIe link by hand on a Raspberry Pi 5](../checks/pcie-by-hand.md).

## Steps

1. Test the image first: detach the endpoint, load the `.bit` into SRAM over JTAG, bring PCIe back and check it.
2. Keep what the flash holds: `sudo fpgas-acorn-flash dump backup.bin` reads the whole flash. Copy `backup.bin` off the Pi, because `/home/pi` is lost at the power cycle in step 4.
3. Write the image with `sudo fpgas-acorn-flash write sqrl_acorn_operational.bin 0x400000 --idcode 0x3636093`.
4. PoE-cycle the host's switch port, then bring PCIe back with `echo 1 | sudo tee /sys/bus/pci/rescan`.

:::{warning}
**Do not write the flash with `litepcie_util flash_write`**. It checks nothing before it writes, and without an offset it writes `0x0`, the golden slot. The flash tool `fpgas-acorn-flash` checks the image against the slot and refuses `0x0` without `--i-know-this-writes-golden`.
:::

## Check

The PCIe endpoint `10ee:7021` is enumerated again after the rescan.

## If it fails

- **The image does not boot, or the card does not come back.** Follow [How to recover an Acorn with a bad image](../troubleshooting/recovery.md).
- **`fpgas-acorn-flash` refuses the write.** The image does not match the slot. The operational slot wants the flavour with the watchdog and the IDCODE of the part that is there.

## Next

- [How to install the fpgas.online images on an Acorn](install-images.md)
- [How to generate multiboot bitstreams by hand](multiboot-bitstreams.md)
