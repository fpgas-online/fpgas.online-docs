Each row of the table is one wire of the serial pair, a null-modem crossover: the end that transmits lands on the receiver of the other end.

| Wire | Transmits | Lands on the host's |
|------|-----------|---------------------|
| K2 | the FPGA | receiver, GPIO15 / RXD0 |
| J2 | the host | transmitter, GPIO14 / TXD0 |
