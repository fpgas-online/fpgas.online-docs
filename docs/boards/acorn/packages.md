# Acorn packages and the boot check

**You have an Acorn on its host (a Raspberry Pi 5 with an M.2 HAT, or a CM4 or CM5 on a Compute Blade) and
want to install the fpgas.online packages for it, run the check, and identify or verify its flash with the
flash tool (`id` and `verify`; writing the flash is on [Installing and updating the
images](designs/install-images.md)).**

On a Raspberry Pi 5, before the check is run: its `p2-uart` and `p2-serial` tests need the header's serial
port on (`/dev/ttyAMA0`) and the kernel console off it: [the Pi's settings](wiring/rpi-5-host.md#the-serial-port).

```{include} ../generated/install-acorn.md
```
