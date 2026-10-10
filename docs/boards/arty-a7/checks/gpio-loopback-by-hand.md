---
type: how-to
owner: documentation maintainers
reader: someone with an Arty A7 and a PMOD HAT who wants to test the cables
review: 2026-11-10
---

# How to run the Arty A7 GPIO loopback test by hand

**You have an Arty A7 cabled to a PMOD HAT and want to run the loopback test.**

The loopback gateware computes `pmodb = ~pmoda`, a per-bit inversion. The Raspberry Pi drives the PMODA pins and reads the inverted result on the PMODB pins.

Only five of the eight lanes can be loop-tested from the Pi. HAT JA pins 2-4 and HAT JB pins 2-4 are the same three GPIO lines (the SPI0 bus). On those three lanes the Pi cannot drive an Arty PMODA pin and read the matching PMODB pin independently.

This procedure is waiting for its run: [test-designs issue #248](https://github.com/fpgas-online/fpgas.online-test-designs/issues/248).

## What you need

- The three PMOD ribbon cables, HAT JA to Arty JA, JB to JB and JC to JC ([Arty A7 wiring to a Raspberry Pi](../setup/wiring.md#pmod-cables)).
- `fpgas-arty-debug` on the Raspberry Pi, from the `fpgas-online-arty-debug` package ([How to install the Arty A7 packages](../setup/packages.md)).
- Nothing else on the Pi using SPI0: the first step takes the bus away from it.

## Steps

1. On the Raspberry Pi, unload the SPI kernel modules with `sudo rmmod spidev spi_bcm2835`, which frees GPIO7-11.
2. On the Raspberry Pi, run the test with `sudo fpgas-arty-debug test pmod`, which loads the loopback design and runs its host script.

```console
$ sudo rmmod spidev spi_bcm2835
$ sudo fpgas-arty-debug test pmod
```

The SPI kernel modules claim GPIO7-11. Those carry HAT JA pin 1 (GPIO8) and HAT JB pins 1-4 (GPIO7 and the shared GPIO9, GPIO10 and GPIO11).

## Check

- The test passes when its host script exits 0, so `echo $?` prints `0`.

## If it fails

- A lane reads back wrong. Compare the lane with the routing tables on [Arty A7 wiring to a Raspberry Pi](../setup/wiring.md#pmod-cables). Arty JC pins 1 and 2 read in the reverse of the documented order there.

## Next

- [How to run the Arty A7 UART test by hand](uart-by-hand.md)
- [The pin-id design](../../pin-id.md)
