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

**Converting a card** means loading the fpgas.online design into it over JTAG and writing that design to the
card's flash, once; after that the card runs it from every power-on. The steps are [written for a Raspberry Pi
5](../designs/install-images.md) and have **not yet been run by us on a Compute
Blade**: on a blade they wait for JTAG (the Host column below).

```{rst-class} nowrap
```

| Card, by its label | On (last read) | Compute Module | What the card runs | PCIe | JTAG (P1) | P2 cable |
|---|---|---|---|---|---|---|
| Acorn CLE-101, no label yet (device DNA not read) | pi14 at ps1 (2026-09-20) | CM4 Rev 1.1 4 GB | SQRL's factory image, `1e24:0101` | `0000:01` | 2026-09-20: no response, TCK floating | not known |
| Acorn CLE-101, no label yet (device DNA not read) | pi16 at ps1 (2026-10-05) | CM5 Lite Rev 1.0 8 GB | SQRL's factory image, `1e24:0101` | `0001:01` | 2026-09-20: no response, TCK floating. 2026-10-05: cannot run (the serial driver holds GPIO14) | not known |
| Acorn CLE-101, device DNA `0x0028e5c45e304854` | pi20 at ps1 (2026-10-05) | CM5 Lite Rev 1.0 8 GB | a vendor XDMA sample image, `10ee:7011` | `0001:01` | 2026-09-20 (kernel 6.12.75): answered, IDCODE `0x3631093`. 2026-10-05 (kernel 6.18.50, serial port on): not tried, expected not to run | on the Extension Port: K2 to GPIO15, J2 to GPIO14, no resistor; J5 and H5 not wired |
| none: the M.2 slot is empty | pi18 at ps1 (2026-09-20) | CM4 Rev 1.1 4 GB | | | | |

pi20 at ps1 is the only blade whose JTAG has answered (on 2026-09-20), so it is the
only one with a device DNA: `0x0028e5c45e304854`, an XC7A100T. The fpgas.online
Acorn design ran on it from SRAM that day (Gen2 x1, the same ident and DNA over
PCIe and over the UART bridge); by that probe its flash holds the vendor XDMA
sample image, and on 2026-10-05 the card enumerated as `10ee:7011`, the ID of
that sample design. "P1 unmated" on pi14 at ps1 and pi16 at ps1 is
read off TCK: the Acorn pulls TCK up, and on pi20 at ps1 the Pi's pull-down cannot move
it, while on pi14 at ps1 and pi16 at ps1 it floats exactly as on pi18 at ps1, which has no card.
Reseating P1 is the first thing to try. (On pi16 at ps1 JTAG will still not run while the serial port holds
GPIO14: the table below.)

These boards are often called LiteFury. Their factory PCI ID identifies them as
SQRL Acorn CLE-101: the same PCB family, XC7A100T with 512 MB of DDR3. See [SQRL
Acorn](../index.md).

**No blade is wired to the [Compute Blade
wiring](../building/compute-blade/index.md) yet.** That wiring puts P1 on
the Extension Port and P2 on the 4-pin UART header, with a 470 Ω resistor in the
J2 wire. pi20 at ps1, the one blade whose wiring has been read, has its P2 serial pair
on Extension Port pins 9 and 10 instead, sharing pin 9 (GPIO14) directly with
TMS and with no resistor, so a design that drives J2 costs JTAG until a PoE
cycle ([why](../wiring/compute-blade-host.md#the-shared-line-and-the-470-ω-resistor)),
and its J5 and H5 are not wired. How pi14 at ps1's and pi16 at ps1's P2 cables are wired is
not known: pi14 at ps1's P1 did not answer on 2026-09-20 and pi16 at ps1's JTAG cannot run
today ([pi16 at ps1 on 5 October 2026](ps1-reads.md#pi16-at-ps1-on-5-october-2026)), so nothing can be
loaded to read them.

## What each blade still needs

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
| pi14 at ps1 | fitted, factory image: to be converted | did not answer: reseat or refit on the Extension Port | not known: build to the UART header, 470 Ω in the J2 wire, J5 and H5 cut back | read its kernel command line and serial getty again (last read 2026-09-20) |
| pi16 at ps1 | fitted, factory image: to be converted | not known (see above): check, reseat or refit on the Extension Port | not known: build to the UART header, 470 Ω in the J2 wire, J5 and H5 cut back | take the kernel console and the getty off `/dev/ttyAMA0` (needed in any case); for JTAG, the serial port off at boot, as above |
| pi18 at ps1 | none: fit one | fit on the Extension Port | fit on the UART header, 470 Ω in the J2 wire, J5 and H5 cut back | read its kernel command line and serial getty again (last read 2026-09-20) |
| pi20 at ps1 | fitted, vendor sample image in flash: to be converted | answered on 2026-09-20: leave the cable. JTAG is expected not to run as the blade boots now (not tried) | move the serial pair from Extension Port pins 9 and 10 to the UART header, and add the 470 Ω resistor in the J2 wire | as pi16 at ps1 (read 2026-10-05: the same kernel and serial-port settings): take the kernel console and the getty off `/dev/ttyAMA0`; for JTAG, the serial port off at boot |

**The Host column is Carl's to do, on the gateway, not on a blade.** The two files it means, `config.txt` and
`cmdline.txt`, are in one directory on the ps1 gateway, `/srv/nfs/rpi/trixie/boot/`, which every netbooted
host at ps1 boots from (read on the ps1 gateway, 6 October 2026): a change there reaches all of them at their
next boot. In order: the host's console and serial port first, then the cables, then the endpoint detached,
then a load over JTAG.

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
`fpgas-verify` from a read of the hardware itself. Run on the blade, once the packages are installed there
([verifying 1](../building/compute-blade/verifying-1.md)):

```console
$ sudo fpgas-verify --label --out labels.pdf
```

- **The Compute Module labels of pi16 at ps1 and pi20 at ps1** exist, from reads
  of 5 October 2026: {download}`on plain US Letter paper, at true size with a
  line to cut along <labels/ps1-compute-modules-letter-plain.pdf>`, and
  {download}`laid out for Avery 5163 / 8163 stickers
  <labels/ps1-compute-modules-avery-5163.pdf>`. Print at 100 %, no scaling. The
  sticker layout is not yet tried on a real sheet: print it on plain paper
  first and hold it against the sticker sheet. "HAT none" on these labels means
  the firmware reported no HAT; the header's pins were deliberately not
  scanned, because on a Compute Blade they are JTAG wires.
- **The Acorn labels are not made yet.** Each waits for its card's conversion
  (above).
- **No labels for pi14 at ps1 and pi18 at ps1.** Their visitor ssh ports did not
  answer on 5 October 2026, so nothing was read from them that day.

The blades have no page under `https://ps1.fpgas.online/fpgas/`: pi14 at ps1, pi16 at ps1,
pi18 at ps1 and pi20 at ps1 all return 404 there (checked 2026-09-03 and again 2026-10-06).

Source: live probes (`lspci -nn`, `openFPGALoader --detect` and `--read-dna`,
pull-up/pull-down on each P2 and JTAG line, the pin-ID check on pi20 at ps1); MACs and
switch ports cross-checked against infra `host_vars/ps1.fpgas.online.yml`.
