:::{warning}
**Never drive a Pi GPIO against an FPGA output.** With the pin-ID design loaded, every P2 ball is an FPGA *output*, J2 included. Setting GPIO14 to `a4` (TXD0) or `op` while pin-ID runs is then output against output on the J2 wire, and it crashes the Pi. Probe with `pinctrl set 14 ip pn` (input, no pull). Restore `pinctrl set 14 a4` only once a design that treats J2 as an input is loaded.
:::
