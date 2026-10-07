RPi GPIO7-11 are the SPI0 bus, and on the Pmod HAT they are JB pin 1 (GPIO7), JA pin 1 (GPIO8), and JA pins
2-4, which are also JB pins 2-4 (GPIO10, GPIO9, GPIO11): [`ui_in` and `uo_out`](../wiring/pins-ui-uo.md),
[`uio`](../wiring/pins-uio-uart.md). **Workaround:** unload `spidev` and `spi_bcm2835`
kernel modules before running PMOD tests.

```console
# Nothing else on the Pi may be using SPI0 -- this takes the bus away from it.
$ sudo rmmod spidev spi_bcm2835
```
