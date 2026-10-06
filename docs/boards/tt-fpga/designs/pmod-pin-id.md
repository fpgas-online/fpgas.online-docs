# Tiny Tapeout FPGA board test: Pmod pin ID

**You have a Tiny Tapeout FPGA demo board cabled to a Raspberry Pi with a Pmod HAT and want to know what the
pin-ID design is, how it is loaded and what a good result is: each FPGA pin sending its own pin number, so
that the far end of every wire can be read off.**

| Test | Bitstream | Wrapper | What it verifies |
|------|-----------|---------|------------------|
| PMOD pin ID | [`pmod-pin-id/.../tt_fpga_platform.bin`](https://github.com/fpgas-online/fpgas.online-test-designs/tree/main/designs/pmod-pin-id/) | [`tt_pmod_wrapper.py`](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/designs/_host/tt_pmod_wrapper.py) | UART TX on each GPIO pin |

The pin ID test and how to read its output are described on
[Pin identification](../../pin-id.md).

## In the boot check

This is the `pin-id` test of the boot check, and the check runs it without any of the steps below: [verifying
1](../building/verifying-1.md). It passes when each Pmod HAT GPIO receives the FPGA pin the expected cabling
puts there (`ui_in` on HAT JA, `uio` on JB, `uo_out` on JC): all 24 signal wires of the three ribbons. From a
failure to the cable: [verifying 2](../building/verifying-2.md).

## What it has measured

The wiring pages' "measured" wires were read with this design on 29 September 2026, and again by the boot
check on 4 October 2026: [sources](../wiring/sources.md). An earlier version of this board's page carried two
mappings that disagreed (which of JA and JC carries `ui_in`, and the bit order) and asked for this design to
settle it. It has: the mapping is the one on [`ui_in` and `uo_out`, wire by wire](../wiring/pins-ui-uo.md),
and the loopback test's pin lists were changed to it
([test-designs issue #19](https://github.com/fpgas-online/fpgas.online-test-designs/issues/19),
[issue #58](https://github.com/fpgas-online/fpgas.online-test-designs/issues/58)).

What it has not measured: the six wires on the three GPIOs that JA and JB share (`ui_in[1]` to `ui_in[3]`,
`uio[1]` to `uio[3]`). The design now sends on those in turns so that each can be read
([issue #142](https://github.com/fpgas-online/fpgas.online-test-designs/issues/142)); no result of that is
recorded on the wiring pages yet.

## By hand

```{include} ../generated/tt-fpga-pins-other.md
:start-after: "### Loading the FPGA: its configuration pins"
:end-before: "The FPGA breakout has no SPI flash"
```

```{include} ../serial-port.inc
```

```{include} wrappers.inc
```

For this test the wrapper is `tt_pmod_wrapper.py`: it programs the FPGA, releases the RP2350's GPIOs to
high-Z and hands off to the test on the Raspberry Pi's GPIOs. **No command line for it is recorded on these
pages**, and it has not been run by us in a form we can show. The check's own tool runs one test with its
output live: [verifying 2](../building/verifying-2.md#the-failing-line).

Before a Pmod test:

```{include} spi-modules.inc
```

## Running it from a workstation

```{include} run-from-workstation.inc
```
