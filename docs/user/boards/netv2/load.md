---
type: how-to
owner: documentation maintainers
reader: a visitor with a NeTV2's page open on welland.fpgas.online
review: 2026-11-10
---

# How to load a design onto a NeTV2 from its board page

**You have a NeTV2's page open on welland.fpgas.online and a bitstream for it. You want the design to run**. The load
goes into the FPGA's SRAM and is lost at power-off. A reset or a reboot also empties `/home/pi`, uploads included. A
visitor never writes the board's flash.

The Pi 5 steps are still waiting for their first run on a host: [test-designs issue #246](https://github.com/fpgas-online/fpgas.online-test-designs/issues/246).

## What you need

- A NeTV2's page, from [the welland list](https://welland.fpgas.online/fpgas/): a board whose label says NeTV2.
- A `.bit` file built for the board's FPGA, here `design.bit`. The FPGA is an XC7A35T, or an XC7A100T on the large variant.
  On a Pi 3B+, step 2 of its part reads the IDCODE that tells them apart; the Pi 5 steps do not show it.
  The host's own test bitstreams for both are in `/usr/share/fpgas-online/netv2/bitstreams/`.

## Steps

1. Upload the file with the page's **upload** button. It goes into `/home/pi/Uploads/` on the host.
2. In the page's terminal, find out which Pi the host is. The line names the model: a Pi 5 or a Pi 3B+.

   ```console
   $ cat /proc/device-tree/model
   ```

3. Follow the part below for your host.

### On a Pi 5

1. List the board's PCIe endpoint. A line is an endpoint to detach. With no line, go to step 3.

   ```console
   $ lspci -D -s 0001:01:00.0
   ```

2. Detach it. The same `lspci` command then prints nothing. If it still prints the line, stop. The host's PCIe
   controller does not survive a load while the endpoint is enumerated.

   ```console
   $ echo 1 | sudo tee /sys/bus/pci/devices/0001:01:00.0/remove
   $ lspci -D -s 0001:01:00.0
   ```

3. Load the design into SRAM through the RP1's PIO peripheral. The pin order is `TDI:TDO:TCK:TMS`.

   ```console
   $ sudo openFPGALoader --cable rp1pio --pins 27:22:4:17 Uploads/design.bit
   ```

4. Rescan the bus to bring the endpoint back.

   ```console
   $ echo 1 | sudo tee /sys/bus/pci/rescan
   ```

5. List the host bridge's driver.

   ```console
   $ ls /sys/bus/platform/drivers/brcm-pcie/
   ```

   If it lists no `1000110000.pcie`, the host bridge removed itself at boot, with no link. Bind it again, with no unbind
   first, and give the link a few seconds. If it lists `1000110000.pcie`, skip the bind.

   ```console
   $ echo 1000110000.pcie | sudo tee /sys/bus/platform/drivers/brcm-pcie/bind
   ```

### On a Pi 3B+

1. Read the two settings that make a load safe. The kernel console UART shares the FPGA's serial TX pin.

   ```console
   $ sysctl kernel.sysrq
   $ cat /proc/cmdline
   ```

   If the command line has `console=serial0`, do not load on this host: choose another NeTV2 from the list. If
   `sysctl` does not print `kernel.sysrq = 0`, set it to 0.

   ```console
   $ sudo sysctl -w kernel.sysrq=0
   ```

2. See the FPGA answer on JTAG.

   ```console
   $ sudo openFPGALoader --cable libgpiod --pins 27:22:4:17 --detect
   ```

3. Load the design into SRAM. The effective JTAG clock is about 5 MHz, so a load is slow. The pin order is
   `TDI:TDO:TCK:TMS`.

   ```console
   $ sudo openFPGALoader --cable libgpiod --pins 27:22:4:17 Uploads/design.bit
   ```

## Check

The load's last line ends with `done 1`. With `done 0` the FPGA is not configured, whatever the exit status; the STAT
register printed under it says why.

On a Pi 5, after the rescan, a design with a PCIe endpoint shows the NeTV2 as a Xilinx device, and the link reads
`Speed 5GT/s, Width x1`.

```console
$ lspci -D -s 0001:01:00.0
$ sudo lspci -vv -s 0001:01:00.0 | grep LnkSta
```

On a Pi 3B+, the detect step lists an XC7A35T board as `idcode 0x0362d093` with IR length 6.

What the design does shows only where the host has a USB HDMI grabber. The page's camera then shows the board's HDMI
output, not the board. Which hosts have one is not settled ([docs issue #189](https://github.com/fpgas-online/fpgas.online-docs/issues/189)).

## If it fails

| What you see | Likely cause | Fix |
|---|---|---|
| The host crashes or drops off during the load on a Pi 5 | the endpoint was still enumerated | wait for the host to come back (press Reset, as on [How to reset a board](../reset.md), if it does not), then follow the steps again from step 1: the reboot emptied `Uploads` |
| openFPGALoader does not know the `rp1pio` cable | the host's openFPGALoader build lacks it; only the `openfpgaloader-fpgasonline-git` package has the cable | choose another NeTV2 from the list: this host cannot load over `rp1pio` |
| The Pi 3B+ drops off when the design starts | the design drives the serial TX line while the kernel console and SysRq are on | make both checks of step 1 before loading again |
| `done 0` | the FPGA did not configure | read the STAT register printed under it, and check that the file was built for the board's FPGA |

More causes are on [How to load a design into a NeTV2 on a Raspberry Pi 5](../../../boards/netv2/setup/load-pi-5.md#if-it-fails)
and [on a Raspberry Pi 3B+](../../../boards/netv2/setup/load-pi-3b-plus.md#if-it-fails).

## Next

- [A NeTV2 on fpgas.online](about.md)
- [The camera on a board](../camera.md)
