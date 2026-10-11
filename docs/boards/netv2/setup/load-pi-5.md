---
type: how-to
owner: documentation maintainers
reader: someone with a NeTV2 on a Raspberry Pi 5 loading a design
review: 2026-11-10
---

# How to load a design into a NeTV2 on a Raspberry Pi 5

**You want to load a bitstream into a NeTV2's FPGA on a Raspberry Pi 5, over GPIO JTAG with openFPGALoader.**

The load goes to the FPGA's SRAM and is lost at power-off. A NeTV2 on a Raspberry Pi 3B+ is on [its own page](load-pi-3b-plus.md).

This procedure is waiting for its run: [test-designs issue #246](https://github.com/fpgas-online/fpgas.online-test-designs/issues/246).

:::{warning}
Reconfiguring the FPGA over JTAG while its PCIe endpoint is enumerated is a surprise removal, and it crashes the BCM2712 root complex. Step 2 detaches it.
:::

## What you need

- A NeTV2 wired as on [NeTV2 wiring to a Raspberry Pi](wiring.md#jtag), with its PCIe link in the Pi 5's PCIe connector.
- The `openfpgaloader-fpgasonline-git` package, which carries the `rp1pio` cable ([What runs on a Pi host](../../../setup/pi.md)). The apt repository is added as on [fpgas-verify: installing it](../../../verify/installing.md).
- A bitstream, here `design.bit`.

## Steps

1. On the Pi, run `lspci -D -s 0001:01:00.0`, the Pi 5's PCIe slot. A line there is an endpoint to detach; no line, go to step 3.
2. On the Pi, detach it with `echo 1 | sudo tee /sys/bus/pci/devices/0001:01:00.0/remove`. Run `lspci -D -s 0001:01:00.0` again: it prints nothing. If it still prints the line, stop.
3. On the Pi, run `sudo openFPGALoader --cable rp1pio --pins 27:22:4:17 design.bit` to load the bitstream through the RP1's PIO peripheral.
4. On the Pi, run `echo 1 | sudo tee /sys/bus/pci/rescan` to bring the endpoint back. If `ls /sys/bus/platform/drivers/brcm-pcie/` lists no `1000110000.pcie`, the host bridge removed itself at boot, with no link. Bind it again, with no unbind first: `echo 1000110000.pcie | sudo tee /sys/bus/platform/drivers/brcm-pcie/bind`. This bind waits for its run on a Pi 5 (test-designs issue #246).

The pin order is `TDI:TDO:TCK:TMS`. The FPGA enumerates only after a bitstream is loaded, and from then on step 2 is mandatory.

## Check

The load's last line in step 3 ends with `done 1`. With `done 0` the FPGA is not configured, whatever the exit status; the STAT register printed under it says why.

After step 4, `lspci -D -s 0001:01:00.0` lists the NeTV2 as a Xilinx device, if the design has a PCIe endpoint. `sudo lspci -vv -s 0001:01:00.0 | grep LnkSta` shows the Gen2 x1 link.

## If it fails

| What you see | Likely cause | Fix |
|---|---|---|
| openFPGALoader does not know the `rp1pio` cable | The openFPGALoader build lacks it; the `openfpgaloader-fpgasonline-git` package has it | Install the package, or run the same command with `--cable libgpiod`, which is slower because the RP1 adds latency to GPIO access |
| The Pi crashes or drops off during the load | The endpoint was still enumerated | Detach it as in step 2, then load again |

## Next

- [How to write a design into a NeTV2's flash](write-flash.md)
- [How to free a NeTV2's serial port before a test](free-serial-port.md)
- [Programming a NeTV2](../overview/programming.md)
