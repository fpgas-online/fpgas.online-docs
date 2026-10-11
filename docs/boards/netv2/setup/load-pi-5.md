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
- The `openfpgaloader-fpgasonline-git` package, which carries the `rp1pio` cable ([What runs on a Pi host](../../../setup/pi.md)).
- A bitstream, here `design.bit`.

## Steps

1. On the Pi, run `lspci -D -d 10ee:` to list any Xilinx device. On a Pi 5 the NeTV2's address is `0001:01:00.0`, the slot the Acorn hosts use.
2. On the Pi, run `echo 1 | sudo tee /sys/bus/pci/devices/0001:01:00.0/remove` with the address from step 1 to detach the endpoint. If `lspci` printed nothing, there is nothing to detach.
3. On the Pi, run `sudo openFPGALoader --cable rp1pio --pins 27:22:4:17 design.bit` to load the bitstream through the RP1's PIO peripheral.
4. On the Pi, run `echo 1 | sudo tee /sys/bus/pci/rescan` to bring the endpoint back. If the Pi booted with no link to the card, the PCIe host bridge removed itself, and a rescan finds nothing. Bind it again instead, with no unbind first: `echo 1000110000.pcie | sudo tee /sys/bus/platform/drivers/brcm-pcie/bind`.

The pin order is `TDI:TDO:TCK:TMS`. The FPGA enumerates only after a bitstream is loaded, and from then on step 2 is mandatory.

## Check

After step 4, `lspci -D -d 10ee:` lists the NeTV2 as a Xilinx device on a Gen2 x1 link, if the design has a PCIe endpoint.

## If it fails

| What you see | Likely cause | Fix |
|---|---|---|
| openFPGALoader does not know the `rp1pio` cable | The openFPGALoader build lacks it; the `openfpgaloader-fpgasonline-git` package has it | Install the package, or run the same command with `--cable libgpiod`, which is slower because the RP1 adds latency to GPIO access |
| The Pi crashes or drops off during the load | The endpoint was still enumerated | Detach it as in step 2, then load again |

## Next

- [How to write a design into a NeTV2's flash](write-flash.md)
- [How to free a NeTV2's serial port before a test](free-serial-port.md)
- [Programming a NeTV2](../overview/programming.md)
