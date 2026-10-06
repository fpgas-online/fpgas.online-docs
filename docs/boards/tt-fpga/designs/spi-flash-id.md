# Tiny Tapeout FPGA board test: SPI flash ID (does not apply)

**You have a Tiny Tapeout FPGA demo board and have read, on an earlier version of these pages or in an old
result, that it has an SPI flash and an SPI flash ID test. It has neither.**

## What the record says

```{include} ../generated/tt-fpga-pins-other.md
:start-after: "### Loading the FPGA: its configuration pins"
:end-before: "The pins of the microcontroller"
```

Source: the breakout's published design
([TinyTapeout/breakout-pcb, `ASIC-simulator/ttdbv3-fpga-ICE40UP5k`](https://github.com/TinyTapeout/breakout-pcb/tree/6e3725f7fc5707d0cbe7632c39b867da740d10d7/ASIC-simulator/ttdbv3-fpga-ICE40UP5k)),
checked there on 4 October 2026 by the fpgas.online-test-designs repository; not measured by us on a board.
So there is no SPI flash ID test for this board
([test-designs issue #52](https://github.com/fpgas-online/fpgas.online-test-designs/issues/52)), and the boot
check runs none: [verifying 1](../building/verifying-1.md).

## What these pages said before

Until 6 October 2026 this board's page said the breakout "also has SPI flash (CS_N=pin 16, CLK=pin 15,
MOSI=pin 14, MISO=pin 17) for persistent bitstream storage, used by the SPI Flash ID test", and listed an
"SPI Flash ID" test that read a JEDEC ID "from on-board flash". Those four pins are the configuration pins in
the table above. That text has been removed, not moved.

## Where the old test still shows

- The results table of 2 October 2026 on [Checking a board:
  fpgas-verify](../../../verify/fpgas-verify.md#current-results) has `spiflash=fail` on each of the three
  Tiny Tapeout FPGA boards read that day. That is the test that was then removed, failing on a board with no
  flash to answer; it is not a fault of those boards.
- [Verifying a deployment](../../../setup/verification.md#tt-fpga-programming) still speaks of "the UART and
  SPI-flash designs" for this board when it describes the older runner.
