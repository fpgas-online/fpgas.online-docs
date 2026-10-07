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

Three reads.

```{image} bootloader-eeprom/check-card.svg
:alt: Three reads: the bootloader date should be 2026/09/25, the boot order BOOT_ORDER=0xf2, and the flash lock SR1 0xbc
:width: 100%
```

```{include} bootloader-eeprom-read-state.inc
```

```{image} bootloader-eeprom/boot-order.svg
:alt: BOOT_ORDER is read from its last digit: 0xf2 is network only; 0xf12 and 0xf2461 also boot local media
:width: 100%
```

## Upgrade a locked Raspberry Pi 5

For a Raspberry Pi 5 whose check says NOT DONE. (How far each step has been
tried by us is listed under [What has been run](bootloader-eeprom.md#what-has-been-run).)

```{image} bootloader-eeprom/kit.svg
:alt: What you need: the Pi 5 with its underside reachable, a microSD card, a Linux computer with a card reader, something to bridge two pads, the Pi's network cable on its switch port
:width: 100%
```

### Step 1: make the card

The Pi stays plugged in and running during this step.

```{image} bootloader-eeprom/card-files.svg
:alt: The finished card holds four files at its top level: recovery.bin, pieeprom.bin, pieeprom.sig and config.txt
:width: 100%
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

### Step 2: network cable out

```{image} bootloader-eeprom/cable-out.svg
:alt: A Raspberry Pi 5, top side up, with its network cable pulled out of the Ethernet socket
:width: 80%
```

1. Pull the Pi's network cable. If the Pi also has a USB-C power supply, pull
   that too. The Pi is now off.
2. Take the Pi out of whatever holds it. Turn it over like the page of a
   book: the USB sockets, on your right in this drawing, end up on your left.

### Step 3: join the two FLASH WP pads

The Pi is off (step 2). This is its underside, USB-A sockets on the left, GPIO
header along the top:

```{figure} bootloader-eeprom/pi5-underside-flash-wp.jpg
:alt: Underside of a Raspberry Pi 5 with the two FLASH WP pads ringed, right of the CE mark and above the micro-HDMI sockets
:width: 100%

Photo: Suyash Dwivedi, [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Raspberry_Pi5_8GB_Bottom_View_(1).jpg), [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/); annotated, same licence.
```

```{figure} bootloader-eeprom/pi5-flash-wp-closeup.jpg
:alt: Close-up of the pads: TP14 on the left, TP1 on the right, FLASH WP printed below
:width: 100%

Photo: Suyash Dwivedi, [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Raspberry_Pi5_8GB_Bottom_View_(1).jpg), [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/); annotated, same licence.
```

```{figure} bootloader-eeprom/pi5-flash-wp-bridged.jpg
:alt: The same close-up with a blob of solder drawn across TP14 and TP1 only
:width: 100%

Photo: Suyash Dwivedi, [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Raspberry_Pi5_8GB_Bottom_View_(1).jpg), [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/); annotated, same licence.
```

```{figure} bootloader-eeprom/pi5-flash-wp-wrong.jpg
:alt: The same close-up with a blob of solder drawn that also reaches TP17, marked wrong
:width: 100%

Photo: Suyash Dwivedi, [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Raspberry_Pi5_8GB_Bottom_View_(1).jpg), [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/); annotated, same licence.
```

:::{warning}
`TP1` carries power when the Pi is on. A bridge that touches anything besides
`TP14` and `TP1` can damage the Pi. If yours does, take it off and make it
again now, while the Pi is off.
:::

1. Find the two pads.
2. Join `TP14` to `TP1` with a small blob of solder across both, as in the
   RIGHT picture.
3. Look at it against the RIGHT and WRONG pictures: one blob, on those two
   pads, touching nothing else. With a multimeter: `TP14` to `TP1` reads a
   short circuit.

No soldering iron? Skip items 2 and 3 of this step. In step 4 you hold tweezers (or a short wire)
on the two pads instead:

```{figure} bootloader-eeprom/pi5-flash-wp-tweezers.jpg
:alt: The same close-up with the two tips of a pair of tweezers drawn, one on TP14 and one on TP1
:width: 100%

Photo: Suyash Dwivedi, [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Raspberry_Pi5_8GB_Bottom_View_(1).jpg), [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/); annotated, same licence.
```

### Step 4: card in, network cable in, wait 60 seconds

```{figure} bootloader-eeprom/pi5-underside-sd-slot.jpg
:alt: Underside of a Raspberry Pi 5 with the microSD slot ringed on the right edge, a card going in, and the bridge still on the FLASH WP pads
:width: 100%

Photo: Suyash Dwivedi, [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Raspberry_Pi5_8GB_Bottom_View_(1).jpg), [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/); annotated, same licence.
```

1. Push the card into the slot.

```{image} bootloader-eeprom/cable-in.svg
:alt: A Raspberry Pi 5, top side up, with its network cable going into the Ethernet socket
:width: 80%
```

2. Plug the network cable in, on the switch port the Pi was on. (The drawing
   shows the Pi top side up; yours is lying upside down. The Ethernet socket
   is the one beside the two USB blocks.)

   No solder bridge? Do this instead of item 2:

   ```{figure} bootloader-eeprom/pi5-flash-wp-tweezers.jpg
   :alt: The same close-up with the two tips of a pair of tweezers drawn, one on TP14 and one on TP1
   :width: 100%

   Photo: Suyash Dwivedi, [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Raspberry_Pi5_8GB_Bottom_View_(1).jpg), [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/); annotated, same licence.
   ```

   - put one tip of the tweezers (or one end of the wire) on each pad;
   - plug the network cable in with your other hand;
   - keep the tips on both pads until the 60 seconds below are over.
3. Wait 60 seconds by a clock. There is nothing to watch for: the Pi writes
   its new bootloader from the card and stops. Whatever the green light does,
   go on to step 5 when the 60 seconds are over.

### Step 5: cable out, card out, bridge off, cable in

```{image} bootloader-eeprom/cable-out.svg
:alt: A Raspberry Pi 5, top side up, with its network cable pulled out of the Ethernet socket
:width: 80%
```

1. Pull the network cable.
2. Pull the card out of its slot.

```{figure} bootloader-eeprom/pi5-flash-wp-clear.jpg
:alt: Close-up of TP14 and TP1 as two separate pads again
:width: 100%

Photo: Suyash Dwivedi, [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Raspberry_Pi5_8GB_Bottom_View_(1).jpg), [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/); annotated, same licence.
```

3. Take the bridge off: wick the solder away (or let go of the wire or
   tweezers). The two pads must be separate again, as in the picture.
4. Put the Pi back where it was.

```{image} bootloader-eeprom/cable-in.svg
:alt: A Raspberry Pi 5, top side up, with its network cable going into the Ethernet socket
:width: 80%
```

5. Plug the network cable in, on the same switch port: the port this Pi
   normally lives on. (Some sites keep one port aside for bringing up new
   Pis, an EEPROM service port. A Pi plugged in there is never locked: not
   that port.)

:::{warning}
Leave the Pi alone for two minutes now. It starts from the network and locks
its flash again while it starts; do not pull the cable during that time. (The
two Pis we read after an upgrade on 6 October 2026 were already locked when
read, 40 and 100 seconds after they started.)
:::

### Step 6: read it back

Do the three reads again, then find your result in the chart at the end of
this step.

```{image} bootloader-eeprom/check-card-after.svg
:alt: Three reads: the bootloader date should be 2026/09/25, the boot order BOOT_ORDER=0xf2, and the flash lock SR1 0xbc
:width: 100%
```
```{include} bootloader-eeprom-read-state.inc
```

Your result:

```{image} bootloader-eeprom/outcomes.svg
:alt: What step 6 can read and what to do: all three as wanted, done; the old date, nothing was written, go back to step 2; the new date but another boot order, make the card again; the new date and boot order but SR1 0x0, power the Pi off and on and read again; no answer after five minutes, go back to step 2 with a checked card
:width: 100%
```
