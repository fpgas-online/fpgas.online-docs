# Tiny Tapeout FPGA board test: UART

**You have a Tiny Tapeout FPGA demo board on a Raspberry Pi and want to know what the UART test design is,
how its serial port is reached from the Raspberry Pi, and what a good result is: printable characters echoed
back through the demo board's microcontroller.**

- **What it verifies:** Serial TX/RX via RP2350 bridge.
- **Bitstream:** [`uart/.../tt_fpga_platform.bin`](https://github.com/fpgas-online/fpgas.online-test-designs/tree/main/designs/uart/).
- **Wrapper:** [`tt_test_wrapper.py`](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/designs/_host/tt_test_wrapper.py).

## The serial port

The TT standard UART uses ui_in[3] (RX) and uo_out[4] (TX), following the
[TinyTapeout UART0 convention](../../pmod/tinytapeout.md#uart-via-rp2040rp2350-built-in-usb-bridge-no-pmod-needed).
Which pins, headers and GPIOs the two signals are on: [the serial port
(UART)](../wiring/pins-uio-uart.md#the-serial-port-uart).

### Access via the RP2350 USB bridge (recommended)

The RP2350 connects to the same FPGA pins via GPIO20/GPIO37 and can bridge UART
data to the USB CDC serial port (`/dev/ttyACM0`). This is the recommended
approach since:

- RPi GPIO11 (to the FPGA's RX, `ui_in[3]`) and GPIO4 (from the FPGA's TX, `uo_out[4]`) are **not a
  hardware UART pair** — the BCM2711 has no UART peripheral assignable to them in these directions (below).
- The NFS boot image has no device tree overlay files, and the root filesystem
  is read-only.
- Software bit-bang UART at 115200 baud is unreliable under a non-RT Linux
  kernel.
- The RP2350 has hardware UART peripherals that can be configured for these
  pins.

- **Device:** `/dev/ttyACM0` (via RP2350 USB CDC).
- **Baud rate:** 115200.
- **Test args:** `--port /dev/ttyACM0 --board tt --skip-banner`.
- **Requires:** the RP2350's UART1 bridged on GPIO20/37 (`tt_test_wrapper.py`:
  `UART(1, 115200, tx=Pin(20), rx=Pin(37))`).

These two signals are what Tiny Tapeout's convention calls UART0; the RP2350 peripheral our bridge uses for
them is its UART1.

### Access via RPi GPIO (not currently feasible)

The RPi would have to transmit on GPIO11 (to `ui_in[3]`) and receive on GPIO4 (from `uo_out[4]`):
[the serial port (UART)](../wiring/pins-uio-uart.md#the-serial-port-uart). The BCM2711 UART3 uses GPIO4/5
(TX/RX), so it has its TX, not its RX, on GPIO4, and no UART uses GPIO11 for TX, so no hardware UART fits
(source: the pin-mapping page of
[fpgas.online-test-designs](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/docs/hardware/tt-fpga-pin-mapping.md);
not verified by us against the BCM2711's documentation). An earlier version of this page named GPIO5/11, and
then GPIO17/19 (GPIO17 is RTS0 and GPIO19 is PCM_FS), as the pair; both came from pin tables that the
measured cabling has replaced. Without
hardware UART support, these pins cannot reliably serve as a serial port at
115200 baud. Nobody has used these two signals as a serial port from the Raspberry Pi's own GPIOs.

## In the boot check

This is the `uart` test of the boot check, which loads the design through the microcontroller and runs the
host test through the UART bridge on `/dev/ttyACM0`: [verifying 1](../building/verifying-1.md). It passed on
2 October 2026 on the three boards then seen at welland: [the boards at welland](../installations/welland.md).

## By hand

```{include} ../generated/tt-fpga-pins-other.md
:start-after: "### Loading the FPGA: its configuration pins"
:end-before: "The FPGA breakout has no SPI flash"
```

```{include} ../serial-port.inc
```

With the packages installed and the daemon stopped as above. For this board the debug tool's `program` and
`test` need `--variant tt-fpga` said out loud ([Which Tiny Tapeout board it
is](../../../verify/fpgas-verify.md#which-tiny-tapeout-board-it-is)); the package's own line, below, has
it without, as the record gives it. Not run by us in either form.

```console
$ sudo fpgas-tt-fpga-debug test uart                 # load one test's design and run its test
$ sudo fpgas-tt-fpga-debug --variant tt-fpga test uart
```

```{include} wrappers.inc
```

For this test the wrapper is `tt_test_wrapper.py`: it programs the FPGA, bridges its serial port and runs
the test in one invocation. It no longer replaces the board's `main.py` when it finishes: [firmware](firmware.md#demoboard-hang-on-boot).

Running the test from a workstation instead, with the older runner: [from a
workstation](from-a-workstation.md).
