# Raspberry Pi PMOD HAT

The Digilent PMOD HAT Adapter connects standard Digilent PMOD modules to a Raspberry Pi's 40-pin GPIO header. In the fpgas.online infrastructure, it enables direct signal connections between a Raspberry Pi host and FPGA boards with PMOD connectors (such as the Arty A7 and TT FPGA Demo Board).

## Key Specifications

| Parameter           | Value                                                     |
| ------------------- | --------------------------------------------------------- |
| PMOD ports          | 3x 12-pin (JA, JB, JC)                                    |
| Total signal pins   | 24 (8 per port)                                           |
| Logic level         | 3.3V (matches RPi GPIO)                                   |
| Max current per pin | 16 mA                                                     |
| RPi header          | 40-pin GPIO (Pi 2/3/4/5 compatible)                       |
| Unused GPIO         | 5 pins available (GPIO22, GPIO23, GPIO24, GPIO25, GPIO27) |

Source: [Digilent PMOD HAT Reference Manual](https://digilent.com/reference/add-ons/pmod-hat/reference-manual)

For the PMOD connector pinouts, interface types, and electrical specification, see the [PMOD interface](index.md) page.

## RPi GPIO to PMOD Pin Mapping

The PMOD HAT maps Raspberry Pi GPIO pins to three PMOD ports (JA, JB, JC). Each PMOD port has 8 signal pins (top row pins 1-4 and bottom row pins 7-10). Only the top rows conform to standard [PMOD interface types](index.md); the bottom rows provide RPi hardware peripherals but not in standard PMOD type positions.

| Port | Top Row (1-4)             | Bottom Row (7-10) | Full 12-pin Type? |
| ---- | ------------------------- | ----------------- | ----------------- |
| JA   | **Type 2 (SPI)** — CE0    | PCM/I2S (custom)  | No                |
| JB   | **Type 2 (SPI)** — CE1    | Mixed + I2C       | No                |
| JC   | **Type 4 (UART)** — UART0 | Mixed + PWM       | No                |

### Port JA — Top Row: Type 2 (SPI) Exact Match

The top row (pins 1-4) exactly matches the [Type 2 (SPI)](index.md#type-2--spi-6-pin) pinout when the RPi's SPI0 hardware controller is enabled. The bottom row carries RPi PCM/I2S signals (not a standard PMOD type).

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

Same SPI bus as JA but with a different chip select (CE1). The bottom row has I2C1 on pins 9-10, but this does not match Type 2A (which expects INT/RESET on pins 7-8).

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

The top row (pins 1-4) exactly matches the [Type 4 (UART)](index.md#type-4--uart-6-pin) pinout (CTS, TXD, RXD, RTS) when the RPi's UART0 hardware controller is enabled. Note: this is Type 4, **not** Type 3 (which has a different pin order: CTS, RTS, RXD, TXD). The bottom row carries mixed signals (not a standard PMOD type).

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

**Notes on JC**:
- GPIO14/15 (JC2/JC3) are the default UART TX/RX pins. If using GPIO UART for other purposes, these pins are not available for PMOD.

Source: [DesignSpark.Pmod HAT.py driver](https://github.com/DesignSparkRS/DesignSpark.Pmod/blob/master/DesignSpark/Pmod/HAT.py), [Digilent PMOD HAT Schematic](https://digilent.com/reference/_media/learn/documentation/schematics/pmod_hat_adapter_sch.pdf), [Digilent PMOD HAT Reference Manual](https://digilent.com/reference/add-ons/pmod-hat/reference-manual)

## Unused GPIO Pins

Seven RPi GPIO pins are not assigned to any PMOD port. Five of them are free for other uses; GPIO0 and GPIO1 are reserved for the HAT ID EEPROM, which is why the Key Specifications above count five available rather than seven:

| RPi GPIO | RPi Header Pin | Notes                 |
| -------- | -------------- | --------------------- |
| GPIO0    | Pin 27         | I2C0_SDA (HAT EEPROM) |
| GPIO1    | Pin 28         | I2C0_SCL (HAT EEPROM) |
| GPIO22   | Pin 15         | Free                  |
| GPIO23   | Pin 16         | Free                  |
| GPIO24   | Pin 18         | Free                  |
| GPIO25   | Pin 22         | Free                  |
| GPIO27   | Pin 13         | Free                  |

Source: [DesignSpark.Pmod HAT.py driver](https://github.com/DesignSparkRS/DesignSpark.Pmod/blob/master/DesignSpark/Pmod/HAT.py), [Digilent PMOD HAT Schematic](https://digilent.com/reference/_media/learn/documentation/schematics/pmod_hat_adapter_sch.pdf)

## Electrical Characteristics

| Parameter                 | Value                                   |
| ------------------------- | --------------------------------------- |
| Logic voltage             | 3.3V (supplied by RPi's 3.3V rail)      |
| Max current per GPIO pin  | 16 mA (RPi BCM2835/BCM2711 limit)       |
| Total GPIO current budget | ~50 mA across all pins (RPi limitation) |
| VCC on PMOD connectors    | 3.3V (from RPi 3.3V rail)               |
| Input threshold (low)     | ~0.8V                                   |
| Input threshold (high)    | ~1.3V                                   |

The PMOD HAT does not include any level shifters or buffers -- signals pass directly from RPi GPIO to PMOD connectors. This means the 3.3V logic level and current limits of the RPi GPIO apply directly.

## Usage in fpgas.online

The PMOD HAT is installed on RPi hosts that have **Arty A7**, **Tiny Tapeout FPGA Demo Board** or [**Tiny Tapeout ASIC demo board**](../tt-asic.md) hardware attached — every one of the six Tiny Tapeout ASIC hosts at Welland carries one. It connects the RPi's GPIO pins to the PMOD connectors on these FPGA boards, enabling the RPi to directly drive and read FPGA I/O pins for testing (GPIO loopback, SPI, UART, etc.).

### Wiring

Ribbon cables connect straight through between matching port names:

| HAT Port | FPGA Board Port | Cable       |
| -------- | --------------- | ----------- |
| JA       | JA              | 12-pin PMOD |
| JB       | JB              | 12-pin PMOD |
| JC       | JC              | 12-pin PMOD |

Straight through is the design, not a guarantee for any individual cable:
pin-level crossovers have been measured on deployed cables. The 2026-03-17
[PMOD cable routing scans](../arty-a7.md#pmod-cable-routing-hat--arty) found HAT
JC pins 1 and 2 crossed relative to Arty JC pins 1 and 2 on one host. Check the
cable before trusting the mapping on a host that has not been scanned.

The full RPi GPIO → PMOD pin → FPGA pin mappings for each board are documented in:

- [Digilent Arty A7](../arty-a7.md)
- [Tiny Tapeout FPGA demo board](../tt-fpga.md)

### Development hosts

Surveyed 2026-03-17. Two PMOD HAT development hosts sit on
`iot.welland.mithis.com`, a separate network that is not part of the
fpgas.online fleet, so no site page lists them.

```{rst-class} nowrap
```

| Host                             | RPi Model | Notes             |
| -------------------------------- | --------------- | ----------------- |
| `rpi5-pmod.iot.welland.mithis.com` | RPi 5           | PMOD HAT dev host |
| `rpi4-pmod.iot.welland.mithis.com` | RPi 4           | PMOD HAT dev host |

## References

- [PMOD interface](index.md)
- Digilent PMOD HAT Reference Manual: <https://digilent.com/reference/add-ons/pmod-hat/reference-manual>
- Digilent PMOD HAT Product Page: <https://digilent.com/shop/pmod-hat-adapter/>
