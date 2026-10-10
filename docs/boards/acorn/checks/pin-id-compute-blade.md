---
type: how-to
owner: documentation maintainers
reader: someone with an Acorn on a Compute Blade who wants to read its wires
review: 2026-11-10
---

# How to run the pin ID test on an Acorn on a Compute Blade

**You have an Acorn wired to a Compute Blade and want the P2 balls to send their own names.**

Only K2 and J2 answer on a blade, because J5 and H5 are not connected. On a Raspberry Pi 5 the load differs: [How to run the pin ID test on an Acorn on a Raspberry Pi 5](pin-id.md).

This procedure is waiting for its run: [test-designs issue #219](https://github.com/fpgas-online/fpgas.online-test-designs/issues/219).

:::{warning}
**Never load pin ID on a blade whose J2 wire has no 470 Ω resistor.**

When the load finishes, the design drives J2, which is on GPIO14. openFPGALoader has left GPIO14 an output. With the resistor that is about 7 mA for a moment. Without it, two outputs are shorted together, which costs JTAG until a power cycle and can crash the host.
:::

```{include} ../inc/gpio-contention.inc
```

## What you need

- An Acorn wired as on [Acorn wiring on a Compute Blade](../setup/compute-blade/wiring.md), with the 470 Ω resistor in the J2 wire ([the shared line](../setup/compute-blade/blade-settings.md#the-shared-line-and-the-470-ω-resistor)).
- `openFPGALoader` with the `libgpiod` cable, the pin order `2:3:4:14` for `--pins`, and the header's chip as `gpiochip0`.
- The header's serial port off in this boot:

  ```{include} ../inc/blade-jtag-serial-off.inc
  ```

- The card's PCI address in `BDF`:

  ```{include} ../inc/blade-first.inc
  ```

- The pin-ID bitstream in `PINID`:

  ```{include} ../inc/release-designs.inc
  ```

- A reader for the pins: [the repository's pin-ID host scanner](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/designs/pmod-pin-id/host/identify_pmod_pins.py), or `gpiomon` edge timestamps decoded by hand.

## Steps

1. On the blade, detach the card's PCIe endpoint before the load ([why](jtag-and-the-pcie-endpoint.md#why-the-endpoint-is-detached-before-a-load)); the card no longer shows in `lspci`.

   ```{include} ../inc/blade-detach.inc
   ```

2. On the blade, type the load and the restore as one command line, so that the pins are put back even if the load fails. GPIO14 is then an input with no pull.

   ```console
   $ openFPGALoader --cable libgpiod --pins 2:3:4:14 $PINID; pinctrl set 14 ip pn; pinctrl set 2,4 no pu
   ```

3. On the blade, run the host scanner with GPIO14 kept an input throughout, and read the name each pin sends. Do not set GPIO14 to `a0` or `a4` while pin ID runs.

   The scanner requests both-edge events through gpiod (v1 or v2) and rebuilds the 1200-baud frames from the kernel timestamps. Do not poll the pins from Python: polling mis-frames the bytes even on a clean signal.

4. On the blade, check the method on a positive control before you trust a negative: drive a spare GPIO and confirm the monitor sees it.

## Check

Only K2 and J2 answer.

```text
GPIO15 -> "K2"
GPIO14 -> "J2"
```

## If it fails

- **The blade crashes when a GPIO is set to output:** pin ID drives all four P2 balls, so a blade output fights an FPGA output. Keep GPIO14 an input (`pinctrl set 14 ip pn`) while pin ID runs.
- **JTAG is lost after the load:** the J2 wire has no 470 Ω resistor, and the design drives J2 against TMS on GPIO14. Power-cycle the blade and fit the resistor.
- **`gpiod_line_request_set_values_subset: Assertion 'request' failed`:** the serial driver holds GPIO14; boot with the header's serial port off.

## Next

- [Acorn wiring on a Compute Blade](../setup/compute-blade/wiring.md)
- [Acorn wiring faults on a Compute Blade](../troubleshooting/compute-blade-wiring.md)
- [JTAG loads and the PCIe endpoint](jtag-and-the-pcie-endpoint.md)
