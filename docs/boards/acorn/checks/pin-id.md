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
- The fpgas.online design in the card's flash: `lspci -nn -s 0001:01:00.0` shows `10ee:7021` before you start. Step 7 checks the card by that ID.
- At a site, the site operator's agreement first. The card is off the PCIe bus from step 2 to step 7, so nobody else can use it.
- `openFPGALoader` with the `libgpiod` cable, and the pin order `10:9:11:8` for `--pins`.
- The pin-ID bitstream in `PINID`:

  ```{include} ../inc/release-designs.inc
  ```

- A checkout of [fpgas.online-test-designs](https://github.com/fpgas-online/fpgas.online-test-designs) on the Pi, for the pin-ID host scanner `designs/pmod-pin-id/host/identify_pmod_pins.py` and `designs/acorn-pcie/host/pcie_match_mps.py`. The steps run from the checkout's top directory.
- `python3-libgpiod`, which the scanner needs and no Acorn package brings: `sudo apt install python3-libgpiod`.

## Steps

1. On the Pi, note how GPIO14 and GPIO15 are set, before step 3 changes GPIO14. Step 7 puts them back from this.

   ```console
   $ sudo pinctrl get 14,15
   ```

2. On the Pi, detach the card's PCIe endpoint before the load
   ([why](jtag-and-the-pcie-endpoint.md#why-the-endpoint-is-detached-before-a-load)). Link the header's GPIO chip as
   `gpiochip0`, because the `libgpiod` cable opens `gpiochip0`. The header's chip is the one `gpiodetect` lists as
   `pinctrl-rp1`; its number varies from 11 to 15, and the line below is for `gpiochip15`. The link stays
   afterwards: the Acorn tools expect it.

   ```console
   $ echo 1 | sudo tee /sys/bus/pci/devices/0001:01:00.0/remove
   $ gpiodetect
   $ sudo ln -sfn /dev/gpiochip15 /dev/gpiochip0
   ```

3. On the Pi, make GPIO14 an input. The pin-ID design drives J2, which is on GPIO14.

   ```console
   $ sudo pinctrl set 14 ip
   ```

4. On the Pi, load the pin-ID design; each ball then transmits its own name at 1200 baud.

   ```console
   $ sudo openFPGALoader --cable libgpiod --pins 10:9:11:8 "$PINID"
   ```

5. On the Pi, run the scanner for the Acorn and read the name each pin sends.

   ```console
   $ sudo python3 designs/pmod-pin-id/host/identify_pmod_pins.py --board acorn
   ```

   The scanner decodes every pin in software, from edge timestamps, so no pin needs a UART. Its options are on
   [Pin-id scanner options](../../pin-id/scanner-options.md).

   When it ends, the scanner sets back each pin that had an alternate function when it started. GPIO15 goes back to
   the serial port, which is safe because the Pi only reads it. GPIO14 stays an input, because step 3 came first;
   without step 3 the Pi would drive J2 against the design
   ([test-designs issue #308](https://github.com/fpgas-online/fpgas.online-test-designs/issues/308)).

6. On the Pi, reset the FPGA over JTAG, so that it loads its flash image again. A reboot of the Pi alone does not:
   the FPGA keeps running the pin-ID design.

   ```console
   $ sudo openFPGALoader --cable libgpiod --pins 10:9:11:8 --reset
   ```

   If `openFPGALoader` printed an error, stop here and leave GPIO14 an input: the FPGA may still run the pin-ID design.

7. On the Pi, put the card back first and the serial pins last.

   Make the JTAG pins inputs with a pull-down, because `openFPGALoader` leaves them driven. Rescan the PCIe bus and
   check that the card is there.

   ```console
   $ for p in 8 9 10 11; do sudo pinctrl set $p ip pd; done
   $ echo 1 | sudo tee /sys/bus/pci/rescan
   $ lspci -nn -s 0001:01:00.0
   ```

   Go on only when `lspci` shows `10ee:7021`, because that proves the FPGA has left the pin-ID design. Then match
   the card's Max_Payload_Size to the root port's, because a rescan leaves it at its reset value.

   ```console
   $ sudo python3 designs/acorn-pcie/host/pcie_match_mps.py
   ```

   Last, set GPIO14 and GPIO15 back to the function and pull that step 1 printed, and copy nothing after the `|`.
   The lines below are for a Pi where step 1 printed `14: a4    pn | hi // GPIO14 = TXD0` and
   `15: a4    pu | hi // GPIO15 = RXD0`. A pin whose function in step 1 was not `aN`, such as `ip` or `no`, is
   left as it is.

   ```console
   $ sudo pinctrl set 14 a4 pn
   $ sudo pinctrl set 15 a4 pu
   ```

## Check

A correctly wired card passes: the scanner's last line is `RESULT: PASS`, and its table shows the same name under
Expect and Got on each row.

| Pi GPIO | Expect | What the wire is |
|---|---|---|
| GPIO15 | K2 | serial TX, on the Pi's RXD0 |
| GPIO14 | J2 | serial RX, on the Pi's TXD0 |
| GPIO3 | J5 | spare GPIO |
| GPIO4 | H5 | spare GPIO |

## If it fails

Whatever failed, do steps 6 and 7 before you leave the Pi, so that the card is back on the bus.

- **The Pi crashes when a GPIO is set to output:** pin ID drives all four P2 balls, so a Pi output fights an FPGA output. Keep GPIO14 an input (`sudo pinctrl set 14 ip`) from step 3 until `lspci` shows the card in step 7.
- **Got shows `(none)` on one row:** no signal reached that GPIO. The wire to that ball is open or on another pin: [Acorn wiring faults on a Raspberry Pi 5](../troubleshooting/rpi-5-wiring.md).
- **Got shows a name that starts with `?`:** a signal reached that GPIO but did not decode. The wire is noisy or shared with another: [Acorn wiring faults on a Raspberry Pi 5](../troubleshooting/rpi-5-wiring.md).
- **Got shows another row's name:** two wires are swapped: [Acorn wiring faults on a Raspberry Pi 5](../troubleshooting/rpi-5-wiring.md).
- **Got shows `(none)` on every row:** the pin-ID design is not running. Run step 4 again and read its output for an error.
- **`lspci` shows nothing in step 7:** the link may not be up yet. Wait ten seconds and rescan again. If it is still missing, run step 6 again, then step 7. If it is missing after that, the FPGA is not running the fpgas.online image. Leave GPIO14 an input. Ask the site operator, then power-cycle the card.

## Next

- [The pin-id design](../../pin-id.md)
- [Acorn wiring faults on a Raspberry Pi 5](../troubleshooting/rpi-5-wiring.md)
- [How to run the Acorn UART and GPIO loopback on a Raspberry Pi 5](uart-gpio-loopback.md)
