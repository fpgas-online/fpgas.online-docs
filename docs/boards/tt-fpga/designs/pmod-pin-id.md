# Tiny Tapeout FPGA board test: Pmod pin ID

**You have a Tiny Tapeout FPGA demo board cabled to a Raspberry Pi with a Pmod HAT and want to know what the
pin-ID design is, how it is loaded and what a good result is: each FPGA pin sending its own pin number, so
that the far end of every wire can be read off.**

- **What it verifies:** UART TX on each GPIO pin.
- **Bitstream:** [`pmod-pin-id/.../tt_fpga_platform.bin`](https://github.com/fpgas-online/fpgas.online-test-designs/tree/main/designs/pmod-pin-id/).
- **Wrapper:** [`tt_pmod_wrapper.py`](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/designs/_host/tt_pmod_wrapper.py).

The pin ID test and how to read its output are described on
[Pin identification](../../pin-id.md).

## In the boot check

This is the `pin-id` test of the boot check, and the check runs it without any of the steps below: [verifying
1](../building/verifying-1.md). It passes when each Pmod HAT GPIO receives the FPGA pin the expected cabling
puts there (`ui_in` on HAT JA, `uio` on JB, `uo_out` on JC). From a failure to the cable: [verifying
2](../building/verifying-2.md).

```{include} ../pin-id-coverage.inc
```

## What it has measured

The wiring pages' "measured" wires were read with this design on 29 September 2026, and again by the boot
check on 4 October 2026: [sources](../wiring/sources.md). An earlier version of this board's page carried two
mappings that disagreed (which of JA and JC carries `ui_in`, and the bit order) and asked for this design to
settle it. It has: the mapping is the one on [`ui_in` and `uo_out`, wire by wire](../wiring/pins-ui-uo.md),
and the loopback test's pin lists were changed to it
([test-designs issue #19](https://github.com/fpgas-online/fpgas.online-test-designs/issues/19),
[issue #58](https://github.com/fpgas-online/fpgas.online-test-designs/issues/58)).

What it has not measured: the six wires on the shared GPIOs (above).

## By hand

```{include} ../streaming-rule.inc
```

```{include} run-the-pmod-test.inc
```

```console
$ sudo fpgas-tt-fpga-debug --variant tt-fpga test pin-id
```

```{include} wrappers.inc
```

For this test the wrapper is `tt_pmod_wrapper.py`: it programs the FPGA, releases the RP2350's GPIOs to
high-Z and hands off to the test on the Raspberry Pi's GPIOs. The older runner, `verify_hardware.py`, run from a workstation, is described for operators on [Verifying a deployment](../../../setup/verification.md#tt-fpga-programming), another page, not in this set; its host table names hosts that no longer exist.
