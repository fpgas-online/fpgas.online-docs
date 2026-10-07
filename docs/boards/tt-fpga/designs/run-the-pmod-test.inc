**No command line for the wrapper `tt_pmod_wrapper.py` is recorded on these pages**, and it has not been run
by us in a form we can show. The check's own debug tool runs one test with its output live. Its form is
`fpgas-tt-fpga-debug [options] test TEST` (the debug tools' usage on [Checking a board:
fpgas-verify](../../../verify/fpgas-verify.md#--help)), and for this board `program` and `test` need
`--variant tt-fpga` said out loud ([Which Tiny Tapeout board it
is](../../../verify/fpgas-verify.md#which-tiny-tapeout-board-it-is)). Not run by us in this form.

What a run needs, in this order, before the command:

1. **The serial port free.** The `fpgas-tt` daemon is stopped (the warning below).
2. **SPI0 free.** The SPI kernel modules unloaded (the command below).
3. **The microcontroller off the signals.** The design loaded with `--gpio-release`. The check's table of
   tests gives this test both: `rmmod spidev spi_bcm2835` as its step before, and `--gpio-release` for its
   load (`PMOD_PRE` and `program_args` in `boards/tt_fpga.py` of fpgas.online-test-designs). Whether the
   debug tool runs them as the check does is not verified by us.

```{include} ../serial-port.inc
```

```{include} spi-modules.inc
```
