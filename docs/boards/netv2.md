# Kosagi NeTV2

The NeTV2 is a Xilinx Artix-7 video overlay and processing board designed by
bunnie (Andrew Huang) and produced by Alphamax/Kosagi. It stacks on a Raspberry
Pi's 40-pin header, and the fleet runs it in two arrangements: five production
boards on RPi 3B+ hosts driven entirely over GPIO JTAG and GPIO UART
([NeTV2](../sites/welland.md#netv2)), and two development boards on a separate
network, one of which, the RPi 5 host, adds a PCIe Gen2 x1 link
([NeTV2 development hosts](../sites/welland.md#netv2-development-hosts-separate-network)).
Every NeTV2 in the fleet is at Welland. This page covers the board itself, its
FPGA pin assignments for each on-board peripheral, how it is wired to its
Raspberry Pi, and how it is programmed and talked to.

## Key Specifications

| Parameter            | Value                                             |
| -------------------- | ------------------------------------------------- |
| FPGA (default)       | Xilinx Artix-7 XC7A35T-FGG484-2                   |
| FPGA (large variant) | Xilinx Artix-7 XC7A100T-FGG484-2                  |
| Package              | FGG484 (484-ball BGA)                             |
| System clock         | 50 MHz (pin J19, LVCMOS33)                        |
| DDR3 SDRAM           | 512 MB (32-bit wide, 4 byte lanes)                |
| Ethernet             | RMII PHY, 100Base-T (independent of host network) |
| HDMI                 | 2x HDMI In + 2x HDMI Out (TMDS_33)                |
| PCIe                 | x1 / x2 / x4                                      |
| SD Card              | Full-size SD slot (SPI and 4-bit modes)           |
| SPI Flash            | Quad SPI                                          |
| User LEDs            | 6 (M21, N20, L21, AA21, R19, M16)                 |

Source: [LiteX platform file for the NeTV2](https://github.com/litex-hub/litex-boards/blob/master/litex_boards/platforms/kosagi_netv2.py)

## FPGA Device Variants

| Variant  | Device String       |
| -------- | ------------------- |
| `a7-35`  | `xc7a35t-fgg484-2`  |
| `a7-100` | `xc7a100t-fgg484-2` |

Both variants share the same FGG484 package and identical pin assignments, so
everything below applies to either. CI builds variant-specific bitstreams:
`*-netv2-a7-35t` and `*-netv2-a7-100t`.

Source: [LiteX platform file for the NeTV2](https://github.com/litex-hub/litex-boards/blob/master/litex_boards/platforms/kosagi_netv2.py)

## Host Connections

The NeTV2 is designed to sit on top of a Raspberry Pi, connecting through the
40-pin GPIO header and optionally through a PCIe link. The two hosts below are
the development boards on the separate `iot.welland.mithis.com` network; their
addresses, models and SSH details are on the site page under
[NeTV2 development hosts](../sites/welland.md#netv2-development-hosts-separate-network).
Five production boards are installed ([NeTV2](../sites/welland.md#netv2)), of
which four are the working fleet: pi18 was already offline at the 2026-03-17
survey. All five are RPi 3B+ hosts without PCIe, carrying the same GPIO JTAG and
GPIO UART wiring as rpi3-netv2 — which says nothing about the tool they are
driven with, see [Programming with openFPGALoader](#programming-with-openfpgaloader).

Probed 2026-03-09.

| Host       | FPGA Variant      | JTAG IDCODE  | Tool [†](#programming-with-openfpgaloader) |
| ---------- | ----------------- | ------------ | ----------------------- |
| rpi5-netv2 | XC7A100T-FGG484-2 | `0x03631093` | openFPGALoader (rp1pio) |
| rpi3-netv2 | XC7A35T-FGG484-2  | `0x0362D093` | OpenOCD (bcm2835gpio)   |

† Which tool rpi5-netv2 actually has is unsettled; see
[Programming with openFPGALoader](#programming-with-openfpgaloader).

### rpi5-netv2

- **Board type**: Bare developer NeTV2 (unpackaged)
- **GPIO connection**: JTAG (4 signals + SRST) and UART (TX/RX)
- **PCIe connection**: Gen2 x1 via RPi5 PCIe connector
- **lspci**: Xilinx device with vendor `10ee`, device `7011`

### rpi3-netv2

- **Board type**: Stock packaged NeTV2 (as shipped by bunnie via Crowd Supply)
- **GPIO connection**: JTAG (4 signals + SRST) and UART (TX/RX)
- **PCIe connection**: Not available (RPi3 has no PCIe interface)

## JTAG via RPi GPIO

The NeTV2 JTAG interface is directly wired to specific Raspberry Pi GPIO pins.
The GPIO-to-JTAG pin mapping originates from the
[alphamax-rpi OpenOCD configuration](https://github.com/alphamaxmedia/netv2mvp-scripts/blob/master/alphamax-rpi.cfg)
in the NeTV2 MVP scripts.

| JTAG Signal | RPi GPIO | RPi Header Pin | Direction (from RPi) |
| ----------- | -------- | -------------- | -------------------- |
| TCK         | GPIO4    | Pin 7          | Output               |
| TMS         | GPIO17   | Pin 11         | Output               |
| TDI         | GPIO27   | Pin 13         | Output               |
| TDO         | GPIO22   | Pin 15         | Input                |
| SRST        | GPIO24   | Pin 18         | Output               |

### Programming with openFPGALoader

openFPGALoader is the primary tool for programming the NeTV2. It supports
multiple JTAG transports over the same GPIO wiring.

#### RPi 3B+ (GPIO bitbang, current deployed hosts)

On RPi 3B+ hosts (pi10, pi12, pi14 and pi16 — pi18 was offline at the
2026-03-17 survey; see [NeTV2](../sites/welland.md#netv2)), openFPGALoader uses
`libgpiod` to drive the JTAG signals through the Linux GPIO subsystem:

```console
$ sudo openFPGALoader --cable libgpiod --pins 27:22:4:17 design.bit
```

To write the bitstream to the on-board SPI flash so it survives a power cycle:

```console
$ sudo openFPGALoader --cable libgpiod --pins 27:22:4:17 --write-flash design.bit
```

Pin order: `TDI:TDO:TCK:TMS`.

This works but is slow (~5 MHz effective JTAG clock) due to GPIO bitbang
overhead.

:::{todo}
The two sources disagree on what actually programs the production RPi 3B+
boards. The board specification (undated) gives the openFPGALoader `libgpiod`
commands above; the Welland site survey of 2026-03-17 records instead that each
production NeTV2 "is programmed via OpenOCD GPIO bitbang JTAG through the RPi's
GPIO header", which is the same wiring but the other tool — and it is the tool
rpi3-netv2 is documented with below. Check one of pi10, pi12, pi14 or pi16,
keep the winner and record the date.
:::

#### RPi 5 (GPIO bitbang, works today, slow)

:::{warning}
Reconfiguring the FPGA over JTAG while its PCIe endpoint is enumerated is a
surprise removal, and it crashes the BCM2712 root complex. On rpi5-netv2 detach
the endpoint before any of the JTAG commands in this section or the next one
([PCIe and JTAG interact](../sites/welland.md#pcie-and-jtag-interact)):

```console
$ lspci -d 10ee:7011
$ echo 1 | sudo tee /sys/bus/pci/devices/0001:01:00.0/remove
```

Take the address from the first command; on a Pi 5 the endpoint enumerates at
`0001:01:00.0`, the slot the Acorn hosts use. Bring it back afterwards with
`echo 1 | sudo tee /sys/bus/pci/rescan`, or by rebooting.
:::

On RPi 5 hosts, the same `libgpiod` cable works but is even slower because the
RPi 5's RP1 I/O controller adds latency to sysfs GPIO access:

```console
$ sudo openFPGALoader --cable libgpiod --pins 27:22:4:17 design.bit
```

#### RPi 5 (RP1 PIO JTAG, not in upstream openFPGALoader)

The `rp1pio` cable drives JTAG through the RP1's PIO peripheral instead of
bit-banging it, which is much faster than the `libgpiod` cable above. It is not
in upstream openFPGALoader; it is installed from the `openfpgaloader-rp1pio`
package, which brings the `librp1jtag0` shared library with it (see
[Packages](../packages.md)). The same PCIe detach applies before this command.

```console
$ sudo openFPGALoader --cable rp1pio --pins 27:22:4:17 design.bit
```

The sources behind the package:

- openFPGALoader with RP1 PIO JTAG support, pending upstream:
  [mithro/openFPGALoader (feature/rp1-jtag-netv2)](https://github.com/mithro/openFPGALoader/tree/feature/rp1-jtag-netv2)
- The RP1 JTAG shared library: [mithro/rp1-jtag](https://github.com/mithro/rp1-jtag)

:::{todo}
† Four artefacts disagree about how rpi5-netv2 is programmed, and none of them
settles it:

- The pin-mapping notes name `openFPGALoader (rp1pio)` as its tool.
- The board specification calls RP1 PIO JTAG a capability still pending
  upstream, not something running here.
- The 2026-03-09 SSH survey found OpenOCD installed on rpi5-netv2 and no
  openFPGALoader at all
  ([NeTV2 development hosts](../sites/welland.md#netv2-development-hosts-separate-network)).
- [`alphamax-rpi5-sysfsgpio.cfg`](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/designs/pcie-enumeration/openocd/alphamax-rpi5-sysfsgpio.cfg)
  in test-designs is a working OpenOCD Pi 5 configuration for this board —
  `sysfsgpio jtag_nums 575 588 598 593` and `sysfsgpio srst_num 595`, which is
  the Pi 5 RP1 gpiochip base 571 plus GPIO 4, 17, 27, 22 and 24, the same
  wiring as the JTAG table above. It corroborates the survey: an OpenOCD path
  for the Pi 5 exists and is checked in.

To settle it today: if the `openfpgaloader-rp1pio` package is installed on the
host, run `sudo openFPGALoader --cable rp1pio --pins 27:22:4:17 --detect`; if it
is not, use OpenOCD with that configuration. Keep the winner, delete the losers
and record the date.
:::

#### Future: NeTV2 board definition in openFPGALoader

Once the NeTV2 board definition is landed upstream in openFPGALoader, the pin
mapping will be built in and the command simplifies to:

```console
$ sudo openFPGALoader -b netv2 design.bit
```

This is tracked in the openFPGALoader fork:
[mithro/openFPGALoader (feature/rp1-jtag-netv2)](https://github.com/mithro/openFPGALoader/tree/feature/rp1-jtag-netv2)

### Programming with OpenOCD

rpi3-netv2 uses OpenOCD 0.10.x with the `bcm2835gpio` interface instead:

```console
$ sudo openocd -f ~/netv2/alphamax-rpi.cfg -c 'init; pld load 0 <bitstream>; exit'
```

The configuration sets `bcm2835gpio_jtag_nums 4 17 27 22`,
`bcm2835gpio_srst_num 24` and peripheral base `0x3F000000`, which is the same
wiring as the table above. The Pi 5 equivalent, using the `sysfsgpio` adapter
because the RP1 has no BCM2835 peripheral window, is
[`alphamax-rpi5-sysfsgpio.cfg`](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/designs/pcie-enumeration/openocd/alphamax-rpi5-sysfsgpio.cfg)
in test-designs.

:::{note}
`pld load 0` takes a device index, not a device name: that is the OpenOCD 0.10.x
syntax.
:::

## Serial / UART

### Primary UART (via RPi GPIO)

The FPGA's UART pins connect to the RPi's GPIO UART through the 40-pin stacking
header. This is a direct GPIO connection, with no USB serial adapter anywhere in
the path.

| Board | Signal  | FPGA Pin | RPi GPIO     | RPi Header Pin |
| ----- | ------- | -------- | ------------ | -------------- |
| NeTV2 | FPGA TX | E14      | GPIO15 (RXD) | Pin 10         |
| NeTV2 | FPGA RX | E13      | GPIO14 (TXD) | Pin 8          |

Both pins are LVCMOS33. The FPGA's TX connects to the RPi's RX (GPIO15) and vice
versa.

Source: [LiteX platform file for the NeTV2](https://github.com/litex-hub/litex-boards/blob/master/litex_boards/platforms/kosagi_netv2.py)

### Serial Device by Host

Which kernel device the GPIO UART appears as depends on the Raspberry Pi model:

| Host       | RPi GPIO UART Device | Symlink          | Reason                              |
| ---------- | -------------------- | ---------------- | ----------------------------------- |
| rpi5-netv2 | `/dev/ttyAMA0`       | —                | RP1 PL011 UART on GPIO14/15         |
| rpi3-netv2 | `/dev/ttyS0`         | `/dev/serial0`   | Mini UART (Bluetooth claims PL011)  |

The production RPi 3B+ hosts are not in this table. By the same reasoning they
should also be on the mini UART at `/dev/ttyS0`, but that is an inference from
the Pi 3 model, not a measurement: the 2026-03-17 Welland survey wrote
`/dev/ttyAMA0` for them. Check before relying on it.

### rpi5-netv2 Specifics

- After stopping `serial-getty`, GPIO14/15 revert to plain GPIO mode. Run
  `pinctrl set 14 a4; pinctrl set 15 a4` to restore the UART function
  (ALT4 = TXD0/RXD0).

### rpi3-netv2 Specifics

- `netv2-status.js`, a pm2-managed Node.js monitoring app, continuously sends
  `json on` commands to the FPGA over the serial port. Stop it with
  `pm2 stop all` (the binary is
  `/home/pi/n/bin/node /home/pi/n/lib/node_modules/pm2/bin/pm2`).
- `serial-getty` must also be stopped.
- Bluetooth (`hciattach`) uses `/dev/ttyAMA0`, the PL011, so the GPIO UART is
  the mini UART at `/dev/ttyS0`.

:::{warning}
Both the getty and, on rpi3-netv2, `netv2-status.js` hold the port open and will
eat or corrupt the design's output. Stop them before running a test, and
remember that stopping the getty on the Pi 5 also drops the pin mux.
:::

### UART Test Parameters

| Parameter        | Value                                                             |
| ---------------- | ----------------------------------------------------------------- |
| Baud rate        | 115200                                                            |
| Test args        | `--port /dev/ttyAMA0 --board netv2 --skip-banner`                 |
| `--skip-banner`  | Required because OpenOCD programming takes ~10s; BIOS banner is missed |

:::{warning}
The recorded `--port /dev/ttyAMA0` is the Pi 5 device and fails on a Pi 3, where
the GPIO UART is `/dev/ttyS0`: change `--port` to match the host. The
`--skip-banner` row belongs to the OpenOCD path on rpi3-netv2 — it is that
tool's ~10s programming time that loses the banner, so a faster loader may not
need it.
:::

### Secondary UART (via PCIe "hax" pins)

| Signal | FPGA Pin | PCIe Hax Pin |
| ------ | -------- | ------------ |
| TX     | B17      | hax7         |
| RX     | A18      | hax8         |

Both are LVCMOS33. These auxiliary pins on the PCIe connector provide a second
serial channel. They are reachable only over the PCIe connector, which means
rpi5-netv2 alone.

## PMOD / GPIO Loopback

The NeTV2 GPIO loopback uses FPGA pins E13 (input) and E14 (output) — the same
pins as the primary UART. It is a 1-bit loopback through the RPi's GPIO14/15.

| Drive RPi GPIO | FPGA Pin (Input) | Read RPi GPIO | FPGA Pin (Output) |
| -------------- | ---------------- | ------------- | ----------------- |
| GPIO14         | E13              | GPIO15        | E14               |

## DDR3 SDRAM

512 MB DDR3 on a 32-bit wide bus, 4 byte lanes, at 1.5V.

| Signal        | FPGA Pins                                      | I/O Standard  |
| ------------- | ---------------------------------------------- | ------------- |
| A[13:0]       | U6 V4 W5 V5 AA1 Y2 AB1 AB3 AB2 Y3 W6 Y1 V2 AA3 | SSTL15_R      |
| BA[2:0]       | U5 W4 V7                                       | SSTL15_R      |
| DQ[7:0]       | C2 F1 B1 F3 A1 D2 B2 E2                        | SSTL15_R      |
| DQ[15:8]      | J5 H3 K1 H2 J1 G2 H5 G3                        | SSTL15_R      |
| DQ[23:16]     | N2 M6 P1 N5 P2 N4 R1 P6                        | SSTL15_R      |
| DQ[31:24]     | K3 M2 K4 M3 J6 L5 J4 K6                        | SSTL15_R      |
| DQS_P[3:0]    | E1 K2 P5 M1                                    | DIFF_SSTL15_R |
| DQS_N[3:0]    | D1 J2 P4 L1                                    | DIFF_SSTL15_R |
| DM[3:0]       | G1 H4 M5 L3                                    | SSTL15_R      |
| CLK_P / CLK_N | R3 / R2                                        | DIFF_SSTL15_R |
| CKE           | Y8                                             | SSTL15_R      |
| ODT           | W9                                             | SSTL15_R      |
| CS_N          | V9                                             | SSTL15_R      |
| RAS_N         | Y9                                             | SSTL15_R      |
| CAS_N         | Y7                                             | SSTL15_R      |
| WE_N          | V8                                             | SSTL15_R      |
| RESET_N       | AB5                                            | LVCMOS15      |

Source: [LiteX platform file for the NeTV2](https://github.com/litex-hub/litex-boards/blob/master/litex_boards/platforms/kosagi_netv2.py)

## PCIe

The NeTV2 supports PCIe x1, x2 and x4 configurations. All share the same clock
and reset pins. Only rpi5-netv2 has a PCIe connection; the RPi 3 has no PCIe.

| Signal        | FPGA Pin(s) | Notes           |
| ------------- | ----------- | --------------- |
| RST_N         | E18         | LVCMOS33        |
| CLK_P / CLK_N | F10 / E10   | Reference clock |

### Lane assignments

| Config    | RX_P | RX_N | TX_P | TX_N |
| --------- | ---- | ---- | ---- | ---- |
| x1 lane 0 | D11  | C11  | D5   | C5   |
| x2 lane 1 | B10  | A10  | B6   | A6   |
| x4 lane 2 | D9   | C9   | D7   | C7   |
| x4 lane 3 | B8   | A8   | B4   | A4   |

### PCIe Detection (rpi5-netv2)

When a bitstream is loaded and the board is connected to the RPi 5 over PCIe
Gen2 x1, the FPGA enumerates as a Xilinx device:

| Parameter | Value                 |
| --------- | --------------------- |
| Vendor ID | `10ee` (Xilinx)       |
| Device ID | `7011`                |
| Link      | Gen2 x1               |
| Command   | `lspci -d 10ee:7011`  |

:::{warning}
As of 2026-03-09, the NeTV2 FPGA is not currently enumerating on the RPi5's PCIe
bus: only the RP1 south bridge is visible in `lspci`. The site page records this
under [Known faults](../sites/welland.md#known-faults) as needing a bitstream
loaded first. Until it enumerates, the detach step above finds nothing to
detach — and the moment it does enumerate, that step becomes mandatory.
:::

Source: [LiteX platform file for the NeTV2](https://github.com/litex-hub/litex-boards/blob/master/litex_boards/platforms/kosagi_netv2.py)

## RMII Ethernet

The NeTV2 has its own Ethernet PHY with an RMII interface, providing a 100Base-T
network connection independent of the Raspberry Pi's network.

| Signal       | FPGA Pin | I/O Standard |
| ------------ | -------- | ------------ |
| ref_clk      | D17      | LVCMOS33     |
| rst_n        | F16      | LVCMOS33     |
| rx_data[1:0] | A20 B18  | LVCMOS33     |
| crs_dv       | C20      | LVCMOS33     |
| tx_en        | A19      | LVCMOS33     |
| tx_data[1:0] | C18 C19  | LVCMOS33     |
| mdc          | F14      | LVCMOS33     |
| mdio         | F13      | LVCMOS33     |
| rx_er        | B20      | LVCMOS33     |
| int_n        | D21      | LVCMOS33     |

The RMII reference clock runs at 50 MHz (pin D17).

Source: [LiteX platform file for the NeTV2](https://github.com/litex-hub/litex-boards/blob/master/litex_boards/platforms/kosagi_netv2.py)

## HDMI

Two HDMI inputs and two HDMI outputs. All HDMI signals use the TMDS_33 I/O
standard.

### HDMI Input 0

| Signal            | FPGA Pins | Notes      |
| ----------------- | --------- | ---------- |
| CLK_P / CLK_N     | L19 / L20 | Inverted   |
| DATA0_P / DATA0_N | K21 / K22 | Inverted   |
| DATA1_P / DATA1_N | J20 / J21 | Inverted   |
| DATA2_P / DATA2_N | J22 / H22 | Inverted   |
| SCL / SDA         | T18 / V18 | I2C (EDID) |

### HDMI Input 1

| Signal            | FPGA Pins   | Notes        |
| ----------------- | ----------- | ------------ |
| CLK_P / CLK_N     | Y18 / Y19   | Inverted     |
| DATA0_P / DATA0_N | AA18 / AB18 | Not inverted |
| DATA1_P / DATA1_N | AA19 / AB20 | Inverted     |
| DATA2_P / DATA2_N | AB21 / AB22 | Inverted     |
| SCL / SDA         | W17 / R17   | SCL inverted |

### HDMI Output 0

| Signal            | FPGA Pins | Notes    |
| ----------------- | --------- | -------- |
| CLK_P / CLK_N     | W19 / W20 | Inverted |
| DATA0_P / DATA0_N | W21 / W22 |          |
| DATA1_P / DATA1_N | U20 / V20 |          |
| DATA2_P / DATA2_N | T21 / U21 |          |

### HDMI Output 1

| Signal            | FPGA Pins | Notes    |
| ----------------- | --------- | -------- |
| CLK_P / CLK_N     | G21 / G22 | Inverted |
| DATA0_P / DATA0_N | E22 / D22 | Inverted |
| DATA1_P / DATA1_N | C22 / B22 | Inverted |
| DATA2_P / DATA2_N | B21 / A21 | Inverted |

Source: [LiteX platform file for the NeTV2](https://github.com/litex-hub/litex-boards/blob/master/litex_boards/platforms/kosagi_netv2.py)

## SPI Flash

On-board quad SPI flash for persistent bitstream storage, used by
`--write-flash` above. Quad SPI mode is available through the `spiflash4x` pad
group.

| Signal     | FPGA Pin | I/O Standard |
| ---------- | -------- | ------------ |
| CS_N       | T19      | LVCMOS33     |
| MOSI (DQ0) | P22      | LVCMOS33     |
| MISO (DQ1) | R22      | LVCMOS33     |
| VPP (DQ2)  | P21      | LVCMOS33     |
| HOLD (DQ3) | R21      | LVCMOS33     |

## SD Card

A full-size SD slot, usable in either SPI or 4-bit mode. The two modes share the
clock pin and reuse the same data pins differently.

### SPI Mode

| Signal | FPGA Pin       |
| ------ | -------------- |
| CLK    | K18            |
| CS_N   | M13            |
| MOSI   | L13 (PULLUP)   |
| MISO   | L15 (PULLUP)   |

### 4-bit Mode

| Signal    | FPGA Pin                     |
| --------- | ---------------------------- |
| CLK       | K18                          |
| CMD       | L13 (PULLUP)                 |
| DATA[3:0] | L15 L16 K14 M13 (PULLUP)     |

## User LEDs

| LED | FPGA Pin | I/O Standard |
| --- | -------- | ------------ |
| 0   | M21      | LVCMOS33     |
| 1   | N20      | LVCMOS33     |
| 2   | L21      | LVCMOS33     |
| 3   | AA21     | LVCMOS33     |
| 4   | R19      | LVCMOS33     |
| 5   | M16      | LVCMOS33     |

## Programming

See [JTAG via RPi GPIO](#jtag-via-rpi-gpio) above for the full openFPGALoader
and OpenOCD commands, and for which host uses which.

### Quick Reference

On rpi5-netv2, detach the PCIe endpoint first — see the warning above.

Volatile load on an RPi 3B+ or RPi 5, GPIO bitbang:

```console
$ sudo openFPGALoader --cable libgpiod --pins 27:22:4:17 design.bit
```

Persistent SPI flash on an RPi 3B+ or RPi 5, GPIO bitbang. This overwrites
whatever bitstream the flash already holds, so keep a copy first:

```console
$ sudo openFPGALoader --cable libgpiod --pins 27:22:4:17 --write-flash design.bit
```

Volatile load on rpi3-netv2, which is driven with OpenOCD instead:

```console
$ sudo openocd -f ~/netv2/alphamax-rpi.cfg -c 'init; pld load 0 <bitstream>; exit'
```

Once the NeTV2 board definition is upstream:

```console
$ sudo openFPGALoader -b netv2 design.bit
```

## LiteX Integration

| Property        | Value                                                  |
| --------------- | ------------------------------------------------------ |
| Platform module | `litex_boards.platforms.kosagi_netv2`                  |
| Target module   | `litex_boards.targets.kosagi_netv2`                    |
| Default clock   | `clk50` (50 MHz, pin J19)                              |
| Programmer      | openFPGALoader (`libgpiod`, pins 27:22:4:17) |
| Toolchain       | Vivado (proprietary) or openXC7 (open source)          |

Source: [LiteX platform file for the NeTV2](https://github.com/litex-hub/litex-boards/blob/master/litex_boards/platforms/kosagi_netv2.py)

## References

- LiteX platform file:
  <https://github.com/litex-hub/litex-boards/blob/master/litex_boards/platforms/kosagi_netv2.py>
- NeTV2 FPGA reference design: <https://github.com/AlphamaxMedia/netv2-fpga>
- NeTV2 MVP scripts: <https://github.com/alphamaxmedia/netv2mvp-scripts>. This
  page's JTAG pin mapping comes from its
  [alphamax-rpi OpenOCD configuration](https://github.com/alphamaxmedia/netv2mvp-scripts/blob/master/alphamax-rpi.cfg).
- OpenOCD configuration for the Pi 5, in test-designs:
  [alphamax-rpi5-sysfsgpio.cfg](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/designs/pcie-enumeration/openocd/alphamax-rpi5-sysfsgpio.cfg)
- bunnie's blog on the NeTV2 design: <https://www.bunniestudios.com/blog/?p=4842>
- Crowd Supply campaign: <https://www.crowdsupply.com/alphamax/netv2>
- NeTV2 schematic: not available online. The pin-mapping notes cited a local
  PDF that is not in any repository.

:::{todo}
Find or publish a canonical URL for the NeTV2 schematic. Until then the only
public hardware reference is the FPGA reference design repository above.
:::
