---
type: how-to
owner: documentation maintainers
reader: someone whose Acorn no longer boots a working image
review: 2026-11-10
---

# How to recover an Acorn with a bad image

**You have an Acorn on a Raspberry Pi 5 whose flash holds a bad fpgas.online image, or you are about to
write its flash, and want to know how the card recovers and what must never be done.** The images and the
flash layout are on [the fpgas.online Acorn design](../overview/design.md).

## Safety rules

:::{danger}
**Never write flash address 0x0 during normal operation.** The golden image
there is the recovery mechanism. Overwrite it badly and the only way back is the
SRAM bootstrap over JTAG; on a board whose JTAG does not answer, there is no
way back at all. `spi_flash.py` refuses 0x0 without
`--i-know-this-writes-golden`; `litepcie_util` does not check.
:::

:::{warning}
1. **Never write 0x0 during normal operation** (above).
2. **Use 0x400000 for operational updates.**
3. **Test a new image with a JTAG SRAM load first**, before writing it to
   flash: detach the endpoint, load the `.bit`, bring PCIe back, check it, and
   only then write the `.bin`.
4. **Keep the JTAG wiring connected** on every deployed board. Without JTAG a
   bad golden image bricks the board until JTAG is reconnected.
5. **Detach the PCIe endpoint before every JTAG load** ([why](../checks/pcie-by-hand.md#detach-the-pcie-endpoint-before-any-jtag-reconfiguration)).
6. **Keep the golden image minimal**: PCIe, flash, ICAP and UART, nothing that
   can fail calibration.
:::

## Recovery

**We hold no dated record of the bad-golden recovery having been run.** The only related record is
acorn-willow's install, last checked 2026-09-21: its steps 1 and 6 load the operational and the golden
`.bit` into SRAM over JTAG, and its step 7 writes the golden slot through the SRAM-loaded golden design
([the record](../setup/install-images.md#steps)).

`golden.bit` below is the golden build's `.bit`. The packages carry only the operational `.bit`; the golden
one comes from the golden build (`acorn_pcie_soc.py --variant <v> --golden --build`, [a Vivado
build](../overview/design.md#images)). By the release tool's naming (from the design's source, `publish_release.py`;
not fetched by us for this page) it is `acorn-cle-215p-golden-sqrl_acorn.bit` in the design's release for a
CLE-215+.

The commands are for a Raspberry Pi 5. On a Compute Blade the recovery is **not yet run by us on this
hardware**; there the JTAG pins are `--pins 2:3:4:14` and the card's address differs per blade ([JTAG on a
blade](../checks/compute-blade-jtag-by-hand.md#jtag-on-a-blade)).

### Bad operational image: automatic

If the image at 0x400000 is corrupt or fails to configure, the watchdog fires,
the FPGA reloads from 0x0, the golden image brings PCIe up, and the host
rewrites the operational slot. Nothing needs doing by hand.

### Bad golden image: SRAM bootstrap

If the image at 0x0 is corrupt, PCIe does not come up at boot. Recovery loads a
working design into SRAM over JTAG and writes the flash through it.

:::{warning}
Files staged under `/home/pi` do not survive a reboot: the Pi root is a
read-only NFS export with a tmpfs overlay (`overlayroot=tmpfs`), so a bitstream
that loaded a minute ago fails with `Open file … FAIL` after a reboot. Copy it
again before each attempt.
:::

:::{warning}
Between steps 1 and 3 the board **must not lose power**. The SRAM-loaded design
is volatile: if power goes before step 3 completes, the flash still holds the
corrupt golden image, and you start again from step 1.
:::

0. **Prove JTAG answers before touching anything.** `--detect` is read-only and
   safe on a live endpoint:

   ```console
   # Pi 5: the libgpiod cable opens gpiochip0; the 40-pin header is gpiochip15
   $ sudo ln -sfn /dev/gpiochip15 /dev/gpiochip0
   $ openFPGALoader --cable libgpiod --pins 10:9:11:8 --detect
   # Expected on a CLE-215+: idcode 0x3636093 (XC7A200T)
   ```

   A CLE-101 or LiteFury carries an XC7A100T and reports a different IDCODE:
   read it off `--detect` on the board in hand. `found 0 devices` means this
   board cannot be rescued over JTAG. Stop here (safety rule 4).

1. **Load the golden `.bit` into SRAM** (volatile):

   ```console
   # Detach anything enumerated. With a corrupt golden image nothing is, so this
   # reports "No such file or directory": carry on.
   $ echo 1 | sudo tee /sys/bus/pci/devices/0001:01:00.0/remove
   # Pi 5: the libgpiod cable opens gpiochip0; the 40-pin header is gpiochip15
   $ sudo ln -sfn /dev/gpiochip15 /dev/gpiochip0
   $ openFPGALoader --cable libgpiod --pins 10:9:11:8 golden.bit
   ```

2. **Bring the endpoint back** (rescan, then the [root-complex
   re-probe](../checks/pcie-by-hand.md#bring-the-endpoint-back-after-a-jtag-load) if needed) and confirm the design enumerated:

   ```console
   $ echo 1 | sudo tee /sys/bus/pci/rescan
   $ lspci -nn -s 0001:01:00.0
   # Expected: Memory controller [0580]: Xilinx Corporation Device [10ee:7021]
   ```

   Still the SQRL ID `1e24:021f`, or no device at all, means the JTAG load did
   not take: go back to step 1 rather than writing flash.

3. **Write the golden image to 0x0**, then the operational one to 0x400000:

   ```console
   $ sudo python3 spi_flash.py write sqrl_acorn_fallback.bin 0x0 --idcode 0x3636093 --i-know-this-writes-golden
   $ sudo python3 spi_flash.py write sqrl_acorn_operational.bin 0x400000 --idcode 0x3636093
   ```

4. **PoE-cycle** the host's switch port. The golden image boots from flash,
   chain-loads the operational one, and PCIe comes up without any JTAG load:
   `lspci -nn -s 0001:01:00.0` shows `10ee:7021` again.

### Summary

| Scenario | Golden OK? | Operational OK? | Recovery | Automatic? |
|----------|-----------|----------------|----------|------------|
| Bad operational | Yes | No | Watchdog falls back to golden; rewrite over PCIe | Yes |
| Bad golden | No | — | SRAM bootstrap: JTAG → SRAM, then PCIe → flash | No |
| Bad golden, JTAG does not answer | No | — | **Bricked** until the JTAG wiring is repaired | No |

:::{danger}
The last row applies to every board whose JTAG does not answer `--detect`
today. No such card may have its golden slot written until its JTAG is repaired. The cards known not to answer: [test-designs issue #209](https://github.com/fpgas-online/fpgas.online-test-designs/issues/209) and [test-designs issue #214](https://github.com/fpgas-online/fpgas.online-test-designs/issues/214).
:::
