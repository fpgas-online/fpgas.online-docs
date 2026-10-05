Open the Pi's board page on the site and use the web terminal there: it logs
you in as user `pi`. (With ssh instead: `ssh pi@` followed by the address on
that page; the same page shows the password.) Run:

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

That is what a Pi that is done prints. Read 1 is the first line of the first
command. Read 2 is the `BOOT_ORDER` line of the second.

Read 3 needs a small script on the Pi (a fleet Pi forgets it at every restart,
so put it there each time). In the terminal on the Pi, type
`cat > read_flash_status.py`, press Enter, paste the text below, press Enter
and then Ctrl-D.

```{literalinclude} bootloader-eeprom/read_flash_status.py
:language: python
```

Then run it. It only reads. (With ssh from a computer that has the script as
a file, {download}`downloaded here <bootloader-eeprom/read_flash_status.py>`,
one command does both: `ssh pi@ADDRESS sudo python3 - < read_flash_status.py`.)

```console
$ sudo python3 read_flash_status.py
jedec ef4015
SR1 0xbc
SR2 0x2
SR3 0x60
```

Read 3 is the `SR1` line: `0xbc` is locked, `0x0` is not locked. If the `jedec`
line is anything other than `ef4015`, this is a flash chip this page does not
cover: stop, and write nothing to that Pi.

Do not use `sudo rpi-eeprom-update` for this check: it prints "up to date" on
Pis that are not on the fleet's bootloader.
