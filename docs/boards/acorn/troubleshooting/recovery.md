---
type: how-to
owner: documentation maintainers
reader: someone whose Acorn on a Raspberry Pi 5 no longer boots a working image
review: 2026-11-10
---

# How to recover an Acorn with a bad image

**You have an Acorn on a Raspberry Pi 5 whose golden image is bad, and want to write a good one back over JTAG.**

The images and the flash layout are on [the fpgas.online Acorn design](../overview/design.md). A bad operational image at 0x400000 needs nothing from you. The watchdog fires, the FPGA reloads from 0x0, the golden image brings PCIe up, and the host rewrites the operational slot. On a Compute Blade use `--pins 2:3:4:14` and the card's address from `lspci` ([how to run JTAG on a Compute Blade](../checks/compute-blade-jtag-by-hand.md)).

This procedure is waiting for its run: [test-designs issue #228](https://github.com/fpgas-online/fpgas.online-test-designs/issues/228).

:::{danger}
**Never write flash address 0x0 during normal operation.** The golden image there is the recovery mechanism. Overwrite it badly and the only way back is the SRAM bootstrap below. On a board whose JTAG does not answer, there is no way back at all. `spi_flash.py` refuses 0x0 without `--i-know-this-writes-golden`; `litepcie_util` does not check.
:::

## What you need

- JTAG wired and answering `--detect` on the Pi (step 1). A card whose JTAG does not answer cannot be rescued, and its golden slot must not be written.
- `openFPGALoader` with the `libgpiod` cable, and `spi_flash.py`.
- `golden.bit`, the golden build's `.bit` (`acorn_pcie_soc.py --variant <v> --golden --build`, [a Vivado build](../overview/design.md#images)); the packages carry only the operational `.bit`. In the design's release it is `acorn-cle-215p-golden-sqrl_acorn.bit` for a CLE-215+.
- `sqrl_acorn_fallback.bin` and `sqrl_acorn_operational.bin`, the golden and operational flash images.
- A copy of every file on the Pi after each reboot, because files under `/home/pi` do not survive one.
- Power to the board until step 4 completes: the SRAM-loaded design is volatile.

## Steps

1. On the Pi, link the header's GPIO chip as `gpiochip0` and read the IDCODE. It is `0x3636093` on a CLE-215+ (XC7A200T); a CLE-101 or LiteFury carries an XC7A100T and reports `0x3631093`.

   ```console
   $ sudo ln -sfn /dev/gpiochip15 /dev/gpiochip0
   $ openFPGALoader --cable libgpiod --pins 10:9:11:8 --detect
   ```

2. On the Pi, detach the endpoint and load `golden.bit` into SRAM. With a corrupt golden image nothing is enumerated, so the detach reports `No such file or directory`: carry on.

   ```console
   $ echo 1 | sudo tee /sys/bus/pci/devices/0001:01:00.0/remove
   ```

   ```console
   $ openFPGALoader --cable libgpiod --pins 10:9:11:8 golden.bit
   ```

3. On the Pi, rescan the bus and list the card; it enumerates as the design ([the way back](../checks/pcie-by-hand.md)).

   ```console
   $ echo 1 | sudo tee /sys/bus/pci/rescan
   $ lspci -nn -s 0001:01:00.0
   ```

4. On the Pi, write the golden image to 0x0, then the operational one to 0x400000; both writes complete.

   ```console
   $ sudo python3 spi_flash.py write sqrl_acorn_fallback.bin 0x0 --idcode 0x3636093 --i-know-this-writes-golden
   ```

   ```console
   $ sudo python3 spi_flash.py write sqrl_acorn_operational.bin 0x400000 --idcode 0x3636093
   ```

5. At the switch, PoE-cycle the host's port; the golden image boots from flash and chain-loads the operational one.

## Check

After step 5 `lspci -nn -s 0001:01:00.0` shows the design's ID again, without any JTAG load. Step 3 shows the same line before the flash is written.

```text
Memory controller [0580]: Xilinx Corporation Device [10ee:7021]
```

## If it fails

- **`found 0 devices` in step 1:** this board cannot be rescued over JTAG; stop and repair the JTAG wiring.
- **Step 3 shows the SQRL ID `1e24:021f`, or no device:** the JTAG load did not take; go back to step 2 rather than writing flash.
- **`Open file … FAIL` after a reboot:** the bitstream is gone, because `/home/pi` is a memory overlay; copy it again before each attempt.
- **The board lost power before step 4 completed:** the flash still holds the corrupt golden image; start again from step 1.
- **The rescan in step 3 finds nothing:** re-probe the slot's root complex, as in [JTAG loads and the PCIe endpoint](../checks/jtag-and-the-pcie-endpoint.md#what-coming-back-looks-like).

:::{danger}
**A bad golden image on a board whose JTAG does not answer `--detect` is bricked.** It stays bricked until the JTAG wiring is repaired.
:::

## Next

- [How to check an Acorn's PCIe link by hand on a Raspberry Pi 5](../checks/pcie-by-hand.md)
- [How to run JTAG by hand on an Acorn on a Raspberry Pi 5](../checks/jtag-by-hand.md)
- [Acorn wiring faults on a Raspberry Pi 5](rpi-5-wiring.md)
