```console
# Which chip is the header? pinctrl-rp1 on a CM5, pinctrl-bcm2711 on a CM4; do not copy the Pi 5 link.
$ gpiodetect
# 0. Detach the endpoint
$ echo 1 | sudo tee /sys/bus/pci/devices/$BDF/remove
# 1. Read-only check (safe without step 0)
$ openFPGALoader --cable libgpiod --pins 2:3:4:14 --detect
# Expected: idcode 0x3631093 (XC7A100T, an Acorn CLE-101 or LiteFury)
#           idcode 0x3636093 (XC7A200T, a CLE-215+ or NiteFury)
# openFPGALoader leaves its pins as outputs (seen after --detect on pi16 at ps1): put them back
$ pinctrl set 2,4 no pu
# 2. Load to SRAM, and put the pins back again
$ openFPGALoader --cable libgpiod --pins 2:3:4:14 $SOC
$ pinctrl set 2,4 no pu
```
