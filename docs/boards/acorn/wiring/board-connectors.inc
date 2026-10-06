## Board connectors

The Acorn has two 6-pin Molex Pico-EZmate connectors. Both are on the
**underside** of the card (the face without the FPGA and heatsink), side by side
along one long edge at the **fan end**, away from the M.2 edge connector. The
silkscreen beside them reads `I/O` / `P2` and `JTAG` / `P1`; P2 is the one nearer
the end of the card.

Pin 1 of each connector is the end **nearest the M.2 edge connector**, and it is
GND on both:

```{include} ../generated/acorn-connectors.md
```

Sources: the "Pico-EZmate connectors pinout on Acorn, Nite/LiteFury" legend on
the [LiteX Acorn CLE-215
wiki](https://github.com/enjoy-digital/litex/wiki/Use-LiteX-on-the-Acorn-CLE-215),
and the silkscreen of RHS Research's 14-pin JTAG adapter (GND, TCK, TDO, TMS,
TDI, VCC). The wiki legend names K2 and J2 from the host's side ("UART RX
(K2)"): K2 is the FPGA's transmitter. The JTAG order is confirmed in service by
pi20 at PS1, whose cable was built from that legend; it has not been checked
with a meter on a bare card.

Cut one Pico-EZmate cable (plug at each end) in half to get the P1 and P2
cables, and strip about 3 mm from each wire. **All six wires are black**, so
there is no colour to go by: count positions from pin 1, and buzz each wire
through before crimping and again once it is in its housing.

:::{warning}
**The VCC (3.3 V) wire of both P1 and P2 must never be connected to the host.**
Cut it back and insulate it. 3.3 V from the Acorn into the header can damage the
Pi.
:::
