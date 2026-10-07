# NeTV2: Serial / UART

**You have a NeTV2 on a Raspberry Pi and want to talk to the design in its FPGA over serial: which pins, which device on which Pi, and what to stop first.**

## Primary UART (via RPi GPIO)

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

## Serial Device by Host

Which kernel device the GPIO UART appears as depends on the Raspberry Pi model:

| Host       | RPi GPIO UART Device | Symlink          | Reason                              |
| ---------- | -------------------- | ---------------- | ----------------------------------- |
| rpi5-netv2 | `/dev/ttyAMA0`       | —                | RP1 PL011 UART on GPIO14/15         |
| rpi3-netv2 | `/dev/ttyS0`         | `/dev/serial0`   | Mini UART (Bluetooth claims PL011)  |
| production RPi 3B+ (pi-sw1-p10…p18) | `/dev/ttyAMA0` | `/dev/serial0` | PL011 on GPIO14/15; Bluetooth disabled on the netboot image |

**Measured 2026-09-06** on the production hosts: `/dev/serial0` is a symlink to
`ttyAMA0`, not `ttyS0`. Unlike the stock rpi3-netv2 image, the netboot image
disables Bluetooth, so the PL011 (`ttyAMA0`) is free for the GPIO header and
`serial0` points at it. The test tracer opened `/dev/serial0` and read the
FPGA's UART there. So on these hosts the GPIO UART is `/dev/serial0` →
`/dev/ttyAMA0`; the "should be `ttyS0`" inference does not hold for this image.
It must be opened with `sudo` — the `pi` user is not in the `dialout` group.

## rpi5-netv2 Specifics

- After stopping `serial-getty`, GPIO14/15 revert to plain GPIO mode. Run
  `pinctrl set 14 a4; pinctrl set 15 a4` to restore the UART function
  (ALT4 = TXD0/RXD0).

## rpi3-netv2 Specifics

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

## UART Test Parameters

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

## Secondary UART (via PCIe "hax" pins)

| Signal | FPGA Pin | PCIe Hax Pin |
| ------ | -------- | ------------ |
| TX     | B17      | hax7         |
| RX     | A18      | hax8         |

Both are LVCMOS33. These auxiliary pins on the PCIe connector provide a second
serial channel. They are reachable only over the PCIe connector, which means
rpi5-netv2 alone.
