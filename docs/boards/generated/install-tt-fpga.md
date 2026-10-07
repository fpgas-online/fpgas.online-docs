% This section ("Installing the TT FPGA Packages") is copied from https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/docs/hardware/tt-fpga.md
% by tools/sync_repos.py. Do not edit it here: change it in test-designs.

## Installing the TT FPGA Packages

Add the fpgas.online APT repository first ([fpgas-verify: installing it](../verify/installing.md#installing)), then on the demo board's Pi:

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

The check finds the board by its Raspberry Pi microcontroller on USB (`2e8a:0005` or `2e8a:000f`, MicroPython's serial port). That does not say whether the demo board carries the FPGA breakout or a Tiny Tapeout chip, so the check asks the board itself (below) and loads a design only into a board that said it is an FPGA board ([Which Tiny Tapeout board it is](../verify/tt-fpga.md#which-tiny-tapeout-board-it-is)). Every board first has what it said judged by [the `sdk` test](../verify/tt-fpga.md#the-sdk-test), which loads nothing; for a board with a Tiny Tapeout chip that is the only test so far, and such a board fails until its Pmod cabling can be tested (the report says so). On an FPGA board it then loads the PMOD pin identification design and checks the PMOD HAT cabling against the expected map (ui_in on HAT JA, uio on JB, uo_out on JC, [TT FPGA Demo Board v3 Pin Mapping](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/docs/hardware/tt-fpga-pin-mapping.md)); a miswired HAT fails the board. It then loads the UART test design through that microcontroller (`tt_fpga_program.py`, over `mpremote`), and runs its host test through the UART bridge on `/dev/ttyACM0`. There is no SPI flash test: the breakout has no flash (see [Programming](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/docs/hardware/tt-fpga.md#programming)). Nothing is written to the demo board: for every load the microcontroller reads the bitstream from the Pi over the serial link (see [Programming](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/docs/hardware/tt-fpga.md#programming)). The board has no flash to compare, so what `changed` compares is its USB serial number. `mpremote` is `micropython-mpremote` in trixie, but only in bookworm-backports for bookworm: without it the check reports an `error`. Only the PMOD loopback test is left to `fpgas-tt-fpga-debug`. When the tests are done the check streams one more design, which moves the seven-segment display and is left running ([what the TT FPGA is left running](../verify/tt-fpga.md#what-the-tt-fpga-is-left-running)); if that load fails the board still passes, with a warning in the report.

Before the first test, while it holds `/dev/ttyACM0`, the check reads whether the board's `main.py` is still the SDK's own (`tt_main_py.py`, with or without rpi-hwid; a changed one is an `error`). It then starts the board's SDK (`tt_sdk_start.py`, see [The SDK's main.py](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/docs/hardware/tt-fpga.md#the-sdks-mainpy)) and then runs `rpi-hwid tinytapeout --json --no-stop-service`, both only when [rpi-hwid](https://github.com/mithro/rpi-hwid) is installed (`python3-rpi-hwid`, which `fpgas-online-verify` suggests, from rpi-hwid's own apt repository). rpi-hwid asks the Tiny Tapeout SDK on the RP2350 which microcontroller, chip, demo board and SDK release this is. The answer goes into the board's identity, for rpi-hwid's Tiny Tapeout label ([TT FPGA identity](../verify/tt-fpga.md#tt-fpga-identity), [Tiny Tapeout fields](../verify/identity.md#tiny-tapeout-fields)). Without rpi-hwid the board cannot be asked which Tiny Tapeout board it is: the check is an `error` and nothing is loaded.

It runs at every boot of the Welland TT FPGA boards: [current results](../verify/current-results.md#current-results).

**Check the board now**, or run one test with its output live (`fpgas-tt-fpga-debug` is in `fpgas-online-tt-fpga-debug`):

```bash
sudo fpgas-tt-fpga-verify --no-publish --report -  # this board only, the JSON report on stdout
sudo fpgas-tt-fpga-debug test uart                 # load one test's design and run its test
```

What the results mean, the report, `changed` and `--update`, the debug tool and common failures: [fpgas-verify: reading the result](../verify/reading-the-result.md#reading-the-result).
