---
type: reference
owner: documentation maintainers
reader: someone looking up which Arty A7 signal goes to which Raspberry Pi port or pin
review: 2026-11-10
---

# Arty A7 wiring to a Raspberry Pi

**You have an Arty A7 on a Raspberry Pi and want to know what connects them.** One USB cable carries JTAG and the console. On a host fitted with a PMOD HAT, three ribbon cables also run from the HAT to the Arty. The FPGA pins of each connector are on [Arty A7 specifications](../overview/specifications.md).

## The USB cable

The Arty has an on-board FTDI FT2232H that provides both JTAG and UART over a single USB connection. Parameter names a property of the JTAG channel and Value gives it.

| Parameter      | Value                                               |
| -------------- | --------------------------------------------------- |
| Interface      | USB JTAG (FTDI FT2232H, channel A)                  |
| Tool           | `openFPGALoader -b arty <bitstream>`                |
| USB device     | Appears as two `/dev/ttyUSB*` devices (JTAG + UART) |
| Bitstream type | `.bit` (volatile SRAM load)                         |

### The UART channel

The FPGA's UART reaches the host through the FTDI FT2232H (channel B) as a USB serial device. The FPGA-side pins are under Serial (UART) on [Arty A7 specifications](../overview/specifications.md#serial-uart). Parameter names a host-side setting and Value gives it.

| Parameter    | Value                              |
| ------------ | ---------------------------------- |
| RPi device   | `/dev/ttyUSB1` (channel B of FTDI) |
| Baud rate    | 115200                             |
| Flow control | None                               |
| Test args    | `--port /dev/ttyUSB1 --board arty` |

`/dev/ttyUSB0` is the JTAG channel and `/dev/ttyUSB1` is the UART channel.

## The Ethernet adapter

The Ethernet test uses a USB Ethernet adapter on the Raspberry Pi connected to the Arty's RJ45 jack. It is independent of the PMOD HAT and of the Pi's own Ethernet. The MII pins are on [Arty A7 specifications](../overview/specifications.md#mii-ethernet).

## PMOD cables

The Raspberry Pi side of these cables is on [RPi GPIO to PMOD pin mapping](../../pmod/rpi-hat.md#rpi-gpio-to-pmod-pin-mapping). It covers the HAT ports JA ([Type 2 (SPI)](../../pmod/index.md#type-2--spi-6-pin), CE0), JB ([Type 2 (SPI)](../../pmod/index.md#type-2--spi-6-pin), CE1) and JC ([Type 4 (UART)](../../pmod/index.md#type-4--uart-6-pin)). It also gives the GPIO each pin lands on and the Raspberry Pi GPIOs no port uses.

The cabling found on other boards differs from these tables: [test-designs issue #58](https://github.com/fpgas-online/fpgas.online-test-designs/issues/58) holds that survey. The ribbon cables in these tables connect straight through: **HAT JA to Arty JA**, **HAT JB to Arty JB** and **HAT JC to Arty JC**. Arty JD is not connected, because the HAT has only 3 ports. The routing was read with the [`pmod-pin-id` design](../../pin-id.md), which sends each FPGA pin's ball name as 1200-baud UART on every PMOD pin.

Each table below has one row per HAT pin. RPi GPIO is the Raspberry Pi GPIO the pin lands on and Scanned FPGA Pin is the ball the scan read there. Expected is the ball the straight-through routing puts there, and Match says whether they agree. It is `yes`, or `reversed` where two pins read in each other's place.

### HAT JA to Arty JA

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

(\*) Pins 2-4 share GPIOs with JB pins 2-4. The scan reads Arty JB's pins (E16, D15, C15) because both cables drive the same GPIO lines. Arty JA pins 2-4 (B11, A11, D12) cannot be independently verified.

### HAT JB to Arty JB

All 8 pins are verified.

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

### HAT JC to Arty JC

Pins 1 and 2 read in the reverse of Digilent's documented order. That follows the Arty's JC connector, not the cable.

| HAT Pin | RPi GPIO | Scanned FPGA Pin | Expected (Arty JC) | Match |
| ------- | -------- | ---------------- | ------------------ | ----- |
| 1       | GPIO16   | V12              | U12                | reversed |
| 2       | GPIO14   | U12              | V12                | reversed |
| 3       | GPIO15   | V10              | V10                | yes   |
| 4       | GPIO17   | V11              | V11                | yes   |
| 7       | GPIO4    | U14              | U14                | yes   |
| 8       | GPIO12   | V14              | V14                | yes   |
| 9       | GPIO5    | T13              | T13                | yes   |
| 10      | GPIO6    | U13              | U13                | yes   |

The pin-id scan reads V12 on HAT JC pin 1 (GPIO16) and U12 on HAT JC pin 2 (GPIO14). It reads the same on every Arty scanned, wherever that connector is cabled. It is not a cable fault, and the check expects V12 and then U12 on these two pins. All other pins match 1:1.
