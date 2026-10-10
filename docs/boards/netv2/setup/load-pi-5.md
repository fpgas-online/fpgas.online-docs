---
type: how-to
owner: documentation maintainers
reader: someone with a NeTV2 on a Raspberry Pi 5 loading a design
review: 2026-11-10
---

# How to load a design into a NeTV2 on a Raspberry Pi 5

**You want to load a bitstream into a NeTV2's FPGA on a Raspberry Pi 5, over GPIO JTAG with openFPGALoader.**

The load goes to the FPGA's SRAM and is lost at power-off. A NeTV2 on a Raspberry Pi 3B+ is on [its own page](load-pi-3b-plus.md).

This procedure is waiting for its run: ISSUE-04.

:::{warning}
Reconfiguring the FPGA over JTAG while its PCIe endpoint is enumerated is a surprise removal, and it crashes the BCM2712 root complex. Detach the endpoint before every JTAG command on this page.
:::

## What you need

- A NeTV2 wired as on [NeTV2 wiring to a Raspberry Pi](wiring.md#jtag), with its PCIe link in the Pi 5's PCIe connector.
- The `openfpgaloader-rp1pio` package, which brings the `librp1jtag0` shared library. [The NeTV2 packages](packages.md) explain the repository that carries it.
- A bitstream, here `design.bit`.

## Steps

1. On the Pi, run `lspci -d 10ee:7011` to find the NeTV2's PCIe address, which on a Pi 5 is `0001:01:00.0`, the slot the Acorn hosts use.
2. On the Pi, run `echo 1 | sudo tee /sys/bus/pci/devices/0001:01:00.0/remove` with the address from step 1 to detach the endpoint; if `lspci` printed nothing, there is nothing to detach.
3. On the Pi, run `sudo openFPGALoader --cable rp1pio --pins 27:22:4:17 design.bit` to load the bitstream through the RP1's PIO peripheral.
4. On the Pi, run `echo 1 | sudo tee /sys/bus/pci/rescan` to bring the endpoint back, or reboot.

The pin order is `TDI:TDO:TCK:TMS`. The FPGA enumerates only after a bitstream is loaded, and from then on step 2 is mandatory.

## Check

After step 4, `lspci -d 10ee:7011` lists the NeTV2 as a Xilinx device on a Gen2 x1 link, if the design has a PCIe endpoint.

## If it fails

| What you see | Likely cause | Fix |
|---|---|---|
| openFPGALoader does not know the `rp1pio` cable | The openFPGALoader build lacks it; only the `openfpgaloader-rp1pio` package has it | Install the package, or run the same command with `--cable libgpiod`, which is slower because the RP1 adds latency to GPIO access |
| The Pi crashes or drops off during the load | The endpoint was still enumerated | Detach it as in step 2, then load again |

## Next

- [How to write a design into a NeTV2's flash](write-flash.md)
- [How to free a NeTV2's serial port before a test](free-serial-port.md)
- [Programming a NeTV2](../overview/programming.md)
