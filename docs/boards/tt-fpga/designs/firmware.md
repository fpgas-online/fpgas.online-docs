# Tiny Tapeout FPGA board: firmware and known workarounds

**You look after a Tiny Tapeout FPGA demo board (version 3, RP2350) on a Raspberry Pi and want to know which
firmware its microcontroller runs, and the workarounds our scripts carry for it.**

```{include} ../streaming-rule.inc
```

That covers `main.py` and the firmware too: the firmware on a board is installed by whoever looks after the
board, and the check writes nothing to it.

:::{warning}
**Nothing replaces `main.py`.** No code of ours writes, replaces or deletes `main.py` or any other file on a
demo board. The public site (and the `fpgas-tt` daemon's design list) depends on the SDK booting into
`DemoBoard()`, so a no-op `main.py` takes the board off
tinytapeout.fpgas.online until the SDK files are restored, and the boot check cannot identify such a
board ([test-designs issue #117](https://github.com/fpgas-online/fpgas.online-test-designs/issues/117)).
The boot check reads `main.py` and reports a board whose file is not the
SDK's own as an `error`; putting the SDK's own file back on such a board is a deliberate act by whoever looks
after the board, not something the tooling does (source: [the board's page in
fpgas.online-test-designs](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/docs/hardware/tt-fpga.md#the-sdks-mainpy)).
:::

## Board firmware

The boards at welland run TT SDK **3.1.0** (read on 5 October 2026 by the boot check, which recorded SDK
3.1.0 and the demo board `TTDBv3 [3.2]`). With 3.1.0 the SDK's `tt` object comes up as `Shuttle FPGA` and the
Commander connects.

The boot check's `sdk` test expects an FPGA board to run SDK 3.1.x on an RP2350, and reads whether the
board's `main.py` is still that release's own: [the `sdk` test](../../../verify/fpgas-verify.md#the-sdk-test),
[TT FPGA identity](../../../verify/fpgas-verify.md#tt-fpga-identity).

## RP2350 considerations

- The public site depends on the SDK booting, so `main.py` is never replaced (the warning at the top of this
  page).
- The `fpgas-tt` daemon owns `/dev/ttboard` on every host of the public site; stop it before using
  `mpremote` directly, after looking for a visitor, and start it again afterwards (the warning on [the UART
  test](uart.md#by-hand)).
- If the RP2350 is unresponsive, a USB power cycle via `uhubctl` or a PoE reset of its Pi can recover it
  (not verified by us; on a Pi 4 `uhubctl` may switch every USB port at once).

## Known Workarounds

### DemoBoard() hang on boot

The stock RP2350 (RP2040 on version 2 boards) `main.py` calls `DemoBoard()` which
probes I2C and can
hang permanently, making the board unrecoverable without a physical reset. SDK 3.1.0 boots cleanly
(history: below).

If a board does hang, a power cycle of its Pi (a PoE cycle of its switch port) resets it (not verified by
us: the board is powered from the Pi's USB); the RP2's
mass-storage bootloader path stalls on
Pi 3B+ hosts, so reflashing from a Pi 3B+ needs the PICOBOOT path rather than
MSC (on 3 September 2026 no TT FPGA host at welland was a Pi 3B+; each was a Pi 4). A reflash is done by
whoever looks after the board; no code of ours writes to a demo board.

### RP2350 PWM first-call bug

The first `PWM()` call on GPIO16 produces a stuck-HIGH output instead of
oscillation. The source text calls this an RP2040 bug, but the
[programming script](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/designs/_host/tt_fpga_program.py) that carries the
workaround labels it "Workaround for RP2350 PWM bug", and every deployed board
is an RP2350B. **Workaround:** deinit and recreate the PWM object:

```python
clk = PWM(Pin(16))
clk.deinit()
utime.sleep_ms(1)
clk = PWM(Pin(16))  # Second call oscillates correctly
```

### SPI kernel module conflict

```{include} spi-modules.inc
```

## History

None of this is done now, and none of it needs doing. Today no code of ours writes to a demo board's
firmware or files.

- **`main.py`.** Until October 2026 the
  [UART test wrapper](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/designs/_host/tt_test_wrapper.py)
  overwrote it with a no-op after every load, as a workaround for the `DemoBoard()` hang. The wrapper no
  longer touches it.
- **The reflash.** On 2026-08-23 the boards then at welland were reflashed to TT SDK 3.1.0 (the shipped
  `ttdbv3` build stalled at boot). The shipped `ttdbv3` firmware hung in `DemoBoard()` on each board then at
  welland; SDK 3.1.0 boots cleanly and each of them reported `board present` on 2026-09-03.
- **GPIOMap firmware mismatch.** Observed on the firmware the boards shipped with: it loaded `GPIOMapTT04`
  instead of `GPIOMapTTDBv3`, but the TTDBv3 hardware uses different GPIO assignments, so `pin_indices()`
  returned wrong pin numbers. **Workaround, still in the code:** all host scripts hardcode the correct GPIO
  pins (SPI: SCK=6, MOSI=3, SS=5, CRESET=1; UART: TX=GPIO20, RX=GPIO37). Not re-checked since the
  2026-08-23 reflash to SDK 3.1.0; the hardcoded pins are correct either way. The pin numbers on the
  [wiring pages](../wiring/pins-other.md) are the TTDBv3 values, not the ones that firmware reported.
- **"Empirically confirmed."** The old page called those pin numbers "empirically confirmed". What the
  records name: each FPGA pin's Raspberry Pi GPIO was measured on 29 September and 4 October 2026
  ([sources](../wiring/sources.md)); the RP2350's loading pins work in every load, and its GPIO20/37 in the
  `uart` test that passed on 2 October 2026. For the RP2350's other GPIO numbers the old page said they were
  empirically confirmed; no record of that measurement is named.
- **The serial pair on the Pi's GPIOs.** An earlier version of the UART page named GPIO5/11, and then
  GPIO17/19 (GPIO17 is RTS0 and GPIO19 is PCM_FS), as the pair; both came from pin tables that the measured
  cabling has replaced ([the UART test](uart.md)).
- **SPI flash.** Until 6 October 2026 this board's page said the breakout "also has SPI flash (CS_N=pin 16,
  CLK=pin 15, MOSI=pin 14, MISO=pin 17) for persistent bitstream storage, used by the SPI Flash ID test".
  Those four pins are the iCE40's configuration pins, which go only to the demo board's microcontroller:
  [the pins that load the FPGA](../wiring/pins-other.md#loading-the-fpga-its-configuration-pins). The
  results of 2 October 2026 on [Checking a board:
  fpgas-verify](../../../verify/fpgas-verify.md#current-results) still show `spiflash=fail` on the boards
  read that day: the test that was then removed, failing on a board with no flash to answer, not a fault of
  those boards.
