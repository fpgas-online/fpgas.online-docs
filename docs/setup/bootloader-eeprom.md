# Bootloader EEPROM: upgrade and lock

Every Raspberry Pi since the Pi 4 keeps its bootloader and the bootloader's
settings in a small flash chip on the board, the bootloader EEPROM. The fleet
keeps it locked ([why](netboot.md#eeprom-write-protect)), so a new bootloader
cannot simply be installed. Pick the part you need:

- **[Check a Pi](#check-a-pi-nothing-is-changed)**: is its bootloader the fleet's, and is it locked?
- **[Upgrade a locked Raspberry Pi 5](#upgrade-a-locked-raspberry-pi-5)**: the steps, for someone with the Pi in hand.
- **[A Compute Module or a Compute Blade](#compute-module-4-compute-module-5-and-the-compute-blade)**: whether it needs anything (usually not), and what is known.
- **[What is behind this page](#what-is-behind-this-page)**: what was measured, what is not known, what does not work.

## Check a Pi (nothing is changed)

```{include} bootloader-eeprom-read-state.inc
```

## Upgrade a locked Raspberry Pi 5

Steps 2 to 6 were done once, on one fleet Pi 5, on 3 Oct 2026. Step 1 was run on
a PC on 5 Oct 2026 as far as the finished files; a card made that way has not
yet been booted by us (how the card used on 3 Oct was made was not recorded).

**You need:** the Pi 5 and access to its underside; a microSD card and a
computer with a card reader; something to join two pads about 2 mm apart (a soldering
iron and solder, or a short wire or fine tweezers you can hold still for a
minute); the Pi's network cable, which also powers it.

:::{warning}
The Pi is **unplugged** for steps 2, 3 and 5. The only time it has power in this
procedure is step 4, and you do not touch the board then except to hold a
bridge that is not soldered.
:::

### Step 1: make the card

On a computer with `git`, `python3` and `openssl`:

```console
$ git clone --depth 1 https://github.com/raspberrypi/rpi-eeprom
$ cd rpi-eeprom
$ mkdir card
```

Save the fleet's settings as `boot.conf` in that directory. This is the whole
file:

```{literalinclude} bootloader-eeprom/boot.conf
:language: ini
```

Put the settings into the `2026/09/25` bootloader image, make its checksum file,
and add the two other files:

```console
$ ./rpi-eeprom-config --config boot.conf --out card/pieeprom.bin \
      firmware-2712/default/pieeprom-2026-09-25.bin
$ ./rpi-eeprom-digest -i card/pieeprom.bin -o card/pieeprom.sig
$ cp firmware-2712/default/recovery.bin card/
$ echo eeprom_write_protect=0 > card/config.txt
```

Check the result before it goes on a card. A boot order other than `0xf2` here
gives a Pi that does not boot from the network afterwards:

```console
$ ./rpi-eeprom-config card/pieeprom.bin
[all]
BOOT_UART=1
WAKE_ON_GPIO=1
POWER_OFF_ON_HALT=0
BOOT_ORDER=0xf2
NET_INSTALL_AT_POWER_ON=0
$ ls -l card
       23 config.txt
  2097152 pieeprom.bin
       80 pieeprom.sig
   104314 recovery.bin
$ sha256sum firmware-2712/default/pieeprom-2026-09-25.bin
02c4daa25df5af66af50da63ee97dfd03b21a40ac5b495a1c447979a2aa00edd  firmware-2712/default/pi...
```

(The listing is shortened to size and name, and the last line is cut after the checksum. `pieeprom.sig` holds the checksum of
your `pieeprom.bin` and the time you made it, so its content differs from run to
run.)

Format the microSD card with one FAT32 partition and copy the four files of
`card/` into its top directory, nothing else. Eject it properly.

### Step 2: unplug the Pi

Pull the network cable (it carries the power). If the Pi has a USB-C supply as
well, pull that too. Take off anything that hides the underside.

### Step 3: bridge the two FLASH WP pads

Turn the Pi over, with the USB-A sockets on your left and the GPIO header along
the top. The two pads are low and a little left of the middle: right of the CE
mark, above the pair of micro-HDMI sockets. The board prints `TP14 TP1` above
them and `FLASH WP` below. They are larger than the test points around them.

```{figure} bootloader-eeprom/pi5-underside-flash-wp.jpg
:alt: Underside of a Raspberry Pi 5 with the two FLASH WP pads ringed, right of the CE mark and above the micro-HDMI sockets
:width: 100%

Where the pads are. Photo: Suyash Dwivedi, [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Raspberry_Pi5_8GB_Bottom_View_(1).jpg), [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/); cropped and annotated by fpgas.online, this version under the same licence.
```

```{figure} bootloader-eeprom/pi5-flash-wp-closeup.jpg
:alt: Close-up of the pads: TP14 on the left, TP1 on the right, FLASH WP printed below
:width: 100%

The two pads close up. TP14 (left) is the flash chip's write-protect line, held low by the board; TP1 (right) is 3.3 V. Photo: Suyash Dwivedi, [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Raspberry_Pi5_8GB_Bottom_View_(1).jpg), [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/); cropped and annotated by fpgas.online, this version under the same licence.
```

Join TP14 to TP1 and nothing else. Either solder a small blob across both pads
(it comes off again in step 5), or be ready to hold a wire or tweezers across
both for the whole of step 4.

```{figure} bootloader-eeprom/pi5-flash-wp-bridged.jpg
:alt: The same close-up with a bridge drawn across TP14 and TP1
:width: 100%

The bridge in place. **This bridge is drawn on the photo; it is not a photo of a real bridge.** Photo: Suyash Dwivedi, [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Raspberry_Pi5_8GB_Bottom_View_(1).jpg), [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/); cropped and annotated by fpgas.online, this version under the same licence.
```

*If the bridge touches a neighbouring test point (TP17 and TP13 are the nearest,
to the left):* take it off and make it again before any power is applied.

### Step 4: card in, power on, wait one minute

Push the card into the slot on the underside, contacts towards the board, until
it stops.

```{figure} bootloader-eeprom/pi5-underside-sd-slot.jpg
:alt: Underside of a Raspberry Pi 5 with the microSD slot ringed on the right edge and the bridge still on the FLASH WP pads
:width: 100%

The card slot, with the bridge still fitted. Photo: Suyash Dwivedi, [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Raspberry_Pi5_8GB_Bottom_View_(1).jpg), [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/); cropped and annotated by fpgas.online, this version under the same licence.
```

Plug the network cable in. The Pi runs `recovery.bin` from the card before
anything else, whatever its boot order, writes the new bootloader and stops; it
does not go on to start an operating system. Leave it for one full minute.

What you may see: the green LED blinking. Raspberry Pi's documentation says a
steady rapid blink means success and an error pattern means failure; on our one
run the LED blinked 3 long, 3 short (an error pattern) **although the write had
succeeded**. So do not go by the LED. The proof is the read in step 6. We have
no photo of the LED during a write.

*If nothing at all lights:* the Pi has no power; check the cable and the switch
port.

### Step 5: unplug, card out, bridge off

Pull the network cable. Take the card out. Take the bridge off (wick the solder
away, or just let go), and look that the two pads are separate again and no
solder went anywhere else. Put back whatever you took off, and plug the Pi in on
its normal fleet port.

It now boots from the network, about two minutes to a login. The fleet's
`config.txt` carries `eeprom_write_protect=1`, and the Pi's firmware locks the
flash again in that same boot. Do not cut the power in the first seconds after
plugging in.

### Step 6: read it back

```{include} bootloader-eeprom-read-state.inc
```

The upgrade is done when all three are true: the first line of
`bootloader_version` is `2026/09/25`, the settings are the six lines of
`boot.conf` from step 1, and `SR1` reads `0xbc`.

| What you read | What happened | What to do |
|---|---|---|
| the old date, old settings | nothing was written: the bridge did not make contact, or the card was not read | repeat from step 2; check the card's four files on a computer |
| the new date, `SR1 0x0` | written, but not locked again (not seen by us) | check that the Pi booted the fleet's root and not a card; power it off and on once and read again |
| the Pi does not come back on the network at all | a wrong `BOOT_ORDER` in the image, or the write was cut short | put the bridge and the card back and run step 4 again with a checked card. The Pi runs `recovery.bin` from a card whatever its flash holds (Raspberry Pi's documentation; **not yet needed, so not yet run, by us**) |

## Compute Module 4, Compute Module 5 and the Compute Blade

:::{warning}
**We cannot give you steps for upgrading the bootloader of a Compute Module in
a Compute Blade yet.** We have not done it, and it depends on parts that only
one model of the blade has (below). What we can give: how to tell whether a
blade needs anything, which the two blades we read do not, and what the two
makers document. Everything in this part beyond the reads is **not yet run by
us on this hardware**.
:::

### Does this blade need it at all?

Usually not. Run these two on the blade; they change nothing and need no root:

```console
$ vcgencmd bootloader_version
$ vcgencmd bootloader_config
```

What two PS1 blades printed on 5 Oct 2026 (both a Compute Module 5 Lite, both
running the site's network-booted root at the time):

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

(That is pi16. pi20 printed `2025/11/05 17:37:18` and the same settings.)

**If your blade boots from the network and prints something like this, leave
its bootloader alone.** These bootloaders netboot as they are: `0xf2461` tries
the SD card (the eMMC on a module that has one; a Lite module has none), NVMe,
USB and then the network, and starts again. `rpi-eeprom-update` prints "UPDATE
AVAILABLE" on both; that only says a newer release exists in the installed
package. On a Compute Module a failed bootloader write is repaired only over
USB, which most blades cannot do (below).

What a change would buy, and neither is needed to get a blade working:

- **A boot order without local media** (`0xf2`), so that a USB stick, an SSD or
  (on a blade with a microSD slot, which the maker says only the Dev model has)
  a card someone fits cannot be booted. With `0xf2461` it can, and it is tried
  before the network. Not tried by us on a blade.
- **One bootloader release across the fleet.**

### What the Compute Blade has for it

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

```{image} bootloader-eeprom/blade-dev.svg
:alt: Outline of a Dev model Compute Blade with the USB Type-C port, the USB switch, the nRPIBOOT button and the DIP switches marked
:width: 100%
```

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

```{image} bootloader-eeprom/blade-dip.svg
:alt: The three DIP switches of a Dev model Compute Blade: 1 write protection (left disabled, right enabled), 2 Wi-Fi (left enabled, right disabled), 3 Bluetooth (left enabled, right disabled)
:width: 100%
```

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

## What is behind this page

The steps above come from these findings. You do not need them to do the job.

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
