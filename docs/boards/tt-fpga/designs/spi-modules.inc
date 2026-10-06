RPi GPIO7-11 overlap with the SPI0 bus and conflict with PMOD HAT pins
(JA/JB pins 2-4). **Workaround:** unload `spidev` and `spi_bcm2835`
kernel modules before running PMOD tests.

```console
# Nothing else on the Pi may be using SPI0 -- this takes the bus away from it.
$ sudo rmmod spidev spi_bcm2835
```
