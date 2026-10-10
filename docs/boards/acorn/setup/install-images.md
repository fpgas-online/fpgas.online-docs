# Acorn: installing and updating the fpgas.online images

**You have an Acorn on a Raspberry Pi 5, its JTAG answers, and you want to see how a card was converted to
the fpgas.online golden and operational images, and how the operational image is updated.** This page is
the dated record of one card's install (acorn-willow, last checked 2026-09-21) with what each step gave,
and the update commands. It is not yet a procedure with every command: the commands for the SRAM loads and
the ICAP warm boots of that record are not on this page. What the two images are is on [the fpgas.online LiteX
SoC](litex-soc.md); what to do when an image is bad is on [Recovery and safety
rules](recovery.md).

## The tool and the files

`spi_flash.py` is the flash tool's source file. The `fpgas-online-acorn-tools` package installs it as
`/usr/bin/fpgas-acorn-flash` ([Installing the Acorn packages](../packages.md#installing-the-acorn-packages)),
so on a host with the packages `sudo fpgas-acorn-flash id` is `sudo python3 spi_flash.py id`. The images are
installed by `fpgas-online-acorn-bitstreams` in `/usr/share/fpgas-online/acorn-pcie/images/`, where
`manifest.json` lists them. For a CLE-215+ the operational image (`sqrl_acorn_operational.bin` below) is
`acorn-cle-215p-sqrl_acorn_operational.bin` there. By the release tool's naming (from the design's source,
`publish_release.py`; not read by us on a host) the golden image (`sqrl_acorn_fallback.bin` below) is
`acorn-cle-215p-golden-sqrl_acorn_fallback.bin`. For a CLE-101 put `cle-101` in place of `cle-215p`.

`<bdf>` on this page is the card's PCIe address: `0001:01:00.0` on a Raspberry Pi 5 with the M.2 HAT.

## Installing the fpgas.online images

This is how a board is moved to the fpgas.online images with `spi_flash.py`
([`verify/src/fpgas_online_verify/boards/acorn/spi_flash.py`](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/verify/src/fpgas_online_verify/boards/acorn/spi_flash.py)),
which drives the SoC's flash core through PCIe BAR0 from Python, with no kernel
module. It is read-only unless told otherwise, checks an image against the slot
(the golden slot wants the flavour that chain-loads 0x400000, the operational
slot the one with the watchdog, both the IDCODE of the part that is there)
before anything is erased, and refuses the golden slot without
`--i-know-this-writes-golden`. The results column is the install of acorn-willow (device DNA `0x0054b48664b04854`), on a Raspberry Pi 5
then named pi-sw2-p48, last checked 2026-09-21.

:::{danger}
Only on a board whose JTAG answers `--detect`. If writing the golden slot goes
wrong, JTAG is the only way back. Check the card's row on [Acorns at welland](../installations/welland.md#the-cards) or [Acorns at
ps1](../installations/ps1.md#the-cards) first, and prove it on the card itself (read-only, safe on a live
endpoint):

```console
# Pi 5: the libgpiod cable opens gpiochip0; the 40-pin header is gpiochip15
$ sudo ln -sfn /dev/gpiochip15 /dev/gpiochip0
$ openFPGALoader --cable libgpiod --pins 10:9:11:8 --detect
# Expected on a CLE-215+: idcode 0x3636093 (XC7A200T). "found 0 devices": stop here.
```
:::

| Step | acorn-willow |
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

**Test a new image with a JTAG SRAM load first**, before writing it to flash: detach the endpoint, load the
`.bit`, bring PCIe back, check it, and only then write the `.bin`.

With the fpgas.online Acorn design running from flash:

```console
$ sudo python3 spi_flash.py verify sqrl_acorn_operational.bin 0x400000   # what is there now
$ sudo python3 spi_flash.py write  sqrl_acorn_operational.bin 0x400000 --idcode 0x3636093
```

then warm-boot to 0x400000 over ICAP, or PoE-cycle the port, and bring PCIe
back with `echo 1 | sudo tee /sys/bus/pci/rescan`. 

:::{warning}
**`litepcie_util` checks nothing before it writes.** `spi_flash.py` checks the image against the slot and
refuses address 0x0 without `--i-know-this-writes-golden`; `litepcie_util` does neither.
:::

With `litepcie_util` (the `litepcie` kernel module loaded; not yet run on fleet hardware), the equivalent is:

```console
$ litepcie_util flash_write operational.bin 0x400000
$ litepcie_util flash_reload        # ICAP warm boot from flash
```

## On a Compute Blade

Converting a card on a Compute Blade is **not yet run by us on this hardware**; the steps above are as run
on a Raspberry Pi 5. What each blade's card still needs is on [Acorns at
ps1](../installations/ps1.md#what-each-blade-still-needs).
