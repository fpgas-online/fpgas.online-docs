---
type: how-to
owner: documentation maintainers
reader: someone putting the fpgas.online images into an Acorn's flash
review: 2026-11-10
---

# How to install the fpgas.online images on an Acorn

You have an Acorn on a Raspberry Pi 5 whose JTAG answers. You want its flash to hold the fpgas.online golden and operational images. This page covers a Raspberry Pi 5. A card on a Compute Blade is not covered: its conversion was begun and stopped, as [test-designs issue #213](https://github.com/fpgas-online/fpgas.online-test-designs/issues/213) describes.

What the two images are is on [the fpgas.online Acorn design](../overview/design.md). What to do when an image is bad is on [How to recover an Acorn with a bad image](../troubleshooting/recovery.md).

## What you need

- The Acorn on a Raspberry Pi 5 with the M.2 HAT, wired for JTAG ([Acorn wiring on a Raspberry Pi 5](rpi-5/wiring.md)).
- The packages `fpgas-online-acorn-tools` and `fpgas-online-acorn-bitstreams` ([Installing the Acorn packages](packages.md#installing-the-acorn-packages)). The tools package installs `spi_flash.py` as `/usr/bin/fpgas-acorn-flash`, so on a host with the packages `sudo fpgas-acorn-flash id` is `sudo python3 spi_flash.py id`.
- The images in `/usr/share/fpgas-online/acorn-pcie/images/`, where `manifest.json` lists them. For a CLE-215+ the operational image (`sqrl_acorn_operational.bin` below) is `acorn-cle-215p-sqrl_acorn_operational.bin` there. The golden image (`sqrl_acorn_fallback.bin` below) is `acorn-cle-215p-golden-sqrl_acorn_fallback.bin`. For a CLE-101 put `cle-101` in place of `cle-215p`.
- The card's PCIe address, `<bdf>` below: `0001:01:00.0` on a Raspberry Pi 5 with the M.2 HAT.
- A way to PoE-cycle the host's switch port, for step 9.
- The load and rescan commands of [How to run JTAG by hand on an Acorn](../checks/jtag-by-hand.md) and [How to check an Acorn's PCIe link by hand](../checks/pcie-by-hand.md).

## Steps

The tool is [`spi_flash.py`](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/verify/src/fpgas_online_verify/boards/acorn/spi_flash.py). How it reaches the flash is on [Reaching an Acorn's flash through PCIe](flash-access.md).

1. On the Pi, prove JTAG with `--detect`, detach the endpoint and load the operational `.bit` into SRAM, then rescan: PCIe enumerates `10ee:7021`.

```console
# Pi 5: the libgpiod cable opens gpiochip0; the 40-pin header is gpiochip15
$ sudo ln -sfn /dev/gpiochip15 /dev/gpiochip0
$ openFPGALoader --cable libgpiod --pins 10:9:11:8 --detect
# Expected on a CLE-215+: idcode 0x3636093 (XC7A200T). "found 0 devices": stop here.
```

2. Read the flash ID with `sudo python3 spi_flash.py id`: S25FL256S, RDID `01 02 19 4d 01 80`, 32 MiB, QUAD bit set.
3. Dump the flash twice with `sudo python3 spi_flash.py dump factory.bin`, the second dump to another file name, and compare them: their SHA-256 is identical. Keep one as the backup of the factory contents, which is the only copy.
4. Write the operational image with `sudo python3 spi_flash.py write sqrl_acorn_operational.bin 0x400000 --idcode 0x3636093`: it is erased, programmed and verified.
5. Warm-boot to `0x400000` over ICAP, endpoint detached, triggered over the UART bridge: the operational image runs from flash with `BOOTSTS = 0x105`.

The operational image runs from flash. The golden image goes in next.

:::{danger}
**If writing the golden slot goes wrong, JTAG is the only way back.** Go on only if step 1 showed that `--detect` answers.
:::

6. Load the golden `.bit` into SRAM as in step 1, and check it: UART, PCIe and flash access all work.
7. From the golden design, write the golden slot with `sudo python3 spi_flash.py write sqrl_acorn_fallback.bin 0x0 --idcode 0x3636093 --i-know-this-writes-golden`: both slots are verified again.
8. Warm-boot to `0x0` over ICAP: the golden image chain-loads the operational one.
9. PoE-cycle the host's switch port and wait more than 90 s. The card shows `10ee:7021`, subsystem `1e24:021f`, 5 GT/s x1, and the UART, PCIe, P2 GPIO and flash checks pass.
10. Reset the SoC's CPU and read the BIOS log from the crossover UART through BAR0, after `setpci -s <bdf> COMMAND=0002:0002`. The log shows DDR3 1 GiB at 800 MT/s, read leveling clean on both modules, and `Memtest OK`.

## Check

The card passes when each of these shows:

- `idcode 0x3636093 (XC7A200T)` from `--detect`, and `10ee:7021` after each rescan.
- `BOOTSTS = 0x105` after the warm boot to `0x400000`.
- `10ee:7021`, subsystem `1e24:021f`, 5 GT/s x1 after the PoE cycle.
- `Memtest OK` in the BIOS log.

## If it fails

- **`found 0 devices` at step 1.** JTAG does not answer. Stop, and follow [Acorn wiring faults on a Raspberry Pi 5](../troubleshooting/rpi-5-wiring.md).
- **`spi_flash.py` refuses a write before erasing.** The image does not match the slot. The golden slot wants the flavour that chain-loads `0x400000`, and the operational slot the one with the watchdog. Both need the IDCODE of the part that is there. Address `0x0` also needs `--i-know-this-writes-golden`. Use the right file.
- **The old configuration still runs after `sudo reboot`.** A reboot need not drop the M.2 rail, so the FPGA can keep its configuration. PoE-cycle the host's switch port, as in step 9.
- **An image is bad after a write.** Follow [How to recover an Acorn with a bad image](../troubleshooting/recovery.md).

## Next

- [How to update the operational image of an Acorn](update-operational-image.md)
- [How to generate multiboot bitstreams by hand](multiboot-bitstreams.md)
- [Reaching an Acorn's flash through PCIe](flash-access.md)
- [How to recover an Acorn with a bad image](../troubleshooting/recovery.md)
