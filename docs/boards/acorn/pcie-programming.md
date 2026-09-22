# Acorn PCIe programming and multiboot

How the Acorn CLE-215+ / LiteFury is programmed, how its flash is laid out for
Xilinx 7-series multiboot, and how to recover from a bad image. See [SQRL Acorn
and LiteFury](index.md) for the board and [Acorn wiring](wiring.md) for the GPIO
JTAG wiring every JTAG command below assumes.

## Programming paths

| Method | Speed | Persistent? | Requires | Notes |
|--------|-------|-------------|----------|-------|
| GPIO JTAG → SRAM | about 16 s for a 1.6 MB XC7A200T bitstream over libgpiod; 24 s for the 2.3 MB fpgas.online SoC over OpenOCD | No (lost at power-off) | the P1 JTAG wiring | Works whatever is loaded. **Detach the PCIe endpoint first** (below) |
| PCIe → SPI flash, `spi_flash.py` | 32 MiB read in 58 s; a 4 MiB slot erased, written and verified in about 20 s | Yes | the fpgas.online Acorn design running (from flash, or loaded into SRAM over JTAG) | Stdlib Python over BAR0, no kernel module. The proven path |
| PCIe → SPI flash, `litepcie_util` | — | Yes | a LiteX PCIe design and the `litepcie` kernel module | Not yet run on fleet hardware |

`openFPGALoader --write-flash` does not work over the GPIO JTAG wiring: its
spiOverJtag bridge never toggles CCLK after configuration, so over that path JTAG
can only load volatile SRAM.

## Detach the PCIe endpoint before any JTAG reconfiguration

:::{warning}
**Detach the PCIe endpoint before any JTAG reconfiguration.** Reconfiguring the
FPGA over JTAG while its endpoint is enumerated is a PCIe surprise removal, and
the Pi 5's BCM2712 root complex does not survive it: the host drops SSH and
reboots. With the endpoint removed first the load completes and the host is
unaffected.
:::

```console
# Detach the endpoint first, before openFPGALoader
$ echo 1 | sudo tee /sys/bus/pci/devices/0001:01:00.0/remove
# ... load ...
# then bring it back: see the next section
```

The rule is the root complex's, not the Acorn's: it applies to any PCIe FPGA on
a Pi 5, the NeTV2 on `rpi5-netv2` included ([PCIe
detection](../netv2.md#pcie-detection-rpi5-netv2)).

Every Welland Pi 5 host uses `0001:01:00.0`. At PS1 the address differs per
blade, so read it from the `PCIe Bus` column in [Compute
blades](../../sites/ps1.md#compute-blades).

Every `openFPGALoader … <bitstream>` below assumes the endpoint is detached.
Read-only operations (`--detect`, `--read-dna`, `--read-xadc`) do not
reconfigure the device and are safe on a live endpoint.

## Bring the endpoint back after a JTAG load

Measured on pi20 (CM5 on a Compute Blade, kernel 6.12.75):

| Design loaded over JTAG | `echo 1 > /sys/bus/pci/rescan` | Root-complex re-probe |
|---|---|---|
| Vendor XDMA image (reloaded from flash with `openFPGALoader --reset`) | re-links at 5 GT/s x1 and enumerates | works |
| LiteX `acorn-pcie` SoC | nothing: the core's LTSSM sits at `0x2d`, and a root-port retrain or secondary-bus reset changes nothing | **links at 5 GT/s x1, enumerates as `10ee:7021`** |

Measured on pi-sw2-p48 (Raspberry Pi 5 with an M.2 HAT, kernel 6.12.96):

| Design loaded over JTAG | `echo 1 > /sys/bus/pci/rescan` | Root-complex re-probe |
|---|---|---|
| LiteX `acorn-pcie` SoC (CLE-215+) | **enough**: the link is up (LTSSM `0x16`, L0, 5 GT/s x1) as soon as the load finishes, and the rescan enumerates `10ee:7021` | not needed |

So try the rescan first, and re-probe the root complex only when `lspci` still
shows nothing. The re-probe toggles PERST# by unbinding and rebinding the slot's
root complex; that touches only the FPGA's PCI domain, because the RP1
southbridge (Ethernet, USB, GPIO) hangs off a different platform device. The
platform device behind the FPGA slot is `1000110000.pcie` on both kinds of host.
Why the CM5 blade needs PERST# and the Pi 5 does not is not understood.

```console
# Which platform device is behind the FPGA slot?
$ readlink -f /sys/bus/pci/devices/0001:00:00.0 | grep -o '[0-9a-f]*\.pcie'
1000110000.pcie
$ echo 1000110000.pcie | sudo tee /sys/bus/platform/drivers/brcm-pcie/unbind
$ echo 1000110000.pcie | sudo tee /sys/bus/platform/drivers/brcm-pcie/bind
$ lspci -nn -s 0001:01:00.0
0001:01:00.0 Memory controller [0580]: Xilinx Corporation Device [10ee:7021]
```

If the link is down when `bind` runs, the driver logs `link down`, `bind` fails
with `No such device`, and the root port `0001:00:00.0` disappears until a later
`bind` succeeds. That is recoverable: load a design that links (or
`openFPGALoader --reset` to reload the flash image) and `bind` again.

## Images

The fpgas.online Acorn design is
[`designs/acorn-pcie`](https://github.com/fpgas-online/fpgas.online-test-designs/tree/main/designs/acorn-pcie)
in fpgas.online-test-designs: PCIe Gen2 x1 (`10ee:7021`, with the board named in
the PCI subsystem ID, `1e24:021f` for a CLE-215+ and `1e24:0101` for a CLE-101),
a UART bridge on P2, device DNA, XADC, the SPI flash core and ICAP. It builds
with Vivado (the XC7A200T is too large for openXC7) in two images:

| Image | Build | File to write | Flash slot |
|---|---|---|---|
| Golden | `acorn_pcie_soc.py --variant <v> --golden --build` | `sqrl_acorn_fallback.bin` (chain-loads 0x400000) | 0x0 |
| Operational | `acorn_pcie_soc.py --variant <v> --build` | `sqrl_acorn_operational.bin` (with the watchdog) | 0x400000 |

The golden image has no DDR3 and no P2 GPIO, so nothing in it can fail
calibration. The `.bit` of each build is for a JTAG SRAM load.

:::{warning}
**Do not use the `pcie-enumeration_acorn-*` assets of the prebuilt release
[`vivado-bitstreams-v0.0-496-gf162f60`](https://github.com/fpgas-online/fpgas.online-test-designs/releases/tag/vivado-bitstreams-v0.0-496-gf162f60)
as a golden or recovery image.** Their I/O reports put the PCIe lane on package
pins D9/D7 (GTP channel X0Y7, M.2 lane 3) instead of B10/B6 (X0Y6, lane 0): the
Xilinx PCIe IP's own XDC pins a x1 core's transceiver and overrides the port
constraints, so on a x1 host the core never leaves Detect. The fpgas.online
Acorn design's build fails if any port is not on the pin it was constrained to.
The release's `pmod-pin-id` Acorn build configures but never toggles a pin; build
that design from `main` instead. The release's other designs are unaffected; for
a CLE-215+ use the `*_acorn-cle-215p_*` files, whose `.bit` header reads
`7a200tfbg484` (IDCODE `0x3636093`).
:::

## What the flash holds

Which image each board boots is on the site pages ([Welland](../../sites/welland.md#sqrl-acorn-cle-215),
[PS1](../../sites/ps1.md#compute-blades)). Two images other than the fpgas.online
one are in service:

- **SQRL factory firmware** (`1e24:021f`): a cryptocurrency mining design, not
  LiteX, so neither `spi_flash.py` nor `litepcie_util` can talk to it. Its BAR0
  (128 KB) is a repeating mining parameter pattern. It is itself a multiboot
  pair: its header at `0x0` sets `WBSTAR = 0x680000` and issues `IPROG`, so the
  mining design lives at `0x680000`, clear of the fpgas.online operational slot.
- **The vendor (RHS Research) XDMA sample image** (`10ee:7011`): x4-capable, two
  BARs, also not LiteX.

A board on either needs the fpgas.online Acorn design loaded into SRAM over JTAG
before its flash can be written; a board whose JTAG does not answer cannot be
moved off it.

## SPI flash layout

The Acorn has a Spansion S25FL256S (256 Mbit = 32 MB) quad-SPI NOR flash.

```text
┌──────────────────────────────────────────────────┐
│ 0x00000000  Golden image (fallback)              │  4 MB
│             - Always boots first                 │
│             - Sets NEXT_CONFIG_ADDR = 0x400000   │
│             - PCIe, UART, flash, ICAP            │
│             - PROTECTED: see the safety rules    │
├──────────────────────────────────────────────────┤
│ 0x00400000  Operational image (updatable)        │  4 MB
│             - Chain-loaded by the golden image   │
│             - Has the TIMER_CFG watchdog         │
│             - If broken, watchdog → golden       │
├──────────────────────────────────────────────────┤
│ 0x00800000  Free                                 │  24 MB
└──────────────────────────────────────────────────┘
```

## Multiboot

1. **Power-on**: the FPGA loads the golden image from flash address 0x0.
2. **Chain-load**: the golden image's `NEXT_CONFIG_ADDR` (0x400000) makes the
   FPGA load the operational image straight away.
3. **Operational runs**, with PCIe, UART and the rest.
4. **If the operational image fails**, the `TIMER_CFG` watchdog detects the
   configuration failure and falls back to address 0x0.
5. **The golden image boots**, PCIe comes up, and the host can rewrite the
   operational slot.

The operational image carries `CONFIGFALLBACK Enable` and `TIMER_CFG
0x0001fbd0`. If it hangs during configuration, the watchdog fires and the FPGA
ignores `WBSTAR`, rebooting from 0x0.

**ICAPE2 warm boot** reconfigures without a power cycle: write the target flash
address to `WBSTAR`, then `IPROG` to the ICAPE2 command register. The PCIe link
drops and retrains once the new image is loaded. LiteX's `ICAP` core
(`self.icap = ICAP(); self.icap.add_reload()`) exposes it.

## Installing the fpgas.online images

This is how a board is moved to the fpgas.online images with `spi_flash.py`
([`designs/acorn-pcie/host/spi_flash.py`](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/designs/acorn-pcie/host/spi_flash.py)),
which drives the SoC's flash core through PCIe BAR0 from Python, with no kernel
module. It is read-only unless told otherwise, checks an image against the slot
(the golden slot wants the flavour that chain-loads 0x400000, the operational
slot the one with the watchdog, both the IDCODE of the part that is there)
before anything is erased, and refuses the golden slot without
`--i-know-this-writes-golden`. The results column is pi-sw2-p48's install.

:::{danger}
Only on a board whose JTAG answers `--detect`. If writing the golden slot goes
wrong, JTAG is the only way back. Check the board's JTAG column on its site page
first.
:::

| Step | pi-sw2-p48 |
|---|---|
| 1. Load the operational `.bit` into SRAM over JTAG (endpoint detached first), bring PCIe back | 24 s (OpenOCD `linuxgpiod`); the rescan enumerates `10ee:7021` |
| 2. `spi_flash.py id` | S25FL256S, RDID `01 02 19 4d 01 80`, 32 MiB, QUAD bit set |
| 3. `spi_flash.py dump factory.bin`, twice, and compare | 58 s each, identical SHA-256; kept as the backup |
| 4. `spi_flash.py write sqrl_acorn_operational.bin 0x400000 --idcode 0x3636093` | erased, programmed and verified in 19 s |
| 5. ICAP warm boot to `0x400000` (endpoint detached; triggered over the UART bridge) | the operational image runs from flash, `BOOTSTS = 0x105`: no fallback, no error |
| 6. Load the golden `.bit` into SRAM and check it | UART, PCIe and flash access all work |
| 7. `spi_flash.py write sqrl_acorn_fallback.bin 0x0 --idcode 0x3636093 --i-know-this-writes-golden`, from the golden design | 20 s; both slots verified again |
| 8. ICAP warm boot to `0x0` | the golden image chain-loads the operational one |
| 9. PoE power cycle | `10ee:7021`, subsystem `1e24:021f`, at kernel t = 2.0 s, 5 GT/s x1; UART, PCIe, P2 GPIO and flash checks pass |
| 10. Reset the SoC's CPU and read the BIOS log from the crossover UART through BAR0 | DDR3 1 GiB at 800 MT/s: read leveling clean on both modules, `Memtest OK`, 35.1 MiB/s write, 46.8 MiB/s read |

Keep the step 3 backup of the factory contents: it is the only copy.

Two properties of the hardware that the tool already handles:

- **The first SPI transfer after every configuration is lost.** `STARTUPE2` does
  not pass the first three `USRCCLKO` edges to the flash clock pin, so the first
  command arrives three clocks short and reads back as all ones. `spi_flash.py`
  spends them with the flash deselected.
- **BAR0 answers only aligned 32-bit reads.** Through
  `/sys/bus/pci/devices/<bdf>/resource0`, a 4-byte slice of the `mmap`
  (`struct.unpack("<I", m[off:off + 4])`) returns the register; a byte-wise slice
  of the same window returns `0xff` for every byte. Enable memory decoding
  first: `setpci -s <bdf> COMMAND=0002:0002`.

After a `sudo reboot` the FPGA can keep its configuration, because a reboot
need not drop the M.2 rail. The reliable power cycle is a PoE cycle of the
host's switch port, which takes a Pi 5 more than 90 s to come back.

## Updating the operational image

With the fpgas.online Acorn design running from flash:

```console
$ sudo python3 spi_flash.py verify sqrl_acorn_operational.bin 0x400000   # what is there now
$ sudo python3 spi_flash.py write  sqrl_acorn_operational.bin 0x400000 --idcode 0x3636093
```

then warm-boot to 0x400000 over ICAP, or PoE-cycle the port, and bring PCIe
back as above. Test a new image with a JTAG SRAM load first (safety rule 3).

With `litepcie_util` (the `litepcie` kernel module loaded; not yet run on fleet
hardware), the equivalent is:

```console
$ litepcie_util flash_write operational.bin 0x400000
$ litepcie_util flash_reload        # ICAP warm boot from flash
```

## Recovery

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

0. **Prove JTAG answers before touching anything.** `--detect` is read-only and
   safe on a live endpoint:

   ```console
   # Pi 5: the libgpiod cable opens gpiochip0; the 40-pin header is gpiochip15
   $ sudo ln -sfn /dev/gpiochip15 /dev/gpiochip0
   $ openFPGALoader --cable libgpiod --pins 10:9:11:8 --detect
   # Expected on a CLE-215+: idcode 0x3636093 (XC7A200T)
   # PS1 Compute Blades: --pins 2:3:4:14
   ```

   A CLE-101 or LiteFury carries an XC7A100T and reports a different IDCODE:
   read it off `--detect` on the board in hand. `found 0 devices` means this
   board cannot be rescued over JTAG. Stop here (safety rule 4).

1. **Load the golden `.bit` into SRAM** (volatile):

   ```console
   # Detach anything enumerated. With a corrupt golden image nothing is, so this
   # reports "No such file or directory": carry on.
   $ echo 1 | sudo tee /sys/bus/pci/devices/0001:01:00.0/remove
   # Pi 0-4 only; harmless on a Pi 5
   $ sudo rmmod spidev spi_bcm2835
   # Pi 5: the libgpiod cable opens gpiochip0; the 40-pin header is gpiochip15
   $ sudo ln -sfn /dev/gpiochip15 /dev/gpiochip0
   $ openFPGALoader --cable libgpiod --pins 10:9:11:8 golden.bit
   # PS1 Compute Blades: --pins 2:3:4:14
   ```

2. **Bring the endpoint back** (rescan, then the root-complex re-probe if
   needed) and confirm the design enumerated:

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

:::{warning}
Between steps 1 and 3 the board **must not lose power**. The SRAM-loaded design
is volatile: if power goes before step 3 completes, the flash still holds the
corrupt golden image, and you start again from step 1.
:::

### Summary

| Scenario | Golden OK? | Operational OK? | Recovery | Automatic? |
|----------|-----------|----------------|----------|------------|
| Bad operational | Yes | No | Watchdog falls back to golden; rewrite over PCIe | Yes |
| Bad golden | No | — | SRAM bootstrap: JTAG → SRAM, then PCIe → flash | No |
| Bad golden, JTAG does not answer | No | — | **Bricked** until the JTAG wiring is repaired | No |

:::{danger}
The last row applies to every board whose JTAG does not answer `--detect`
today. Which boards those are is on the site pages; none of them may have its
golden slot written until its JTAG is repaired.
:::

## Generating multiboot bitstreams by hand

The fpgas.online Acorn design's build produces both flavours. For any other
design, set the properties in Vivado:

```tcl
# Golden: chain-load the operational slot
set_property BITSTREAM.CONFIG.NEXT_CONFIG_ADDR 0x00400000 [current_design]
write_bitstream -force golden.bit
write_cfgmem -force -format bin -interface spix4 -size 16 -loadbit "up 0x0 golden.bit" -file golden.bin

# Operational: watchdog and fallback
set_property BITSTREAM.CONFIG.TIMER_CFG 0x0001fbd0 [current_design]
set_property BITSTREAM.CONFIG.CONFIGFALLBACK Enable [current_design]
write_bitstream -force operational.bit
write_cfgmem -force -format bin -interface spix4 -size 16 -loadbit "up 0x0 operational.bit" -file operational.bin
```

openXC7 does not support `NEXT_CONFIG_ADDR`, so golden images need Vivado; that
is acceptable for an image written once and rarely changed.

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
5. **Detach the PCIe endpoint before every JTAG load** ([why](#detach-the-pcie-endpoint-before-any-jtag-reconfiguration)).
6. **Keep the golden image minimal**: PCIe, flash, ICAP and UART, nothing that
   can fail calibration.
:::

## Future: flash over JTAG

When openFPGALoader's `--write-flash` works over the GPIO JTAG wiring, initial
setup becomes a single JTAG flash write, golden recovery no longer needs the
volatile SRAM step, and the "bricked" row above disappears. Until then the SRAM
bootstrap is the recovery path.

## References

- Xilinx XAPP1247, MultiBoot with SPI: <https://docs.amd.com/v/u/en-US/xapp1247-multiboot-spi>
- LiteX Acorn CLE-215 wiki: <https://github.com/enjoy-digital/litex/wiki/Use-LiteX-on-the-Acorn-CLE-215>
- LitePCIe: <https://github.com/enjoy-digital/litepcie>
- LiteX ICAP core: <https://github.com/enjoy-digital/litex/blob/master/litex/soc/cores/icap.py>
- The fpgas.online Acorn design: [`designs/acorn-pcie`](https://github.com/fpgas-online/fpgas.online-test-designs/tree/main/designs/acorn-pcie)
- Acorn board spec: [SQRL Acorn and LiteFury](index.md)
- GPIO JTAG wiring: [Acorn wiring](wiring.md#p1-jtag)
