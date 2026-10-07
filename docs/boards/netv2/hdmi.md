# NeTV2: HDMI

**You are building or checking a design that uses the NeTV2's HDMI inputs or outputs and need their FPGA pins.**

Two HDMI inputs and two HDMI outputs. All HDMI signals use the TMDS_33 I/O
standard.

## HDMI Input 0

| Signal            | FPGA Pins | Notes      |
| ----------------- | --------- | ---------- |
| CLK_P / CLK_N     | L19 / L20 | Inverted   |
| DATA0_P / DATA0_N | K21 / K22 | Inverted   |
| DATA1_P / DATA1_N | J20 / J21 | Inverted   |
| DATA2_P / DATA2_N | J22 / H22 | Inverted   |
| SCL / SDA         | T18 / V18 | I2C (EDID) |

## HDMI Input 1

| Signal            | FPGA Pins   | Notes        |
| ----------------- | ----------- | ------------ |
| CLK_P / CLK_N     | Y18 / Y19   | Inverted     |
| DATA0_P / DATA0_N | AA18 / AB18 | Not inverted |
| DATA1_P / DATA1_N | AA19 / AB20 | Inverted     |
| DATA2_P / DATA2_N | AB21 / AB22 | Inverted     |
| SCL / SDA         | W17 / R17   | SCL inverted |

## HDMI Output 0

| Signal            | FPGA Pins | Notes    |
| ----------------- | --------- | -------- |
| CLK_P / CLK_N     | W19 / W20 | Inverted |
| DATA0_P / DATA0_N | W21 / W22 |          |
| DATA1_P / DATA1_N | U20 / V20 |          |
| DATA2_P / DATA2_N | T21 / U21 |          |

## HDMI Output 1

| Signal            | FPGA Pins | Notes    |
| ----------------- | --------- | -------- |
| CLK_P / CLK_N     | G21 / G22 | Inverted |
| DATA0_P / DATA0_N | E22 / D22 | Inverted |
| DATA1_P / DATA1_N | C22 / B22 | Inverted |
| DATA2_P / DATA2_N | B21 / A21 | Inverted |

Source: [LiteX platform file for the NeTV2](https://github.com/litex-hub/litex-boards/blob/master/litex_boards/platforms/kosagi_netv2.py)
