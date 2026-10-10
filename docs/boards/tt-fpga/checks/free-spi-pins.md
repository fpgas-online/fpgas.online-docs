---
type: how-to
owner: documentation maintainers
reader: someone about to run a PMOD test against a Tiny Tapeout FPGA demo board
review: 2026-11-10
---

# How to free the Raspberry Pi's SPI pins before a PMOD test

**You want to run a PMOD test against a Tiny Tapeout FPGA demo board, and the Pi's SPI modules hold GPIO7-11.**

Raspberry Pi GPIO7-11 overlap with the SPI0 bus and conflict with the PMOD HAT pins JA/JB pins 2-4. Under the pin mapping, GPIO7-11 carry JB1/`uio[0]` and JA1-4/`uo_out[0:3]`. The same five GPIOs are contended either way.

## What you need

- `sudo` on the Raspberry Pi that has the board and its PMOD HAT.
- Nothing else on the Pi using SPI0: this step takes the bus away from it.
- The check's debug tool, `fpgas-tt-fpga-debug`, from [How to install the Tiny Tapeout FPGA packages](../setup/packages.md).
- The board's GPIO pins released to high impedance after FPGA programming (`--gpio-release`).

## Steps

1. On the Pi, run `sudo rmmod spidev spi_bcm2835` to unload the SPI kernel modules, which frees GPIO7-11.

## Check

The SPI modules no longer claim GPIO7-11. A PMOD test can then use HAT JA pins 1-4 and JB pin 1, which carry `uo_out[2]`, `uo_out[4]`, `uo_out[6]` and `uo_out[7]`.

## If it fails

| What you see | Likely cause | Fix |
|---|---|---|
| `uo_out[1:3]` and `uio[1:3]` disagree when both are driven | JA pins 2-4 and JB pins 2-4 share Raspberry Pi GPIOs | [Shared GPIOs of JA and JB](../setup/wiring.md#shared-gpios-of-ja-and-jb) |
| The board's outputs fight the Pi's drive | The RP2350 did not release its GPIO pins | Load the design with `--gpio-release` |

## Next

- [Tiny Tapeout FPGA demo board test designs](test-designs.md)
- [Tiny Tapeout FPGA demo board pin mapping](../overview/pin-mapping.md)
