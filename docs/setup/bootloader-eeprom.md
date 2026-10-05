# Bootloader EEPROM: upgrade and lock

Every Raspberry Pi since the Pi 4 keeps its bootloader and the bootloader's
settings in a small flash chip on the board, the bootloader EEPROM. On a fleet
Pi that chip is locked, so that nobody with root on the Pi can change how it
boots; a new bootloader therefore cannot simply be installed. Pick the part
you need:

- **[Check a Pi 5](#check-a-pi-5-nothing-is-changed)**: is its bootloader the fleet's, and is it locked?
- **[Upgrade a locked Raspberry Pi 5](#upgrade-a-locked-raspberry-pi-5)**: six steps, for someone with the Pi in hand.
- **[A Compute Module or a Compute Blade](#compute-module-4-compute-module-5-and-the-compute-blade)**: how to tell whether it needs anything (the two blades we read need nothing). There are no upgrade steps for it on this page.
- **[What is behind this page](#what-is-behind-this-page)**: what has been run and measured, what is not known, what does not work.

## Check a Pi 5 (nothing is changed)

Three reads, for a **Raspberry Pi 5**. (This page has no check and no upgrade
steps for a Pi 4.)

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
tried by us is listed under [What has been run](#what-has-been-run).)

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

No soldering iron? Skip 2 and 3. In step 4 you hold tweezers (or a short wire)
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

   No solder bridge? Do this instead of 2:

   ```{figure} bootloader-eeprom/pi5-flash-wp-tweezers.jpg
   :alt: The same close-up with the two tips of a pair of tweezers drawn, one on TP14 and one on TP1
   :width: 100%

   Photo: Suyash Dwivedi, [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Raspberry_Pi5_8GB_Bottom_View_(1).jpg), [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/); annotated, same licence.
   ```

   - put one tip of the tweezers (or one end of the wire) on each pad;
   - plug the network cable in with your other hand;
   - keep the tips on both pads until the 60 seconds of item 3 are over.
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
its flash again while it starts; do not pull the cable during that time.
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

## Compute Module 4, Compute Module 5 and the Compute Blade

:::{warning}
**There are no upgrade steps for a Compute Module in a Compute Blade on this
page, because we have not done one.** What this part gives you is how to tell
whether your blade needs anything. Both blades we read are fine as they are
and need nothing.
:::

### Does this blade need anything?

Log in to the blade the way you normally do and run these two. They change
nothing and need no root.

```console
$ vcgencmd bootloader_version
2025/12/08 19:29:54
version 2226a853bb9f5fd80392e3a4a89e457aeca88008 (release)
timestamp 1765222194
update-time 1774980226
capabilities 0x0000007f
$ vcgencmd bootloader_config
[all]
BOOT_UART=1
# Default BOOT_ORDER for provisioning
# SD -> NVMe -> USB -> Network
BOOT_ORDER=0xf2461
```

That is what one blade of ours (a Compute Module 5 Lite) printed while it was
running from the network.

```{image} bootloader-eeprom/boot-order-blade.svg
:alt: 0xf2461 read from its last digit: SD card, NVMe, USB, then the network, then round again
:width: 100%
```

:::{important}
**What to do**

- Your blade starts from the network, and its `BOOT_ORDER` has a `2` in it (as
  `0xf2461` has): **do nothing.** Its bootloader is fine as it is.
- Your blade does not start from the network, or its `BOOT_ORDER` has no `2`
  in it: **do not try to change it from this page.** If the blade is part of
  fpgas.online, open an issue at
  [fpgas-online/fpgas.online-docs](https://github.com/fpgas-online/fpgas.online-docs/issues)
  with the two outputs above. If it is your own, this page cannot help you
  further: what the blade's maker and Raspberry Pi document is quoted at the
  end of this page, untested by us.
- Your blade is meant to start from its own storage (an SSD or a card) and
  does: it is not broken, and nothing on this page applies to it.
:::

A date in the first line that is older or newer than the one above is not a
reason to act, and neither is "UPDATE AVAILABLE" from `rpi-eeprom-update`.

### Why there are no steps: what a blade would need

```{image} bootloader-eeprom/blade-dev.svg
:alt: Outline of a Dev model Compute Blade with the USB Type-C port (1), the USB switch (2), the nRPIBOOT button (3) and the DIP switches marked
:width: 100%
```

A Compute Module's bootloader is written over USB from another computer, and
that needs the three parts numbered 1, 2 and 3 in the drawing. The blade's
maker says only the Dev model has them. A failed write on a Compute Module can
be repaired only the same way, which is why a blade that works is left alone.

```{image} bootloader-eeprom/blade-dip.svg
:alt: The three DIP switches of a Dev model Compute Blade: 1 write protection (left disabled, right enabled), 2 Wi-Fi, 3 Bluetooth
:width: 85%
```

The Dev model also has the switch that holds the bootloader's write protection.

## What is behind this page

You do not need this part to do the job.

### What has been run

- **Upgrade of a locked Pi 5, steps 2 to 6:** once, on one fleet Pi 5, on 3 Oct
  2026, and not exactly as written here. How the card used that day was made
  was not recorded. The Pi sat on the site's EEPROM service port for the
  write and was moved to a normal port afterwards, where it read locked
  (`SR1 0xbc`) when next looked at; the lock coming back in the first start
  after a card write was not watched. That a normal fleet start locks an
  unlocked flash within that one start was measured on another occasion
  (`SR1` from `0x00` to `0xbc`).
- **The times in the steps** (60 seconds for the write, two minutes for the
  start, five minutes before calling a Pi gone) are generous round figures of
  ours, not measurements of the write.
- **Step 1:** the commands up to the four files were run on a PC on 5 Oct 2026
  (raspberrypi/rpi-eeprom at commit `a72213d`, fetched with `git clone --depth 1`
  on the day that commit was its newest); the outputs shown are from that run. Formatting a card and booting a Pi from a card made this way:
  **not yet run by us.**
- **The check:** the outputs are from fleet Pi 5s on 4 Oct 2026 (four boards
  for the status registers). The read script printed exactly as shown has
  **not yet been run in that form**; the same code inside another tool
  produced the values.
- **The board page and its web terminal** have no picture on this page yet.
- **The pictures of the bridge** are drawn on a photo. We have no photo of a
  real bridge, of a card going in, or of the LED during a write.
- **The LED during the write:** Raspberry Pi's documentation says a steady
  rapid blink means success and an error pattern means failure. On our one run
  it blinked 3 long, 3 short, an error pattern, although the write had
  succeeded. That is why step 4 says to ignore it.
- **The "another boot order", "SR1 0x0" and "no answer" rows of step 6:** not
  seen by us. A Pi that is written but not locked can be changed by anyone
  with root on it, which on a public site is every visitor: that is why its
  row says to tell the operator if it stays unlocked. That a Pi 5 runs `recovery.bin` from a card whatever its flash holds is
  Raspberry Pi's documentation, not yet needed and so not yet run by us.
- **Compute Module, Compute Blade:** only the two reads. Nothing that changes
  a bootloader has been run by us on that hardware.

### What two fleet Pi 5s printed

A Pi that still needed the upgrade, 4 Oct 2026, beside the done one shown in
the check:

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

`sudo rpi-eeprom-update` printed `BOOTLOADER: up to date` on both: it compares
with the package installed in the root, not with what the fleet wants. The
second PS1 blade read on 5 Oct 2026 (pi20) printed `2025/11/05 17:37:18` and
the same settings as the blade shown above (pi16).

### The lock, bit by bit

```{image} bootloader-eeprom/sr1-bits.svg
:alt: Status register 1 bit by bit: 0xbc is SRP, TB, BP2, BP1 and BP0 set (locked); 0x00 (printed as 0x0) is not locked
:width: 100%
```

The script prints `0x00` as `0x0`. The W25Q16JV datasheet also says that with
QE = 1, as these flashes have, the `/WP` pin is not used; what that means for
the lock is under [Not yet known](#not-yet-known).

### Why the flash is locked

See [EEPROM write protect](netboot.md#eeprom-write-protect).

### What was measured on the Pi 5

All of it on Pi 5 boards with the W25Q16 flash, netbooting the fleet root, on
3 and 4 Oct 2026. Observations 2 to 5 are from one board.

| | Observation |
|---|---|
| 1 | `eeprom_write_protect=1` in the `config.txt` served over netboot **is applied**: SR1 went from `0x00` to `0xbc` in one boot (one board). All four Pi 5s we read were locked this way, two of them never handled for it. |
| 2 | `eeprom_write_protect=0` served over netboot **was not applied**: SR1 stayed `0xbc` over four boots. The `TP14` to `TP1` bridge was believed fitted during those boots, but that was not checked and cannot be read from software (observation 6). |
| 3 | With the flash protected, the netboot self-update fetched `pieeprom.sig` and `pieeprom.upd`, wrote nothing, tried once more and then booted the operating system. **Nothing anywhere reported the failed update.** |
| 4 | An SD card holding `recovery.bin`, `pieeprom.bin` and a `config.txt` with `eeprom_write_protect=0` (whether `pieeprom.sig` was on it was not recorded), with the `TP14` and `TP1` pads bridged, cleared the protection and wrote the new bootloader. The activity LED blinked 3 long, 3 short although the write had succeeded. |
| 5 | With the flash unprotected and already holding the offered image, the netboot self-update found nothing to do and booted on. |
| 6 | The flash's `/WP` pin goes to no SoC GPIO: software cannot read whether the pads are bridged. |
| 7 | A bootloader of `2026/05/26` already provides `/dev/pio0` (RP1 PIO). The upgrade to `2026/09/25` is for a uniform fleet. |

Observation 1 does not fit a plain reading of Raspberry Pi's description
(quoted further down), where the setting is "for `recovery.bin`": the bootloader applied it from
a netbooted `config.txt`. For observation 2 the simplest explanation is a bridge
that was not making contact; the other is that the bootloader sets but does not
clear the protection outside `recovery.bin`. Which it is has not been found out
(the bootloader's UART log during such a boot has not been captured), so an
unlock over netboot is **not shown to work**, and not shown to be impossible.

### Not yet known

- **Whether the lock holds against root on the Pi.** Raspberry Pi's
  documentation says the Pi 5's `/WP` pin is low by default, so the status
  register cannot be changed without bridging the pads. The W25Q16JV datasheet
  says that with `QE=1` (which these flashes have) the `/WP` function is
  disabled. If the datasheet is right, root could clear the protection with two
  SPI commands. **Nobody has tried it.** Until it is tried, treat the lock as
  protection against accident and against the standard tools, not as proven
  against a determined visitor.
- Whether the SD card route works without the bridge.
- Whether `eeprom_write_protect=0` over netboot unlocks a Pi 5 whose bridge is
  known to be fitted (observation 2).
- What `rpi-eeprom-update -a` or `rpi-eeprom-config --apply` does on a locked,
  netbooted fleet Pi. Neither has been run by us there.
- Whether a Pi 5 that does not boot any more is repaired by the same card.
  Raspberry Pi documents that it is (below); we have not had such a board.

### What does not work

- A netboot self-update against the protected flash: nothing is written and
  nothing reports it (observation 3). `rpi-eeprom-update -a` and
  `rpi-eeprom-config --apply` stage the same kind of update for the bootloader
  to apply, so the same outcome is expected; not yet run by us.
- Serving `eeprom_write_protect=0` to the Pi over netboot did not unlock it when
  tried, with the caveat of observation 2.
- `flashrom`: Raspberry Pi's documentation says it "does not support clearing
  of the write-protect regions and will fail to update the EEPROM if
  write-protect regions are defined".

### What Raspberry Pi says (Pi 4 and Pi 5)

From the [`config.txt` documentation,
`eeprom_write_protect`](https://www.raspberrypi.com/documentation/computers/config_txt.html#eeprom_write_protect):

> Configures the EEPROM `write status register`. This can be set either to mark
> the entire EEPROM as write-protected, or to clear write-protection.
>
> This option must be used in conjunction with the EEPROM `/WP` pin which
> controls updates to the EEPROM `Write Status Register`. Pulling `/WP` low (CM4
> `EEPROM_nWP` or on a Raspberry Pi 4 `TP5`) does NOT write-protect the EEPROM
> unless the `Write Status Register` has also been configured.
>
> [...]
>
> `eeprom_write_protect` settings in `config.txt` for `recovery.bin`.
>
> [...]
>
> On Raspberry Pi 5 `/WP` is pulled low by default and consequently
> write-protect is enabled as soon as the `Write Status Register` is configured.
> To clear write-protect pull `/WP` high by connecting `TP14` and `TP1`.

Values: `1` protects the whole EEPROM, `0` clears the protection, `-1` (the
default) does nothing.

From [Raspberry Pi boot EEPROM,
`recovery.bin`](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#recovery-bin):

> At power on, the ROM found on BCM2711 and BCM2712 looks for a file called
> `recovery.bin` in the root directory of the boot partition on the SD card. If
> a valid `recovery.bin` is found then the ROM executes this instead of the
> contents of the EEPROM. This mechanism ensures that the bootloader flash image
> can always be reset to a valid image with factory default settings.

and, on the same page:

> If the bootloader update image is called `pieeprom.bin` then `recovery.bin`
> will stop after the update has completed. On success the HDMI output will be
> green and the green activity LED is flashed rapidly. If the update fails, the
> HDMI output will be red and an error code will be displayed by the activity
> LED.

### The service port at Welland

At Welland one switch port is kept as an EEPROM service port. The gateway serves
a Pi on that port its own boot tree, holding the target `pieeprom.upd` and
`pieeprom.sig` and a `config.txt` with `eeprom_write_protect=0`, and no other
port sees those files. With today's findings it upgrades only a Pi whose flash
is **not** protected (a new Pi, or one cleared with the card), and it is where an
upgrade can be watched. Making it a managed feature that upgrades a locked Pi
without a visit is open work.

### What the Compute Blade's maker documents

:::{warning}
Untested by us. Do not follow these as steps.
:::

Only the **Dev** model of the Compute Blade has the parts for the USB route.
The maker says so where it describes writing an operating system to a module's
eMMC, in a guide written for the Compute Module 4 ([image
guide](https://docs.computeblade.com/blade/getting-started/image)); the same
port and button are what a bootloader flash over USB needs:

> eMMC can only be imaged on Dev blade as it has USB Type-C port, USB switch,
> and nRPIBOOT button

and, for putting the module into USB boot:

> From the usbboot directory run `sudo ./rpiboot`
>
> Move the USB switch to the USB Type-C position. Then, while holding down the
> nRPIBOOT button on the blade connect the USB Type-C cable.
>
> The Device will reconnect several times. On the last time it will appear as a
> USB media device.

The [USB switch](https://docs.computeblade.com/blade/guides/usb) is there
because "The compute module can only operate one USB port at a time." The
maker's [usbboot guide](https://docs.computeblade.com/blade/advanced-guides/usbboot)
covers building `rpiboot` and says the configuration is edited in
`/usbboot/<firmware directory>/config.txt`; for the flash itself it points to
Raspberry Pi's "Flash Compute Module bootloader EEPROM", which is the procedure
printed again [below](#what-raspberry-pi-documents-for-a-compute-module).

The write-protect pin is on a DIP switch, again on the Dev model only. From the
maker's [DIP switch guide](https://docs.computeblade.com/blade/guides/dip):

> DIP Switch is ONLY populated on Dev model Compute Blades.
>
> Only change switch positions when the Blade is unplugged from power.

> To enable write protection, changes are required to `config.txt`. It can be
> found in the directory `/boot/firmware/`, or flash the EEPROM using usbboot
> adding the following line to the `config.txt` file `eeprom_write_protect=1`
> This will pull the `EEPROM_nWP` pin low. This will enable the DIP switch.

Read with Raspberry Pi's description (quoted below), that is the same two-part lock:
`eeprom_write_protect=1` sets the flash's status register, and switch 1 is what
holds `EEPROM_nWP` low. Raspberry Pi requires `EEPROM_nWP` not to be low while
the bootloader is flashed, and the maker's table calls the left position
"Disabled", so left is the position for an upgrade. That last step is our
inference from the two documents, not something either states or we have tried.

### What is not known about the blade

- **Which model the PS1 blades are.** We have not recorded it. The maker's
  pages name a Dev model and a TPM model. On a blade that is not a Dev model
  the maker describes no USB Type-C port, no nRPIBOOT button and no DIP
  switch, so, as far as those pages go, neither the USB route nor the hardware
  lock exists on the blade itself; the module would then have to go into a
  carrier that has them (Raspberry Pi describes the route on its own IO
  boards), which we have not done.
- **What a blade without the DIP switch does with `EEPROM_nWP`** (tied low,
  tied high or left open). The maker's pages we read do not say.
- **Whether a blade's bootloader can be updated from the running system.**
  Raspberry Pi's self-update needs update files in the boot file system it
  booted from ("For network boot make sure that the TFTP `boot` directory can
  be mounted through NFS and that `rpi-eeprom-update` can write to it"), and
  it "does not update the bootloader atomically". On a netboot root like PS1's,
  a read-only export under a tmpfs overlay, a file written on the blade never
  reaches the boot directory the bootloader reads, so we expect it not to
  work there. Not tried by us on any Compute Module.

### What Raspberry Pi documents for a Compute Module

:::{warning}
Untested by us on this hardware. Do not follow these as steps on a blade: they
are written for Raspberry Pi's own IO boards.
:::

:::{warning}
**Not yet run by us on this hardware.** Everything in this section is Raspberry
Pi's documentation, quoted from
[raspberrypi/documentation](https://github.com/raspberrypi/documentation) at
commit `287523e6`. No fpgas.online Compute Module has had its bootloader
upgraded or locked by this procedure. Read the bootloader state first (the
`vcgencmd` commands above work on a Compute Module; the device node of the boot
flash and its part have not been read by us on a CM4 or CM5).
:::

The SD card route above **does not exist** on a Compute Module. From [Compute
Module EEPROM
bootloader](https://www.raspberrypi.com/documentation/computers/compute-module.html#compute-module-eeprom-bootloader):

> On Compute Modules with an EEPROM bootloader, ROM never runs `recovery.bin`
> from SD/eMMC. These Compute Modules disable the `rpi-eeprom-update` service by
> default, because eMMC is not removable and an invalid `recovery.bin` file
> could prevent the system from booting.
>
> You can override this behaviour with `self-update` mode. In `self-update`
> mode, you can update the bootloader from USB MSD or network boot.
>
> WARNING: `self-update` mode does not update the bootloader atomically. If a
> power failure occurs during an EEPROM update, you could corrupt the EEPROM.

and from the Pi boot EEPROM page: "Reflashing the bootloader over USB is also
the only option available for CM4 and CM4S."

**Flashing the bootloader over USB (`rpiboot`).**

This needs a second computer with
[`rpiboot`](https://github.com/raspberrypi/usbboot) (`sudo apt install rpiboot`,
or built from source), a USB cable to the carrier's USB device port, and the
carrier's `nRPI_BOOT` jumper or button, which makes the module wait for a USB
host instead of booting. Raspberry Pi describes it for its own IO boards ("Fit
`nRPI_BOOT` to J2 (`disable eMMC Boot`) on the IO board jumper"); another
carrier brings `nRPI_BOOT` and the USB device port out in its own way, to be
looked up in that carrier's documentation.

> To flash the bootloader EEPROM:
>
> 1. Set up the hardware as you would when flashing the eMMC, but ensure
>    `EEPROM_nWP` is _not_ pulled low.
> 2. Run the following command to write `recovery/pieeprom.bin` to the
>    bootloader EEPROM: `./rpiboot -d recovery`
> 3. When complete, `EEPROM_nWP` can be pulled low again.

**Setting the configuration and the lock.**

> To modify the Compute Module EEPROM bootloader configuration:
>
> 1. Navigate to the `usbboot/recovery` directory.
> 2. If you require a specific bootloader release, replace
>    `pieeprom.original.bin` with the equivalent from your bootloader release.
> 3. Edit the default `boot.conf` bootloader configuration file to define a
>    `BOOT_ORDER`: For network boot, use `BOOT_ORDER=0xf2`. For SD/eMMC boot,
>    use `BOOT_ORDER=0xf1`. For USB boot failing over to eMMC, use
>    `BOOT_ORDER=0xf15`. For NVMe boot, use `BOOT_ORDER=0xf6`.
> 4. Run `./update-pieeprom.sh` to generate a new EEPROM image `pieeprom.bin`
>    image file.
> 5. If you require EEPROM write-protection, add `eeprom_write_protect=1` to
>    `/boot/firmware/config.txt`. When enabled in software, you can lock
>    hardware write-protection by pulling the `EEPROM_nWP` pin low.
> 6. Run the following command to write the updated `pieeprom.bin` image to
>    EEPROM: `../rpiboot -d .`

So on a Compute Module the lock has two parts, as on the Pi 4: the status
register, set by `eeprom_write_protect=1`, and the `EEPROM_nWP` pin of the
module's connector, which the carrier must pull low for the status register to
stay as set. Raspberry Pi's step 5 names `/boot/firmware/config.txt` while step
6 flashes from the `usbboot/recovery` directory, which has a `config.txt` of its
own; which of the two the setting has to be in is not clear from the text and
not tried by us. Whether a given carrier pulls `EEPROM_nWP` low, leaves it open or
brings it to a jumper is a property of that carrier. For the upgrade it must
**not** be low; for the lock it must be.

**Differences from the Pi 5.**

- No card route and no `recovery.bin` from storage. Raspberry Pi names USB
  `rpiboot` as the only way to reflash a CM4; for a CM5 we infer the same from
  the passage above. A Compute Module whose bootloader is broken therefore
  needs its carrier's USB device port and `nRPI_BOOT`.
- Self-update over netboot exists but "does not update the bootloader
  atomically": a power cut during the write can leave a module that only
  `rpiboot` repairs.
- Our Pi 5 finding that a protected flash ignores a netboot self-update
  silently (observation 3) may hold here too: read the version after any
  upgrade.

## Sources

- Measurements: fpgas.online Welland fleet, 3 and 4 Oct 2026, Pi 5.
- [Raspberry Pi documentation](https://github.com/raspberrypi/documentation),
  commit `287523e6`: `computers/config_txt/boot.adoc`,
  `computers/raspberry-pi/boot-eeprom.adoc`,
  `computers/raspberry-pi/eeprom-bootloader.adoc`,
  `computers/compute-module/cm-bootloader.adoc`,
  `computers/compute-module/cm-emmc-flashing.adoc`.
- Winbond W25Q16JV datasheet (status register bits, `/WP` and `QE`).
- [Compute Blade documentation](https://docs.computeblade.com/) (Uptime Lab),
  read 5 Oct 2026: getting-started/image, guides/dip, guides/usb,
  advanced-guides/usbboot.
- Bootloader reads of two PS1 Compute Blades (Compute Module 5 Lite), 5 Oct
  2026.
- Figures: `docs/setup/bootloader-eeprom/make_figures.py` in this repository
  draws them. The photographs are crops of "Raspberry Pi5 8GB Bottom View
  (1).jpg" by Suyash Dwivedi, [Wikimedia
  Commons](https://commons.wikimedia.org/wiki/File:Raspberry_Pi5_8GB_Bottom_View_(1).jpg),
  [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/); the
  annotated versions are under the same licence.
- Step 1 as run: [raspberrypi/rpi-eeprom](https://github.com/raspberrypi/rpi-eeprom)
  at commit `a72213d`, 5 Oct 2026, on a PC.
