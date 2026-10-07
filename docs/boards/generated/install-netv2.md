% This section ("Installing the NeTV2 Packages") is copied from https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/docs/hardware/netv2.md
% by tools/sync_test_designs.py. Do not edit it here: change it in test-designs.

## Installing the NeTV2 Packages

Add the fpgas.online APT repository first ([fpgas-verify: installing it](../verify/installing.md#installing)), then on the NeTV2's Pi:

```bash
sudo apt install fpgas-online-netv2
```

| Package | Installs |
|---------|----------|
| `fpgas-online-netv2` | installs everything below to check a NeTV2, and turns the boot check (`fpgas-verify.service`) on for it |
| `fpgas-online-netv2-tools` | the NeTV2's module of `fpgas_online_verify`, and `fpgas-netv2-verify`; with `python3-serial`, openFPGALoader and openocd |
| `fpgas-online-netv2-bitstreams` | the XC7A35T and XC7A100T test bitstreams built by the same commit's CI, in `/usr/share/fpgas-online/netv2/bitstreams/` |
| `fpgas-online-verify` | `fpgas-verify`, the unit, and the host test scripts |

The NeTV2 has no USB, so the check finds it with a JTAG scan over the Pi's header: TCK GPIO4, TMS GPIO17, TDI GPIO27, TDO GPIO22. The scan drives GPIO 4, 17 and 27. On a host set up with `fpgas-online-netv2` that is all it looks for; with `fpgas-online-all-boards` it scans only when no USB or PCI board was found (`--no-probe` rules it out). The scan reads the whole IDCODE (OpenOCD on a Pi 3/4, openFPGALoader's raw scan on a Pi 5), whose part says which FPGA is fitted, so which bitstreams to use; its silicon version is reported (the report's `jtag.idcode_version`) and does not matter ([fpgas-verify: the JTAG IDCODE](../verify/idcode-and-dna.md#the-jtag-idcode)). A variant set with `--variant` that is not the IDCODE's part fails the board. It then reads the device DNA with `openFPGALoader --read-dna` on the same pins (`rp1pio` on a Pi 5, `libgpiod` on a Pi 3/4), which loads nothing, and puts the pins back as after the scan; a DNA that cannot be read, or is all zeros or all ones, fails the board ([fpgas-verify: the device DNA](../verify/idcode-and-dna.md#the-device-dna)). The check loads the UART, DDR and SPI flash test designs into SRAM, with openocd on a Pi 3/4 and openFPGALoader's `rp1pio` cable on a Pi 5. It runs each design's host test on `/dev/ttyAMA0`, then reads back the flash's boot image region. The IDCODE, the device DNA, the flash's JEDEC ID and that region's sha256 are what `changed` compares.

On a Pi 5, add the [fpgas.online-fpga-tools repository](https://github.com/fpgas-online/fpgas.online-fpga-tools#debian-packages-bookworm-trixie-sid-arm64-armhf) **before** installing: only its openFPGALoader builds have the `rp1pio` cable. They also have the SPI-over-JTAG bridge for the XC7A35T-FGG484, which Debian bookworm's `openfpgaloader` lacks, so on bookworm the flash readback of an XC7A35T board fails without them.

It runs at every boot of the Welland NeTV2s: [current results](../verify/current-results.md#current-results).

**Check the board now**, or run one test with its output live (`fpgas-netv2-debug` is in `fpgas-online-netv2-debug`):

```bash
sudo fpgas-netv2-verify --no-publish --report -  # this board only, the JSON report on stdout
sudo fpgas-netv2-debug test uart                 # load one test's design and run its test
```

What the results mean, the report, `changed` and `--update`, the debug tool and common failures: [fpgas-verify: reading the result](../verify/reading-the-result.md#reading-the-result).
