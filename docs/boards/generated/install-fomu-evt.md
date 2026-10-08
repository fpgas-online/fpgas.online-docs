% This section ("Installing the Fomu Packages") is copied from https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/docs/hardware/fomu-evt.md
% by tools/sync_repos.py. Do not edit it here: change it in test-designs.

## Installing the Fomu Packages

Add the fpgas.online APT repository first ([fpgas-verify: installing it](../verify/installing.md#installing)), then on the Fomu's Pi:

```bash
sudo apt install fpgas-online-fomu
```

| Package | Installs |
|---------|----------|
| `fpgas-online-fomu` | installs everything below to check a Fomu, and turns the boot check (`fpgas-verify.service`) on for it |
| `fpgas-online-fomu-tools` | the Fomu's module of `fpgas_online_verify`, and `fpgas-fomu-verify`; with `python3-serial` and openFPGALoader |
| `fpgas-online-fomu-bitstreams` | the test bitstreams built by the same commit's CI, in `/usr/share/fpgas-online/fomu/bitstreams/` |
| `fpgas-online-verify` | `fpgas-verify`, the unit, and the host test scripts |

The EVT sits on the Pi's GPIO header ([how it is wired](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/docs/hardware/fomu-pin-mapping.md#the-pis-header)).

How the check works with it:
- **Finding it.** The check reads the iCE40's CDONE (GPIO17), which drives nothing: high means the board is there and running a design. foboot's DFU bootloader on USB (`1209:5bf0`) finds it too, but is not needed. A Fomu whose USB is being analysed, or that runs a design with no USB, is still found.
- **Identifying it**, before any test. The check holds the iCE40 in reset and reads the flash's JEDEC ID and 64-bit unique ID over the header with read commands only. It then sets every line back to an input and lets the iCE40 boot from its flash, into foboot, as at power-up. That stops whatever design was running, so only the check does it. The `header` test judges the reading.
- **The board's label** is the flash's unique ID (`flash_uid`): foboot has no USB serial number.
- **The `foboot` test** passes when foboot appears on USB within 10 s of the reset.
- **The UART test.** The check loads the UART test design with openFPGALoader over DFU and runs its host test on `/dev/serial0`. That is the only test that loads a design at boot. A DFU load replaces the bootloader until the next reset, and it writes the design into the flash's user image. So the flash's contents are not part of what `changed` compares; its IDs are.
- `fpgas-fomu-debug` runs the SPI flash, PMOD loopback and pin identification tests, one per power cycle. The PMOD tests assume a PMOD HAT ([not a loopback on the EVT](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/docs/hardware/fomu-pin-mapping.md#not-a-loopback-on-the-evt)).

**Check the board now**, or run one test with its output live (`fpgas-fomu-debug` is in `fpgas-online-fomu-debug`):

```bash
sudo fpgas-fomu-verify --no-publish --report -  # this board only, the JSON report on stdout
sudo fpgas-fomu-debug test spiflash             # load one test's design and run its test
```

What the results mean, the report, `changed` and `--update`, the debug tool and common failures: [fpgas-verify: reading the result](../verify/reading-the-result.md#reading-the-result).
