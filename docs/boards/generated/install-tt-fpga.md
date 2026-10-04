% This section ("Installing the TT FPGA Packages") is copied from https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/docs/hardware/tt-fpga.md
% by tools/sync_test_designs.py. Do not edit it here: change it in test-designs.

## Installing the TT FPGA Packages

Add the fpgas.online APT repository first ([verify.md: Installing](../verify/fpgas-verify.md#installing)), then on the demo board's Pi:

```bash
sudo apt install fpgas-online-tt-fpga
```

| Package | Installs |
|---------|----------|
| `fpgas-online-tt-fpga` | installs everything below to check a TT FPGA Demo Board, and turns the boot check (`fpgas-verify.service`) on for it |
| `fpgas-online-tt-fpga-tools` | the board's module of `fpgas_online_verify`, and `fpgas-tt-fpga-verify`; with `python3-serial` and `python3-libgpiod` (the PMOD HAT scan), and recommending `micropython-mpremote` and `raspi-utils-core` (`pinctrl`, which puts back the Pi's SPI/UART/I2C pin functions after the scan; Raspberry Pi OS only) |
| `fpgas-online-tt-fpga-bitstreams` | the test bitstreams built by the same commit's CI, in `/usr/share/fpgas-online/tt-fpga/bitstreams/` |
| `fpgas-online-verify` | `fpgas-verify`, the unit, and the host test scripts |

`fpgas-online-tt` is a different package: the TT site's own.

The check finds the board by its Raspberry Pi microcontroller on USB (vendor `2e8a`). It first loads the PMOD pin identification design and checks the PMOD HAT cabling against the expected map (ui_in on HAT JA, uio on JB, uo_out on JC, [tt-fpga-pin-mapping.md](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/docs/hardware/tt-fpga-pin-mapping.md)); a miswired HAT fails the board. It then loads the UART test design through that microcontroller (`tt_fpga_program.py`, over `mpremote`), and runs its host test through the UART bridge on `/dev/ttyACM0`. There is no SPI flash test: the breakout has no flash (see [Programming](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/docs/hardware/tt-fpga.md#programming)). Nothing is written to the demo board: for every load the microcontroller reads the bitstream from the Pi over the serial link (see [Programming](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/docs/hardware/tt-fpga.md#programming)). The board has no flash to compare, so what `changed` compares is its USB serial number. `mpremote` is `micropython-mpremote` in trixie, but only in bookworm-backports for bookworm: without it the check reports an `error`. Only the PMOD loopback test is left to `fpgas-tt-fpga-debug`.

Before the first test, while it holds `/dev/ttyACM0`, the check reads whether the board's `main.py` is still the SDK's own (`tt_main_py.py`, with or without rpi-hwid; a changed one is an `error`). It then starts the board's SDK (`tt_sdk_start.py`, see [The SDK's main.py](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/docs/hardware/tt-fpga.md#the-sdks-mainpy)) and then runs `rpi-hwid tinytapeout --json --no-stop-service`, both only when [rpi-hwid](https://github.com/mithro/rpi-hwid) is installed (`python3-rpi-hwid`, which `fpgas-online-verify` suggests). rpi-hwid asks the Tiny Tapeout SDK on the RP2350 which microcontroller, chip, demo board and SDK release this is. The answer goes into the board's identity, for rpi-hwid's Tiny Tapeout label ([TT FPGA identity](../verify/fpgas-verify.md#tt-fpga-identity), [Tiny Tapeout fields](../verify/identity.md#tiny-tapeout-fields)). Without rpi-hwid those fields are not read, and the board does not fail for it.

It runs at every boot of the Welland TT FPGA boards: [current results](../verify/fpgas-verify.md#current-results).

**Check the board now**, or run one test with its output live (`fpgas-tt-fpga-debug` is in `fpgas-online-tt-fpga-debug`):

```bash
sudo fpgas-tt-fpga-verify --no-publish --report -  # this board only, the JSON report on stdout
sudo fpgas-tt-fpga-debug test uart                 # load one test's design and run its test
```

What the results mean, the report, `changed` and `--update`, the debug tool and common failures: [verify.md](../verify/fpgas-verify.md#reading-the-result).
