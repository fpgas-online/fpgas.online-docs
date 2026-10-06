% This section ("Installing the Arty Packages") is copied from https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/docs/hardware/arty-a7.md
% by tools/sync_test_designs.py. Do not edit it here: change it in test-designs.

## Installing the Arty Packages

Add the fpgas.online APT repository first ([verify.md: Installing](../verify/fpgas-verify.md#installing)), then on the Arty's Pi:

```bash
sudo apt install fpgas-online-arty
```

| Package | Installs |
|---------|----------|
| `fpgas-online-arty` | installs everything below to check an Arty, and turns the boot check (`fpgas-verify.service`) on for it |
| `fpgas-online-arty-tools` | the Arty's module of `fpgas_online_verify`, and `fpgas-arty-verify`; with `python3-serial`, openFPGALoader, `python3-libgpiod` (the PMOD HAT scan) and `iproute2`/`ping`/`arping` (the Ethernet test, which runs as root), and recommending `raspi-utils-core` (`pinctrl`, which puts back the Pi's SPI/UART/I2C pin functions after the scan; Raspberry Pi OS only) |
| `fpgas-online-arty-bitstreams` | the Arty A7-35T test bitstreams built by the same commit's CI, in `/usr/share/fpgas-online/arty/bitstreams/` |
| `fpgas-online-verify` | `fpgas-verify`, the unit, and the host test scripts |

At boot the check finds the Arty by its FT2232H on USB (`0403:6010`). It reads the FPGA's whole JTAG IDCODE over that FT2232H, which must be an XC7A35T in any silicon version; the report's `jtag` has it decoded (`idcode_version`, `idcode_device` and the others, [verify.md: the IDCODE](../verify/fpgas-verify.md#the-jtag-idcode)), then its device DNA with `openFPGALoader -b arty --read-dna` over the same FT2232H, which loads nothing; a DNA that cannot be read, or is all zeros or all ones, fails the board ([verify.md: the device DNA](../verify/fpgas-verify.md#the-device-dna)). It then loads the UART, DDR, SPI flash, Ethernet and PMOD pin identification test designs into SRAM with openFPGALoader, one at a time, and runs each one's host test. The Ethernet test pings the design through the Pi's USB Ethernet adapter cabled to the Arty's RJ45; it never touches an interface the Pi uses itself. The pin identification scan checks the PMOD HAT cabling against the expected map (HAT JA/JB/JC → Arty JA/JB/JC, [PMOD Cable Routing](https://github.com/fpgas-online/fpgas.online-test-designs/blob/acorn-check-pages/docs/hardware/arty-a7-pin-mapping.md#pmod-cable-routing-hat--arty)). A failure in either fails the board, like any other test. Last, it reads back the flash's boot image region (the first 2.1 MiB) through openFPGALoader's SPI-over-JTAG bridge. The FTDI serial number, the IDCODE, the device DNA, the flash's JEDEC ID and that region's sha256 are what `changed` compares. The Arty is left running the SPI-over-JTAG bridge, and comes back to its flash image at the next power cycle. Only the PMOD loopback test is left to `fpgas-arty-debug`.

For the fpgas.online openFPGALoader build, add the [fpgas.online-fpga-tools repository](https://github.com/fpgas-online/fpgas.online-fpga-tools#debian-packages-bookworm-trixie-sid-arm64-armhf) **before** installing; otherwise apt installs Debian's `openfpgaloader`. That works for the Arty from 0.13.0 on (trixie's), because the check reads the device DNA with `--read-dna`. Bookworm's (0.10.0) is too old, so on bookworm `fpgas-online-arty` installs only with the repository added.

It runs at every boot of the Welland Arties: [current results](../verify/fpgas-verify.md#current-results).

**Check the board now**, or run one test with its output live (`fpgas-arty-debug` is in `fpgas-online-arty-debug`):

```bash
sudo fpgas-arty-verify --no-publish --report -  # this board only, the JSON report on stdout
sudo fpgas-arty-debug test ddr                  # load one test's design and run its test
```

What the results mean, the report, `changed` and `--update`, the debug tool and common failures: [verify.md](../verify/fpgas-verify.md#reading-the-result).
