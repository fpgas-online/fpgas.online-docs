# Bootloader EEPROM on a Raspberry Pi 5: step 1, make the card

**You are upgrading a locked Raspberry Pi 5 ([what you need](bootloader-eeprom-pi5-upgrade.md))
and now make its microSD card on a Linux computer.**

The Pi stays plugged in and running during this step.

```{image} bootloader-eeprom/card-files.svg
:alt: The finished card holds four files at its top level: recovery.bin, pieeprom.bin, pieeprom.sig and config.txt
:width: 100%
:class: only-light
```

```{image} bootloader-eeprom/card-files-dark.svg
:alt: The finished card holds four files at its top level: recovery.bin, pieeprom.bin, pieeprom.sig and config.txt
:width: 100%
:class: only-dark
```

On the computer, get Raspberry Pi's bootloader files, at the version these
steps were written with:

```console
$ git clone https://github.com/raspberrypi/rpi-eeprom
$ cd rpi-eeprom
$ git checkout a72213d02af27f2dc3b86f584988aec407e46378
$ mkdir card
```

Make the settings file. Paste this whole block as it is:

```console
$ cat > boot.conf <<'EOF'
[all]
BOOT_UART=1
WAKE_ON_GPIO=1
POWER_OFF_ON_HALT=0
BOOT_ORDER=0xf2
NET_INSTALL_AT_POWER_ON=0
EOF
```

Make the four files:

```console
$ ./rpi-eeprom-config --config boot.conf --out card/pieeprom.bin \
      firmware-2712/default/pieeprom-2026-09-25.bin
$ ./rpi-eeprom-digest -i card/pieeprom.bin -o card/pieeprom.sig
$ cp firmware-2712/default/recovery.bin card/
$ echo eeprom_write_protect=0 > card/config.txt
```

Check them. The first command must print `[all]` and the five settings, and
the second must list the four files with these sizes:

```console
$ ./rpi-eeprom-config card/pieeprom.bin
[all]
BOOT_UART=1
WAKE_ON_GPIO=1
POWER_OFF_ON_HALT=0
BOOT_ORDER=0xf2
NET_INSTALL_AT_POWER_ON=0
$ wc -c card/*
     23 card/config.txt
2097152 card/pieeprom.bin
     80 card/pieeprom.sig
 104314 card/recovery.bin
2201569 total
```

If `BOOT_ORDER` there is not `0xf2`, stop and make `boot.conf` again: a card
with another boot order leaves a Pi that does not start from the network.

Now the card. Find its name: run `lsblk` before you put the card in the reader
and again after. The line that is new is the card. In this example (yours
will differ) it is `sdb`:

```console
$ lsblk -d -o NAME,SIZE,MODEL
NAME      SIZE MODEL
nvme0n1 476.9G Samsung SSD 980
$ lsblk -d -o NAME,SIZE,MODEL
NAME      SIZE MODEL
nvme0n1 476.9G Samsung SSD 980
sdb      29.7G STORAGE DEVICE
```

The next commands erase everything on the card. Put your card's name in the
first line in place of `sdX`, and check it twice: the wrong name erases
another disk. (For a name like `mmcblk0` the second line is
`PART=${DISK}p1`.) The `umount` lets go of the card if your desktop opened it
by itself; "not mounted" from it is fine.

```console
$ DISK=/dev/sdX
$ PART=${DISK}1
$ sudo umount ${DISK}*
$ sudo wipefs -a $DISK
$ echo 'type=c' | sudo sfdisk $DISK
$ sudo mkfs.vfat -F 32 $PART
$ sudo mount $PART /mnt
$ sudo cp card/* /mnt/
$ ls /mnt
config.txt  pieeprom.bin  pieeprom.sig  recovery.bin
$ sudo umount /mnt
```

Take the card out of the reader.
