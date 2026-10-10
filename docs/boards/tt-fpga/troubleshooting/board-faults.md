---
type: reference
owner: documentation maintainers
reader: someone whose Tiny Tapeout FPGA demo board hangs, has no clock, or does not answer
review: 2026-11-10
---

# Tiny Tapeout FPGA demo board faults

**Your demo board hangs at boot, shows no clock, or does not answer, and you want the likely cause.**

What the firmware does is on [The firmware on a Tiny Tapeout FPGA demo board](../overview/firmware.md). What happens on the Raspberry Pi side is on [Tiny Tapeout FPGA demo board faults on the Raspberry Pi](pi-faults.md).

What you see is the symptom, Likely cause the reason, and Fix what to do.

| What you see | Likely cause | Fix |
|---|---|---|
| The board never comes up | The stock `main.py` calls `DemoBoard()`, which probes I2C and can hang permanently. The `ttdbv3` firmware the boards shipped with did this | A PoE cycle of the board's switch port resets it; if the RP2350 is unresponsive, a USB power cycle with `uhubctl` can also recover it. SDK 3.1.0 boots cleanly, and the board reports `board present` |
| The board is off the public site although the Pi is up | A `main.py` that does nothing: the site and the daemon's design list depend on the SDK booting into `DemoBoard()` | Recovery without a file write is [fpgas.online-tt issue #21](https://github.com/fpgas-online/fpgas.online-tt/issues/21) |
| `pin_indices()` returns wrong pin numbers | The firmware the boards shipped with loaded `GPIOMapTT04`, and the TTDBv3 hardware uses different GPIO assignments | All host scripts hardcode the correct GPIO pins (SPI: SCK=6, MOSI=3, SS=5, CRESET=1; UART: TX=GPIO20, RX=GPIO37) |
| The clock output on GPIO16 is stuck high instead of oscillating | The first `PWM()` call on GPIO16 of the RP2350 produces a stuck-HIGH output | Deinit and recreate the PWM object, as the code below shows |
| The check fails with `dip-switches fail: switch N is on` | A DIP switch on `ui_in` is on | Set all DIP switches off and run the check again: [The DIP switches](../../../verify/tt-fpga.md#the-dip-switches) |

## RP2350 PWM first-call bug

The first `PWM()` call on GPIO16 produces a stuck-HIGH output instead of oscillation. The [programming script](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/designs/_host/tt_fpga_program.py) that carries the workaround labels it "Workaround for RP2350 PWM bug". The workaround deinits and recreates the PWM object:

```python
clk = PWM(Pin(16))
clk.deinit()
utime.sleep_ms(1)
clk = PWM(Pin(16))  # Second call oscillates correctly
```
