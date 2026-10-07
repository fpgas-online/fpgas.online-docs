# PMOD interface: the 8-pin I2C interface and the summary table

**You want the extended 8-pin I2C interface, or all the interface types in one table.**

## Extended Interface: I2C (8-pin)

The I2C PMOD interface is not part of the standard Digilent PMOD specification but is defined as an extension. It uses an 8-pin connector with paired signals for improved signal integrity.

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

Each signal has two pins for lower impedance and better signal integrity at higher I2C speeds (400 kHz Fast Mode, 1 MHz Fast Mode Plus).

Source: [High Speed PMOD Spreadsheet](https://docs.google.com/spreadsheets/d/1D-GboyrP57VVpejQzEm0P1WEORo1LAIt92hk1bZGEoo/edit?gid=0#gid=0)

## Summary Table

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
