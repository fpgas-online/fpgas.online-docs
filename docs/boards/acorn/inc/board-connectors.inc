## Board connectors

The Acorn has two 6-pin Molex Pico-EZmate connectors. Both are on the **underside** of the card (the face without the FPGA and heatsink). They sit side by side along one long edge at the **fan end**, away from the M.2 edge connector. The silkscreen beside them reads `I/O` / `P2` and `JTAG` / `P1`, and P2 is the one nearer the end of the card.

Pin 1 of each connector is the end **nearest the M.2 edge connector**, and it is GND on both. Both cables have six black wires, so a wire is told by its position from pin 1.

Each row of the table is one pin, with its signal on P2 and on P1, named after the "Pico-EZmate connectors pinout on Acorn, Nite/LiteFury" legend of the [LiteX Acorn CLE-215 wiki](https://github.com/enjoy-digital/litex/wiki/Use-LiteX-on-the-Acorn-CLE-215). The legend names K2 and J2 from the host's side. The table names them from the FPGA's side, so K2 is the FPGA's transmitter.

```{include} /boards/acorn/generated/acorn-connectors.md
```

:::{warning}
**The VCC (3.3 V) wire of both P1 and P2 must never be connected to the host.** Cut it back and insulate it. 3.3 V from the Acorn into the header can damage the Pi.
:::
