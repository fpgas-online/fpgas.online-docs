---
type: how-to
owner: documentation maintainers
reader: someone with an Acorn on a Compute Blade who wants to run JTAG
review: 2026-11-10
---

# How to run JTAG by hand on an Acorn on a Compute Blade

**You have an Acorn wired to a Compute Blade and want to see its JTAG answer, then load a design over it.**

Which wire goes where is on [Acorn wiring on a Compute Blade](../setup/compute-blade/wiring.md). The line JTAG shares with the serial pair is on [the blade's pins, the shared line and settings](../setup/compute-blade/blade-settings.md#the-shared-line-and-the-470-ω-resistor). On a Raspberry Pi 5 the commands differ: [How to run JTAG by hand on an Acorn on a Raspberry Pi 5](jtag-by-hand.md).

This procedure is waiting for its run: [test-designs issue #237](https://github.com/fpgas-online/fpgas.online-test-designs/issues/237).

## What you need

- An Acorn wired as on [Acorn wiring on a Compute Blade](../setup/compute-blade/wiring.md), on a blade with a CM4 or a CM5.
- The pin order `2:3:4:14` for `--pins`: TDI (GPIO2), TDO (GPIO3), TCK (GPIO4), TMS (GPIO14).
- `openFPGALoader` with the `libgpiod` cable; version 0.13.1 has `--read-dna`, `--read-xadc` and `--read-register`, all read-only.
- The header's serial port off in this boot:

  ```{include} ../inc/blade-jtag-serial-off.inc
  ```

- The card's PCI address in `BDF`:

  ```{include} ../inc/blade-first.inc
  ```

- The fpgas.online Acorn design's `.bit` file in `SOC`:

  ```{include} ../inc/soc-file.inc
  ```

## Steps

1. On the blade, run `gpiodetect` to find the header's chip: `pinctrl-rp1` on a CM5, `pinctrl-bcm2711` on a CM4. Do not copy the Pi 5's `gpiochip15` link.

   ```console
   $ gpiodetect
   ```

2. On the blade, make that chip `gpiochip0` if it is not already, because the `libgpiod` cable opens `/dev/gpiochip0`. Under kernel 6.18 the CM5's chip is already `gpiochip0`.

   ```console
   $ sudo ln -sfn /dev/gpiochipN /dev/gpiochip0   # N from gpiodetect; skip when the chip is gpiochip0
   ```

3. On the blade, detach the card's PCIe endpoint, so that the load cannot remove it under the host ([why](jtag-and-the-pcie-endpoint.md#why-the-endpoint-is-detached-before-a-load)); `lspci` no longer lists the card.

   ```{include} ../inc/blade-detach.inc
   ```

4. On the blade, read the IDCODE with a read-only `--detect`, which is safe without step 3; it prints the IDCODE. Then put the pins back, because openFPGALoader leaves GPIO2 and GPIO4 as outputs driving low.

   ```console
   $ openFPGALoader --cable libgpiod --pins 2:3:4:14 --detect
   $ pinctrl set 2,4 no pu
   ```

5. On the blade, load the design into SRAM and put the pins back again; the load ends with the done message of openFPGALoader.

   ```console
   $ openFPGALoader --cable libgpiod --pins 2:3:4:14 $SOC
   $ pinctrl set 2,4 no pu
   ```

6. In a boot with the serial port on, give GPIO14 and GPIO15 back to the serial port with the line for your module. Do this only when the loaded design treats J2 as an input: the fpgas.online design does, pin ID does not. The UART function differs per module, and `pinctrl funcs 14,15` lists them.

   On a CM4 (BCM2711), GPIO14 is TXD0 and GPIO15 is RXD0 at `a0`:

   ```console
   $ pinctrl set 14,15 a0
   ```

   On a CM5 (RP1), they are TXD0 and RXD0 at `a4`:

   ```console
   $ pinctrl set 14,15 a4
   ```

## Check

Step 4 prints the IDCODE of the chip. After step 5 the FPGA runs the design. The PCIe page confirms it by bringing the endpoint back.

```text
idcode 0x3631093 (XC7A100T, an Acorn CLE-101 or LiteFury)
idcode 0x3636093 (XC7A200T, a CLE-215+ or NiteFury)
```

Never pass `--write-flash` here. An SRAM load is lost at power-off, so a reboot restores whatever is in flash.

## If it fails

- **`gpiod_line_request_set_values_subset: Assertion 'request' failed`:** the serial driver holds GPIO14 (`enable_uart=1`; `dmesg` says `pin gpio14 already requested by 1f00030000.serial`); boot with the header's serial port off ([why](jtag-and-the-pcie-endpoint.md#why-a-blade-needs-its-serial-port-off-for-jtag)).
- **`--detect` says `found 0 devices`:** the P1 cable is unmated or miswired; check TCK for the Acorn's pull-up and reseat P1.
- **JTAG fails with `--pins 10:9:11:8`:** that is the Pi 5's pin order; use `--pins 2:3:4:14`.
- **`Open file … FAIL` in under 0.1 s:** the bitstream is gone, because `/home/pi` is a memory overlay that loses its files at reboot; copy it again.
- **The UART is dead after JTAG:** openFPGALoader left GPIO14 an output; run step 6 for your module.

## Next

- [How to check an Acorn's PCIe link by hand on a Compute Blade](pcie-by-hand-compute-blade.md)
- [JTAG loads and the PCIe endpoint](jtag-and-the-pcie-endpoint.md)
- [Acorn wiring faults on a Compute Blade](../troubleshooting/compute-blade-wiring.md)
