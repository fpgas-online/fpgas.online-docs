# Fomu EVT

The Fomu is a tiny FPGA board that fits inside a USB Type-A port, designed by
Sean Cross (xobs) and Tim Ansell; the EVT (Engineering Validation Test)
revision is the one used in the fpgas.online test infrastructure. It is built
around a Lattice iCE40UP5K with native USB — the FPGA has dedicated USB I/O
pins, so there is no external PHY and no FTDI — which means the board enumerates
as a USB device by itself and is programmed over USB DFU rather than over JTAG.
Two boards are installed, both at Welland, on Raspberry Pi 3B+ hosts with a USB
protocol analyser inline; their addresses, MACs and analysers are in the
[Fomu EVT host table](../sites/welland.md#fomu-evt). This page covers the board
itself, its iCE40 pin assignments for each on-board peripheral, how it is
programmed and monitored, and how it is wired to its Raspberry Pi.

## Key Specifications

| Parameter            | Value                                     |
| -------------------- | ----------------------------------------- |
| FPGA                 | Lattice iCE40UP5K-SG48                    |
| Package              | SG48 (48-pin QFN)                         |
| Logic cells          | 5,280 LUT4s                               |
| SPRAM                | 128 KB (4 x 32 KB blocks)                 |
| DPRAM (EBR)          | 120 Kbit (15 x 8 Kbit blocks)             |
| DSP blocks           | 8 (16x16 multiply-accumulate)             |
| System clock         | 48 MHz (pin 44, LVCMOS33)                 |
| Internal oscillators | 48 MHz HFOSC, 10 kHz LFOSC                |
| USB                  | Native USB 1.1 Full Speed (ValentyUSB core) |
| SPI Flash            | Quad SPI for bitstream storage            |
| RGB LED              | 1 (active-low, pins R=40, G=39, B=41)     |
| Touch pads           | 4 (pins 48, 47, 46, 45)                   |
| PMOD connectors      | 2 half-PMOD (4 signal pins each)          |
| External SDRAM       | None (SPRAM only)                         |
| Form factor          | Fits inside a USB Type-A port             |

:::{note}
The two source documents disagree about the block RAM. The board specification
above says 120 Kbit as 15 blocks of 8 Kbit; the pin-mapping document says 30 EBR
blocks totalling 15 KB. The totals agree (120 Kbit is 15 KB) — it is the block
count and block size that differ, and the iCE40UP5K datasheet is the tie-breaker
before either figure is quoted elsewhere.
:::

Source: [LiteX platform file for the Fomu EVT](https://github.com/litex-hub/litex-boards/blob/master/litex_boards/platforms/kosagi_fomu_evt.py),
[Fomu hardware repository](https://github.com/im-tomu/fomu-hardware)

## USB Interface

The Fomu connects directly to a USB port and implements a full USB 1.1 Full
Speed device using the ValentyUSB soft core on the iCE40UP5K. No external USB
PHY is needed — the iCE40UP5K has dedicated USB I/O pins.

| Signal    | iCE40 Pin | I/O Standard | Description                             |
| --------- | --------- | ------------ | --------------------------------------- |
| D+        | 34        | LVCMOS33     | USB data positive                       |
| D-        | 37        | LVCMOS33     | USB data negative                       |
| Pull-up   | 35        | LVCMOS33     | 1.5K pullup for Full Speed identification |
| Pull-down | 36        | LVCMOS33     | Pulldown resistor control               |

All USB pins use the LVCMOS33 I/O standard.

The USB interface supports DFU (Device Firmware Upgrade) for bitstream loading,
as well as acting as a CDC-ACM serial port or a custom USB device depending on
the loaded design.

Source: [LiteX platform file for the Fomu EVT](https://github.com/litex-hub/litex-boards/blob/master/litex_boards/platforms/kosagi_fomu_evt.py)

## Serial (UART)

The EVT board has a serial port that can be used for debugging. In practice the
USB interface (CDC-ACM or DFU) is the primary communication channel. How these
two pins reach the Pi is covered under
[UART interface](#uart-interface).

| Signal | FPGA Pin | I/O Standard | Notes       |
| ------ | -------- | ------------ | ----------- |
| RX     | 21       | LVCMOS33     |             |
| TX     | 13       | LVCMOS33     | Has PULLUP  |

Source: [LiteX platform file for the Fomu EVT](https://github.com/litex-hub/litex-boards/blob/master/litex_boards/platforms/kosagi_fomu_evt.py)

## SPI Flash

The Fomu stores its bitstream in an external SPI flash on dedicated iCE40 SPI
pins. The iCE40UP5K loads the bitstream from flash automatically on power-up.

| Signal     | iCE40 Pin | I/O Standard |
| ---------- | --------- | ------------ |
| CS_N       | 16        | LVCMOS33     |
| CLK        | 15        | LVCMOS33     |
| MOSI (DQ0) | 14        | LVCMOS33     |
| MISO (DQ1) | 17        | LVCMOS33     |
| WP (DQ2)   | 18        | LVCMOS33     |
| HOLD (DQ3) | 19        | LVCMOS33     |

Quad SPI (4x) mode is supported, via the `spiflash4x` resource in the LiteX
platform file.

Source: [LiteX platform file for the Fomu EVT](https://github.com/litex-hub/litex-boards/blob/master/litex_boards/platforms/kosagi_fomu_evt.py)

## RGB LED

The Fomu has a single RGB LED driven by the iCE40UP5K's internal LED driver IP
(active-low accent LED and the `SB_RGBA_DRV` primitive).

| Color | FPGA Pin | Active |
| ----- | -------- | ------ |
| Red   | 40       | Low    |
| Green | 39       | Low    |
| Blue  | 41       | Low    |

The `user_led_n` signal (active-low) is on pin 41 (blue).

## Touch Pads

The EVT board has 4 capacitive touch pads that can be used as user inputs.

| Pad     | FPGA Pin |
| ------- | -------- |
| Touch 0 | 48       |
| Touch 1 | 47       |
| Touch 2 | 46       |
| Touch 3 | 45       |

These are directly connected to FPGA I/O pins. Capacitive touch sensing is
implemented in the FPGA fabric.

## Buttons

Two active-low buttons:

| Button | FPGA Pin | I/O Standard |
| ------ | -------- | ------------ |
| BTN0   | 42       | LVCMOS33     |
| BTN1   | 38       | LVCMOS33     |

## PMOD Connectors

The EVT board has two half-PMOD connectors — a standard 6-pin PMOD carrying 4
signals plus GND and VCC, 4 signal pins each. The loopback gateware drives them
against each other; see [PMOD / GPIO loopback](#pmod--gpio-loopback).

### PMODA_N

| Index | FPGA Pin |
| ----- | -------- |
| 0     | 28       |
| 1     | 27       |
| 2     | 26       |
| 3     | 23       |

### PMODB_N

| Index | FPGA Pin |
| ----- | -------- |
| 0     | 48       |
| 1     | 47       |
| 2     | 46       |
| 3     | 45       |

Note: PMODB_N shares its pins with the touch pads.

Source: [LiteX platform file for the Fomu EVT](https://github.com/litex-hub/litex-boards/blob/master/litex_boards/platforms/kosagi_fomu_evt.py)

## I2C

| Signal | iCE40 Pin | I/O Standard |
| ------ | --------- | ------------ |
| SCL    | 12        | LVCMOS18     |
| SDA    | 20        | LVCMOS18     |

Note that the I2C interface uses LVCMOS18 (1.8V) rather than the 3.3V used by
every other pin on the board.

## Debug Header

The Fomu EVT has a debug connector with 6 pins:

| Index | iCE40 Pin |
| ----- | --------- |
| dbg:0 | 20        |
| dbg:1 | 12        |
| dbg:2 | 11        |
| dbg:3 | 25        |
| dbg:4 | 10        |
| dbg:5 | 9         |

## Programming

### USB DFU (primary method)

The Fomu is programmed over USB using the DFU (Device Firmware Upgrade)
protocol. The `dfu-util` tool is used:

```console
# List connected DFU devices.
$ dfu-util -l
# Program a bitstream.
$ dfu-util -D design.dfu
# Program with explicit device selection.
$ dfu-util -d 1209:5bf0 -D design.dfu
```

The DFU bootloader resides in the SPI flash and provides a USB DFU interface
when no valid application is present or when the user triggers DFU mode. The
test infrastructure drives the same interface through `openFPGALoader` instead;
see [Programming interface](#programming-interface).

### IceStorm Programmer (iceprog)

For direct SPI flash programming (this requires an external SPI programmer, so
it is not something that can be done from the Pi host):

```console
$ iceprog design.bin
```

Source: [Fomu Workshop](https://workshop.fomu.im)

## USB monitoring

Each Fomu host has an inline USB protocol analyser between the Fomu and the Pi's
USB port, so the Fomu's native USB traffic — DFU programming, CDC-ACM serial,
custom USB protocols — can be captured and analysed without modifying the FPGA
design or the host software. Which analyser is on which host, along with the
hosts' addresses and the Fomu's `1209:5bf0` VID:PID and DFU version, is in the
[Fomu EVT host table](../sites/welland.md#fomu-evt).

| Host | Analyzer     | USB VID:PID |
| ---- | ------------ | ----------- |
| pi17 | OpenVizsla   | `1d50:607c` |
| pi21 | Cythion/LUNA | `16d0:05a5` |

### OpenVizsla (pi17)

The [OpenVizsla](https://github.com/openvizsla/ov_ftdi) is an open-source USB
protocol analyzer. It captures USB traffic between the Fomu and the RPi host for
debugging and test verification.

### Cythion/LUNA (pi21)

The [Cythion](https://greatscottgadgets.com/cythion/) (from Great Scott Gadgets)
is a USB multitool running the [LUNA](https://github.com/greatscottgadgets/luna)
USB framework. It provides USB protocol analysis, traffic capture, and can also
act as a USB host or device for testing. It is connected inline between the Fomu
and the RPi host.

:::{note}
The host names `pi17` and `pi21` here are the flat `piNN` names used before the
2026-08-23 renumbering, and neither host has been re-probed since the survey.
The old addresses no longer resolve; derive the current name and address of each
host from its switch port using the
[Fomu EVT host table](../sites/welland.md#fomu-evt). The Welland
[Known faults](../sites/welland.md#known-faults) also record pi21's Cythion/LUNA
and its Fomu as offline at that survey.
:::

Source: dnsmasq `pibs.conf` on tweed, verified 2026-03-17.

## LiteX Integration

| Property        | Value                                             |
| --------------- | ------------------------------------------------- |
| Platform module | `litex_boards.platforms.kosagi_fomu_evt`          |
| Target module   | `litex_boards.targets.kosagi_fomu`                |
| Default clock   | `clk48` (48 MHz, pin 44)                          |
| Programmer      | IceStorm (`iceprog`)                              |
| Toolchain       | Yosys + nextpnr-ice40 (open source, IceStorm flow) |

The pin-mapping notes give the toolchain as `icestorm` / `nextpnr-ice40`, which
is the same open-source flow.

Source: [LiteX platform file for the Fomu EVT](https://github.com/litex-hub/litex-boards/blob/master/litex_boards/platforms/kosagi_fomu_evt.py)

## Wiring to the Raspberry Pi

How the board is connected on the two Welland hosts, and what has to be true on
the Pi before a test will pass.

### Physical form factor

The Fomu EVT is a tiny PCB that fits inside a USB-A connector. On pi17 and pi21
the Fomu connects to the Pi in two ways:

- **GPIO header**: the Fomu sits directly on the Pi GPIO header as a standard
  HAT, connecting UART and GPIO signals.
- **USB**: the Fomu's USB-A connector plugs into the Pi's USB port, through the
  inline USB analyser — OpenVizsla on pi17, Cythion/LUNA on pi21, see
  [USB monitoring](#usb-monitoring).

### Programming interface

The Fomu boots from SPI flash into a DFU bootloader. Programming loads a new
bitstream into volatile SRAM over USB DFU.

| Parameter      | Value                                |
| -------------- | ------------------------------------ |
| Interface      | USB DFU (iCE40 SRAM load)            |
| USB VID:PID    | `1209:5bf0` (DFU bootloader)         |
| Tool           | `openFPGALoader -b fomu <bitstream>` |
| Bitstream type | `.bin` (volatile SRAM load)          |
| Bootloader     | DFU Bootloader v2.0.4                |

#### DFU bootloader timeout

The DFU bootloader has a timeout of about 3 minutes. If no DFU activity occurs
within that window, the bootloader warm-boots the iCE40 to load the user
bitstream from SPI flash. The user bitstream typically has no USB, so the Fomu
disappears from USB.

:::{warning}
A Fomu that has vanished from `lsusb` is usually not broken — it has timed out
of DFU, or it is running a test bitstream with no USB core. The recovery is a
PoE power cycle, which resets the Fomu and restarts the DFU bootloader.
The
[hardware verification script](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/verify_hardware.py)
(`verify_hardware.py`) does this automatically: it triggers a PoE reset and
retries programming when DFU is unavailable. Do not go looking for a dead board before power-cycling it.
:::

### USB connection to the Pi

The USB pins are listed under [USB Interface](#usb-interface). The USB interface
is active only when the DFU bootloader or a USB-enabled bitstream is loaded. The
custom test bitstreams (UART echo, GPIO loopback) do not include USB, so the
Fomu disappears from USB after programming — which is expected, not a fault.

### UART interface

The FPGA's serial pins (TX on iCE40 pin 13, RX on pin 21, see
[Serial (UART)](#serial-uart)) connect to the Pi's GPIO UART through the GPIO
header. This is a direct connection, **not** through USB.

| Signal          | iCE40 Pin | Direction | I/O Standard      |
| --------------- | --------- | --------- | ----------------- |
| TX (FPGA → RPi) | 13        | Output    | LVCMOS33 (PULLUP) |
| RX (RPi → FPGA) | 21        | Input     | LVCMOS33          |

| Parameter  | Value                                            |
| ---------- | ------------------------------------------------ |
| RPi device | `/dev/serial0` → `/dev/ttyAMA0`                  |
| Baud rate  | 115200                                           |
| Test args  | `--port /dev/serial0 --board fomu --skip-banner` |

On pi17 and pi21 (Raspberry Pi 3) `hciuart` is inactive, so `/dev/ttyAMA0` (the
PL011) is available on GPIO14/GPIO15 for the FPGA UART. `serial-getty` must be
masked, not just stopped, or it will come back and consume the serial data.

:::{todo}
Document the exact Fomu-to-RPi GPIO header pin mapping from iCE40 pins 13, 21 to
RPi GPIO14, GPIO15.

The method is the
[pin-ID design](pin-id.md): load it on the Fomu and read back which Pi GPIO
carries which FPGA pin's identity.
:::

#### UART pre-test requirements

```console
# Mask prevents systemd from restarting the serial login console.
$ sudo systemctl mask serial-getty@ttyAMA0
# Stop the currently running instance.
$ sudo systemctl stop serial-getty@ttyAMA0
# Kill any remaining process holding the port.
$ sudo fuser -k /dev/serial0
# Fix permissions after serial-getty releases the device.
$ sudo chmod 666 /dev/serial0
```

### PMOD / GPIO loopback

The Fomu EVT has two PMOD-style connectors defined in the platform file (see
[PMOD Connectors](#pmod-connectors)). The loopback gateware uses `pmoda_n` as
input and `pmodb_n` as output.

#### pmoda_n (loopback input)

| Index | iCE40 Pin |
| ----- | --------- |
| 0     | 28        |
| 1     | 27        |
| 2     | 26        |
| 3     | 23        |

#### pmodb_n (loopback output)

| Index | iCE40 Pin |
| ----- | --------- |
| 0     | 48        |
| 1     | 47        |
| 2     | 46        |
| 3     | 45        |

Note: `pmodb_n` shares pins with `touch_pins`, the capacitive touch pads on the
Fomu.

#### Confirmed loopback pair

Only 1 of the 4 loopback pairs connects to a Pi GPIO through the GPIO header:

| Drive RPi GPIO | Read RPi GPIO | Status    |
| -------------- | ------------- | --------- |
| GPIO27         | GPIO9         | Confirmed |

:::{todo}
Determine which iCE40 pins GPIO27 and GPIO9 map to through the GPIO header. The
Fomu-to-RPi header pin mapping needs physical inspection.

The method is the
[pin-ID design](pin-id.md), which names each FPGA pin on the wire, so a scan
from the Pi gives the mapping without opening anything up.
:::

#### Loopback pre-test requirements

```console
# GPIO9 is SPI0_MISO -- nothing else on the Pi may be using SPI0, this takes
# the bus away from the kernel driver.
$ sudo rmmod spidev spi_bcm2835
```

The Fomu GPIO output has slow propagation, roughly 5 ms of settle time, so the
test uses a poll-until-stable loop rather than a single read.

### Other signals

| Signal          | iCE40 Pin | IO Standard | Function                 |
| --------------- | --------- | ----------- | ------------------------ |
| clk48           | 44        | LVCMOS33    | 48 MHz oscillator input  |
| user_led_n      | 41        | LVCMOS33    | User LED (active low)    |
| RGB LED R       | 40        | LVCMOS33    | RGB LED red              |
| RGB LED G       | 39        | LVCMOS33    | RGB LED green            |
| RGB LED B       | 41        | LVCMOS33    | RGB LED blue             |
| user_btn_n[0]   | 42        | LVCMOS33    | Capacitive touch button  |
| user_btn_n[1]   | 38        | LVCMOS33    | Capacitive touch button  |

The SPI flash, I2C and debug-header pins are the same in the pin-mapping notes
as on the board itself; they are listed once above under
[SPI Flash](#spi-flash), [I2C](#i2c) and [Debug Header](#debug-header).

## References

- LiteX platform file:
  <https://github.com/litex-hub/litex-boards/blob/master/litex_boards/platforms/kosagi_fomu_evt.py>
- Fomu Workshop (getting started guide): <https://workshop.fomu.im>
- Fomu hardware design files: <https://github.com/im-tomu/fomu-hardware>, with
  the [EVT PCB](https://github.com/im-tomu/fomu-hardware/tree/evt/hardware/pcb)
  on the `evt` branch
- Crowd Supply campaign: <https://www.crowdsupply.com/sutajio-kosagi/fomu>
- [Raspberry Pi PMOD HAT](pmod/rpi-hat.md), referenced by the pin-mapping notes.
  The Fomu is not fitted with one — it sits on the GPIO header directly — so the
  HAT page is background for the PMOD signalling only.
- [Hardware verification script](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/verify_hardware.py)
  (`verify_hardware.py` in the test-designs repository), which drives
  programming and the PoE reset recovery.
