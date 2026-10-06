# Tiny Tapeout FPGA board test: Pmod loopback

**You have a Tiny Tapeout FPGA demo board cabled to a Raspberry Pi with a Pmod HAT and want to know what the
loopback design is, what must be true before it runs and what a good result is: the Raspberry Pi drives the
eight `ui_in` signals and reads each one back, inverted, on `uo_out`.**

| Test | Bitstream | Wrapper | What it verifies |
|------|-----------|---------|------------------|
| PMOD loopback | [`pmod-loopback/.../tt_fpga_platform.bin`](https://github.com/fpgas-online/fpgas.online-test-designs/tree/main/designs/pmod-loopback/) | [`tt_pmod_wrapper.py`](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/designs/_host/tt_pmod_wrapper.py) | GPIO inversion across wired pin pairs |

## What it does

The GPIO loopback test uses all 8 ui_in pins (drive) and all 8 uo_out pins
(read). The FPGA computes `uo_out = ~ui_in`. The RPi drives the 8 `ui_in` pins through HAT JA and reads the 8
`uo_out` pins through HAT JC; bit i is driven on JA and read on JC. The pins:
[`ui_in` and `uo_out`, wire by wire](../wiring/pins-ui-uo.md).

It is not one of the tests the boot check runs: it is the `pmod` test of `fpgas-tt-fpga-debug`.

**What it cannot tell.** It drives and reads position by position, and the FPGA returns `uo_out = ~ui_in` bit
for bit, so any permutation that is the same in the two pin lists passes. A pass confirms that the cables are
connected, not that the bit order is right. The [pin-ID test](pmod-pin-id.md) does tell.

## Before running the test

```{include} ../generated/tt-fpga-pins-other.md
:start-after: "### Loading the FPGA: its configuration pins"
:end-before: "The FPGA breakout has no SPI flash"
```

```{include} ../serial-port.inc
```

- `rmmod spidev spi_bcm2835` — SPI kernel modules claim GPIO7-11 (HAT JA pins 1-4 and JB pin 1, used by
  `ui_in[0]` to `ui_in[3]` and `uio[0]`); the command is below this list
- RP2350 GPIOs must be released to high-Z after FPGA programming (the
  programming wrapper handles this automatically)
- Driving `ui_in[1]` to `ui_in[3]` also drives `uio[1]` to `uio[3]`: HAT JA pins 2-4 and HAT JB pins 2-4 are
  the [same RPi GPIO lines](../../pmod/rpi-hat.md) (GPIO10, GPIO9, GPIO11 — the shared SPI0 bus). The loopback
  design does not use `uio`, so no conflict occurs. A design that drives `uio[1]` to `uio[3]` would fight the
  Raspberry Pi on those three GPIOs: [the shared GPIOs](../wiring/pins-uio-uart.md).

```{include} spi-modules.inc
```

## Running it

```{include} wrappers.inc
```

For this test the wrapper is `tt_pmod_wrapper.py`. **No command line for it is recorded on these pages.** With
the packages installed, the record gives `sudo fpgas-tt-fpga-debug test uart` for the `uart` test; for this
test the name is `pmod`. That form is not written down anywhere as run by us: see [verifying
2](../building/verifying-2.md#the-failing-line) for what the check's documentation says of the tool.

### From a workstation

```{include} run-from-workstation.inc
```

## What has been measured

An earlier version of this page said all 8 pairs were "empirically confirmed (4-transition verification)" on
the board then on the host called pi33. That run used pin lists that predated the measured cabling
([test-designs issue #19](https://github.com/fpgas-online/fpgas.online-test-designs/issues/19)), and by the
paragraph above it confirmed only that the cables were connected. No run with the present pin lists is
recorded on these pages: not yet run by us on this hardware in its present form.
