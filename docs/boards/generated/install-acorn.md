% This section ("Installing the Acorn Packages") is copied from https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/docs/hardware/acorn.md
% by tools/sync_repos.py. Do not edit it here: change it in test-designs.

(installing-the-acorn-packages)=

This is for an Acorn on a Raspberry Pi 5. On a Compute Blade, follow [How to run the Acorn check on a Compute Blade](../checks/compute-blade.md) instead: there the packages are installed after each boot.

## What you need

- a Raspberry Pi 5 with the Acorn and both cables fitted ([How to fit the cables and the card (Raspberry Pi 5)](rpi-5/fitting.md))
- the fpgas.online apt repository added on the Pi ([fpgas-verify: installing it, step 1](../../../verify/installing.md#installing))
- on bookworm: the fpgas.online-fpga-tools apt repository added too ([fpgas-verify: installing it, step 2](../../../verify/installing.md#installing)). Debian bookworm's openFPGALoader is too old for the check
- the header's serial port on (`/dev/ttyAMA0`) and the kernel console off it, for the `p2-uart` and `p2-serial` tests ([A Raspberry Pi 5's settings for an Acorn](rpi-5/pi-settings.md#the-serial-port))

## Steps

**1.** Install the Acorn's packages. This also turns the check at boot on (`fpgas-verify.service`).

```bash
sudo apt install fpgas-online-acorn
```

**2.** Check the board now. Nothing is sent to the site: `--no-publish` makes sure.

```bash
sudo fpgas-acorn-verify --no-publish
```

## Check

The first line of the output starts with `fpgas-verify: pass`. The board's line under it ends in `pass`, and so does the line of each test (`jtag       pass`, for one). The result is `pass` only when every test passes. [fpgas-verify: reading the result](../../../verify/reading-the-result.md#reading-the-result) shows a whole pass as the tool prints it.

## If it fails

- The first line names the result, and the output ends with `RESULT:` and `What to do:`. [fpgas-verify: reading the result](../../../verify/reading-the-result.md#reading-the-result) says what each result means.
- [A failing Acorn test on a Raspberry Pi 5](../troubleshooting/rpi-5-failing-test.md) goes from a failing line to the wire.
- A reason that starts `unconverted:` means the card runs the image it was sold with, or Xilinx's XDMA sample design, and not the fpgas.online one. If the card is an Acorn, convert it: [Acorn PCIe programming and multiboot](../pcie-programming.md). The XDMA sample can also be a NeTV2 on PCIe, which that page does not apply to. On a Compute Blade, do not convert a card.
- To look at the card yourself, install `fpgas-online-acorn-debug` and run its two reads:

```bash
sudo fpgas-acorn-debug detect       # the Acorn-family endpoints on PCI
sudo fpgas-acorn-debug identify     # the running build and the flash's part, JEDEC ID and unique ID, read live
```

## Next

- [How to run the Acorn check on a Raspberry Pi 5](../checks/rpi-5.md): reading the result, test by test.
- [fpgas-verify: what an Acorn check tests](../../../verify/acorn.md#acorn): each test, and when it passes.
- [Acorn packages](../../../verify/installing.md#acorn-packages): what each package installs.
- [Acorn PCIe programming and multiboot](../pcie-programming.md): writing the flash with `fpgas-acorn-flash`, and converting a card.
