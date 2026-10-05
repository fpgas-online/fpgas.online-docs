# Bootloader EEPROM: upgrade and lock

Every Raspberry Pi since the Pi 4 keeps its second-stage bootloader and the
bootloader's configuration (`BOOT_ORDER` and so on) in a small SPI flash on the
board, usually called the bootloader EEPROM. It is the one piece of state on a
fleet Pi that is not in the shared NFS root and does not go away at a reboot, so
the fleet keeps it **locked** ([why](netboot.md#eeprom-write-protect)). This page
is how to read its state, how to upgrade it although it is locked, and how it is
locked again afterwards.

What is on this page has two kinds of source, and each section says which:

- **Raspberry Pi 5**: what we ran and measured on fleet Pi 5s (Rev 1.1, boot
  flash Winbond W25Q16, JEDEC id `ef4015`) on 3 and 4 Oct 2026.
- **Compute Module 4 and Compute Module 5**: Raspberry Pi's own documentation,
  quoted. **Not yet run by us on this hardware.**

## What the fleet wants

| | Target |
|---|---|
| Bootloader release | `2026/09/25` (default release channel) |
| `BOOT_ORDER` | `0xf2`: network, then start again. No SD card, no USB |
| `BOOT_UART` | `1`: the bootloader logs to the debug UART |
| `NET_INSTALL_AT_POWER_ON` | `0` |
| `POWER_OFF_ON_HALT`, `WAKE_ON_GPIO` | `0`, `1` |
| Flash protection | whole array protected: status register 1 reads `0xbc` |

A Pi with another boot order (a stock Pi 5 has `0xf12` or `0xf21`: SD card
first) still netboots when no card is fitted, but it will boot whatever card
somebody puts in.

## Read the state (any Pi, no change made)

```console
$ vcgencmd bootloader_version
$ vcgencmd bootloader_config
$ sudo rpi-eeprom-update
```

`rpi-eeprom-update` without options only reports. The flash's own protection
state is in its status registers, which no packaged tool prints. On a Pi 5 the
boot flash is `/dev/spidev10.0`, and four read commands give the part and the
three registers (`9Fh` JEDEC id, `05h` SR1, `35h` SR2, `15h` SR3). Read commands
change nothing:

```python
import array, ctypes, fcntl, os, struct

def xfer(fd, tx):
    txb = ctypes.create_string_buffer(bytes(tx), len(tx))
    rxb = ctypes.create_string_buffer(len(tx))
    msg = struct.pack("QQIIHBBBBBB", ctypes.addressof(txb), ctypes.addressof(rxb),
                      len(tx), 1000000, 0, 8, 0, 0, 0, 0, 0)
    fcntl.ioctl(fd, 0x40206B00, array.array("B", msg), True)  # SPI_IOC_MESSAGE(1)
    return rxb.raw

fd = os.open("/dev/spidev10.0", os.O_RDWR)
print("jedec", xfer(fd, [0x9F, 0, 0, 0])[1:].hex())
for name, cmd in (("SR1", 0x05), ("SR2", 0x35), ("SR3", 0x15)):
    print(name, hex(xfer(fd, [cmd, 0])[1]))
```

On a locked fleet Pi 5 this reads `ef4015`, SR1 `0xbc`, SR2 `0x02`, SR3 `0x60`.
SR1 `0xbc` is `SRP=1`, `TB=1`, `BP2..0=111` (the whole array protected); SR2
`0x02` is `QE=1`, `SRL=0`. An unprotected flash reads SR1 `0x00`.

## Raspberry Pi 5

### What was measured

All of it on Pi 5 Rev 1.1 boards with the W25Q16 flash, netbooting the fleet
root, on 3 and 4 Oct 2026.

| | Observation |
|---|---|
| 1 | `eeprom_write_protect=1` in the `config.txt` served over netboot **is applied**: SR1 went from `0x00` to `0xbc` in one boot. This is how every fleet Pi gets locked, including Pis nobody has handled. |
| 2 | `eeprom_write_protect=0` served over netboot **was not applied**: SR1 stayed `0xbc` over four boots. |
| 3 | With the flash protected, the netboot self-update fetched `pieeprom.sig` and `pieeprom.upd`, wrote nothing, tried once more and then booted the operating system. **Nothing anywhere reported the failed update.** |
| 4 | An SD card holding `recovery.bin`, `pieeprom.bin`, `pieeprom.sig` and a `config.txt` with `eeprom_write_protect=0`, with the `TP14` and `TP1` pads bridged, cleared the protection and wrote the new bootloader. The activity LED blinked 3 long, 3 short although the write had succeeded. |
| 5 | With the flash unprotected and already holding the offered image, the netboot self-update found nothing to do and booted on. |
| 6 | The flash's `/WP` pin goes to no SoC GPIO: software cannot read whether the pads are bridged. |
| 7 | A bootloader of `2026/05/26` already provides `/dev/pio0` (RP1 PIO). The upgrade to `2026/09/25` is for a uniform fleet. |

Observations 1 and 2 do not fit a plain reading of Raspberry Pi's description
below, where the setting is "for `recovery.bin`". We have not found out why the
unlock over netboot fails (the bootloader's UART log during such a boot has not
been captured).

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
- Whether a Pi 5 that does not boot any more is repaired by the same card.
  Raspberry Pi documents that it is (below); we have not had such a board.

### Upgrade a locked Pi 5 (the one route that has worked for us)

Needed: a hand at the board, a microSD card, something to bridge two pads.

1. **Prepare the card** (FAT partition), with these four files in its root:
   - `recovery.bin` and the release's `pieeprom.bin`, from the
     [rpi-eeprom](https://github.com/raspberrypi/rpi-eeprom) package or
     repository (directory `firmware-2712` for a Pi 5);
   - the configuration put into the image with
     `rpi-eeprom-config --config boot.conf --out pieeprom.bin pieeprom-<release>.bin`,
     where `boot.conf` holds the settings from [What the fleet
     wants](#what-the-fleet-wants);
   - `pieeprom.sig`, made with `rpi-eeprom-digest -i pieeprom.bin -o pieeprom.sig`;
   - `config.txt` with the one line `eeprom_write_protect=0`.

   Check before use: `rpi-eeprom-config pieeprom.bin` prints the configuration
   inside the image. A card with a wrong boot order produces a Pi that does not
   netboot.
2. **Unplug the Pi** (on a PoE port: the network cable).
3. **Bridge `TP14` and `TP1`**: the two pads marked `FLASH WP` on the underside
   of the Pi 5, to the right of the CE mark, above the two micro-HDMI sockets.
   `TP14` is the flash's `/WP`, `TP1` is 3.3 V.
4. **Fit the card and power the Pi.** The ROM runs `recovery.bin` from the card
   before the bootloader in the flash, whatever the boot order. Give it a
   minute. With a file named `pieeprom.bin` the Pi stops after writing and does
   not boot on. Do not take the LED as the verdict (observation 4).
5. **Unplug, take the card out, take the bridge off, plug the Pi in on its
   fleet port.** It netboots; the served `config.txt` has
   `eeprom_write_protect=1` and the flash is locked again in that boot
   (observation 1).
6. **Read the state** as above. The upgrade is done when the version is the
   target, the configuration is the fleet's, and SR1 reads `0xbc`. Because a
   failed update is silent (observation 3), this read is the only proof.

What can go wrong:

| What | How it shows | Recovery |
|---|---|---|
| Bridge without contact, or card not read | Version unchanged at step 6 | Repeat from step 2 |
| Power lost while writing, or a bad image | The Pi does not boot | The same card again: the ROM runs `recovery.bin` from an SD card whatever the flash holds (Raspberry Pi's documentation; not yet needed by us) |
| Wrong configuration in the image | The Pi does not netboot | Correct the card, repeat |

### What does not work

- `rpi-eeprom-update -a` or `rpi-eeprom-config --apply` on a running fleet Pi:
  the flash is protected, and the update they stage is then ignored silently
  (observation 3).
- Serving `eeprom_write_protect=0` to the Pi over netboot (observation 2).
- `flashrom`: Raspberry Pi's documentation says it "does not support clearing
  of the write-protect regions and will fail to update the EEPROM if
  write-protect regions are defined".

### The service port

At Welland one switch port is kept as an EEPROM service port. The gateway serves
a Pi on that port its own boot tree, holding the target `pieeprom.upd` and
`pieeprom.sig` and a `config.txt` with `eeprom_write_protect=0`, and no other
port sees those files. With today's findings it upgrades only a Pi whose flash
is **not** protected (a new Pi, or one cleared with the card), and it is where an
upgrade can be watched. Making it a managed feature that upgrades a locked Pi
without a visit is open work.

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
> `eeprom_write_protect` settings in `config.txt` for `recovery.bin`.
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

## Compute Module 4 and Compute Module 5

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

### Flash the bootloader over USB (`rpiboot`)

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

### Set the configuration and the lock

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
stay as set. Whether a given carrier pulls `EEPROM_nWP` low, leaves it open or
brings it to a jumper is a property of that carrier. For the upgrade it must
**not** be low; for the lock it must be.

### Differences from the Pi 5 to keep in mind

- No card route and no `recovery.bin` from storage: USB `rpiboot` is the
  repair route, so a Compute Module whose bootloader is broken needs its
  carrier's USB device port and `nRPI_BOOT`.
- Self-update over netboot exists but "does not update the bootloader
  atomically": a power cut during the write can leave a module that only
  `rpiboot` repairs.
- Our Pi 5 finding that a protected flash ignores a netboot self-update
  silently (observation 3) may hold here too: read the version after any
  upgrade.

## Sources

- Measurements: fpgas.online Welland fleet, 3 and 4 Oct 2026, Pi 5 Rev 1.1.
- [Raspberry Pi documentation](https://github.com/raspberrypi/documentation),
  commit `287523e6`: `computers/config_txt/boot.adoc`,
  `computers/raspberry-pi/boot-eeprom.adoc`,
  `computers/raspberry-pi/eeprom-bootloader.adoc`,
  `computers/compute-module/cm-bootloader.adoc`,
  `computers/compute-module/cm-emmc-flashing.adoc`.
- Winbond W25Q16JV datasheet (status register bits, `/WP` and `QE`).
