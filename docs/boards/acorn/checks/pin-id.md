---
type: how-to
owner: documentation maintainers
reader: someone with an Acorn on a Raspberry Pi 5 who wants to read its wires
review: 2026-11-10
---

# How to run the pin ID test on an Acorn on a Raspberry Pi 5

**You have an Acorn wired to a Raspberry Pi 5 and want each P2 ball to send its own name.**

A card that runs the fpgas.online design needs no pin-ID design. Its boot check names a wrong wire: [How to run the Acorn check on a Raspberry Pi 5](rpi-5.md). On a Compute Blade the load differs: [How to run the pin ID test on an Acorn on a Compute Blade](pin-id-compute-blade.md).

This procedure is waiting for its run: [test-designs issue #229](https://github.com/fpgas-online/fpgas.online-test-designs/issues/229).

```{include} ../inc/gpio-contention.inc
```

## What you need

- An Acorn wired as on [Acorn wiring on a Raspberry Pi 5](../setup/rpi-5/wiring.md), in the M.2 HAT slot, where the card is at `0001:01:00.0`.
- `openFPGALoader` with the `libgpiod` cable, and the pin order `10:9:11:8` for `--pins`.
- The pin-ID bitstream in `PINID`:

  ```{include} ../inc/release-designs.inc
  ```

- The repository's pin-ID host scanner, [`identify_pmod_pins.py`](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/designs/pmod-pin-id/host/identify_pmod_pins.py), on the Pi.
- `python3-libgpiod`, which the scanner needs and no Acorn package brings: `sudo apt install python3-libgpiod`.

## Steps

1. On the Pi, keep how the pins are set before you change them. Step 7 puts them back from this.

   ```console
   $ pinctrl get 8-11,14,15
   ```

2. On the Pi, detach the card's PCIe endpoint before the load
   ([why](jtag-and-the-pcie-endpoint.md#why-the-endpoint-is-detached-before-a-load)). Link the header's GPIO chip as
   `gpiochip0`, because the `libgpiod` cable opens `gpiochip0` and the header is `gpiochip15`.

   ```console
   $ echo 1 | sudo tee /sys/bus/pci/devices/0001:01:00.0/remove
   $ sudo ln -sfn /dev/gpiochip15 /dev/gpiochip0
   ```

3. On the Pi, make GPIO14 an input. The pin-ID design drives J2, which is on GPIO14.

   ```console
   $ pinctrl set 14 ip
   ```

4. On the Pi, load the pin-ID design; each ball then transmits its own name at 1200 baud.

   ```console
   $ openFPGALoader --cable libgpiod --pins 10:9:11:8 $PINID
   ```

5. On the Pi, run the scanner for the Acorn and read the name each pin sends. When it ends it gives GPIO14 back to
   the serial port while the design still drives J2 ([test-designs issue #308](https://github.com/fpgas-online/fpgas.online-test-designs/issues/308)).
   Make GPIO14 an input again at once.

   ```console
   $ python3 identify_pmod_pins.py --board acorn
   $ pinctrl set 14 ip
   ```

   The scanner decodes every pin in software, from edge timestamps, so no pin needs a UART. Its options are on
   [Pin-id scanner options](../../pin-id/scanner-options.md).

6. On the Pi, reset the FPGA over JTAG, so that it loads its flash image again. A reboot of the Pi alone does not:
   the FPGA keeps running the pin-ID design.

   ```console
   $ openFPGALoader --cable libgpiod --pins 10:9:11:8 --reset
   ```

7. On the Pi, set each pin back to what step 1 printed, for example `pinctrl set 14 a4` where step 1 showed `a4`.

## Check

A correctly wired card sends each name on its Pi GPIO.

```text
GPIO15 -> "K2"  (serial TX, on the Pi's RXD0)
GPIO14 -> "J2"  (serial RX, on the Pi's TXD0)
GPIO3  -> "J5"  (spare GPIO)
GPIO4  -> "H5"  (spare GPIO)
```

## If it fails

- **The Pi crashes when a GPIO is set to output:** pin ID drives all four P2 balls, so a Pi output fights an FPGA output. Keep GPIO14 an input (`pinctrl set 14 ip`) from step 3 to step 6.
- **The bytes are mis-framed on a clean signal:** the reader polls the pins from Python. Read edge timestamps instead.

## Next

- [The pin-id design](../../pin-id.md)
- [Acorn wiring faults on a Raspberry Pi 5](../troubleshooting/rpi-5-wiring.md)
- [How to run the Acorn UART and GPIO loopback on a Raspberry Pi 5](uart-gpio-loopback.md)
