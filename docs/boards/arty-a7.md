# Digilent Arty A7

The Digilent Arty A7 is a Xilinx Artix-7 development board and the most numerous
FPGA board in the fleet: five at Welland ([Arty A7-35T](../sites/welland.md#arty-a7-35t))
and eight at PS1 ([Arty A7 hosts](../sites/ps1.md#arty-a7-hosts)). Each board
reaches its Raspberry Pi host over a single USB cable — an on-board FTDI
FT2232HQ gives the host both a JTAG channel and a UART channel — and, on hosts
fitted with a [PMOD HAT](pmod/rpi-hat.md), over three ribbon cables from the
HAT's PMOD ports to the Arty's own.

This page covers the board itself, its FPGA pin assignments for every on-board
peripheral, how it is programmed, and the measured
[wiring to the Raspberry Pi](#wiring-to-the-raspberry-pi) including the
[PMOD cable routing](#pmod-cable-routing-hat--arty). Which host carries which
Arty is on the two site pages linked above.

## Key Specifications

| Parameter | Value |
|-----------|-------|
| FPGA (A7-35 variant) | Xilinx Artix-7 XC7A35T**I**CSG324-1L |
| FPGA (A7-100 variant) | Xilinx Artix-7 XC7A100TCSG324-1 |
| Package | CSG324 (324-ball BGA) |
| System clock | 100 MHz (pin E3, LVCMOS33) |
| DDR3 SDRAM | 256 MB, MT41K128M16JT-125 (16-bit bus) |
| Ethernet PHY | TI DP83848J, MII interface (100Base-T) |
| USB-UART/JTAG | FTDI FT2232HQ (dual-channel) |
| SPI Flash | Quad SPI (pins L13, L16, K17, K18, L14, M14) |
| User LEDs | 4 green (H5, J5, T9, T10) + 4 RGB |
| User switches | 4 (A8, C11, C10, A10) |
| User buttons | 4 (D9, C9, B9, B8) |
| PMOD connectors | 4x 12-pin (JA, JB, JC, JD) |
| I/O standard | LVCMOS33 (3.3V) for most I/O |
| Power | USB or external 7-15V |

:::{todo}
The two sources disagree on the package of the A7-35 boards in the fleet. The
table above (from the board specification) says CSG324; the pin-mapping notes
recorded a different device and package for the three hosts they were measured
on:

| Parameter | Value |
| --------- | ----- |
| FPGA | Xilinx Artix-7 XC7A35T-CPG236-1 |
| Package | CPG236 |

Every FPGA pin name on this page comes from the LiteX `digilent_arty`
platform, whose two device strings are both CSG324 parts (see
[FPGA Device Variants](#fpga-device-variants)), so CPG236 looks like a
transcription error in the pin-mapping notes rather than a second board type.
Confirm against a board and delete the loser.
:::

The bold **I** in the A7-35 device string is the temperature grade: the boards
in the fleet are the industrial-grade, low-power part, which is the `a7-35`
variant below.

Source: [Digilent Arty A7 Reference Manual](https://digilent.com/reference/programmable-logic/arty-a7/reference-manual)

## FPGA Device Variants

The LiteX platform file defines two variants:

| Variant | Device String | Notes |
|---------|--------------|-------|
| `a7-35` | `xc7a35ticsg324-1L` | Industrial temp, low power |
| `a7-100` | `xc7a100tcsg324-1` | Larger fabric, commercial temp |

Source: [digilent_arty.py](https://github.com/litex-hub/litex-boards/blob/master/litex_boards/platforms/digilent_arty.py)

## Serial (UART)

The primary serial port uses the FTDI FT2232HQ USB-to-UART bridge. This is
**not** a GPIO connection — it goes through USB, so the FPGA's TX and RX pins
face the on-board FTDI chip rather than the Raspberry Pi header.

| Signal | FPGA Pin | Direction | IO Standard |
| --------------- | -------- | --------- | ----------- |
| TX (FPGA → RPi) | D10      | Output    | LVCMOS33    |
| RX (RPi → FPGA) | A9       | Input     | LVCMOS33    |

The FTDI chip provides two channels: Channel A for JTAG and Channel B for UART.
The UART typically appears as `/dev/ttyUSB1` on Linux (the second of two USB
serial devices created by the FT2232HQ). The host-side settings are under
[UART Interface](#uart-interface).

## DDR3 SDRAM

- Part: MT41K128M16JT-125 (Micron, 128M x 16-bit = 256 MB)
- Interface: 16-bit data bus (DQ[15:0]), 2 byte lanes (DM/DQS pairs)
- I/O Standard: SSTL135 (1.35V)
- FPGA I/O bank 34 has INTERNAL_VREF set to 0.675V

| Signal        | FPGA Pins                                 | IO Standard  |
| ------------- | ----------------------------------------- | ------------ |
| A[13:0]       | R2 M6 N4 T1 N6 R7 V6 U7 R8 V7 R6 U6 T6 T8 | SSTL135      |
| BA[2:0]       | R1 P4 P2                                  | SSTL135      |
| DQ[7:0]       | K5 L3 K3 L6 M3 M1 L4 M2                   | SSTL135      |
| DQ[15:8]      | V4 T5 U4 V5 V1 T3 U3 R3                   | SSTL135      |
| DQS_P[1:0]    | N2 U2                                     | DIFF_SSTL135 |
| DQS_N[1:0]    | N1 V2                                     | DIFF_SSTL135 |
| DM[1:0]       | L1 U1                                     | SSTL135      |
| CLK_P / CLK_N | U9 / V9                                   | DIFF_SSTL135 |
| CKE           | N5                                        | SSTL135      |
| ODT           | R5                                        | SSTL135      |
| CS_N          | U8                                        | SSTL135      |
| RAS_N         | P3                                        | SSTL135      |
| CAS_N         | M4                                        | SSTL135      |
| WE_N          | P5                                        | SSTL135      |
| RESET_N       | K6                                        | SSTL135      |

Source: [digilent_arty.py](https://github.com/litex-hub/litex-boards/blob/master/litex_boards/platforms/digilent_arty.py)

## MII Ethernet

The Arty uses a TI DP83848J Ethernet PHY with a standard MII (Media Independent
Interface), supporting 10/100 Mbps. Every MII signal is LVCMOS33.

| Signal | FPGA Pin | Direction |
|--------|----------|-----------|
| ref_clk | G18 | Output (25 MHz) |
| tx_clk | H16 | Input |
| rx_clk | F15 | Input |
| rst_n | C16 | Output |
| mdio | K13 | Bidirectional |
| mdc | F16 | Output |
| rx_dv | G16 | Input |
| rx_er | C17 | Input |
| rx_data[3:0] | D18 E17 E18 G17 | Input |
| tx_en | H15 | Output |
| tx_data[3:0] | H14 J14 J13 H17 | Output |
| col | D17 | Input |
| crs | G14 | Input |

The Ethernet test uses a USB Ethernet adapter on the RPi connected to the Arty's
RJ45 jack, independent of the PMOD HAT and of the RPi's own Ethernet. Both site
pages record which adapter is fitted to each host.

Source: [digilent_arty.py](https://github.com/litex-hub/litex-boards/blob/master/litex_boards/platforms/digilent_arty.py), [Digilent Arty A7 Reference Manual](https://digilent.com/reference/programmable-logic/arty-a7/reference-manual)

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
[PMOD Connectors (FPGA Side)](#pmod-connectors-fpga-side) and by the
[PMOD interface specification](pmod/index.md).

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
Raspberry Pi via a Digilent [PMOD HAT adapter](pmod/rpi-hat.md). This enables
PMOD loopback testing where the RPi drives signals through the PMOD HAT to the
Arty's PMOD connectors and verifies correct signal propagation. The measured
cable routing is in
[PMOD Cable Routing: HAT ↔ Arty](#pmod-cable-routing-hat--arty).

## SPI Flash

On-board SPI flash for persistent bitstream storage. Every line is LVCMOS33.

| Signal | FPGA Pin |
|--------|----------|
| CS_N | L13 |
| CLK | L16 |
| MOSI (DQ0) | K17 |
| MISO (DQ1) | K18 |
| WP (DQ2) | L14 |
| HOLD (DQ3) | M14 |

Quad SPI (4x) mode is supported via the `spiflash4x` resource. The bitstream
configuration enables SPI_BUSWIDTH=4.

There is also a secondary SPI resource on a directly accessible header:

| Signal | FPGA Pin | IO Standard |
| ------ | -------- | ----------- |
| clk    | F1       | LVCMOS33    |
| cs_n   | C1       | LVCMOS33    |
| mosi   | H1       | LVCMOS33    |
| miso   | G1       | LVCMOS33    |

## LiteX Integration

| Property | Value |
|----------|-------|
| Platform module | `litex_boards.platforms.digilent_arty` |
| Target module | `litex_boards.targets.digilent_arty` |
| Default clock | `clk100` (100 MHz, pin E3) |
| Programmer | OpenOCD with `openocd_xc7_ft2232.cfg` |
| BSCAN SPI bitstream | `bscan_spi_xc7a35t.bit` or `bscan_spi_xc7a100t.bit` |
| Toolchain | Vivado (proprietary) or openXC7 (open source) |

Source: [digilent_arty.py](https://github.com/litex-hub/litex-boards/blob/master/litex_boards/platforms/digilent_arty.py)

## Programming

### Via openFPGALoader (USB-JTAG)

```console
# The first form is a volatile load, lost on the next power cycle. The second
# writes the on-board SPI flash and replaces whatever was there.
$ openFPGALoader -b arty design.bit
$ openFPGALoader -b arty --write-flash design.bit
```

### Via OpenOCD (USB-JTAG)

```console
$ openocd -f openocd_xc7_ft2232.cfg -c "init; pld load 0 design.bit; exit"
```

## Wiring to the Raspberry Pi

Each Arty connects to its Raspberry Pi host in two independent ways: one USB
cable carrying both JTAG and the console, and — on hosts fitted with a
[PMOD HAT](pmod/rpi-hat.md) — three PMOD ribbon cables carrying FPGA I/O
directly to the Pi's GPIO header. A third path, the USB Ethernet adapter wired
to the Arty's RJ45 jack, is described under [MII Ethernet](#mii-ethernet).

### Programming Interface

The Arty has an on-board FTDI FT2232H providing both JTAG and UART over a single
USB connection.

| Parameter      | Value                                               |
| -------------- | --------------------------------------------------- |
| Interface      | USB JTAG (FTDI FT2232H, channel A)                  |
| Tool           | `openFPGALoader -b arty <bitstream>`                |
| USB device     | Appears as two `/dev/ttyUSB*` devices (JTAG + UART) |
| Bitstream type | `.bit` (volatile SRAM load)                         |

The commands are under [Programming](#programming). A board whose FTDI is
disconnected has no `/dev/ttyUSB*` devices at all and cannot be programmed or
consoled — see [Known faults](../sites/welland.md#known-faults) on the Welland
page.

### UART Interface

The FPGA's UART reaches the host RPi through the FTDI FT2232H (channel B) as a
USB serial device; the FPGA-side pins are under [Serial (UART)](#serial-uart).

| Parameter    | Value                              |
| ------------ | ---------------------------------- |
| RPi device   | `/dev/ttyUSB1` (channel B of FTDI) |
| Baud rate    | 115200                             |
| Flow control | None                               |
| Test args    | `--port /dev/ttyUSB1 --board arty` |

Note: `/dev/ttyUSB0` is the JTAG channel, `/dev/ttyUSB1` is the UART channel.

### PMOD Connectors (FPGA Side)

The Arty has four PMOD connectors. The GPIO loopback test uses PMODA (input) and
PMODB (output).

#### PMODA

| PMOD Pin | Signal Index | FPGA Pin | IO Standard |
| -------- | ------------ | -------- | ----------- |
| 1        | pmoda:0      | G13      | LVCMOS33    |
| 2        | pmoda:1      | B11      | LVCMOS33    |
| 3        | pmoda:2      | A11      | LVCMOS33    |
| 4        | pmoda:3      | D12      | LVCMOS33    |
| 7        | pmoda:4      | D13      | LVCMOS33    |
| 8        | pmoda:5      | B18      | LVCMOS33    |
| 9        | pmoda:6      | A18      | LVCMOS33    |
| 10       | pmoda:7      | K16      | LVCMOS33    |

#### PMODB

| PMOD Pin | Signal Index | FPGA Pin | IO Standard |
| -------- | ------------ | -------- | ----------- |
| 1        | pmodb:0      | E15      | LVCMOS33    |
| 2        | pmodb:1      | E16      | LVCMOS33    |
| 3        | pmodb:2      | D15      | LVCMOS33    |
| 4        | pmodb:3      | C15      | LVCMOS33    |
| 7        | pmodb:4      | J17      | LVCMOS33    |
| 8        | pmodb:5      | J18      | LVCMOS33    |
| 9        | pmodb:6      | K15      | LVCMOS33    |
| 10       | pmodb:7      | J15      | LVCMOS33    |

#### PMODC

| PMOD Pin | Signal Index | FPGA Pin | IO Standard |
| -------- | ------------ | -------- | ----------- |
| 1        | pmodc:0      | U12      | LVCMOS33    |
| 2        | pmodc:1      | V12      | LVCMOS33    |
| 3        | pmodc:2      | V10      | LVCMOS33    |
| 4        | pmodc:3      | V11      | LVCMOS33    |
| 7        | pmodc:4      | U14      | LVCMOS33    |
| 8        | pmodc:5      | V14      | LVCMOS33    |
| 9        | pmodc:6      | T13      | LVCMOS33    |
| 10       | pmodc:7      | U13      | LVCMOS33    |

#### PMODD (not cabled to the HAT)

| PMOD Pin | Signal Index | FPGA Pin | IO Standard |
| -------- | ------------ | -------- | ----------- |
| 1        | pmodd:0      | D4       | LVCMOS33    |
| 2        | pmodd:1      | D3       | LVCMOS33    |
| 3        | pmodd:2      | F4       | LVCMOS33    |
| 4        | pmodd:3      | F3       | LVCMOS33    |
| 7        | pmodd:4      | E2       | LVCMOS33    |
| 8        | pmodd:5      | D2       | LVCMOS33    |
| 9        | pmodd:6      | H2       | LVCMOS33    |
| 10       | pmodd:7      | G2       | LVCMOS33    |

Source: `_connectors` in digilent_arty.py

The Raspberry Pi side of these cables — the three HAT ports JA
([Type 2 (SPI)](pmod/index.md#type-2--spi-6-pin), CE0), JB
([Type 2 (SPI)](pmod/index.md#type-2--spi-6-pin), CE1) and JC
([Type 4 (UART)](pmod/index.md#type-4--uart-6-pin)), the GPIO each pin lands on,
and the RPi GPIOs no port uses — is in
[RPi GPIO to PMOD Pin Mapping](pmod/rpi-hat.md#rpi-gpio-to-pmod-pin-mapping)
rather than repeated here.

### PMOD Cable Routing: HAT ↔ Arty

Ribbon cables connect straight through: **HAT JA → Arty JA**, **HAT JB → Arty
JB**, **HAT JC → Arty JC**. Arty JD is not connected (the HAT has only 3 ports).

Verified using the [`pmod-pin-id` design](pin-id.md), which transmits each FPGA
pin's ball name as 1200-baud UART on every PMOD pin. Two independent scans (PMOD
names and FPGA pin names) cross-validated.

:::{note}
These scans are from the 2026-03-17 survey and name their hosts by the flat
`piNN` names used before the 2026-08-23 renumbering, and they have not been
re-probed since. Which site they were run from is not settled — see
[the todo below](#which-site-were-these-hosts-at). If these are Welland hosts,
the addresses quoted below no longer resolve and the current name of a host has
to be derived from its switch port using the
[Arty A7-35T host table](../sites/welland.md#arty-a7-35t); if they are PS1
hosts, pi3, pi5 and pi9 are still at exactly these addresses in the
[Arty A7 hosts table](../sites/ps1.md#arty-a7-hosts). The routing itself is a
property of the cables and the board, not of the host, so it is recorded here
rather than on a site page.
:::

#### Pi9 (21 of 24 unique GPIOs scanned)

Scanned 2026-03-17.

This is the one host that produced a full scan, and it is also the host whose
site is in question — see [Which site were these hosts at?](#which-site-were-these-hosts-at)
before using the name `pi9` to find the board.

**HAT JA → Arty JA**

| HAT Pin | RPi GPIO | Scanned FPGA Pin | Expected (Arty JA) | Match |
| ------- | -------- | ---------------- | ------------------ | ----- |
| 1       | GPIO8    | G13              | G13                | yes   |
| 2       | GPIO10   | E16              | B11 (but shared\*) | (\*)  |
| 3       | GPIO9    | D15              | A11 (but shared\*) | (\*)  |
| 4       | GPIO11   | C15              | D12 (but shared\*) | (\*)  |
| 7       | GPIO19   | D13              | D13                | yes   |
| 8       | GPIO21   | B18              | B18                | yes   |
| 9       | GPIO20   | A18              | A18                | yes   |
| 10      | GPIO18   | K16              | K16                | yes   |

(\*) Pins 2-4 share GPIOs with JB pins 2-4. The scan reads Arty JB's pins (E16,
D15, C15) because both cables drive the same GPIO lines. Arty JA pins 2-4 (B11,
A11, D12) cannot be independently verified.

**HAT JB → Arty JB** (all 8 pins verified)

| HAT Pin | RPi GPIO | Scanned FPGA Pin | Expected (Arty JB) | Match |
| ------- | -------- | ---------------- | ------------------ | ----- |
| 1       | GPIO7    | E15              | E15                | yes   |
| 2       | GPIO10   | E16              | E16                | yes   |
| 3       | GPIO9    | D15              | D15                | yes   |
| 4       | GPIO11   | C15              | C15                | yes   |
| 7       | GPIO26   | J17              | J17                | yes   |
| 8       | GPIO13   | J18              | J18                | yes   |
| 9       | GPIO3    | K15              | K15                | yes   |
| 10      | GPIO2    | J15              | J15                | yes   |

**HAT JC → Arty JC** (pins 1↔2 swapped in cable)

| HAT Pin | RPi GPIO | Scanned FPGA Pin | Expected (Arty JC) | Match |
| ------- | -------- | ---------------- | ------------------ | ----- |
| 1       | GPIO16   | V12              | U12                | SWAP  |
| 2       | GPIO14   | U12              | V12                | SWAP  |
| 3       | GPIO15   | V10              | V10                | yes   |
| 4       | GPIO17   | V11              | V11                | yes   |
| 7       | GPIO4    | U14              | U14                | yes   |
| 8       | GPIO12   | V14              | V14                | yes   |
| 9       | GPIO5    | T13              | T13                | yes   |
| 10      | GPIO6    | U13              | U13                | yes   |

HAT JC pins 1 and 2 are swapped relative to Arty JC pins 1 and 2. This is a
physical cable crossover — GPIO16 connects to Arty JC pin 2 (V12) and GPIO14
connects to Arty JC pin 1 (U12). All other pins match 1:1.

#### Pi3

Scanned 2026-03-17.

Pi3 detected fewer pins (12 of 21 unique GPIOs). All detected pins match pi9's
results exactly, confirming the same cable routing. HAT JC top-row and some
JA/JB pins showed no signal — likely loose cables or missing connections on this
host.

#### Pi5 (offline)

Scanned 2026-03-17.

Pi5 (10.21.0.105) was unreachable during scanning — host appears powered off.

(unproven-lanes)=

#### Unproven lanes

:::{todo}
Three lanes of the HAT ↔ Arty routing cannot be proven from the Pi, one whole
connector was never scanned, and one crossover is known (JC pins 1 and 2):

- Arty JA pins 2, 3 and 4 (B11, A11, D12) cannot be verified from the Pi,
  because HAT JA pins 2-4 and HAT JB pins 2-4 are the same three GPIO lines and
  the scan always reads the JB end (E16, D15, C15). Proving them needs a
  gateware-side scan, or JB unplugged while JA is scanned.
- Arty JD has no HAT port and was never scanned at all.
- HAT JC pins 1 and 2 are crossed on pi9. Whether that crossover is in that one
  cable or in every cable of the batch is unknown, because pi3 saw no signal on
  the JC top row and pi5 was off. Any design using JC1/JC2 must either account
  for the swap or be checked per host.

Re-run the [`pmod-pin-id`](pin-id.md) scan on the current Arty hosts at both
sites, record the date, and say per host whether JC is crossed.
:::

(which-site-were-these-hosts-at)=

#### Which site were these hosts at?

:::{todo}
The 2026-03-17 scans record only the flat names pi3, pi5 and pi9, and both sites
used flat `10.21.0.0/24` addressing at the time, so the addresses do not say
which site was scanned. The evidence:

- Welland's [Known faults](../sites/welland.md#known-faults) carry a `pi9` Arty
  from this same survey whose FTDI is disconnected, so that board could not be
  programmed or tested on 2026-03-17. The `pmod-pin-id` scan needs the FTDI JTAG
  channel to load its bitstream, and pi9 produced a successful 21-of-24 scan
  that day. That argues **against** these being the Welland hosts.
- The [PS1 Arty table](../sites/ps1.md#arty-a7-hosts) has pi3, pi5 and pi9 at
  exactly 10.21.0.103, 10.21.0.105 and 10.21.0.109. It records pi9 online with a
  working FTDI, but that column has no date or provenance.
- The [Welland Arty table](../sites/welland.md#arty-a7-35t) has pi7, pi9, pi11,
  pi13 and pi26 — no pi3 and no pi5.
- `verify_hardware.py` in the test-designs repository defines **both** sets at
  identical addresses, and names pi11, not pi9, as the FTDI-disconnected Welland
  board, contradicting the Welland site notes:

  ```text
  "welland-pi3": {... "gateway": "welland", "target": "10.21.0.103", "board": "arty"},
  "welland-pi5": {... "gateway": "welland", "target": "10.21.0.105", "board": "arty"},
  "welland-pi9": {... "gateway": "welland", "target": "10.21.0.109", "board": "arty"},
  # welland-pi11: arty - FTDI disconnected, cannot program/test
  ...
  "ps1-pi3":     {... "gateway": "ps1",     "target": "10.21.0.103", "board": "arty"},
  "ps1-pi5":     {... "gateway": "ps1",     "target": "10.21.0.105", "board": "arty"},
  "ps1-pi9":     {... "gateway": "ps1",     "target": "10.21.0.109", "board": "arty"},
  ```

- The test-designs `plan.md` groups "Arty A7 (pi3/5/9)" with hosts that are
  otherwise Welland's, but names no site.
- The survey found 10.21.0.105 unreachable, which fits either site: PS1 records
  pi5 as online, but with no date or provenance for that column, and Welland has
  no host at .105 at all.

The balance favours PS1, but it is not settled. Ask the operator which site the
2026-03-17 `pmod-pin-id` run was made from, then either move the per-host detail
to that site page or say so here — and while doing it, settle whether pi9 or
pi11 is the Welland board with the disconnected FTDI.
:::

### GPIO Loopback Test

The loopback gateware computes `pmodb = ~pmoda` (per-bit inversion). The RPi
drives PMODA pins and reads the inverted result on PMODB pins. The loopback
pairs can be derived from the per-host PMOD cable routing tables above.

Only five of the eight lanes can actually be loop-tested from the Pi. HAT JA
pins 2-4 and HAT JB pins 2-4 are the same three GPIO lines (the SPI0 bus), so
the Pi cannot drive an Arty PMODA pin and read the corresponding PMODB pin
independently on those three lanes — see
[the routing todo](#unproven-lanes) above.

#### Pre-test Requirements

The SPI kernel modules claim GPIO7-11, which carry HAT JA pin 1 (GPIO8) and HAT
JB pins 1-4 (GPIO7 and the shared GPIO9/10/11). Unloading them frees these GPIOs
for the loopback test.

```console
# Nothing else on the Pi may be using SPI0 -- this takes the bus away from it.
$ sudo rmmod spidev spi_bcm2835
```

## References

- LiteX platform file: <https://github.com/litex-hub/litex-boards/blob/master/litex_boards/platforms/digilent_arty.py>
- Digilent Arty A7 Reference Manual: <https://digilent.com/reference/programmable-logic/arty-a7/reference-manual>
- Digilent Arty A7 Product Page: <https://digilent.com/shop/arty-a7-artix-7-fpga-development-board/>
- [PMOD interface specification](pmod/index.md)
- [Raspberry Pi PMOD HAT](pmod/rpi-hat.md)
