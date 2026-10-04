% This section ("Installing the Fomu Packages") is copied from https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/docs/hardware/fomu-evt.md
% by tools/sync_test_designs.py. Do not edit it here: change it in test-designs.

## Installing the Fomu Packages

Add the fpgas.online APT repository first ([verify.md: Installing](../verify/fpgas-verify.md#installing)), then on the Fomu's Pi:

```bash
sudo apt install fpgas-online-fomu
```

| Package | Installs |
|---------|----------|
| `fpgas-online-fomu` | installs everything below to check a Fomu, and turns the boot check (`fpgas-verify.service`) on for it |
| `fpgas-online-fomu-tools` | the Fomu's module of `fpgas_online_verify`, and `fpgas-fomu-verify`; with `python3-serial` and openFPGALoader |
| `fpgas-online-fomu-bitstreams` | the test bitstreams built by the same commit's CI, in `/usr/share/fpgas-online/fomu/bitstreams/` |
| `fpgas-online-verify` | `fpgas-verify`, the unit, and the host test scripts |

The check finds the Fomu by its foboot DFU bootloader on USB (`1209:5bf0`), which is there from power-up until a design is loaded. It loads the UART test design with openFPGALoader over DFU and runs its host test on `/dev/serial0`. That is the only test at boot: a DFU load replaces the bootloader until the next power cycle, and it writes the design into the flash's user image. So the Fomu's flash is not part of what `changed` compares; its USB serial number is. `fpgas-fomu-debug` runs the SPI flash, PMOD loopback and pin identification tests, one per power cycle.

Welland's Fomu (pi-sw1-p17) does not enumerate, so that Pi reports `missing` ([current results](../verify/fpgas-verify.md#current-results)).

**Check the board now**, or run one test with its output live (`fpgas-fomu-debug` is in `fpgas-online-fomu-debug`):

```bash
sudo fpgas-fomu-verify --no-publish --report -  # this board only, the JSON report on stdout
sudo fpgas-fomu-debug test spiflash             # load one test's design and run its test
```

What the results mean, the report, `changed` and `--update`, the debug tool and common failures: [verify.md](../verify/fpgas-verify.md#reading-the-result).
