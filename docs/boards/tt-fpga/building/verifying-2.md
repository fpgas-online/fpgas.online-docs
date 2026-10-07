# Tiny Tapeout FPGA board on a Raspberry Pi: verifying 2, from a failing line to the cable

**You have run the check on a Tiny Tapeout FPGA demo board on a Raspberry Pi with a Pmod HAT, its `pin-id`
test failed, and you want to find the cable or wire at fault.**

**No worked example yet.** We hold no recorded output of a failing `pin-id` test on this board to show here,
and this page has not been followed by us from a real fault to a repaired cable. It says what the check's own
documentation records.

## What the Pmod wiring test is

On an FPGA board the check's `pin-id` test is the wiring test: it loads the pin identification design, in
which each FPGA pin sends its own pin number, and the Raspberry Pi reads which number arrives on which GPIO of
the Pmod HAT. It passes when each GPIO hears the pin the expected cabling puts there. The design and its
reader: [the pin-ID test](../designs/pmod-pin-id.md).

```{include} ../pin-id-coverage.inc
```

## The failing line

The summary's line for a cabling fault, and what the check's documentation says of it ([Common
failures](../../../verify/fpgas-verify.md#common-failures)):

> `fail`: `N/24 pins match expected wiring`: the Pmod HAT cabling differs from the board's expected map: the
> table above that line shows each wire, what was expected on it and what was heard. The line after it says how
> many of the cabling's signal wires the test covers: all 24 on a TT FPGA board.

The summary keeps only a failed test's last 8 output lines. To see the whole table, run the test on its own
with its output live. `fpgas-tt-fpga-debug program` and `test` do not ask the board what it is, so they need
`--variant tt-fpga` said out loud ([Which Tiny Tapeout board it
is](../../../verify/fpgas-verify.md#which-tiny-tapeout-board-it-is), another page, not in this set).

```{include} ../serial-port.inc
```

```console
$ sudo fpgas-tt-fpga-debug --variant tt-fpga test pin-id
```

The record gives this form for the `uart` test (`sudo fpgas-tt-fpga-debug --variant tt-fpga test uart`);
with `pin-id` it is not run by us.

## From a wire in the table to the cable

The test's table shows each wire, what was expected on it and what was heard (its columns are not shown
here: we hold no recorded output). Find the wire in the tables of [`ui_in` and
`uo_out`](../wiring/pins-ui-uo.md) or [`uio`](../wiring/pins-uio-uart.md), by its Raspberry Pi GPIO or its
iCE40 pin: the row there gives the Pmod HAT port and pin and the demo board header and pin, which is the wire
to look at. Which header goes to which port:

[![Which Pmod header of the demo board goes to which port of the Pmod HAT](../generated/tt-fpga-pmod-cables.png)](../generated/tt-fpga-pmod-cables.svg){.only-light}
[![Which Pmod header of the demo board goes to which port of the Pmod HAT](../generated/tt-fpga-pmod-cables-dark.png)](../generated/tt-fpga-pmod-cables-dark.svg){.only-dark}

What is recorded about kinds of fault:

- **Two ribbons swapped as a whole** is caught. For the JA and JB ribbons that is by their other five wires;
  for JA and JC swapped, the test's own unit test holds it to failing (source: the pin-mapping page and
  `test_identify_pmod_pins.py` of
  [fpgas.online-test-designs](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/docs/hardware/tt-fpga-pin-mapping.md)).
  Not tried by us on a board.
- **What `pin-id` cannot tell**: the JA wire and the JB wire of the same number (2, 3 or 4)
  swapped with each other. The HAT joins those two wires on one Pi pin, so the Pi hears the same two pin
  numbers either way. Every other miswiring of the three ribbons changes what some Pi pin hears.
- `pin-id` checks each Pmod pin in one direction only, FPGA to Pi.
- **A cable turned round** (pin 1 at the wrong end) puts 3.3 V on signal pins: [which cable goes
  where](../wiring/cables.md). What the test reports for it is not recorded.

## Other failing lines on this board

These are not cabling faults. What each means, in one line here; the whole explanation is under "Common
failures" on [Checking a board: fpgas-verify](../../../verify/fpgas-verify.md#common-failures), another page,
not in this set:

- `error`: `the board did not say which Tiny Tapeout board it is, so no test was run and nothing was loaded`:
  the demo board could not be asked what it is; the rest of the line says why (rpi-hwid not installed, its
  `main.py` changed, its SDK did not start). rpi-hwid: [verifying 1, step 3](verifying-1.md).
- `fail`: `a Raspberry Pi RP2 is on USB but is not running the Tiny Tapeout firmware`: the microcontroller
  is in its USB boot loader. Power-cycle the board.
- `error`: `… is not installed` (`mpremote`): install it ([verifying 1, step 3](verifying-1.md); on
  bookworm from backports).
- `fail`: `sdk fail: …`: the Tiny Tapeout SDK on the board is not a release known to work with what the
  board carries. The firmware is installed by whoever looks after the board; the check writes nothing to it.

## The loopback test

The Pmod loopback is a second test of the INPUT and OUTPUT cables, and is not part of the boot check: [the
Pmod loopback test](../designs/pmod-loopback.md).
