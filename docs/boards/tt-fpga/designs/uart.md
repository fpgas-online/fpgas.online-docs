# Tiny Tapeout FPGA board test: UART

**You have a Tiny Tapeout FPGA demo board on a Raspberry Pi and want to know what the UART test design is,
how its serial port is reached from the Raspberry Pi, and what a good result is: printable characters echoed
back through the demo board's microcontroller.**

| Test | Bitstream | Wrapper | What it verifies |
|------|-----------|---------|------------------|
| UART echo | [`uart/.../tt_fpga_platform.bin`](https://github.com/fpgas-online/fpgas.online-test-designs/tree/main/designs/uart/) | [`tt_test_wrapper.py`](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/designs/_host/tt_test_wrapper.py) | Serial TX/RX via RP2350 bridge |

## The serial port

The TT standard UART uses ui_in[3] (RX) and uo_out[4] (TX), following the
[TinyTapeout UART0 convention](../../pmod/tinytapeout.md#uart-via-rp2040rp2350-built-in-usb-bridge-no-pmod-needed).
Which pins, headers and GPIOs the two signals are on: [the serial port
(UART)](../wiring/pins-uio-uart.md#the-serial-port-uart).

### Access via the RP2350 USB bridge (recommended)

The RP2350 connects to the same FPGA pins via GPIO20/GPIO37 and can bridge UART
data to the USB CDC serial port (`/dev/ttyACM0`). This is the recommended
approach since:

- The two RPi GPIOs the signals reach through the Pmod HAT (the table linked above) are **not a hardware UART
  pair** — the BCM2711 has no UART peripheral assignable to them in these directions.
- The NFS boot image has no device tree overlay files, and the root filesystem
  is read-only.
- Software bit-bang UART at 115200 baud is unreliable under a non-RT Linux
  kernel.
- The RP2350 has hardware UART peripherals that can be configured for these
  pins.

| Parameter | Value                                                   |
| --------- | ------------------------------------------------------- |
| Device    | `/dev/ttyACM0` (via RP2350 USB CDC)                     |
| Baud rate | 115200                                                  |
| Test args | `--port /dev/ttyACM0 --board tt --skip-banner`          |
| Requires  | the RP2350's UART1 bridged on GPIO20/37 (`tt_test_wrapper.py`: `UART(1, 115200, tx=Pin(20), rx=Pin(37))`) |

These two signals are what Tiny Tapeout's convention calls UART0; the RP2350 peripheral our bridge uses for
them is its UART1.

### Access via RPi GPIO (not currently feasible)

The RPi would have to transmit on the GPIO that reaches `ui_in[3]` and receive on the one `uo_out[4]`
reaches ([the serial port (UART)](../wiring/pins-uio-uart.md#the-serial-port-uart) gives both). On the
BCM2711 no hardware UART has its TX and its RX on those two GPIOs that way round (source: the pin-mapping
page of
[fpgas.online-test-designs](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/docs/hardware/tt-fpga-pin-mapping.md)). Without
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

With the packages installed (the daemon stopped as above):

```console
$ sudo fpgas-tt-fpga-debug test uart                 # load one test's design and run its test
```

```{include} wrappers.inc
```

For this test the wrapper is `tt_test_wrapper.py`: it programs the FPGA, bridges its serial port and runs
the test in one invocation. It no longer replaces the board's `main.py` when it finishes: [firmware](firmware.md#demoboard-hang-on-boot).

### From a workstation

```{include} run-from-workstation.inc
```
