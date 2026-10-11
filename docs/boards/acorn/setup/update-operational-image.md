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
- The replacement image as `sqrl_acorn_operational.bin`, and its `.bit`, kept on your own machine. Every power cycle clears `/home/pi`, so the steps copy them again.
- The load command of [How to run JTAG by hand on an Acorn on a Raspberry Pi 5](../checks/jtag-by-hand.md).
- The rescan command of [How to check an Acorn's PCIe link by hand on a Raspberry Pi 5](../checks/pcie-by-hand.md).

## Steps

1. Copy the `.bit` and `sqrl_acorn_operational.bin` into `/home/pi` on the Pi, and run every command there. Test the image first: detach the endpoint, load the `.bit` into SRAM over JTAG, bring PCIe back and check it.
2. At the switch, PoE-cycle the host's port and wait more than 90 s. The card runs its flash image again, not the test load of step 1.
3. On the Pi, keep what the flash holds: `sudo fpgas-acorn-flash dump backup.bin` reads all 32 MiB in about a minute.
4. On the Pi, run `sudo chown pi backup.bin`. From your own machine, copy it off with `scp pi@HOST:backup.bin .`, adding the options your `ssh` login needs. Check that it arrived.
5. Copy `sqrl_acorn_operational.bin` into `/home/pi` again, because the cycle in step 2 cleared it. On the Pi, write the image with `sudo fpgas-acorn-flash write sqrl_acorn_operational.bin 0x400000 --idcode 0x3636093`. On a CLE-101 the IDCODE is `0x3631093`.
6. At the switch, PoE-cycle the host's port and wait more than 90 s.
7. Copy `sqrl_acorn_operational.bin` into `/home/pi` again. On the Pi, check that the slot holds the image of step 5: `sudo fpgas-acorn-flash verify sqrl_acorn_operational.bin 0x400000`.

:::{warning}
**Do not write the flash with `litepcie_util flash_write`**. It checks nothing before it writes, and without an offset it writes `0x0`, the golden slot. The flash tool `fpgas-acorn-flash` checks the image against the slot and refuses `0x0` without `--i-know-this-writes-golden`.
:::

## Check

Step 7 passes, and `lspci -nn -s 0001:01:00.0` lists the design's ID `10ee:7021` without any JTAG load.

## If it fails

- **The image does not boot, or the card does not come back.** Follow [How to recover an Acorn with a bad image](../troubleshooting/recovery.md).
- **`fpgas-acorn-flash` refuses to start, because the `litepcie` module is loaded.** Unload it with `sudo rmmod litepcie`, then run the step again.
- **`fpgas-acorn-flash` refuses the write.** The image does not match the slot. The operational slot wants the flavour with the watchdog and the IDCODE of the part that is there.

## Next

- [How to install the fpgas.online images on an Acorn](install-images.md)
- [How to generate multiboot bitstreams by hand](multiboot-bitstreams.md)
