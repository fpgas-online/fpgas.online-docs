# Tiny Tapeout FPGA board test: Pmod loopback

**You have a Tiny Tapeout FPGA demo board cabled to a Raspberry Pi with a Pmod HAT and want to know what the
loopback design is, what must be true before it runs and what a good result is: the Raspberry Pi drives the
eight `ui_in` signals and reads each one back, inverted, on `uo_out`.**

- **What it verifies:** GPIO inversion across wired pin pairs.
- **Bitstream:** [`pmod-loopback/.../tt_fpga_platform.bin`](https://github.com/fpgas-online/fpgas.online-test-designs/tree/main/designs/pmod-loopback/).
- **Wrapper:** [`tt_pmod_wrapper.py`](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/designs/_host/tt_pmod_wrapper.py).

## What it does

The GPIO loopback test uses all 8 ui_in pins (drive) and all 8 uo_out pins
(read). The FPGA computes `uo_out = ~ui_in`. The RPi drives the 8 `ui_in` pins through HAT JA and reads the 8
`uo_out` pins through HAT JC; bit i is driven on JA and read on JC. The pins:
[`ui_in` and `uo_out`, wire by wire](../wiring/pins-ui-uo.md).

It is not one of the tests the boot check runs: it is the `pmod` test of `fpgas-tt-fpga-debug`.

**What it cannot tell.** It drives and reads position by position, and the FPGA returns `uo_out = ~ui_in` bit
for bit, so any permutation that is the same in the two pin lists passes. A pass confirms that the cables are
connected, not that the bit order is right. The [pin-ID test](pmod-pin-id.md) does tell.

## The shared GPIOs

HAT JA pins 2-4 and HAT JB pins 2-4 are the [same RPi GPIO lines](../../pmod/rpi-hat.md) (GPIO10, GPIO9,
GPIO11 — the shared SPI0 bus), so `ui_in[1]` to `ui_in[3]` and `uio[1]` to `uio[3]` are connected at the RPi
side ([the shared GPIOs](../wiring/pins-uio-uart.md)). That conflict has several consequences:

- **GPIO loopback test**: Works because the test only drives ui_in (JA) and reads uo_out (JC). The uio pins
  (JB) are not driven during this test, so no conflict occurs.
- **Bidirectional I/O test**: Cannot independently test uio[1,2,3] because they are shorted to ui_in[1,2,3]
  respectively. If both are driven, the conflicting outputs may cause contention or incorrect readings.
- **SPI kernel modules**: Must be unloaded (`rmmod spidev spi_bcm2835`) since GPIO7-11 overlap with HAT JA
  pins 1-4 and JB pins 1-4.

The 5 unaffected uio bits (uio[0], uio[4:7]) on JB pins 1 and 7-10 use unique RPi GPIOs and work correctly.

## Running it

```{include} ../generated/tt-fpga-pins-other.md
:start-after: "### Loading the FPGA: its configuration pins"
:end-before: "The FPGA breakout has no SPI flash"
```

```{include} run-the-pmod-test.inc
```

```console
$ sudo fpgas-tt-fpga-debug --variant tt-fpga test pmod
```

```{include} wrappers.inc
```

For this test the wrapper is `tt_pmod_wrapper.py`. Running the test from a workstation instead, with the older
runner: [from a workstation](from-a-workstation.md).

## What has been measured

An earlier version of this page said all 8 pairs were "empirically confirmed (4-transition verification)" on
the board then on the host called pi33. That run used pin lists that predated the measured cabling
([test-designs issue #19](https://github.com/fpgas-online/fpgas.online-test-designs/issues/19)), and by the
paragraph above it confirmed only that the cables were connected. No run with the present pin lists is
recorded on these pages: not yet run by us on this hardware in its present form.
