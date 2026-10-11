---
type: how-to
owner: documentation maintainers
reader: someone with an Acorn on a Raspberry Pi 5 who wants to test its serial pair
review: 2026-11-10
---

# How to run the Acorn UART and GPIO loopback on a Raspberry Pi 5

**You have an Acorn wired to a Raspberry Pi 5 and want to see that the serial pair of P2 carries in both directions.**

The loopback design (`pmod-loopback`) returns on K2 the inverse of what it sees on J2, and nothing else: GPIO14 to J2, inverted, K2, GPIO15. It does not touch J5 or H5; the boot check tests those two wires with `p2-gpio`. On a card that runs the fpgas.online design, the boot check tests the same wires itself (`p2-uart`, `p2-serial`). The tests are on [Acorn tests and their wires on a Raspberry Pi 5](rpi-5-tests.md).

On a Compute Blade this cannot be done by hand in one boot. The load needs the header's serial port off, and the test needs it on ([why](jtag-and-the-pcie-endpoint.md#why-a-blade-needs-its-serial-port-off-for-jtag)). The check tests the pair there with `p2-uart` and `p2-serial`.

This procedure is waiting for its run: [test-designs issue #230](https://github.com/fpgas-online/fpgas.online-test-designs/issues/230).

## What you need

- An Acorn wired as on [Acorn wiring on a Raspberry Pi 5](../setup/rpi-5/wiring.md), in the M.2 HAT slot, where the card is at `0001:01:00.0`.
- The fpgas.online images in the card's flash, so that it comes back after step 7. They go in as on [How to install the fpgas.online images on an Acorn](../setup/install-images.md).
- The kernel console off the FPGA's serial port, and SysRq disabled: [A Raspberry Pi 5's settings for an Acorn](../setup/rpi-5/pi-settings.md#kernel-console-on-the-fpga-uart). Check `cat /proc/cmdline` before the load.
- `openFPGALoader` with the `libgpiod` cable, and the pin order `10:9:11:8` for `--pins`.
- The loopback bitstream in `LOOPBACK`; for a CLE-215+ and the release's file the name is `pmod-loopback_acorn-cle-215p_vivado-vivado_sqrl_acorn.bit`:

  ```{include} ../inc/release-designs.inc
  ```

  `<variant>` is `cle-215p`, `cle-215` or `cle-101`.

## Steps

1. On the Pi, stop and mask the getty on the FPGA's serial port; the port is free for the test.

   ```console
   $ sudo systemctl stop serial-getty@ttyAMA0
   $ sudo systemctl mask serial-getty@ttyAMA0
   ```

2. On the Pi, detach the card's PCIe endpoint, as before every JTAG load ([why](jtag-and-the-pcie-endpoint.md#why-the-endpoint-is-detached-before-a-load)); the card no longer shows in `lspci`.

   ```console
   $ echo 1 | sudo tee /sys/bus/pci/devices/0001:01:00.0/remove
   ```

3. On the Pi, link the header's GPIO chip as `gpiochip0`, because the `libgpiod` cable opens `gpiochip0` and the header is `gpiochip15`.

   ```console
   $ sudo ln -sfn /dev/gpiochip15 /dev/gpiochip0
   ```

4. On the Pi, load the loopback bitstream into SRAM; the load ends with the done message of openFPGALoader.

   ```console
   $ openFPGALoader --cable libgpiod --pins 10:9:11:8 $LOOPBACK
   ```

5. On the Pi, set the port and read it for three seconds without sending anything. Keep what it prints.

   ```console
   $ stty -F /dev/ttyAMA0 115200 raw -echo
   $ timeout 3 cat /dev/ttyAMA0 | od -An -tx1
   ```

6. On the Pi, read again while a word is sent. The loopback inverts each bit, so the bytes are not the bytes sent.

   ```console
   $ (sleep 1; echo test > /dev/ttyAMA0) &
   $ timeout 3 cat /dev/ttyAMA0 | od -An -tx1
   ```

7. At the switch, PoE-cycle the host's port and wait more than 90 s. The card loads its flash images again, and `lspci -nn -s 0001:01:00.0` lists it. A netbooted Pi's root is thrown away at every reboot ([Netboot and the NFS root](../../../setup/netboot.md)). On a netbooted Pi, step 1's mask, the `gpiochip0` link and the port settings go with it. On a Pi that boots from its own card, run `sudo systemctl unmask serial-getty@ttyAMA0` first.

## Check

Run step 6 twice. When J2 and K2 both carry, step 6 prints more bytes than step 5 each time. That is the expected result; its run will show it (test-designs issue #230). Step 5 alone shows at most that K2 is driven: the design holds the idle line low, which the Pi reads as a break. The inverted bytes may arrive as framing errors, so the check counts bytes and cannot compare them; a loopback that can is [test-designs issue #297](https://github.com/fpgas-online/fpgas.online-test-designs/issues/297).

## If it fails

Two items below send you to the pin-ID design. Read its hazard first:

```{include} ../inc/gpio-contention.inc
```

- **Step 5 and step 6 both print nothing:** K2 or GPIO15 is not connected, serial-getty holds the port, or the baud is wrong. Check that step 1 ran and step 5 set 115200. Then run pin ID and check that GPIO15 reads `K2`.
- **Step 6 prints no more bytes than step 5:** nothing reached J2. J2 or GPIO14 is not connected, or K2 and J2 are not crossed over. Run pin ID and check that GPIO14 reads `J2`, then give GPIO14 back with `pinctrl set 14 a4` and run again from step 4.
- **After any failure:** step 7's PoE cycle puts the card and the Pi back.
- **The Pi reboots when the design loads:** the kernel console is on the FPGA's serial port; fix it as in [the Pi's settings](../setup/rpi-5/pi-settings.md#kernel-console-on-the-fpga-uart).

## Next

- [How to run the pin ID test on an Acorn on a Raspberry Pi 5](pin-id.md)
- [Acorn wiring faults on a Raspberry Pi 5](../troubleshooting/rpi-5-wiring.md)
- [How to run JTAG by hand on an Acorn on a Raspberry Pi 5](jtag-by-hand.md)
