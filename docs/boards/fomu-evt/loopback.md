# Fomu EVT: the PMOD / GPIO loopback test

**You want to run the PMOD / GPIO loopback test between a Fomu and its Raspberry Pi.**

## PMOD / GPIO loopback

The Fomu EVT has two PMOD-style connectors defined in the platform file (see
[PMOD Connectors](peripherals.md#pmod-connectors)). The loopback gateware uses `pmoda_n` as
input and `pmodb_n` as output.

### pmoda_n (loopback input)

| Index | iCE40 Pin |
| ----- | --------- |
| 0     | 28        |
| 1     | 27        |
| 2     | 26        |
| 3     | 23        |

### pmodb_n (loopback output)

| Index | iCE40 Pin |
| ----- | --------- |
| 0     | 48        |
| 1     | 47        |
| 2     | 46        |
| 3     | 45        |

Note: `pmodb_n` shares pins with `touch_pins`, the capacitive touch pads on the
Fomu.

### Confirmed loopback pair

Only 1 of the 4 loopback pairs connects to a Pi GPIO through the GPIO header:

| Drive RPi GPIO | Read RPi GPIO | Status    |
| -------------- | ------------- | --------- |
| GPIO27         | GPIO9         | Confirmed |

:::{todo}
Determine which iCE40 pins GPIO27 and GPIO9 map to through the GPIO header. The
Fomu-to-RPi header pin mapping needs physical inspection.

The method is the
[pin-ID design](../pin-id.md), which names each FPGA pin on the wire, so a scan
from the Pi gives the mapping without opening anything up.
:::

### Loopback pre-test requirements

```console
# GPIO9 is SPI0_MISO -- nothing else on the Pi may be using SPI0, this takes
# the bus away from the kernel driver.
$ sudo rmmod spidev spi_bcm2835
```

The Fomu GPIO output has slow propagation, roughly 5 ms of settle time, so the
test uses a poll-until-stable loop rather than a single read.
