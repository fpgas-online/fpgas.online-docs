# PMOD interface: physical connectors

**You want the PMOD connector's pin numbering, single and double width, and its electrical limits.**

## Physical Connectors

PMOD connectors use standard 100 mil (2.54 mm) pitch pin headers. There are two widths:

### Single Width (6-pin, 1×6)

4 signal pins + 1 GND + 1 VCC.

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

8 signal pins + 2 GND + 2 VCC. The top row (pins 1-6) matches the single width pinout.

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

| Parameter           | Value                       |
| ------------------- | --------------------------- |
| VCC voltage         | 3.3V (standard)             |
| Max current per VCC | 100 mA                      |
| I/O standard        | LVCMOS33 (matched to VCC)   |
| Pin pitch           | 100 mil (2.54 mm)           |
| Connector type      | Standard 100 mil pin header |

See also: [the standard interface types](types.md), which use this pin numbering; [the summary table](i2c-summary.md#summary-table).
