---
type: how-to
owner: documentation maintainers
reader: someone about to run the Fomu EVT's PMOD loopback test on its Raspberry Pi
review: 2026-11-10
---

# How to free the Pi's SPI0 bus for the Fomu PMOD loopback test

**You want the Fomu EVT's loopback test to read GPIO9, which SPI0 drivers hold.**

The loopback wires are on [Fomu EVT wiring to a Raspberry Pi](../setup/wiring.md#confirmed-loopback-pair).

This procedure is waiting for its run: [test-designs issue #251](https://github.com/fpgas-online/fpgas.online-test-designs/issues/251). The pair it reads is contested: [test-designs issue #202](https://github.com/fpgas-online/fpgas.online-test-designs/issues/202) says the loopback cannot pass on the EVT as wired.

## What you need

- A Raspberry Pi with the Fomu EVT on its GPIO header, loaded with the loopback gateware.
- `sudo` rights on the Pi.

## Steps

1. On the Pi, take SPI0 away from the kernel driver, because GPIO9 is SPI0_MISO and nothing else on the Pi may be using SPI0.

```console
$ sudo rmmod spidev spi_bcm2835
```

2. Run the loopback test, the check's `pmod` test, which drives GPIO27 and reads GPIO9. It polls until the value is stable, because the Fomu's output settles in roughly 5 ms.

## Check

- `rmmod` returns without an error.
- The read of GPIO9 follows what is driven on GPIO27.

## If it fails

| What you see | Likely cause | Fix |
|---|---|---|
| The test cannot read GPIO9 | The SPI0 drivers `spidev` and `spi_bcm2835` are still loaded | Run step 1 |
| GPIO9 does not follow GPIO27 at once | The Fomu GPIO output has slow propagation, roughly 5 ms | Poll until the value is stable instead of reading once |

## Next

- [Fomu EVT test faults](../troubleshooting/test-faults.md)
- [Fomu EVT checks](index.md)
- [fpgas-verify: what an Arty, NeTV2, Fomu or TT FPGA check tests](../../../verify/tests.md#what-each-boards-check-tests)
