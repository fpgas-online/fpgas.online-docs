# Acorn test: JTAG by hand

**You have an Acorn wired to a Raspberry Pi 5 or to a Compute Blade and want to see by hand that its JTAG
answers, and load a design into the FPGA over it.** The boot check reads the IDCODE and the device DNA over
P1 by itself (`jtag`): [Installing the Acorn packages](../packages.md#installing-the-acorn-packages). A load
over JTAG lands in SRAM and works on every variant; the IDCODE tells an XC7A200T (CLE-215+, CLE-215,
NiteFury) from an XC7A100T (CLE-101, LiteFury).

## What differs between the carriers

The steps are the same on both carriers; the commands are not. What differs:

| | Raspberry Pi 5 | Compute Blade, CM4 | Compute Blade, CM5 |
|---|---|---|---|
| JTAG `--pins` (TDI:TDO:TCK:TMS) | `10:9:11:8` | `2:3:4:14` | `2:3:4:14` |
| GPIO chip for the `libgpiod` cable, which opens `/dev/gpiochip0` | `gpiochip15` under kernel 6.12 at Welland: link it as `gpiochip0` first | not read by us: run `gpiodetect` and link the chip labelled `pinctrl-bcm2711` as `gpiochip0` only if it is not that already | `pinctrl-rp1` was `gpiochip0` already on pi16 at ps1 and pi20 at ps1 (kernel 6.18.50, 2026-10-05): no link there |
| PCIe address of the card (`BDF` below) | `0001:01:00.0` | `0000:01:00.0` (pi14 at ps1) | `0001:01:00.0` (pi16 at ps1, pi20 at ps1) |
| Root complex behind the slot | `1000110000.pcie` | not read by us: find it with the `readlink` line of [PCIe by hand](pcie.md#on-a-compute-blade) | `1000110000.pcie` (pi20 at ps1, kernel 6.12.75) |
| FPGA serial port | `/dev/ttyAMA0`, GPIO14/15 at `a4` | `/dev/ttyAMA0`, GPIO14/15 at `a0` | `/dev/ttyAMA0`, GPIO14/15 at `a4`, but only in a boot with the header's serial port on, in which JTAG cannot run (kernel 6.18) |
| J5 and H5 | wired to GPIO3 and GPIO4 | not wired | not wired |
| Boot configuration for the JTAG steps | as the fleet boots | not read by us on a CM4 | `enable_uart=0` and no `console=serial0`: on pi16 at ps1 (kernel 6.18.50, 2026-10-05) JTAG cannot run with `enable_uart=1`. Not yet run by us on this hardware |

:::{warning}
**Detach the PCIe endpoint before every JTAG reconfiguration**, on either
carrier. Reconfiguring the FPGA while its endpoint is enumerated is a surprise
removal that the BCM2712 root complex (Pi 5, CM5) does not survive: the Pi drops
SSH and reboots. With the endpoint removed first the load completes and the host
is unaffected. Not measured on a CM4 (BCM2711); detach there too.
:::

```{include} soc-file.inc
```

## On a Raspberry Pi 5

```console
# 0. Detach the endpoint (bring it back afterwards with: echo 1 | sudo tee /sys/bus/pci/rescan, or reboot)
$ echo 1 | sudo tee /sys/bus/pci/devices/0001:01:00.0/remove
# The libgpiod cable opens gpiochip0, the header is gpiochip15
$ sudo ln -sfn /dev/gpiochip15 /dev/gpiochip0
# 1. Read-only check (safe without step 0)
$ openFPGALoader --cable libgpiod --pins 10:9:11:8 --detect
# Expected: idcode 0x3636093 (XC7A200T)
# 2. Load to SRAM. About 16 s for a 1.6 MB XC7A200T bitstream over libgpiod.
$ openFPGALoader --cable libgpiod --pins 10:9:11:8 $SOC
```

## On a Compute Blade

```{include} blade-first.inc
```

```{include} ../wiring/blade-jtag-serial-off.inc
```

Booted with the header's serial port off:

```{include} ../wiring/blade-jtag-commands.inc
```

## After the load

Never pass `--write-flash` here: an SRAM load is lost at power-off, so a reboot
restores whatever is in flash, which makes every experiment safe. Writing the
flash is covered in [Acorn PCIe programming and multiboot](install-images.md).

:::{warning}
**Files staged under `/home/pi` do not survive a reboot** on a host whose root
is an overlay in memory (`overlayroot=tmpfs` on a read-only NFS root, as on the
fleet). The symptom is openFPGALoader printing `Open file … FAIL` in under
0.1 s: copy the bitstream again.
:::

## If it goes wrong

| Problem | Likely cause | Fix |
|---------|--------------|-----|
| JTAG programming fails | wrong pins | check the pin order |
| `gpiod_line_request_set_values_subset: Assertion 'request' failed` on a Compute Blade | The serial driver holds GPIO14 (`enable_uart=1`; `dmesg`: `pin gpio14 already requested by 1f00030000.serial`) | JTAG needs the header's serial port off at boot ([JTAG on a blade](../wiring/compute-blade-jtag.md#jtag-on-a-blade)); not yet run by us on this hardware |
| `--detect` says `found 0 devices` but PCIe enumerates | P1 (JTAG) cable unmated or miswired | Check TCK for the Acorn's pull-up; reseat P1 |
| `Open file … FAIL` in < 0.1 s | The bitstream is gone: `/home/pi` is a tmpfs overlay, lost at reboot | Copy the file again |
| JTAG fails on a Compute Blade | Wrong pin order | Use `--pins 2:3:4:14`, not `--pins 10:9:11:8` |

On a Raspberry Pi 5, `JTAG init failed with: Unable to open gpio chip` means the `gpiochip0` link of the
block above is missing.
