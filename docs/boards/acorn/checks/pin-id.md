---
type: how-to
owner: documentation maintainers
reader: someone with an Acorn on a Raspberry Pi 5 who wants to read its wires
review: 2026-11-10
---

# How to run the pin ID test on an Acorn on a Raspberry Pi 5

**You have an Acorn wired to a Raspberry Pi 5 and want each P2 ball to send its own name.**

The boot check names a wrong wire without this design on a card that runs the fpgas.online design: [on a Raspberry Pi 5](rpi-5.md). On a Compute Blade the load differs: [How to run the pin ID test on an Acorn on a Compute Blade](pin-id-compute-blade.md).

```{include} ../inc/gpio-contention.inc
```

## What you need

- An Acorn wired as on [Acorn wiring on a Raspberry Pi 5](../setup/rpi-5/wiring.md), in the M.2 HAT slot, where the card is at `0001:01:00.0`.
- `openFPGALoader` with the `libgpiod` cable, and the pin order `10:9:11:8` for `--pins`.
- The pin-ID bitstream in `PINID`:

  ```{include} ../inc/release-designs.inc
  ```

- A reader for the pins: [the repository's pin-ID host scanner](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/designs/pmod-pin-id/host/identify_pmod_pins.py), or `gpiomon` edge timestamps decoded by hand.

## Steps

1. On the Pi, detach the card's PCIe endpoint before the load ([why](jtag-and-the-pcie-endpoint.md#why-the-endpoint-is-detached-before-a-load)); the card no longer shows in `lspci`.

   ```console
   $ echo 1 | sudo tee /sys/bus/pci/devices/0001:01:00.0/remove
   ```

2. On the Pi, link the header's GPIO chip as `gpiochip0`, because the `libgpiod` cable opens `gpiochip0` and the header is `gpiochip15`.

   ```console
   $ sudo ln -sfn /dev/gpiochip15 /dev/gpiochip0
   ```

3. On the Pi, load the pin-ID design; each ball then transmits its own name at 1200 baud.

   ```console
   $ openFPGALoader --cable libgpiod --pins 10:9:11:8 $PINID
   ```

4. On the Pi, run the host scanner with GPIO14 kept an input throughout, and read the name each pin sends.

   Only GPIO15 can be a hardware UART receiver on a Pi 5, so the scanner decodes the other three from edge timestamps. It requests both-edge events through gpiod (v1 or v2) and finds the header chip by label. It rebuilds the 1200-baud frames from the kernel timestamps: 833 µs per bit against nanosecond stamps.

5. On the Pi, check the method on a positive control before you trust a negative: drive a spare GPIO and confirm the monitor sees it.

## Check

A correctly wired card sends each name on its Pi GPIO.

```text
GPIO15 -> "K2"  (serial TX, on the Pi's RXD0)
GPIO14 -> "J2"  (serial RX, on the Pi's TXD0)
GPIO3  -> "J5"  (spare GPIO)
GPIO4  -> "H5"  (spare GPIO)
```

## If it fails

- **The Pi crashes when a GPIO is set to output:** pin ID drives all four P2 balls, so a Pi output fights an FPGA output. Keep GPIO14 an input (`pinctrl set 14 ip pn`) while pin ID runs.
- **The bytes are mis-framed on a clean signal:** the reader polls the pins from Python. Read edge timestamps instead.

## Next

- [Verifying wiring with the pin-id design](../../pin-id.md)
- [Acorn wiring faults on a Raspberry Pi 5](../troubleshooting/rpi-5-wiring.md)
- [How to run the Acorn UART and GPIO loopback on a Raspberry Pi 5](uart-gpio-loopback.md)
