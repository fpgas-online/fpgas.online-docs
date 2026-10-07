# Fomu EVT: wiring to the Raspberry Pi

**You want to know how a Fomu is joined to its Raspberry Pi: the USB port, the DFU bootloader, the UART and the other signals.**

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
  [USB monitoring](usb-monitoring.md#usb-monitoring).

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

(dfu-bootloader-timeout)=

#### DFU bootloader timeout

If no DFU activity occurs within the bootloader's window, the bootloader
warm-boots the iCE40 to load the user bitstream from SPI flash. The user
bitstream typically has no USB, so the Fomu disappears from USB.

:::{warning}
A Fomu that has vanished from `lsusb` is usually not broken — it has timed out
of DFU after about 3 minutes, or it is running a test bitstream with no USB
core. The recovery is a PoE power cycle, which resets the Fomu and restarts the
DFU bootloader. The
[hardware verification script](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/verify_hardware.py)
(`verify_hardware.py`) does this automatically: it triggers a PoE reset and
retries programming when DFU is unavailable. Do not go looking for a dead board
before power-cycling it.

The round trip is worth spelling out: the PoE cycle brings DFU back, but it
also discards the volatile SRAM load, so whatever was programmed is gone and
the roughly three-minute window starts over — reprogram inside it or the board
drops off USB again.
:::

### USB connection to the Pi

The USB pins are listed under [USB Interface](usb-serial.md#usb-interface). The USB interface
is active only when the DFU bootloader or a USB-enabled bitstream is loaded. The
custom test bitstreams (UART echo, GPIO loopback) do not include USB, so the
Fomu disappears from USB after programming — which is expected, not a fault.

### UART interface

The FPGA's serial pins (TX on iCE40 pin 13, RX on pin 21, see
[Serial (UART)](usb-serial.md#serial-uart)) connect to the Pi's GPIO UART through the GPIO
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

`--port /dev/serial0` is the model-agnostic form and is the one to use:
`/dev/serial0` is the symlink the Pi points at whichever UART is on
GPIO14/GPIO15, so it is right on every host regardless of which kernel device
that turns out to be.

Which device it resolves to is less certain. The survey recorded
`/dev/ttyAMA0`, on the grounds that `hciuart` is inactive on pi17 and pi21 so
the PL011 is free for the FPGA UART — but that is
**recorded as `/dev/ttyAMA0` by the 2026-03-17 survey and unverified**. On a
stock Raspberry Pi 3B+ Bluetooth holds the PL011 and the GPIO UART is the mini
UART at `/dev/ttyS0`; the same hedge applies to the NeTV2 hosts, which are the
same model from the same survey — see
[Serial Device by Host](../netv2.md#serial-device-by-host). Resolve the symlink on
the host before assuming either name.

`serial-getty` must be masked, not just stopped, or it will come back and
consume the serial data.

:::{todo}
Document the exact Fomu-to-RPi GPIO header pin mapping from iCE40 pins 13, 21 to
RPi GPIO14, GPIO15.

The method is the
[pin-ID design](../pin-id.md): load it on the Fomu and read back which Pi GPIO
carries which FPGA pin's identity.
:::

#### UART pre-test requirements

```console
# Stop early if there is no GPIO UART here -- without this the lookup below
# resolves to nothing and the mask silently targets the wrong unit.
$ [ -e /dev/serial0 ] || { echo "no GPIO UART on this host"; exit 1; }
# Resolve serial0 to the real device so this works whether the GPIO UART is
# the PL011 (ttyAMA0) or the mini UART (ttyS0) on this host.
$ GETTY="serial-getty@$(basename "$(readlink -f /dev/serial0)").service"
# Mask prevents systemd from restarting the serial login console.
$ sudo systemctl mask "$GETTY"
# Stop the currently running instance.
$ sudo systemctl stop "$GETTY"
# Kill any remaining process holding the port.
$ sudo fuser -k /dev/serial0
# Fix permissions after serial-getty releases the device.
$ sudo chmod 666 /dev/serial0
```

The survey wrote these as `serial-getty@ttyAMA0`; the form above masks whichever
unit actually owns the port on the host.

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
as on the board itself; they are listed once under
[SPI Flash](peripherals.md#spi-flash), [I2C](peripherals.md#i2c) and [Debug Header](peripherals.md#debug-header).
