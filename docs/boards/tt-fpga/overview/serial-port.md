---
type: explanation
owner: documentation maintainers
reader: someone using a demo board's serial port with their own tool
review: 2026-11-10
---

# Serial port ownership on a Tiny Tapeout FPGA demo board

**You want to use a demo board's serial port from a tool of your own, and want to know who holds it.**

The steps to stop and start the owner are on [How to stop the fpgas-tt daemon and start it again](../setup/stop-daemon.md). How the daemon is installed and configured is on [The Tiny Tapeout stack](../../../setup/tinytapeout.md).

## The port and its owner

The demo board shows up on the Raspberry Pi as `/dev/ttyACM0`, with VID:PID `2e8a:0005` (MicroPython Board in FS mode). A udev symlink, **`/dev/ttboard`**, points at it, and it is the name the Pi daemon opens.

The serial port has a permanent owner. Every Tiny Tapeout host runs the [`fpgas-tt`](https://github.com/fpgas-online/fpgas.online-tt) daemon, which holds `/dev/ttboard` open at 115200 baud. It fans the port out as a WebSocket on port 8765, with `WS /serial` and `GET /health`. The port is reachable only from the gateway, thanks to the per-port VLANs. While the daemon runs, `fuser /dev/ttyACM0` shows the daemon's python3 process.

## What that means for a tool

A tool that opens `/dev/ttyACM0` itself cannot do so while the daemon runs. `mpremote` and the [bitstream programming script](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/designs/_host/tt_fpga_program.py) are two such tools. The daemon is stopped first and started again afterwards. The other way is to drive the board through the daemon's `/serial` socket.

The daemon must be started again, because the board is on a public web site while you work. With the daemon stopped, the board drops off the site. The bitstream-loading and design-listing features live in the daemon, as `/designs` and `/bitstream`, with demos from the `fpgas-online-tt-demos` package. The public site uses them.

## How a test reaches the FPGA UART

The recommended access is through the RP2350 USB bridge. The RP2350 connects to the same FPGA pins on GPIO20 and GPIO37. It bridges UART data to the USB CDC serial port `/dev/ttyACM0`.

A test uses `--port /dev/ttyACM0 --board tt --skip-banner` at 115200 baud. It needs RP2350 firmware configured to bridge UART0 on GPIO20/37. The UART pins are in [the pin mapping](pin-mapping.md#uart-interface).

Five reasons make the bridge the recommended access:

- Raspberry Pi GPIO5 and GPIO11 are **not hardware UART pins**: the BCM2711 has no UART peripheral assignable to this GPIO pair.
- If the other pin tables are the right ones, the pair is GPIO17 and GPIO19 instead. That is no better: GPIO17 is RTS0 and GPIO19 is PCM_FS, so neither is a UART data pin.
- The NFS boot image has no device tree overlay files, and the root filesystem is read-only.
- Software bit-bang UART at 115200 baud is unreliable under a non-RT Linux kernel.
- The RP2350 has hardware UART peripherals that can be configured for these pins.

Access through the Raspberry Pi GPIO is not feasible. GPIO5 and GPIO11 are not assignable to any BCM2711 hardware UART as a pair. The BCM2711 UART3 uses GPIO4/5 (TX/RX), and no UART uses GPIO11 for TX. Without hardware UART support, these pins cannot reliably serve as a serial port at 115200 baud.
