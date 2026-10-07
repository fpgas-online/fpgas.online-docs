# Arty A7: PMOD connectors

**You want the Arty's PMOD pin numbering and FPGA pins, and how the test infrastructure uses them.**

## PMOD Connectors

The Arty A7 has four 12-pin PMOD connectors (JA through JD). Each connector
provides 8 signal pins plus power (VCC) and ground (GND). All PMOD I/O use
LVCMOS33 (3.3V) standard.

### PMOD Pin Numbering

Standard 12-pin PMOD connector layout:

```text
           ┌─────────────────────────────────────┐
Top row:   │ Pin1  Pin2  Pin3  Pin4  GND   VCC   │
Bottom row:│ Pin5  Pin6  Pin7  Pin8  GND   VCC   │
           └─────────────────────────────────────┘
```

Pins 1-4 are the top row, pins 5-8 are the bottom row (numbered 0-7 in LiteX,
where 0-3 = top, 4-7 = bottom). The physical connector numbers the bottom row
7-10 (pins 5 and 6 of each row are GND and VCC), which is the numbering used by
the per-connector tables under
[PMOD Connectors (FPGA Side)](wiring.md#pmod-connectors-fpga-side) and by the
[PMOD interface specification](../pmod/index.md).

### PMOD FPGA Pin Assignments

| LiteX Index | PMODA (JA) | PMODB (JB) | PMODC (JC) | PMODD (JD) |
|-------------|-----------|-----------|-----------|-----------|
| 0 (top pin 1) | G13 | E15 | U12 | D4 |
| 1 (top pin 2) | B11 | E16 | V12 | D3 |
| 2 (top pin 3) | A11 | D15 | V10 | F4 |
| 3 (top pin 4) | D12 | C15 | V11 | F3 |
| 4 (bottom pin 7) | D13 | J17 | U14 | E2 |
| 5 (bottom pin 8) | B18 | J18 | V14 | D2 |
| 6 (bottom pin 9) | A18 | K15 | T13 | H2 |
| 7 (bottom pin 10) | K16 | J15 | U13 | G2 |

Source: [digilent_arty.py `_connectors`](https://github.com/litex-hub/litex-boards/blob/master/litex_boards/platforms/digilent_arty.py)

### PMOD Usage in Test Infrastructure

In the fpgas.online setup, the Arty A7's PMOD connectors can be connected to a
Raspberry Pi via a Digilent [PMOD HAT adapter](../pmod/rpi-hat.md). This enables
PMOD loopback testing where the RPi drives signals through the PMOD HAT to the
Arty's PMOD connectors and verifies correct signal propagation. The measured
cable routing is in
[PMOD Cable Routing: HAT ↔ Arty](cable-routing.md#pmod-cable-routing-hat--arty).
