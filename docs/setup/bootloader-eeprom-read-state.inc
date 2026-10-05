```{image} bootloader-eeprom/check-card.svg
:alt: Three reads: the bootloader date should be 2026/09/25, the boot order BOOT_ORDER=0xf2, and the flash lock SR1 0xbc
:width: 100%
```

Log in to the Pi as user `pi` (ssh, or the web terminal on its board page) and
run:

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

That is a Pi that is done. Only the first line of the first command and the
`BOOT_ORDER` line of the second matter for the check; the full settings the
fleet wants are the six lines shown.

```{image} bootloader-eeprom/boot-order.svg
:alt: BOOT_ORDER is read from its last digit: 0xf2 is network only; 0xf12 and 0xf2461 also boot local media
:width: 100%
```

For the third read, put this script on the Pi. Either
{download}`download it <bootloader-eeprom/read_flash_status.py>` and copy it over, or
type `cat > read_flash_status.py` on the Pi, paste the text below, and press
Ctrl-D:

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

It only reads. `SR1 0xbc` is locked, `SR1 0x0` is not:

```{image} bootloader-eeprom/sr1-bits.svg
:alt: Status register 1 bit by bit: 0xbc is SRP, TB, BP2, BP1 and BP0 set (locked); 0x00 is not locked
:width: 100%
```

If `jedec` is anything other than `ef4015`, this is a flash chip this page
does not cover: stop, and write nothing to that Pi.

Do not go by `sudo rpi-eeprom-update`: it prints "up to date" on Pis that are
not on the fleet's bootloader.
