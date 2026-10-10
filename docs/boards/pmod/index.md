---
type: reference
owner: documentation maintainers
reader: someone looking up a PMOD connector type, its pins or its electrical figures
review: 2026-11-10
---

# PMOD interface

**The PMOD (Peripheral Module) interface is Digilent's standard for connecting peripheral modules to FPGA and microcontroller host boards**. This page is the reference for the standard PMOD connector types, their pins and the extended I2C interface. It follows the [Digilent PMOD Interface Specification 1.3.1](https://digilent.com/reference/pmod/pmod-interface-specification) and does not cover the pins of any one board.

## Physical Connectors

PMOD connectors use standard 100 mil (2.54 mm) pitch pin headers in two widths.

### Single Width (6-pin, 1×6)

A single width connector has 4 signal pins, 1 GND and 1 VCC. The Function column names what each pin carries.

```text
Host side (looking at board edge):

  ┌───┬───┬───┬───┬───┬───┐
  │ 1 │ 2 │ 3 │ 4 │ 5 │ 6 │
  └───┴───┴───┴───┴───┴───┘
   IO  IO  IO  IO GND VCC
        ◄── 0.40" ──►
   ◄0.15"►  (edge setback)
```

| Pin | Function   |
| --- | ---------- |
| 1   | Signal I/O |
| 2   | Signal I/O |
| 3   | Signal I/O |
| 4   | Signal I/O |
| 5   | GND        |
| 6   | VCC        |

### Double Width (12-pin, 2×6)

A double width connector has 8 signal pins, 2 GND and 2 VCC, and its top row (pins 1-6) matches the single width pinout. The two Pin and Function column pairs are the top and bottom rows.

```text
Host side (looking at board edge):

  ┌───┬───┬───┬───┬───┬───┐
  │ 1 │ 2 │ 3 │ 4 │ 5 │ 6 │  (top row)
  ├───┼───┼───┼───┼───┼───┤
  │ 7 │ 8 │ 9 │10 │11 │12 │  (bottom row)
  └───┴───┴───┴───┴───┴───┘
   IO  IO  IO  IO GND VCC
        ◄── 0.45" ──►
   ◄0.20"►  (edge setback)
```

| Pin | Function   | Pin | Function   |
| --- | ---------- | --- | ---------- |
| 1   | Signal I/O | 7   | Signal I/O |
| 2   | Signal I/O | 8   | Signal I/O |
| 3   | Signal I/O | 9   | Signal I/O |
| 4   | Signal I/O | 10  | Signal I/O |
| 5   | GND        | 11  | GND        |
| 6   | VCC        | 12  | VCC        |

### Electrical Characteristics

The Parameter column names a property of the connector and the Value column gives it.

| Parameter           | Value                       |
| ------------------- | --------------------------- |
| VCC voltage         | 3.3V (standard)             |
| Max current per VCC | 100 mA                      |
| I/O standard        | LVCMOS33 (matched to VCC)   |
| Pin pitch           | 100 mil (2.54 mm)           |
| Connector type      | Standard 100 mil pin header |

## Standard PMOD Interface Types

Digilent defines 9 interface types that assign protocols to the signal pins. All types share pins 5 and 6 (and 11 and 12 for double width) as GND and VCC. In each table Signal is the pin's name and Direction is the pin's direction as the type below defines it.

### Type 1 — GPIO (6-pin)

General-purpose I/O: all 4 signal pins are bidirectional.

| Pin | Signal | Direction |
| --- | ------ | --------- |
| 1   | IO1    | In/Out    |
| 2   | IO2    | In/Out    |
| 3   | IO3    | In/Out    |
| 4   | IO4    | In/Out    |
| 5   | GND    | —         |
| 6   | VCC    | —         |

### Type 1A — Expanded GPIO (12-pin)

Double-width GPIO: 8 bidirectional I/O pins in two banks, A and B.

| Pin | Signal | Direction | Pin | Signal | Direction |
| --- | ------ | --------- | --- | ------ | --------- |
| 1   | IOA1   | In/Out    | 7   | IOB1   | In/Out    |
| 2   | IOA2   | In/Out    | 8   | IOB2   | In/Out    |
| 3   | IOA3   | In/Out    | 9   | IOB3   | In/Out    |
| 4   | IOA4   | In/Out    | 10  | IOB4   | In/Out    |
| 5   | GND    | —         | 11  | GND    | —         |
| 6   | VCC    | —         | 12  | VCC    | —         |

### Type 2 — SPI (6-pin)

SPI bus interface. Direction is from the host's perspective, and the host is the SPI master. Description gives the signal's role.

| Pin | Signal | Direction | Description                           |
| --- | ------ | --------- | ------------------------------------- |
| 1   | SS     | Out       | Slave Select (active low)             |
| 2   | MOSI   | Out       | Master Out Slave In (data to slave)   |
| 3   | MISO   | In        | Master In Slave Out (data from slave) |
| 4   | SCK    | Out       | Serial Clock (from master)            |
| 5   | GND    | —         |                                       |
| 6   | VCC    | —         |                                       |

### Type 2A — Expanded SPI (12-pin)

SPI with additional control signals on the bottom row. Direction and Description follow Type 2, with N/S for not specified.

| Pin | Signal | Direction | Pin | Signal | Direction | Description                    |
| --- | ------ | --------- | --- | ------ | --------- | ------------------------------ |
| 1   | SS     | Out       | 7   | INT    | In        | Interrupt (peripheral → host)  |
| 2   | MOSI   | Out       | 8   | RESET  | Out       | Reset (host → peripheral)      |
| 3   | MISO   | In        | 9   | N/S    | N/S       | Module-specific or unconnected |
| 4   | SCK    | Out       | 10  | N/S    | N/S       | Module-specific or unconnected |
| 5   | GND    | —         | 11  | GND    | —         |                                |
| 6   | VCC    | —         | 12  | VCC    | —         |                                |

### Type 3 — UART (6-pin)

UART with hardware flow control. Direction is from the **peripheral's** perspective: the peripheral sends CTS and RXD, and receives RTS and TXD. Out therefore means the host drives the signal, which differs from Type 4.

| Pin | Signal | Direction | Description                               |
| --- | ------ | --------- | ----------------------------------------- |
| 1   | CTS    | Out       | Permission for peripheral to send to host |
| 2   | RTS    | In        | Request from peripheral to send to host   |
| 3   | RXD    | In        | Data from peripheral to host              |
| 4   | TXD    | Out       | Data from host to peripheral              |
| 5   | GND    | —         |                                           |
| 6   | VCC    | —         |                                           |

### Type 4 — UART (6-pin)

UART with hardware flow control. Direction is from the **device's** perspective: the device asserts CTS when ready to receive and RTS when ready to send.

| Pin | Signal | Direction | Description                       |
| --- | ------ | --------- | --------------------------------- |
| 1   | CTS    | In        | Device transmits only when active |
| 2   | TXD    | Out       | Data from peripheral to host      |
| 3   | RXD    | In        | Data from host to peripheral      |
| 4   | RTS    | Out       | Device is ready to receive data   |
| 5   | GND    | —         |                                   |
| 6   | VCC    | —         |                                   |

### Type 4A — Expanded UART (12-pin)

UART (Type 4 pinout) with additional control signals on the bottom row. Direction and Description follow Type 4, with N/S for not specified.

| Pin | Signal | Direction | Pin | Signal | Direction | Description                    |
| --- | ------ | --------- | --- | ------ | --------- | ------------------------------ |
| 1   | CTS    | In        | 7   | INT    | In        | Interrupt (peripheral → host)  |
| 2   | TXD    | Out       | 8   | RESET  | Out       | Reset (host → peripheral)      |
| 3   | RXD    | In        | 9   | N/S    | N/S       | Module-specific or unconnected |
| 4   | RTS    | Out       | 10  | N/S    | N/S       | Module-specific or unconnected |
| 5   | GND    | —         | 11  | GND    | —         |                                |
| 6   | VCC    | —         | 12  | VCC    | —         |                                |

### Type 5 — H-Bridge (6-pin)

Single H-bridge motor driver interface. Description gives the signal's role.

| Pin | Signal | Direction | Description                |
| --- | ------ | --------- | -------------------------- |
| 1   | DIR    | Out       | Motor direction            |
| 2   | EN     | Out       | Motor enable (active high) |
| 3   | SA     | In        | Feedback sense A           |
| 4   | SB     | In        | Feedback sense B           |
| 5   | GND    | —         |                            |
| 6   | VCC    | —         |                            |

### Type 6 — Dual H-Bridge (6-pin)

Two H-bridge motor or phase drivers on a single 6-pin connector, with no feedback. Description gives the signal's role.

| Pin | Signal | Direction | Description                           |
| --- | ------ | --------- | ------------------------------------- |
| 1   | DIR1   | Out       | Motor/Phase 1 direction (active high) |
| 2   | EN1    | Out       | Motor/Phase 1 enable                  |
| 3   | DIR2   | Out       | Motor/Phase 2 direction (active high) |
| 4   | EN2    | Out       | Motor/Phase 2 enable                  |
| 5   | GND    | —         |                                       |
| 6   | VCC    | —         |                                       |

## Extended Interface: I2C (8-pin)

The I2C PMOD interface is an extension that the standard Digilent PMOD specification does not define, listed in the [High Speed PMOD Spreadsheet](https://docs.google.com/spreadsheets/d/1D-GboyrP57VVpejQzEm0P1WEORo1LAIt92hk1bZGEoo/edit?gid=0#gid=0). It uses an 8-pin connector with each signal on two pins. The pairing lowers impedance, which suits 400 kHz Fast Mode and 1 MHz Fast Mode Plus.

```text
  ┌───┬───┬───┬───┬───┬───┬───┬───┐
  │ 1 │ 2 │ 3 │ 4 │ 5 │ 6 │ 7 │ 8 │
  └───┴───┴───┴───┴───┴───┴───┴───┘
  SCL SCL SDA SDA GND GND VCC VCC
```

| Pin | Signal | Pin | Signal |
| --- | ------ | --- | ------ |
| 1   | SCL    | 2   | SCL    |
| 3   | SDA    | 4   | SDA    |
| 5   | GND    | 6   | GND    |
| 7   | VCC    | 8   | VCC    |

## Summary Table

Width is single (6-pin) or double (12-pin), Pins is the pin count and Protocol is what the signal pins carry.

| Type | Name           | Width  | Pins | Protocol          |
| ---- | -------------- | ------ | ---- | ----------------- |
| 1    | GPIO           | Single | 6    | General I/O       |
| 1A   | Expanded GPIO  | Double | 12   | General I/O (×8)  |
| 2    | SPI            | Single | 6    | SPI bus           |
| 2A   | Expanded SPI   | Double | 12   | SPI + INT/RESET   |
| 3    | UART           | Single | 6    | UART + flow ctrl  |
| 4    | UART           | Single | 6    | UART + flow ctrl  |
| 4A   | Expanded UART  | Double | 12   | UART + INT/RESET  |
| 5    | H-Bridge       | Single | 6    | Motor driver      |
| 6    | Dual H-Bridge  | Single | 6    | Dual motor driver |
| —    | I2C (extended) | Custom | 8    | I2C bus           |

## References

- Digilent PMOD Interface Specification 1.3.1: <https://digilent.com/reference/pmod/pmod-interface-specification>
- Digilent PMOD product listing: <https://digilent.com/reference/pmod/start>
- High Speed PMOD Spreadsheet: <https://docs.google.com/spreadsheets/d/1D-GboyrP57VVpejQzEm0P1WEORo1LAIt92hk1bZGEoo/edit?gid=0#gid=0>
- Digilent PMOD HAT Adapter (for RPi): [Raspberry Pi PMOD HAT](rpi-hat.md)

## Board-specific pinouts

How the PMOD signals map onto the Raspberry Pi HAT and onto Tiny Tapeout demo boards:

- [Raspberry Pi PMOD HAT](rpi-hat.md): the Raspberry Pi GPIOs behind each PMOD pin of the HAT.
- [Tiny Tapeout PMOD layouts](tinytapeout.md): the PMOD layouts of the Tiny Tapeout demo boards.

