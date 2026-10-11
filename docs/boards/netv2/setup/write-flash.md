---
type: how-to
owner: documentation maintainers
reader: someone who wants a bitstream to stay on a NeTV2
review: 2026-11-10
---

# How to write a design into a NeTV2's flash

**You want a bitstream written to a NeTV2's SPI flash, so that it survives a power cycle.**

The write replaces the bitstream in the NeTV2's own SPI flash. Step 3 first copies that bitstream region into `backup.bin` on the Pi, and you copy it to your own machine. This page is for someone setting up or looking after a NeTV2; a visitor to a site's board page never writes the flash. Loading into SRAM only is on [the Raspberry Pi 3B+ page](load-pi-3b-plus.md) and [the Raspberry Pi 5 page](load-pi-5.md).

This procedure is waiting for its run: [test-designs issue #249](https://github.com/fpgas-online/fpgas.online-test-designs/issues/249).

## What you need

- A NeTV2 wired as on [NeTV2 wiring to a Raspberry Pi](wiring.md#jtag), with openFPGALoader on the Pi. The pins are `27:22:4:17`, in the order `TDI:TDO:TCK:TMS`.
- The cable for your Pi: `-c rp1pio` on a Raspberry Pi 5, from the `openfpgaloader-fpgasonline-git` package; `--cable libgpiod` on a Raspberry Pi 3B+.
- The FPGA's part and the size of its bitstream region in bytes. An XC7A35T board is `xc7a35tfgg484` and `2228224`; an XC7A100T board is `xc7a100tfgg484` and `3866624`.
- Which of the two your board is: its JTAG scan reads `0x0362d093` on an XC7A35T and `0x03631093` on an XC7A100T ([FPGA device variants](../overview/specifications.md#fpga-device-variants)).
- A bitstream, here `design.bit`, no larger than the region.

## Steps

1. On a Raspberry Pi 5, run `lspci -D -s 0001:01:00.0`, the Pi 5's PCIe slot. A line there is an endpoint to detach; no line, go to step 3.
2. On a Raspberry Pi 5, detach it with `echo 1 | sudo tee /sys/bus/pci/devices/0001:01:00.0/remove`. Run `lspci -D -s 0001:01:00.0` again: it prints nothing. If it still prints the line, stop.
3. On the Pi, keep a copy of the bitstream region. Put your cable, part and size in place of `CABLE`, `PART` and `SIZE`. `ls -l backup.bin` shows `SIZE` bytes. Copy `backup.bin` to your own machine: a netbooted Pi loses it at its next reboot.

   ```console
   $ sudo openFPGALoader CABLE --pins 27:22:4:17 --fpga-part PART --dump-flash --file-size SIZE backup.bin
   ```

4. On a Raspberry Pi 5, run `lspci -D -s 0001:01:00.0` again. If it prints a line, the endpoint came back after step 3: repeat step 2.
5. On the Pi, write the bitstream to the flash and read it back. Without `--fpga-part`, openFPGALoader writes nothing.

   ```console
   $ sudo openFPGALoader CABLE --pins 27:22:4:17 --fpga-part PART --write-flash --verify design.bit
   ```

To put the old bitstream back, run step 4, then step 5 with `backup.bin` in place of `design.bit`.

## Check

Step 5 prints no line with `failed` and no `Can't program SPI flash`. Read the output rather than the exit status: some openFPGALoader builds exit 0 after a failed write. That the FPGA then starts the design from flash at power-up waits for this page's run ([test-designs issue #249](https://github.com/fpgas-online/fpgas.online-test-designs/issues/249)).

## If it fails

| What you see | Likely cause | Fix |
|---|---|---|
| The Pi crashes or drops off during the write | On a Raspberry Pi 5, the PCIe endpoint was still enumerated | Detach it as in steps 1 and 2, then write again |
| `Can't program SPI flash: missing device-package information` | the command had no `--fpga-part` | run it again with the part from What you need |
| `Verification failed at` an address | the flash does not hold what was written | write again; if it fails again, write `backup.bin` back |

## Next

- [How to load a design into a NeTV2 on a Raspberry Pi 3B+](load-pi-3b-plus.md)
- [How to load a design into a NeTV2 on a Raspberry Pi 5](load-pi-5.md)
- [Programming a NeTV2](../overview/programming.md)
