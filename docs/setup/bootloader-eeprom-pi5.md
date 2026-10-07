# Bootloader EEPROM on a Raspberry Pi 5: check, upgrade and lock

**You have a Raspberry Pi 5 of the fleet** (at welland, each Acorn sits on one)
**and want to know whether its bootloader is the fleet's and locked, and to
upgrade it if it is not.** A Compute Module in a Compute Blade has [its own
page](bootloader-eeprom-compute-module.md); nothing here is for one.

The bootloader and its settings are in a small flash chip on the board, the
bootloader EEPROM. On a fleet Pi that chip is locked, so that nobody with root
on the Pi can change how it boots; a new bootloader therefore cannot simply be
installed. First check; upgrade only if the check says NOT DONE.

## Check the Pi 5 (nothing is changed)

- [Check it](bootloader-eeprom-pi5-check.md): three reads on the running Pi
  say DONE or NOT DONE.

## Upgrade a locked Raspberry Pi 5

- [What you need](bootloader-eeprom-pi5-upgrade.md): the bench list, and the
  six steps.

(step-1-make-the-card)=
- [Step 1: make the card](bootloader-eeprom-pi5-step-1.md), on a Linux
  computer; the Pi keeps running.

(step-2-network-cable-out)=
- [Step 2: network cable out](bootloader-eeprom-pi5-step-2.md): the Pi off and
  turned over.

(step-3-join-the-two-flash-wp-pads)=
- [Step 3: join the two FLASH WP pads](bootloader-eeprom-pi5-step-3.md), with
  solder, or get tweezers ready.

(step-4-card-in-network-cable-in-wait-60-seconds)=
- [Step 4: card in, network cable in, wait 60
  seconds](bootloader-eeprom-pi5-step-4.md): the Pi writes its new bootloader.

(step-5-cable-out-card-out-bridge-off-cable-in)=
- [Step 5: cable out, card out, bridge off, cable
  in](bootloader-eeprom-pi5-step-5.md): the Pi back on its own port, two
  minutes alone.

(step-6-read-it-back)=
- [Step 6: read it back](bootloader-eeprom-pi5-step-6.md): the three reads
  again, and what your result means.

```{toctree}
:hidden:

Check it <bootloader-eeprom-pi5-check>
Upgrade: what you need <bootloader-eeprom-pi5-upgrade>
Step 1: make the card <bootloader-eeprom-pi5-step-1>
Step 2: network cable out <bootloader-eeprom-pi5-step-2>
Step 3: join the WP pads <bootloader-eeprom-pi5-step-3>
Step 4: card in, wait 60 s <bootloader-eeprom-pi5-step-4>
Step 5: bridge off <bootloader-eeprom-pi5-step-5>
Step 6: read it back <bootloader-eeprom-pi5-step-6>
```
