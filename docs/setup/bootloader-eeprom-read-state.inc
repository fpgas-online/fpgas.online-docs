Run these three on the Pi. None of them changes anything.

```console
$ vcgencmd bootloader_version
$ vcgencmd bootloader_config
$ sudo rpi-eeprom-update
```

**What a Pi 5 that is done looks like** (read on a fleet Pi 5 on 4 Oct 2026):

```console
$ vcgencmd bootloader_version
2026/09/25 15:59:09
version 1accd6659983613cd104973ce2432da14f1a7682 (release)
timestamp 1790351949
update-time 1791022751
capabilities 0x0000007f
$ vcgencmd bootloader_config
[all]
BOOT_UART=1
WAKE_ON_GPIO=1
POWER_OFF_ON_HALT=0
BOOT_ORDER=0xf2
NET_INSTALL_AT_POWER_ON=0
```

**What a Pi 5 that still needs the upgrade looks like** (another fleet Pi 5, the
same day): an older date in the first line, and a boot order that is not `0xf2`.

```console
$ vcgencmd bootloader_version
2026/05/26 16:01:25
version 086b83e3332dfc8927c56762771d082f3077a1ae (release)
timestamp 1779807685
update-time 0
capabilities 0x0000007f
$ vcgencmd bootloader_config
[all]
BOOT_UART=1
BOOT_ORDER=0xf12
NET_INSTALL_AT_POWER_ON=1
```

| Read | Wanted | If it is something else |
|---|---|---|
| first line of `bootloader_version` | `2026/09/25` | an older date: the upgrade has not been written |
| `BOOT_ORDER` | `0xf2` (network, then start again; read from the last digit: `1` SD card, `2` network, `6` NVMe, `4` USB, `f` start again) | any `1`, `4` or `6` in it: the Pi can boot a card, a USB stick or an SSD someone fits |
| `BOOT_UART` | `1` | the bootloader does not log to the debug UART |
| `NET_INSTALL_AT_POWER_ON` | `0` | |
| `POWER_OFF_ON_HALT`, `WAKE_ON_GPIO` | `0`, `1` | |

`sudo rpi-eeprom-update` only reports; do not go by its "up to date" or "update
available" line, which compares with the package installed in the root, not
with what the fleet wants. On both Pis above it printed `BOOTLOADER: up to
date`.

**Is the flash locked?** No packaged tool we found prints the flash's status
registers. This script does (read commands only; it changes nothing). Save it
on the Pi as `read_flash_status.py`:

```{literalinclude} bootloader-eeprom/read_flash_status.py
:language: python
```

```console
$ sudo python3 read_flash_status.py
jedec ef4015
SR1 0xbc
SR2 0x2
SR3 0x60
```

Those are the values this code read on every locked fleet Pi 5 (4 Oct 2026,
four boards; the script in exactly this form has not been run yet). `SR1 0xbc` is
locked; `SR1 0x0` is not locked:

```{image} bootloader-eeprom/sr1-bits.svg
:alt: Status register 1 bit by bit: 0xbc is SRP, TB, BP2, BP1 and BP0 set (locked); 0x00 is not locked
:width: 100%
```

A `jedec` other than `ef4015` is a flash part we have not handled: stop and do
not write anything to that Pi.
