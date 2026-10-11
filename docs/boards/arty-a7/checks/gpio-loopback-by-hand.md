---
type: how-to
owner: documentation maintainers
reader: someone with an Arty A7 and a PMOD HAT who wants to test the cables
review: 2026-11-10
---

# How to run the Arty A7 GPIO loopback test by hand

**You have an Arty A7 cabled to a PMOD HAT and want to run the loopback test.**

The loopback gateware computes `pmodb = ~pmoda`, a per-bit inversion. The Raspberry Pi drives the PMODA pins and reads the inverted result on the PMODB pins.

The test checks six pin pairs, not every lane: `BOARD_CONFIGS["arty"]` in the test's [host script](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/designs/pmod-loopback/host/test_pmod_loopback.py) lists them. HAT JA pins 2-4 and HAT JB pins 2-4 are the same three GPIO lines (the SPI0 bus). On those three lanes the Pi cannot drive an Arty PMODA pin and read the matching PMODB pin independently.

This procedure is waiting for its run: [test-designs issue #248](https://github.com/fpgas-online/fpgas.online-test-designs/issues/248).

## What you need

- The three PMOD ribbon cables, HAT JA to Arty JA, JB to JB and JC to JC ([Arty A7 wiring to a Raspberry Pi](../setup/wiring.md#pmod-cables)).
- The fpgas.online apt repository on the Raspberry Pi: [How to install the Arty A7 packages](../setup/packages.md). Step 1 installs the debug tool, which `fpgas-online-arty` does not bring.
- Nothing else on the Pi using SPI0: the test takes the bus away from it.

## Steps

1. On the Raspberry Pi, install the debug tool, `fpgas-arty-debug`.

   ```console
   $ sudo apt install fpgas-online-arty-debug
   ```

2. On the Raspberry Pi, run the test. It unloads the SPI kernel modules `spidev` and `spi_bcm2835` itself, which frees GPIO7-11, then loads the loopback design and runs its host script. GPIO7-11 carry HAT JA pin 1 (GPIO8) and HAT JB pins 1-4 (GPIO7 and the shared GPIO9, GPIO10 and GPIO11).

   ```console
   $ sudo fpgas-arty-debug test pmod
   ```

## Check

- The test passes when its host script exits 0, so `echo $?` prints `0`.

## If it fails

- A lane reads back wrong. Compare the lane with the routing tables on [Arty A7 wiring to a Raspberry Pi](../setup/wiring.md#pmod-cables).

## Next

- [How to run the Arty A7 UART test by hand](uart-by-hand.md)
- [The pin-id design](../../pin-id.md)
