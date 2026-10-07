# Acorns at ps1

**You look after the Acorns at ps1 (Pumping Station: One, Chicago) and want to
know which card is where, what state it is in, and what it still needs.** The
hosts as hosts (addresses, switch ports, power) are on the [PS1 site
page](../../../sites/ps1-boards.md#compute-blades); what was read on each blade, with
its date, is on [Acorns at ps1: what was read on each blade](ps1-reads.md).

## The cards

Four Compute Blades; an Acorn was seen on three of them (on pi18 at ps1 none was
seen: below). A card is named by its label once it
has one: an Acorn's label carries its device DNA and its flash ID, and the
flash ID is read through the fpgas.online design, so a card gets its label when
it is converted. Until then a row says where the card was last read.

**Which physical blade carries which name: we hold no record of where each one is.** Nothing we have says which
slot or position pi14 at ps1, pi16 at ps1, pi18 at ps1 or pi20 at ps1 is in. What ties a name to a blade is
its Ethernet MAC address and its Compute Module's serial number, read on each blade on 7 October 2026 (they
match the ps1 gateway's DHCP reservations):

| Name | Compute Module | Serial number | Ethernet MAC |
|------|----------------|---------------|--------------|
| pi14 at ps1 | CM4 Rev 1.1 4 GB | `10000000d00eb762` | `2c:cf:67:37:d4:bd` |
| pi16 at ps1 | CM5 Lite 8 GB | `9fb8cfc7cb291e63` | `2c:cf:67:fb:91:e5` |
| pi18 at ps1 | CM4 Rev 1.1 4 GB | `100000004e45f174` | `2c:cf:67:37:d5:08` |
| pi20 at ps1 | CM5 Lite 8 GB | `d85a19afde59093d` | `2c:cf:67:fd:1e:be` |

On a blade that is running, `ip link` prints its MAC (the `link/ether` line of `eth0`). How to read the MAC or
the serial number off a blade in the hand, without running it (a sticker on the module or on the blade), is
**not verified by us**.

**Telling the blades apart on the bench.** What the records say each one has, to look for (none of these has
been checked by eye by us):

- pi18 at ps1: no card seen in its M.2 slot (no PCIe device on 7 October 2026).
- pi14 at ps1 and pi18 at ps1 carry a Compute Module 4; pi16 at ps1 and pi20 at ps1 a Compute Module 5
  Lite. Which marking on the module tells the two apart is not recorded by us.
- Between the two Compute Module 5 blades: which header pins pi20 at ps1's old serial wires sit on is not
  recorded by us (below), and neither is how pi16 at ps1's cables are wired, so the wires do not tell the two
  apart: use the way below.

A way that does not depend on looking, **not yet tried by us**: with every other blade running, unplug one
blade's PoE cable and wait a minute; the name whose visitor port then stops answering is that blade. The
ports are 11422 for pi14 at ps1, 11622 for pi16 at ps1, 11822 for pi18 at ps1 and 12022 for pi20 at ps1
(`ssh -p 11622 pi@ps1.fpgas.online` and so on). Plug it back in and wait until its port answers again: pi20 at ps1 answered
about three and a half minutes after a reboot (7 October 2026, 14:22, before our test of 15:52). Anything installed on it is gone (below).

All four answered on their visitor ports on 7 October 2026 (pi14 at ps1 and pi18 at ps1 had not on
5 October); pi20 at ps1 restarted every 2 to 3 minutes from 15:52 to about 18:09 that day (one boot, from about 17:06,
stayed up at least 12 minutes: below). **If a blade's ssh port does not answer**, nothing can be run on it from this guide; first find out
whether it is powered and its network link is up (its lights; the gateway's view of it): **not yet checked by
us**. Its cables can still be made, bench-checked and fitted.

**An install on a blade lasts until its next boot.** The blades run their root file system from the gateway with
an overlay in memory (`overlayroot=tmpfs` on the kernel command line, read 7 October 2026), so packages
installed on a blade are gone after it reboots: an install of 5 October on pi16 at ps1 was gone on
7 October. Putting them into the shared root on the gateway is the gateway's owner's to do, and is not
written here.

**Converting a card** means loading the fpgas.online design into it over JTAG and writing that design to the
card's flash, once; after that the card runs it from every power-on. The steps are [written for a Raspberry Pi
5](../designs/install-images.md) and have **not yet been run by us on a Compute
Blade** to their end: begun once on pi20 at ps1 on 7 October 2026 and stopped before the flash write (the
Host column below).

```{rst-class} nowrap
```

| Card, by its label | On (last read) | Compute Module | What the card runs | PCIe | JTAG (P1) | P2 cable |
|---|---|---|---|---|---|---|
| Acorn CLE-101, no label yet (device DNA not read) | pi14 at ps1 (`1e24:0101` seen 2026-10-07) | CM4 Rev 1.1 4 GB | SQRL's factory image, `1e24:0101` | `0000:01` | 2026-09-20: no response, TCK floating | not known |
| Acorn CLE-101, no label yet (device DNA not read) | pi16 at ps1 (2026-10-05) | CM5 Lite Rev 1.0 8 GB | SQRL's factory image, `1e24:0101` | `0001:01` | 2026-09-20: no response, TCK floating. 2026-10-05: cannot run (the serial driver holds GPIO14) | not known |
| Acorn CLE-101, device DNA `0x0028e5c45e304854` | pi20 at ps1 (2026-10-07) | CM5 Lite Rev 1.0 8 GB | a vendor XDMA sample image, `10ee:7011` (read 2026-10-05; on 2026-10-07 our SoC was loaded into its SRAM for a test, the flash unchanged: below) | `0001:01` | 2026-09-20 (kernel 6.12.75): answered, IDCODE `0x3631093`. 2026-10-07 (kernel 6.18, serial port on): the check's `jtag` test failed: GPIO14 is held by the serial port. 2026-10-07, the header's serial port off at boot: `jtag` passed, IDCODE `0x13631093` (the same part; the 2026-09-20 reading left out the version digit), DNA as in the first column | on the Extension Port: K2 to GPIO15, J2 to GPIO14, no resistor; J5 and H5 not wired |
| none seen: no PCIe device (2026-10-07; the slot is empty, or a card has no link: `lspci` cannot tell) | pi18 at ps1 (2026-10-07) | CM4 Rev 1.1 4 GB | | | | |

How each card was read, and what "P1 unmated" rests on, is on [Acorns at ps1: what was read on each
blade](ps1-reads.md#the-cards-as-read).

**No blade is wired to the guide yet**; how each is wired today is on [what was read on each
blade](ps1-reads.md#the-cards-as-read).

## What each blade still needs

**The check on the two Compute Module 4 blades (pi14 at ps1 and pi18 at ps1) has not been run by us**: it
was run as written only on pi16 at ps1 and pi20 at ps1, both Compute Module 5 (7 October 2026). `vcgencmd`
hung for good on the two CM4 blades that day. Until the check has been tried on a CM4 blade, make, check
and fit pi14 at ps1's cables, and run the check on the two CM5 blades only.

**What to build.** P2: four new cables by the guide, one for each blade; pi20 at ps1's present serial wiring
is taken off (below). P1: one new cable for pi18 at ps1, certainly. On pi14 at ps1 and pi16 at ps1 TCK reads
as if no P1 cable were mated (a cable may be fitted and loose, or not fitted at all): reseat a fitted one
first; if none is fitted, or it still reads unmated, build a new one by the guide. Before refitting an
existing P1 cable: with the blade off and the card out, check it as [JTAG connector
2](../building/compute-blade/jtag-connector-2.md) step 2 does (each plug contact to its cavity, and no other),
then run the [bench check](../building/compute-blade/bench-check.md) with it before power-on. pi20 at ps1's P1 answered
on 2026-09-20: keep it, by the steps for its old serial wiring (below). So: four P2 cables, and one
to three P1 cables. Each bought Molex cable gives one P1 half and one P2 half, so that takes four Molex cables,
with one to three P1 halves spare. The terminals are 3 per P2 cable and 5 per P1 cable: 17 to 27 in all, and
a few spare. pi18 at ps1 also needs a card; which card goes there is not recorded by us.

**Before anything is fitted, refitted or reseated: power the blade off (unplug its PoE cable, and a USB-C cable if
one is plugged in).** And before any design is loaded over JTAG:

:::{warning}
Reconfiguring the FPGA over JTAG while its PCIe endpoint is enumerated is a
surprise removal. Detach the endpoint first, using the host's own bus from the
`PCIe` column of the table above:

```console
$ BDF=0001:01:00.0           # pi16 at ps1, pi20 at ps1; 0000:01:00.0 on the CM4 blade pi14 at ps1
$ echo 1 | sudo tee /sys/bus/pci/devices/$BDF/remove
```

No way of bringing the endpoint back after a load has worked on a blade yet. On pi20 at ps1 on 7 October
2026 a bus rescan did not bring it back, a root-complex re-probe failed, and after the reboot that followed,
the blade restarted every 2 to 3 minutes for over two hours (whether the load, the re-probe or the reboot
caused it is not known: below). Loading a
bitstream on a blade is not part of this guide until a way back is known.
`--detect` and the other read-only queries are safe without this; **loading a
bitstream is not**.
:::

To reach the wiring of the [Compute Blade building guide](../building/compute-blade/index.md), from what the table above
records. None of us has wired a blade this way or
converted a card on one yet (one conversion was begun on pi20 at ps1 and stopped before the flash write: below): **not yet run by us on this hardware**.

| Blade | Card | P1 (JTAG) cable | P2 (serial) cable | Host |
|-------|------|-----------------|-------------------|------|
| pi14 at ps1 | fitted, factory image: to be converted | not mated, or its TCK wire open (TCK follows the host's pull, as on the empty pi18 at ps1: 2026-09-20 and again 2026-10-07): reseat a fitted one; if none, or still unmated, build a new one | not known: build to the UART header, 470 Ω in the J2 wire, J5 and H5 cut back | as pi16 at ps1 (read 2026-10-07: the same serial-port settings); a Compute Module 4: (b) not yet run, and `gpioinfo` names no user for line 14 there (2026-10-07) |
| pi16 at ps1 | fitted, factory image: to be converted | not mated, or its TCK wire open (TCK follows the host's pull, as on the empty pi18 at ps1: 2026-10-07): reseat a fitted one; if none, or still unmated, build a new one | not known: build to the UART header, 470 Ω in the J2 wire, J5 and H5 cut back | (a) for the serial-pair tests: the kernel console and the getty off `/dev/ttyAMA0`; (b) only for JTAG: the serial port off at boot (below; run on pi20 at ps1, 7 October 2026) |
| pi18 at ps1 | none seen: look; if the slot is empty, fit one | fit on the Extension Port | fit on the UART header, 470 Ω in the J2 wire, J5 and H5 cut back | as pi16 at ps1 (read 2026-10-07: the same serial-port settings); a Compute Module 4: (b) not yet run, and `gpioinfo` names no user for line 14 there (2026-10-07) |
| pi20 at ps1 | fitted, vendor sample image in flash: to be converted | answered on 2026-09-20: keep the cable, by the steps below. On 2026-10-07 JTAG could not run with the header's serial port on (it holds GPIO14), and read the IDCODE and DNA with the port off at boot, the Host column's (b) | build a new one by the guide for the UART header (470 Ω in the J2 wire) and take the old serial wiring off (its pair is wired to GPIO14 and GPIO15; which header pins is not recorded: below) | as pi16 at ps1 (read 2026-10-05: the same kernel and serial-port settings): (a) for the serial-pair tests: the kernel console and the getty off `/dev/ttyAMA0`; (b) only for JTAG: the serial port off at boot (below; run on pi20 at ps1, 7 October 2026) |

**The Host column is Carl's to do, on the gateway, not on a blade.** The two files it means, `config.txt` and
`cmdline.txt`, are in one directory on the ps1 gateway, `/srv/nfs/rpi/trixie/boot/`, which every netbooted
host at ps1 boots from: on 7 October 2026 twelve hosts at ps1, not only the four blades (read on the ps1
gateway, 6 and 7 October 2026). For (b) there are two ways, and which to take is Carl's choice
([verifying 3](../building/compute-blade/verifying-3.md) has both, with their undo):

- **Change the shared directory.** At their next boot all twelve lose their console and login on the header's
  serial pins, and the firmware's boot messages there. They include pi21 at ps1, which carries a Tiny Tapeout
  board, and seven hosts we cannot name. Undo: put the two files back (keep a copy of both first).
- **Change one blade only.** Copy the directory, make the change in the copy, and point only that blade's link
  in `/srv/tftp/` at the copy. Undo: point the link back at `/srv/nfs/rpi/trixie/boot`. This is how pi20 at
  ps1 was tested on 7 October 2026. Its link points at the shared directory again: it was put back at 17:19:48 that
  day, and the shared directory has served every boot of pi20 at ps1 since 17:20 (the gateway's TFTP and NFS logs), and at 18:10 its serial port was on
  again (`serial0` was `ttyAMA0`). A change to the shared directory reaches pi20 at ps1 as it reaches the
  other hosts.

**The order of work.** The cables come first: making them, checking them on the bench and fitting them needs
nothing from the gateway. Then the Host column's (a), and the serial-pair checks run in a boot with the serial
port on. Then (b), only when JTAG is to run on a blade, which is what converting a card needs: with the serial
port off, `/dev/ttyAMA0` is not there, so the `p2-uart`, `p2-serial` and `scratch` tests cannot pass in that
boot ([verifying 3](../building/compute-blade/verifying-3.md)). Both are changes to the gateway's boot files,
so they are Carl's to decide and to time, (b) for every host or for one blade only (above). A load over
JTAG, which converting a card needs, is not part of this guide yet (the warning above).

What the Host column's (b) is, as run on pi20 at ps1 on 7 October 2026 ([verifying
3](../building/compute-blade/verifying-3.md) has the steps, both ways and their undo): in `config.txt`'s `[all]`
section `enable_uart=1` becomes `enable_uart=0` and the line `uart_2ndstage=1` is taken out; in `cmdline.txt`
the word `console=serial0,115200` is taken out. In that boot GPIO14 had no user, the login prompt went to the
Compute Module 5's own debug serial port (not on the header), so nothing more had to be taken off the header's
pins, and the check's `jtag` test read the FPGA's IDCODE and device DNA (after checking that GPIO14 followed
the Pi's pull both ways, verifying 3's step for a blade with no 470 Ω in its J2 wire, as pi20 at ps1 has).
**Not yet run on a Compute Module 4 blade.** Converting pi20 at ps1's card was begun on 7 October 2026: a load of our SoC
into the FPGA (its SRAM, not its flash) over JTAG worked, but the card's PCIe endpoint did not come back on a
bus rescan, a root-complex re-probe failed (the bind answered "No such device" and the root port was gone
too), and the run stopped there. An `openFPGALoader --reset` at 17:19 put the vendor's sample image back in
the FPGA, from the flash, which was never written.

**After test 6 (converting pi20 at ps1's card) was stopped at step 1b (the root-complex re-probe and the reboot
after it; 15:52, Adelaide time, 7 October 2026), pi20 at ps1 restarted every 2 to 3 minutes (one boot, from
about 17:06, stayed up at least 12 minutes) until about 18:09,
then stayed up; no power cycle was run by us; the cause is not known. It is back on Carl's shared boot files
(above) with the card on the vendor image. The Acorn's flash was never written. The files in Carl's
shared boot directory were never changed: for the test, pi20 at ps1's link pointed at a copy, and at 17:19:48 it was put
back and the copy was removed.**

The Host column's (a) has no written steps and has **not been tried by us**. What is known: on pi20 at ps1
(read 7 October 2026) the login prompt on `/dev/ttyAMA0` was there only because of the word
`console=serial0,115200` in `cmdline.txt`; with that word out and `enable_uart=1` kept, the header's serial
port would stay on for the serial-pair tests with nothing else using it. That is the expectation, not a run.

**pi20 at ps1's present P2 wiring is not the guide's.** Its serial pair is wired straight to GPIO14 (J2) and
GPIO15 (K2), with no resistor: read with the pin-ID design on 31 August 2026, when a design driving J2 stopped
JTAG until a PoE cycle, so J2 and P1's TMS share GPIO14 (fpgas.online-test-designs issue 4, the comment of
2026-08-31). GPIO14 is on Extension Port pin 9 and on UART header pin 3 (Uptime Lab's GPIO guide). Which of
these pins the old serial wires sit on, and whether J2 shares a terminal or a housing with P1's TMS wire, is
not recorded by us. Build a new P2 cable by the guide ([UART connector
1](../building/compute-blade/uart-connector-1.md) and 2) first. Then, with the blade powered off (unplug its PoE
cable, and a USB-C cable if one is plugged in), look at Extension Port pins 9 and 10 and UART header pins 3 and 4, and
note which housing sits where:

1. If the serial wires are in a housing of their own, take that housing off the blade and the old cable off
   the card, and leave P1's housing in place.
2. If a serial wire shares a housing, a terminal or a splice with P1's TMS wire, do not cut or pull it: take
   P1's cable off too, and build a new P1 cable by the guide ([JTAG connector
   1](../building/compute-blade/jtag-connector-1.md) and 2).
3. If P1's housing came off or moved, take the card out and the P1 plug out of its socket. Check with the meter,
   as [JTAG connector 2](../building/compute-blade/jtag-connector-2.md) step 2 does, that the plug's contact 4
   (TMS) beeps to the housing cavity over Extension Port pin 9 and to no other cavity. If it does not, or the
   housing is not the guide's 2×5, build a new P1 cable.
4. Fit the new P2 cable on the UART header. Whether P1's TMS works is shown only by the check's `jtag` test, in
   a boot with the header's serial port off ([verifying 3](../building/compute-blade/verifying-3.md)); the meter
   cannot reach it with the card fitted.

The parts are on [Compute Blade cables: parts and tools](../building/compute-blade/bom.md). Once
a blade is wired, [check it](../building/compute-blade/verifying-1.md).

pi20 at ps1's serial pair is direct on GPIO14 and GPIO15 without the resistor. From the
check's code, not from a run on a blade: `fpgas-verify`'s `p2-serial` test never
has both ends driving a wire at once (the Pi's pins are inputs while the FPGA
drives, and the FPGA's are inputs while the Pi drives), so it does not rely on
the resistor, and the fpgas.online design treats J2 as an input. What the
missing resistor does not survive is a design that drives J2, such as pin-ID.

## Labels

Each host and each card gets a label with what identifies it, made by
`fpgas-verify` from a read of the hardware itself. **Not on pi14 at ps1 or pi18 at ps1:** the label read asks
the firmware (`vcgencmd`), which hung for good on those two Compute Module 4 blades on 7 October 2026. On
pi16 at ps1 or pi20 at ps1, once the packages are installed there
([verifying 1](../building/compute-blade/verifying-1.md)):

```console
$ sudo fpgas-verify --label --out labels.pdf
```

- **The Compute Module labels of pi16 at ps1 and pi20 at ps1** exist, from reads
  of 5 October 2026. A label names no host: the one with eth MAC
  `2c:cf:67:fb:91:e5` is pi16 at ps1's, the one with `2c:cf:67:fd:1e:be` is pi20
  at ps1's. They are {download}`on plain US Letter paper, at true size with a
  line to cut along <labels/ps1-compute-modules-letter-plain.pdf>`, and
  {download}`laid out for Avery 5163 / 8163 stickers
  <labels/ps1-compute-modules-avery-5163.pdf>`. Print at 100 %, no scaling. The
  sticker layout is not yet tried on a real sheet: print it on plain paper
  first and hold it against the sticker sheet. "HAT none" on these labels means
  the firmware reported no HAT; the header's pins were deliberately not
  scanned, because on a Compute Blade they are JTAG wires.
- **The Acorn labels are not made yet.** Each waits for its card's conversion
  (above).
- **No labels yet for pi14 at ps1 and pi18 at ps1.** Their visitor ports did not answer on 5 October 2026,
  when the other two were read. Both answered on 7 October 2026, but the label read asks the firmware
  (`vcgencmd`), which hung for good on both that day: do not run it there; their labels wait until that is settled.
- **The two labels that exist were checked against the modules on 7 October 2026**: every printed field
  matches what pi16 at ps1 and pi20 at ps1 report.

The blades have no page under `https://ps1.fpgas.online/fpgas/`: pi14 at ps1, pi16 at ps1,
pi18 at ps1 and pi20 at ps1 all return 404 there (checked 2026-09-03 and again 2026-10-06).

Source: live probes (`lspci -nn`, `openFPGALoader --detect` and `--read-dna`,
pull-up/pull-down on each P2 and JTAG line, the pin-ID check on pi20 at ps1); MACs and
switch ports cross-checked against infra `host_vars/ps1.fpgas.online.yml`.
