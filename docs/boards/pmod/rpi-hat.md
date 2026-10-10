---
type: reference
owner: documentation maintainers
reader: someone looking up which Raspberry Pi GPIO a PMOD HAT pin reaches
review: 2026-11-10
---

# Raspberry Pi PMOD HAT

**The Digilent PMOD HAT Adapter connects standard Digilent PMOD modules to a Raspberry Pi's 40-pin GPIO header**. This page is the reference for its ports, the GPIO behind each PMOD pin, its unused GPIOs and its electrical figures. It also names the boards that use it. The PMOD connector types themselves are on the [PMOD interface](index.md) page.

## Key Specifications

The Parameter column names a property of the HAT, as in the [Digilent PMOD HAT Reference Manual](https://digilent.com/reference/add-ons/pmod-hat/reference-manual), and the Value column gives it.

| Parameter           | Value                                                     |
| ------------------- | --------------------------------------------------------- |
| PMOD ports          | 3x 12-pin (JA, JB, JC)                                    |
| Total signal pins   | 24 (8 per port)                                           |
| Logic level         | 3.3V (matches RPi GPIO)                                   |
| Max current per pin | 16 mA                                                     |
| RPi header          | 40-pin GPIO (Pi 2/3/4/5 compatible)                       |
| Unused GPIO         | 5 pins available (GPIO22, GPIO23, GPIO24, GPIO25, GPIO27) |

## RPi GPIO to PMOD Pin Mapping

The PMOD HAT maps Raspberry Pi GPIO pins to three PMOD ports, JA, JB and JC. Each port has 8 signal pins, in the top row (pins 1-4) and the bottom row (pins 7-10). Only the top rows conform to standard [PMOD interface types](index.md). The bottom rows carry Raspberry Pi hardware peripherals, but not in standard PMOD type positions.

In the table, Top Row gives the type and peripheral. Bottom Row gives the peripheral. Full 12-pin Type says whether the port matches a double width type.

| Port | Top Row (1-4)             | Bottom Row (7-10) | Full 12-pin Type? |
| ---- | ------------------------- | ----------------- | ----------------- |
| JA   | **Type 2 (SPI)** — CE0    | PCM/I2S (custom)  | No                |
| JB   | **Type 2 (SPI)** — CE1    | Mixed + I2C       | No                |
| JC   | **Type 4 (UART)** — UART0 | Mixed + PWM       | No                |

### Port JA — Top Row: Type 2 (SPI) Exact Match

The top row (pins 1-4) exactly matches the [Type 2 (SPI)](index.md#type-2--spi-6-pin) pinout when the Raspberry Pi's SPI0 hardware controller is enabled. The bottom row carries Raspberry Pi PCM/I2S signals, which are not a standard PMOD type. In this table and the two below, RPi GPIO is the BCM GPIO number and RPi Header Pin is the 40-pin header position. BCM Function is the pin's peripheral function. The last column gives the pin of the matching standard type.

| PMOD Pin | Signal | RPi GPIO | RPi Header Pin | BCM Function   | Type 2 Standard |
| -------- | ------ | -------- | -------------- | -------------- | --------------- |
| JA1      | CS     | GPIO8    | Pin 24         | SPI0_CE0       | SS (Out)        |
| JA2      | MOSI   | GPIO10   | Pin 19         | SPI0_MOSI (\*) | MOSI (Out)      |
| JA3      | MISO   | GPIO9    | Pin 21         | SPI0_MISO (\*) | MISO (In)       |
| JA4      | SCK    | GPIO11   | Pin 23         | SPI0_SCLK (\*) | SCK (Out)       |
| JA7      | I/O 5  | GPIO19   | Pin 35         | PCM_FS         | —               |
| JA8      | I/O 6  | GPIO21   | Pin 40         | PCM_DOUT       | —               |
| JA9      | I/O 7  | GPIO20   | Pin 38         | PCM_DIN        | —               |
| JA10     | I/O 8  | GPIO18   | Pin 12         | PCM_CLK / PWM0 | —               |

(\*) Shared with JB pins 2-4 — see note below.

### Port JB — Top Row: Type 2 (SPI) Exact Match

Port JB uses the same SPI bus as JA with a different chip select, CE1. The bottom row has I2C1 on pins 9-10, which does not match Type 2A, because Type 2A expects INT and RESET on pins 7-8.

| PMOD Pin | Signal | RPi GPIO | RPi Header Pin | BCM Function   | Type 2 Standard |
| -------- | ------ | -------- | -------------- | -------------- | --------------- |
| JB1      | CS     | GPIO7    | Pin 26         | SPI0_CE1       | SS (Out)        |
| JB2      | MOSI   | GPIO10   | Pin 19         | SPI0_MOSI (\*) | MOSI (Out)      |
| JB3      | MISO   | GPIO9    | Pin 21         | SPI0_MISO (\*) | MISO (In)       |
| JB4      | SCK    | GPIO11   | Pin 23         | SPI0_SCLK (\*) | SCK (Out)       |
| JB7      | I/O 5  | GPIO26   | Pin 37         |                | —               |
| JB8      | I/O 6  | GPIO13   | Pin 33         | PWM1           | —               |
| JB9      | I/O 7  | GPIO3    | Pin 5          | I2C1_SCL       | —               |
| JB10     | I/O 8  | GPIO2    | Pin 3          | I2C1_SDA       | —               |

(\*) JA pins 2-4 and JB pins 2-4 are the **same physical GPIO lines** (GPIO10, GPIO9, GPIO11 = SPI0 MOSI/MISO/SCLK). They share a single SPI bus with different chip selects (JA1=CE0, JB1=CE1). When using these ports for GPIO (not SPI), pins 2-4 of both ports will read/drive the same signal.

### Port JC — Top Row: Type 4 (UART) Exact Match

The top row (pins 1-4) exactly matches the [Type 4 (UART)](index.md#type-4--uart-6-pin) pinout (CTS, TXD, RXD, RTS) when the Raspberry Pi's UART0 hardware controller is enabled. This is Type 4, **not** Type 3, which has a different pin order (CTS, RTS, RXD, TXD). The bottom row carries mixed signals, which are not a standard PMOD type.

| PMOD Pin | Signal | RPi GPIO | RPi Header Pin | BCM Function | Type 4 Standard |
| -------- | ------ | -------- | -------------- | ------------ | --------------- |
| JC1      | CTS    | GPIO16   | Pin 36         | CTS0         | CTS (In)        |
| JC2      | TXD    | GPIO14   | Pin 8          | TXD0         | TXD (Out)       |
| JC3      | RXD    | GPIO15   | Pin 10         | RXD0         | RXD (In)        |
| JC4      | RTS    | GPIO17   | Pin 11         | RTS0         | RTS (Out)       |
| JC7      | I/O 5  | GPIO4    | Pin 7          | GPCLK0       | —               |
| JC8      | I/O 6  | GPIO12   | Pin 32         | PWM0         | —               |
| JC9      | I/O 7  | GPIO5    | Pin 29         |              | —               |
| JC10     | I/O 8  | GPIO6    | Pin 31         |              | —               |

GPIO14 and GPIO15 (JC2 and JC3) are the default UART TX and RX pins. If the GPIO UART is used for anything else, these pins are not available for PMOD.

The port tables follow the [DesignSpark.Pmod HAT.py driver](https://github.com/DesignSparkRS/DesignSpark.Pmod/blob/master/DesignSpark/Pmod/HAT.py) and the [Digilent PMOD HAT schematic](https://digilent.com/reference/_media/learn/documentation/schematics/pmod_hat_adapter_sch.pdf).

## Unused GPIO Pins

Seven Raspberry Pi GPIOs are assigned to no PMOD port. GPIO0 and GPIO1 are reserved for the HAT ID EEPROM, and the other five are free, which is why Key Specifications lists five unused GPIOs. In the table, Notes gives the GPIO's use.

| RPi GPIO | RPi Header Pin | Notes                 |
| -------- | -------------- | --------------------- |
| GPIO0    | Pin 27         | I2C0_SDA (HAT EEPROM) |
| GPIO1    | Pin 28         | I2C0_SCL (HAT EEPROM) |
| GPIO22   | Pin 15         | Free                  |
| GPIO23   | Pin 16         | Free                  |
| GPIO24   | Pin 18         | Free                  |
| GPIO25   | Pin 22         | Free                  |
| GPIO27   | Pin 13         | Free                  |

## Electrical Characteristics

The Parameter column names an electrical property and the Value column gives it.

| Parameter                 | Value                                   |
| ------------------------- | --------------------------------------- |
| Logic voltage             | 3.3V (supplied by RPi's 3.3V rail)      |
| Max current per GPIO pin  | 16 mA (RPi BCM2835/BCM2711 limit)       |
| Total GPIO current budget | ~50 mA across all pins (RPi limitation) |
| VCC on PMOD connectors    | 3.3V (from RPi 3.3V rail)               |
| Input threshold (low)     | ~0.8V                                   |
| Input threshold (high)    | ~1.3V                                   |

The PMOD HAT has no level shifters or buffers, so signals pass directly from the Raspberry Pi GPIO to the PMOD connectors. The 3.3V logic level and the current limits of the Raspberry Pi GPIO therefore apply directly.

## Boards that use the HAT

The HAT is fitted to hosts with an Arty A7, a Tiny Tapeout FPGA demo board or a [Tiny Tapeout ASIC demo board](../tt-asic.md) attached. It connects the Raspberry Pi's GPIO pins to the PMOD connectors on these boards. The Raspberry Pi can then drive and read their I/O pins for GPIO loopback, SPI and UART tests.

### Wiring

Ribbon cables connect straight through between matching port names. The HAT Port column is the port on the HAT, FPGA Board Port is the port it joins and Cable is the cable type.

| HAT Port | FPGA Board Port | Cable       |
| -------- | --------------- | ----------- |
| JA       | JA              | 12-pin PMOD |
| JB       | JB              | 12-pin PMOD |
| JC       | JC              | 12-pin PMOD |

Straight through is the design, not a guarantee for any individual cable, because pin-level crossovers have been measured on deployed cables. The Arty A7 page's [PMOD cable routing tables](../arty-a7.md#pmod-cable-routing-hat--arty) record one. On one cable, HAT JC pins 1 and 2 were found crossed relative to Arty JC pins 1 and 2.

The full Raspberry Pi GPIO to PMOD pin to FPGA pin mappings for each board are on these pages:

- [Digilent Arty A7](../arty-a7.md)
- [Tiny Tapeout FPGA demo board](../tt-fpga.md)

## References

- [PMOD interface](index.md)
- Digilent PMOD HAT Reference Manual: <https://digilent.com/reference/add-ons/pmod-hat/reference-manual>
- Digilent PMOD HAT Product Page: <https://digilent.com/shop/pmod-hat-adapter/>
