The serial pair is a **null-modem crossover**: the FPGA's transmitter (K2) lands
on the Pi's receiver (GPIO15 / RXD0) and the FPGA's receiver (J2) on the Pi's
transmitter (GPIO14 / TXD0). This is the Raspberry Pi header convention that
`/dev/ttyAMA0` uses, and the one the NeTV2 boards use
([NeTV2 primary UART](/boards/netv2/setup/wiring.md#primary-uart)).
