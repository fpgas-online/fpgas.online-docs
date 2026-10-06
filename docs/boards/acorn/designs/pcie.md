# Acorn test: PCIe by hand

**You have an Acorn on a Raspberry Pi 5 or in a Compute Blade and want to see by hand that the card is on
the PCIe bus, detach it before a JTAG load, load the fpgas.online design and bring the card back on the
bus.** The boot check does the reading part by itself (`pcie-link`, `pcie-bar0`): [Installing the Acorn
packages](../packages.md#installing-the-acorn-packages). The design is built for the CLE-215+, the CLE-215
and the CLE-101.

## Detach the PCIe endpoint before any JTAG reconfiguration

:::{warning}
**Detach the PCIe endpoint before any JTAG reconfiguration.** Reconfiguring the
FPGA over JTAG while its endpoint is enumerated is a PCIe surprise removal, and
the Pi 5's BCM2712 root complex does not survive it: the host drops SSH and
reboots. With the endpoint removed first the load completes and the host is
unaffected.
:::

The rule is the root complex's, not the Acorn's: it applies to any PCIe FPGA on
a Pi 5, the NeTV2 on `rpi5-netv2` included ([PCIe
detection](../../netv2.md#pcie-detection-rpi5-netv2)).

Every `openFPGALoader … <bitstream>` on these pages assumes the endpoint is detached.
Read-only operations (`--detect`, `--read-dna`, `--read-xadc`) do not
reconfigure the device and are safe on a live endpoint.

```{include} soc-file.inc
```

## On a Raspberry Pi 5

Every Welland Pi 5 host uses `0001:01:00.0`.

### Is the card on the bus?

```console
$ lspci -nn -s 0001:01:00.0
```

```{include} lspci-ids.inc
```

If the Acorn doesn't appear, check the M.2 seating and the HAT's FPC
cable, and `dmesg | grep -i pci`.

### Detach the endpoint

```console
# Detach the endpoint first, before openFPGALoader
$ echo 1 | sudo tee /sys/bus/pci/devices/0001:01:00.0/remove
# ... load ...
# then bring it back: the next step
```

### Load the design and bring the endpoint back

```console
$ echo 1 | sudo tee /sys/bus/pci/devices/0001:01:00.0/remove   # detach first
# The libgpiod cable opens gpiochip0, the header is gpiochip15
$ sudo ln -sfn /dev/gpiochip15 /dev/gpiochip0
$ openFPGALoader --cable libgpiod --pins 10:9:11:8 $SOC
$ echo 1 | sudo tee /sys/bus/pci/rescan
$ lspci -nn -d 10ee:
# Expected: Xilinx Corporation Device [10ee:7021] (the LitePCIe default for one lane)
```

## On a Compute Blade

```{include} blade-first.inc
```

```{include} ../wiring/blade-jtag-serial-off.inc
```

### Is the card on the bus?

```console
$ lspci -nn -s $BDF
```

```{include} lspci-ids.inc
```

If the Acorn doesn't appear, check the M.2 seating, and `dmesg | grep -i pci`.

### Detach the endpoint

At PS1 the address differs per blade, so read it from the `PCIe` column in [Acorns at
ps1](../installations/ps1.md#the-cards).

```{include} ../wiring/blade-detach.inc
```

### Load the design and bring the endpoint back

The load, rescan and re-probe are as measured on pi20 at ps1, a
CM5; the `pinctrl` line as run on pi16 at ps1; the root complex's name on a CM4 is not
read by us, so take it from the `readlink` line:

```console
$ echo 1 | sudo tee /sys/bus/pci/devices/$BDF/remove   # detach first
$ openFPGALoader --cable libgpiod --pins 2:3:4:14 $SOC
$ pinctrl set 2,4 no pu
$ echo 1 | sudo tee /sys/bus/pci/rescan
$ lspci -nn -d 10ee:
# Nothing? On pi20 at ps1 a rescan was not enough: re-probe the root complex of the slot.
$ RC=$(readlink -f /sys/bus/pci/devices/${BDF%%:*}:00:00.0 | grep -o '[0-9a-f]*\.pcie')
$ echo $RC
1000110000.pcie
$ echo $RC | sudo tee /sys/bus/platform/drivers/brcm-pcie/unbind
$ echo $RC | sudo tee /sys/bus/platform/drivers/brcm-pcie/bind
$ lspci -nn -d 10ee:
# Expected: Xilinx Corporation Device [10ee:7021]
```

When the rescan is enough and when the re-probe is needed is under [Bring the
endpoint back after a JTAG
load](#bring-the-endpoint-back-after-a-jtag-load).

## Bring the endpoint back after a JTAG load

Measured on pi20 at ps1 (CM5 on a Compute Blade, kernel 6.12.75):

| Design loaded over JTAG | `echo 1 > /sys/bus/pci/rescan` | Root-complex re-probe |
|---|---|---|
| Vendor XDMA image (reloaded from flash with `openFPGALoader --reset`) | re-links at 5 GT/s x1 and enumerates | works |
| LiteX `acorn-pcie` SoC | nothing: the core's LTSSM sits at `0x2d`, and a root-port retrain or secondary-bus reset changes nothing | **links at 5 GT/s x1, enumerates as `10ee:7021`** |

Measured on a Raspberry Pi 5 with an M.2 HAT (kernel 6.12.96; the host was then named pi-sw2-p48):

| Design loaded over JTAG | `echo 1 > /sys/bus/pci/rescan` | Root-complex re-probe |
|---|---|---|
| LiteX `acorn-pcie` SoC (CLE-215+) | **enough**: the link is up (LTSSM `0x16`, L0, 5 GT/s x1) as soon as the load finishes, and the rescan enumerates `10ee:7021` | not needed |

So try the rescan first, and re-probe the root complex only when `lspci` still
shows nothing. The re-probe toggles PERST# by unbinding and rebinding the slot's
root complex; that touches only the FPGA's PCI domain, because the RP1
southbridge (Ethernet, USB, GPIO) hangs off a different platform device. The
platform device behind the FPGA slot is `1000110000.pcie` on both kinds of host.
Why the CM5 blade needs PERST# and the Pi 5 does not is not understood.

```console
# Which platform device is behind the FPGA slot?
$ readlink -f /sys/bus/pci/devices/0001:00:00.0 | grep -o '[0-9a-f]*\.pcie'
1000110000.pcie
$ echo 1000110000.pcie | sudo tee /sys/bus/platform/drivers/brcm-pcie/unbind
$ echo 1000110000.pcie | sudo tee /sys/bus/platform/drivers/brcm-pcie/bind
$ lspci -nn -s 0001:01:00.0
0001:01:00.0 Memory controller [0580]: Xilinx Corporation Device [10ee:7021]
```

If the link is down when `bind` runs, the driver logs `link down`, `bind` fails
with `No such device`, and the root port `0001:00:00.0` disappears until a later
`bind` succeeds. That is recoverable: load a design that links (or
`openFPGALoader --reset` to reload the flash image) and `bind` again.

## If it goes wrong

| Problem | Likely cause | Fix |
|---------|--------------|-----|
| Acorn not on PCIe | M.2 not seated, FPC cable loose | Reseat the M.2 card, check the FPC |
| Pi reboots or SSH drops during a JTAG load | FPGA reconfigured while its PCIe endpoint was enumerated | `echo 1 > /sys/bus/pci/devices/0001:01:00.0/remove` before loading (`0000:01:00.0` on a CM4 blade) |
| PCIe device missing after loading a design | Not rescanned, or (on a CM5 blade) a LiteX design that needs PERST# | Rescan; if still missing, re-probe the slot's root complex ([procedure](#bring-the-endpoint-back-after-a-jtag-load)); if it still does not link, check the build's I/O report has the lane on B10/B6 |
