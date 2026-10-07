# Acorns at ps1

**You look after the Acorns at ps1 (Pumping Station: One, Chicago) and want to
know which card is where, what state it is in, and what it still needs.** The
hosts as hosts (addresses, switch ports, power) are on the [PS1 site
page](../../../sites/ps1.md#compute-blades); what was read on each blade, with
its date, is on [Acorns at ps1: what was read on each blade](ps1-reads.md).

## The cards

Four Compute Blades; three carry an Acorn. A card is named by its label once it
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
- Between the two Compute Module 5 blades: pi20 at ps1's serial pair was recorded (5 October 2026) on
  Extension Port pins 9 and 10, so it is the one with a wire on pin 10 (GPIO15); the guide's P1 cable uses
  no pin 10. How the Extension Port's pins are numbered is on [the blade's
  pins](../wiring/compute-blade-host.md). If no wire is on pin 10 of either, the two cannot be told apart
  by eye: use the way below.

A way that does not depend on looking, **not yet tried by us**: with every other blade running, unplug one
blade's PoE cable and wait a minute; the name whose visitor port then stops answering is that blade. The
ports are 11422 for pi14 at ps1, 11622 for pi16 at ps1, 11822 for pi18 at ps1 and 12022 for pi20 at ps1
(`ssh -p 11622 pi@ps1.fpgas.online` and so on). Plug it back in; how long it takes to boot at ps1 is not
recorded by us: wait until its port answers again. Anything installed on it is gone (below).

All four answered on their visitor ports on 7 October 2026 (pi14 at ps1 and pi18 at ps1 had not on
5 October). **If a blade's ssh port does not answer**, nothing can be run on it from this guide; first find out
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
Blade**: on a blade they wait for JTAG (the Host column below).

```{rst-class} nowrap
```

| Card, by its label | On (last read) | Compute Module | What the card runs | PCIe | JTAG (P1) | P2 cable |
|---|---|---|---|---|---|---|
| Acorn CLE-101, no label yet (device DNA not read) | pi14 at ps1 (`1e24:0101` seen 2026-10-07) | CM4 Rev 1.1 4 GB | SQRL's factory image, `1e24:0101` | `0000:01` | 2026-09-20: no response, TCK floating | not known |
| Acorn CLE-101, no label yet (device DNA not read) | pi16 at ps1 (2026-10-05) | CM5 Lite Rev 1.0 8 GB | SQRL's factory image, `1e24:0101` | `0001:01` | 2026-09-20: no response, TCK floating. 2026-10-05: cannot run (the serial driver holds GPIO14) | not known |
| Acorn CLE-101, device DNA `0x0028e5c45e304854` | pi20 at ps1 (2026-10-05) | CM5 Lite Rev 1.0 8 GB | a vendor XDMA sample image, `10ee:7011` | `0001:01` | 2026-09-20 (kernel 6.12.75): answered, IDCODE `0x3631093`. 2026-10-05 (kernel 6.18.50, serial port on): not tried, expected not to run | on the Extension Port: K2 to GPIO15, J2 to GPIO14, no resistor; J5 and H5 not wired |
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
first; if none is fitted, or it still reads unmated, build a new one by the guide. pi20 at ps1's P1 answered
on 2026-09-20: leave it, unless taking its old serial wiring off disturbs it. So: four P2 cables, and one
to three P1 cables. pi18 at ps1 also needs a card; which card goes there is not recorded by us.

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

Restore it by rebooting, or as described under [Bring the endpoint back after a
JTAG load](../designs/pcie.md#bring-the-endpoint-back-after-a-jtag-load)
(on a blade a LiteX design needs a root-complex re-probe, not just a rescan).
`--detect` and the other read-only queries are safe without this; **loading a
bitstream is not**.
:::

To reach the wiring of the [Compute Blade building guide](../building/compute-blade/index.md), from what the table above
records. None of us has wired a blade this way or
converted a card on one yet: **not yet run by us on this hardware**.

| Blade | Card | P1 (JTAG) cable | P2 (serial) cable | Host |
|-------|------|-----------------|-------------------|------|
| pi14 at ps1 | fitted, factory image: to be converted | not mated, or its TCK wire open (TCK follows the host's pull, as on the empty pi18 at ps1: 2026-09-20 and again 2026-10-07): reseat a fitted one; if none, or still unmated, build a new one | not known: build to the UART header, 470 Ω in the J2 wire, J5 and H5 cut back | as pi16 at ps1 (read 2026-10-07: the same serial-port settings) |
| pi16 at ps1 | fitted, factory image: to be converted | not mated, or its TCK wire open (TCK follows the host's pull, as on the empty pi18 at ps1: 2026-10-07): reseat a fitted one; if none, or still unmated, build a new one | not known: build to the UART header, 470 Ω in the J2 wire, J5 and H5 cut back | (a) for the serial-pair tests: the kernel console and the getty off `/dev/ttyAMA0`; (b) only for JTAG: the serial port off at boot (below) |
| pi18 at ps1 | none seen: look; if the slot is empty, fit one | fit on the Extension Port | fit on the UART header, 470 Ω in the J2 wire, J5 and H5 cut back | as pi16 at ps1 (read 2026-10-07: the same serial-port settings) |
| pi20 at ps1 | fitted, vendor sample image in flash: to be converted | answered on 2026-09-20: leave the cable. JTAG is expected not to run as the blade boots now (not tried) | build a new one by the guide for the UART header (470 Ω in the J2 wire) and take the old serial wiring off Extension Port pins 9 and 10 (below) | as pi16 at ps1 (read 2026-10-05: the same kernel and serial-port settings): (a) for the serial-pair tests: the kernel console and the getty off `/dev/ttyAMA0`; (b) only for JTAG: the serial port off at boot (below) |

**The Host column is Carl's to do, on the gateway, not on a blade.** The two files it means, `config.txt` and
`cmdline.txt`, are in one directory on the ps1 gateway, `/srv/nfs/rpi/trixie/boot/`, which every netbooted
host at ps1 boots from (read on the ps1 gateway, 6 October 2026): a change there reaches all of them at their
next boot.

**The order of work.** The cables come first: making them, checking them on the bench and fitting them needs
nothing from the gateway. Then the Host column's (a), and the serial-pair checks run in a boot with the serial
port on. Then (b), only when JTAG is to run on a blade, which is what converting a card needs: with the serial
port off, `/dev/ttyAMA0` is not there, so the `p2-uart`, `p2-serial` and `scratch` tests cannot pass in that
boot ([verifying 3](../building/compute-blade/verifying-3.md)). Both are changes for every netbooted host at
ps1, so they are Carl's to decide and to time. Then, for a load over JTAG: the endpoint detached first (the
warning above), then the load.

What the Host column's change is, as far as it is written: the two lines are in the paragraph that begins "JTAG and the serial pair share
GPIO14" on [verifying 3](../building/compute-blade/verifying-3.md): `enable_uart=0` in `config.txt` (or, if
the port is switched on by a `uart0` overlay or parameter line, that line taken out instead), and
`console=serial0,115200` out of `cmdline.txt` if it is there. Raspberry Pi's documentation does not say that
this frees GPIO14 on a Compute Module 5. **Not yet tried by us on a blade.** Taking the
login prompt (the serial getty) off that port as well has **no written steps yet**; whether it is still
needed once `enable_uart=0` is set has not been tried either.

**pi20 at ps1's present P2 wiring is not the guide's.** How its cable is made was not recorded, only where
its serial pair lands (Extension Port pins 9 and 10). The way to the guide's wiring that needs no knowledge of
the old cable: build a new P2 cable by the guide ([UART connector
1](../building/compute-blade/uart-connector-1.md) and 2), take the old P2 cable off the card and the blade, and
fit the new one on the UART header. Whether the P1 cable's housing then matches the guide's has to be looked
at against [JTAG connector 2](../building/compute-blade/jtag-connector-2.md): **not yet done by us.**

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
  (`vcgencmd`), which hung on both that day; their labels wait for a reboot of the two blades.
- **The two labels that exist were checked against the modules on 7 October 2026**: every printed field
  matches what pi16 at ps1 and pi20 at ps1 report.

The blades have no page under `https://ps1.fpgas.online/fpgas/`: pi14 at ps1, pi16 at ps1,
pi18 at ps1 and pi20 at ps1 all return 404 there (checked 2026-09-03 and again 2026-10-06).

Source: live probes (`lspci -nn`, `openFPGALoader --detect` and `--read-dna`,
pull-up/pull-down on each P2 and JTAG line, the pin-ID check on pi20 at ps1); MACs and
switch ports cross-checked against infra `host_vars/ps1.fpgas.online.yml`.
