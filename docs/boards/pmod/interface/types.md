# PMOD interface: the standard interface types

**You want the pinout of a standard PMOD interface type: GPIO, SPI, UART or H-bridge.**

## Standard PMOD Interface Types

Digilent defines 9 interface types that assign specific protocols to the signal pins. All types share pins 5/6 (and 11/12 for double width) as GND/VCC.

### Type 1 — GPIO (6-pin)

General-purpose I/O. All 4 signal pins are bidirectional.

| Pin | Signal | Direction |
| --- | ------ | --------- |
| 1   | IO1    | In/Out    |
| 2   | IO2    | In/Out    |
| 3   | IO3    | In/Out    |
| 4   | IO4    | In/Out    |
| 5   | GND    | —         |
| 6   | VCC    | —         |

### Type 1A — Expanded GPIO (12-pin)

Double-width GPIO with 8 bidirectional I/O pins in two banks (A and B).

| Pin | Signal | Direction | Pin | Signal | Direction |
| --- | ------ | --------- | --- | ------ | --------- |
| 1   | IOA1   | In/Out    | 7   | IOB1   | In/Out    |
| 2   | IOA2   | In/Out    | 8   | IOB2   | In/Out    |
| 3   | IOA3   | In/Out    | 9   | IOB3   | In/Out    |
| 4   | IOA4   | In/Out    | 10  | IOB4   | In/Out    |
| 5   | GND    | —         | 11  | GND    | —         |
| 6   | VCC    | —         | 12  | VCC    | —         |

### Type 2 — SPI (6-pin)

SPI bus interface. Direction is from the host's perspective (host is SPI master).

| Pin | Signal | Direction | Description                           |
| --- | ------ | --------- | ------------------------------------- |
| 1   | SS     | Out       | Slave Select (active low)             |
| 2   | MOSI   | Out       | Master Out Slave In (data to slave)   |
| 3   | MISO   | In        | Master In Slave Out (data from slave) |
| 4   | SCK    | Out       | Serial Clock (from master)            |
| 5   | GND    | —         |                                       |
| 6   | VCC    | —         |                                       |

### Type 2A — Expanded SPI (12-pin)

SPI with additional control signals on the bottom row.

| Pin | Signal | Direction | Pin | Signal | Direction | Description                    |
| --- | ------ | --------- | --- | ------ | --------- | ------------------------------ |
| 1   | SS     | Out       | 7   | INT    | In        | Interrupt (peripheral → host)  |
| 2   | MOSI   | Out       | 8   | RESET  | Out       | Reset (host → peripheral)      |
| 3   | MISO   | In        | 9   | N/S    | N/S       | Module-specific or unconnected |
| 4   | SCK    | Out       | 10  | N/S    | N/S       | Module-specific or unconnected |
| 5   | GND    | —         | 11  | GND    | —         |                                |
| 6   | VCC    | —         | 12  | VCC    | —         |                                |

### Type 3 — UART (6-pin)

UART with hardware flow control. Direction is from the **peripheral's** perspective (peripheral sends CTS/RXD, receives RTS/TXD).

| Pin | Signal | Direction | Description                               |
| --- | ------ | --------- | ----------------------------------------- |
| 1   | CTS    | Out       | Permission for peripheral to send to host |
| 2   | RTS    | In        | Request from peripheral to send to host   |
| 3   | RXD    | In        | Data from peripheral to host              |
| 4   | TXD    | Out       | Data from host to peripheral              |
| 5   | GND    | —         |                                           |
| 6   | VCC    | —         |                                           |

Note: Type 3 is defined from a different perspective than Type 4. Type 3 "Out" means the host drives the signal.

### Type 4 — UART (6-pin)

UART with hardware flow control. Direction is from the **device's** perspective (device asserts CTS when ready to receive, asserts RTS when ready to send).

| Pin | Signal | Direction | Description                       |
| --- | ------ | --------- | --------------------------------- |
| 1   | CTS    | In        | Device transmits only when active |
| 2   | TXD    | Out       | Data from peripheral to host      |
| 3   | RXD    | In        | Data from host to peripheral      |
| 4   | RTS    | Out       | Device is ready to receive data   |
| 5   | GND    | —         |                                   |
| 6   | VCC    | —         |                                   |

### Type 4A — Expanded UART (12-pin)

UART (Type 4 pinout) with additional control signals on the bottom row.

| Pin | Signal | Direction | Pin | Signal | Direction | Description                    |
| --- | ------ | --------- | --- | ------ | --------- | ------------------------------ |
| 1   | CTS    | In        | 7   | INT    | In        | Interrupt (peripheral → host)  |
| 2   | TXD    | Out       | 8   | RESET  | Out       | Reset (host → peripheral)      |
| 3   | RXD    | In        | 9   | N/S    | N/S       | Module-specific or unconnected |
| 4   | RTS    | Out       | 10  | N/S    | N/S       | Module-specific or unconnected |
| 5   | GND    | —         | 11  | GND    | —         |                                |
| 6   | VCC    | —         | 12  | VCC    | —         |                                |

### Type 5 — H-Bridge (6-pin)

Single H-bridge motor driver interface.

| Pin | Signal | Direction | Description                |
| --- | ------ | --------- | -------------------------- |
| 1   | DIR    | Out       | Motor direction            |
| 2   | EN     | Out       | Motor enable (active high) |
| 3   | SA     | In        | Feedback sense A           |
| 4   | SB     | In        | Feedback sense B           |
| 5   | GND    | —         |                            |
| 6   | VCC    | —         |                            |

### Type 6 — Dual H-Bridge (6-pin)

Two H-bridge motor/phase drivers on a single 6-pin connector (no feedback).

| Pin | Signal | Direction | Description                           |
| --- | ------ | --------- | ------------------------------------- |
| 1   | DIR1   | Out       | Motor/Phase 1 direction (active high) |
| 2   | EN1    | Out       | Motor/Phase 1 enable                  |
| 3   | DIR2   | Out       | Motor/Phase 2 direction (active high) |
| 4   | EN2    | Out       | Motor/Phase 2 enable                  |
| 5   | GND    | —         |                                       |
| 6   | VCC    | —         |                                       |

See also: [the connector's pin numbering](connectors.md) these pinouts use; [all the types in one table](i2c-summary.md#summary-table).
