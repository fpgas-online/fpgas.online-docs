---
type: reference
owner: documentation maintainers
reader: someone whose Fomu EVT does not answer the UART or the PMOD loopback test
review: 2026-11-10
---

# Fomu EVT test faults

**Your Fomu EVT is loaded, but its UART or loopback test fails.**

The Pi's side of the UART test is on [How to stop the serial login console before a Fomu UART test](../checks/stop-serial-console.md). The loopback test is on [How to free the Pi's SPI0 bus for the Fomu PMOD loopback test](../checks/loopback-spi-bus.md).

Each row gives what you see, the likely cause and the fix.

| Problem | Likely cause | Fix |
|---------|--------------|-----|
| `no GPIO UART on this host` | `/dev/serial0` does not exist on this Pi | Run the UART test on a Pi that has the GPIO UART |
| The serial data never reaches the test | `serial-getty` was stopped but not masked, so it came back and consumes the data | Mask the unit, as in the serial console how-to |
| The loopback test cannot read GPIO9 | The SPI0 drivers `spidev` and `spi_bcm2835` are loaded | `sudo rmmod spidev spi_bcm2835` |
| The loopback read is wrong on the first look | The Fomu GPIO output settles in roughly 5 ms | Poll until the value is stable |
