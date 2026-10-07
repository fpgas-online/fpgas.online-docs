% This section ("Installing the Acorn Packages") is copied from https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/docs/hardware/acorn.md
% by tools/sync_test_designs.py. Do not edit it here: change it in test-designs.

## Installing the Acorn Packages

Add the fpgas.online APT repository first ([verify.md: Installing](../../verify/fpgas-verify.md#installing)), then on the Acorn's Pi 5 host:

```bash
sudo apt install fpgas-online-acorn
```

| Package | Version scheme | Installs |
|---------|----------------|----------|
| `fpgas-online-acorn` | `X.Y.postN` from `git describe` (e.g. `0.0.post576`) | installs everything below to check an Acorn, and turns the boot check (`fpgas-verify.service`) on for it |
| `fpgas-online-acorn-tools` | `X.Y.postN` | the Acorn's module of `fpgas_online_verify` (`suite.py`, `check.py`, `bist.py`, `links.py`, `setup.py`, `spi_flash.py`, `uartbone_link.py`, and `data/wiring.toml` and `data/expected.toml`), `/usr/bin/fpgas-acorn-verify` and `/usr/bin/fpgas-acorn-flash`; with openFPGALoader for the P1 JTAG check (recommending `raspi-utils-core`, whose `pinctrl` puts the JTAG pins back after it and drives the Pi's side of J5/H5; Raspberry Pi OS only), and `python3-serial` for the P2 UART check |
| `fpgas-online-acorn-bitstreams` | pinned release date + commit (e.g. `20260923+ge48a750c8303`) | `/usr/share/fpgas-online/acorn-pcie/images/`: `manifest.json`, and for each of `cle-215p` / `cle-101` the golden (`0x000000`) and operational (`0x400000`) flash images, the operational `.bit`, and the CSR maps |
| `fpgas-online-verify` | `X.Y.postN` | `fpgas-verify` and its unit |

The tools package depends on one exact bitstreams version. Which release that is comes from [`packaging/acorn-pcie/release.toml`](https://github.com/fpgas-online/fpgas.online-test-designs/blob/dark-variants/packaging/acorn-pcie/release.toml), and a new release reaches hosts only when a reviewed PR moves that pin. Every package is built, and its install rules are checked in clean Debian bookworm and trixie, by [`collect-bitstreams.yml`](https://github.com/fpgas-online/fpgas.online-test-designs/blob/dark-variants/.github/workflows/collect-bitstreams.yml).

At boot the check finds the Acorn on PCI (Xilinx `10ee` or SQRL `1e24`), works out which setup the host is
from its device-tree model, and runs these tests ([verify.md](../../verify/fpgas-verify.md#what-each-boards-check-tests) has the
details). It never writes the flash and never reconfigures the FPGA, and a fault in one test does not stop
the others:

| Test | Checks |
|---|---|
| `pcie-link` | the link is 5.0 GT/s x1 ([`expected.toml`](https://github.com/fpgas-online/fpgas.online-test-designs/blob/dark-variants/docs/wiring/acorn/expected.toml)) |
| `pcie-bar0` | over BAR0: the operational build of the installed release runs, the flash identifies itself, the device DNA reads, and the XADC temperature and voltages are in range |
| `rp1-pio` | Pi 5 / CM5 only: `/dev/pio0` opens, for openfpgaloader-rp1pio; when it does not, the `rp1_fw` / `rp1_pio` modules and the kernel's reason are reported (`failed to contact RP1 firmware` on bootloader 2024/11/05) |
| `jtag` | over P1: the whole IDCODE, decoded into `idcode_version`, `idcode_part_number`, `idcode_manufacturer_id`, `idcode_manufacturer` and `idcode_device`, must be the variant's part in any silicon version ([verify.md: the IDCODE](../../verify/fpgas-verify.md#the-jtag-idcode)); and the device DNA, which must be BAR0's (this proves TDI) |
| `flash` | both 4 MiB slots hold the release's images |
| `ddr` | the BIOS console read out, then the DRAM BIST over the whole DRAM, two passes: no errors, and write and read at least 1100 MB/s ([`expected.toml`](https://github.com/fpgas-online/fpgas.online-test-designs/blob/dark-variants/docs/wiring/acorn/expected.toml)); p48 measures 1327 / 1350 MB/s |
| `p2-uart` | the UARTBone bridge on P2 at 1200 and 921600 baud: identifier, DNA and XADC, as over BAR0 |
| `p2-serial` | both setups: J2 and K2 borrowed with `p2_serial` and tested both ways, the switch's own timeout, and the UARTBone answering again |
| `scratch` | the `ctrl` scratch register written and read back over BAR0 and over P2 |
| `p2-gpio` | Pi 5 setup only: J5 and H5 driven from the FPGA and read on GPIO3/GPIO4, then driven from the Pi and read on the FPGA |
| `power-cycle` (opt-in: `power-cycle-check = on`, set on the fpgas.online fleet) | the FPGA restarted since the last check (it was configured, or its SoC reset), that is, it did not keep its state across the Pi's restart ([verify.md](../../verify/fpgas-verify.md#the-acorns-power-cycle-check-opt-in)) |

Where each setup's wires land on the host:

| Setup | JTAG `--pins` | openFPGALoader cable | J2 / K2 | J5 / H5 |
|---|---|---|---|---|
| Pi 5 + Waveshare HAT | `10:9:11:8` | `libgpiod` (the RP1's GPIO chip, linked as `/dev/gpiochip0`) | GPIO14 / GPIO15 | GPIO3 / GPIO4 |
| Compute Blade, CM4 | `2:3:4:14` | `libgpiod` (the BCM2711's GPIO chip; a CM4 has no RP1, so no `rp1pio`) | GPIO14 / GPIO15 | cut |
| Compute Blade, CM5 | `2:3:4:14` | `libgpiod` (the RP1's GPIO chip) | GPIO14 / GPIO15 | cut |

On the Blade J2 shares GPIO14 with TMS through 470 Ω, so after the JTAG test GPIO14 goes back to its UART
function. On a CM5 with kernel 6.18 the kernel does not lend GPIO14 while the serial port has it, so with the
serial port on the `jtag` test fails saying so, without running openFPGALoader
([#127](https://github.com/fpgas-online/fpgas.online-test-designs/issues/127)). The PCI slot and IDs, the device DNA, the flash's identity and the sha256 of each slot are what
`changed` compares, so a flash rewritten since the last run (by `fpgas-acorn-flash write`, say) is fatal
until `sudo fpgas-verify --update`. The PCIe transfer rate (DMA) is not measured yet.

**Check the board now:**

```bash
sudo fpgas-verify                                    # what the boot unit runs
sudo fpgas-acorn-verify --no-publish --report -      # the Acorn only, the JSON report on stdout
```

The result is `pass` only when every test passes. A board running its golden image (the operational slot did
not boot) fails. A kernel driver bound to the board (`litepcie.ko`) is unbound for the check, when a test asked for
uses BAR0, and bound again afterwards (`fpgas-acorn-flash` instead refuses a board a driver is bound to). A board still on SQRL's factory
image, or the vendor XDMA sample, is `fail` with a reason starting `unconverted:`: it does not run the
fpgas.online image, so it cannot be offered to users until `fpgas-acorn-flash` converts it (the XDMA sample can
also be a NeTV2 on PCIe, which that tool does not apply to). A PCIe Screamer (PCILeech, `10ee:0666`) or a stock
Xilinx XDMA design (most likely a PicoEVB: `10ee:7021` with the Xilinx default subsystem, told apart
from an old fpgas.online build by its XDMA class code and BAR2) is named, and fails: fpgas.online has no test design for it yet. Any
other PCIe FPGA whose design the check does not recognise is `fail` too. A Pi with no Acorn is `missing`:
fatal, since the host was set up for one.

**When a check fails**, `sudo apt install fpgas-online-acorn-debug`. It brings openFPGALoader for loading the `.bit` over GPIO JTAG ([below](https://github.com/fpgas-online/fpgas.online-test-designs/blob/dark-variants/docs/hardware/acorn.md#via-gpio-jtag-openfpgaloader--what-the-fleet-uses)), which is how a board still on SQRL's factory image is converted, and `python3-serial` for `fpgas-acorn-flash --uart`:

```bash
sudo fpgas-acorn-debug detect       # the Acorn-family endpoints on PCI
sudo fpgas-acorn-debug identify     # the running build and the flash's part, JEDEC ID and unique ID, read live
```

For the fpgas.online openFPGALoader build (with the RP1 PIO JTAG cable and SPI flash info), add the [fpgas.online-fpga-tools repository](https://github.com/fpgas-online/fpgas.online-fpga-tools#debian-packages-bookworm-trixie-sid-arm64-armhf) **before** installing. Otherwise apt installs Debian's own package (bookworm 0.10.0, trixie 0.13.1). Adding the repository afterwards does not replace it; run `sudo apt install openfpgaloader-fpgasonline` to switch. Fleet Pis already get the patched `openfpgaloader-fpgasonline-git` from the infra role.

**Use the flash tool** against the installed images (CLE-215+ shown; use `acorn-cle-101-*` for a CLE-101):

```bash
sudo fpgas-acorn-flash id
sudo fpgas-acorn-flash verify /usr/share/fpgas-online/acorn-pcie/images/acorn-cle-215p-sqrl_acorn_operational.bin 0x400000
```

Writing the flash, and converting a board that still runs the factory image, are covered in [acorn-pcie-programming.md](pcie-programming.md). After writing it, run `sudo fpgas-verify --update`. `fpgas-acorn-flash` reaches the flash through the fpgas.online SoC's PCIe BAR0, so it needs that SoC to be running already. By default it expects the SoC at `0001:01:00.0`; pass `--bdf` for another address, or `--uart PORT` to use the UART bridge instead.
