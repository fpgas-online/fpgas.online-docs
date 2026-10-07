# Arty A7: the GPIO loopback test

**You want to run the GPIO loopback test between an Arty and its Raspberry Pi.**

## GPIO Loopback Test

The loopback gateware computes `pmodb = ~pmoda` (per-bit inversion). The RPi
drives PMODA pins and reads the inverted result on PMODB pins. The loopback
pairs can be derived from the per-host PMOD cable routing tables ([PMOD cable
routing](cable-routing.md)).

Only five of the eight lanes can actually be loop-tested from the Pi. HAT JA
pins 2-4 and HAT JB pins 2-4 are the same three GPIO lines (the SPI0 bus), so
the Pi cannot drive an Arty PMODA pin and read the corresponding PMODB pin
independently on those three lanes — see
[the routing todo](cable-routing.md#unproven-lanes).

### Pre-test Requirements

The SPI kernel modules claim GPIO7-11, which carry HAT JA pin 1 (GPIO8) and HAT
JB pins 1-4 (GPIO7 and the shared GPIO9/10/11). Unloading them frees these GPIOs
for the loopback test.

```console
# Nothing else on the Pi may be using SPI0 -- this takes the bus away from it.
$ sudo rmmod spidev spi_bcm2835
```
