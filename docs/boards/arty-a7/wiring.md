# Arty A7: wiring to the Raspberry Pi

**You want to know how an Arty is joined to its Raspberry Pi: the USB cable's JTAG and UART, and the Arty's PMOD pins that the HAT's cables reach.**

## Wiring to the Raspberry Pi

Each Arty connects to its Raspberry Pi host in two independent ways: one USB
cable carrying both JTAG and the console, and — on hosts fitted with a
[PMOD HAT](../pmod/rpi-hat.md) — three PMOD ribbon cables carrying FPGA I/O
directly to the Pi's GPIO header. A third path, the USB Ethernet adapter wired
to the Arty's RJ45 jack, is described under [MII Ethernet](ethernet.md#mii-ethernet).

### Programming Interface

The Arty has an on-board FTDI FT2232H providing both JTAG and UART over a single
USB connection.

| Parameter      | Value                                               |
| -------------- | --------------------------------------------------- |
| Interface      | USB JTAG (FTDI FT2232H, channel A)                  |
| Tool           | `openFPGALoader -b arty <bitstream>`                |
| USB device     | Appears as two `/dev/ttyUSB*` devices (JTAG + UART) |
| Bitstream type | `.bit` (volatile SRAM load)                         |

The commands are under [Programming](programming.md#programming). A board whose FTDI is
disconnected has no `/dev/ttyUSB*` devices at all and cannot be programmed or
consoled — see [Known faults](../../sites/welland.md#known-faults) on the Welland
page.

### UART Interface

The FPGA's UART reaches the host RPi through the FTDI FT2232H (channel B) as a
USB serial device; the FPGA-side pins are under [Serial (UART)](serial.md#serial-uart).

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
([Type 2 (SPI)](../pmod/index.md#type-2--spi-6-pin), CE0), JB
([Type 2 (SPI)](../pmod/index.md#type-2--spi-6-pin), CE1) and JC
([Type 4 (UART)](../pmod/index.md#type-4--uart-6-pin)), the GPIO each pin lands on,
and the RPi GPIOs no port uses — is in
[RPi GPIO to PMOD Pin Mapping](../pmod/rpi-hat.md#rpi-gpio-to-pmod-pin-mapping)
rather than repeated here.
