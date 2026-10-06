# Acorns at ps1: what was read on each blade

**You want the record behind [Acorns at ps1](ps1.md): what was read on each
Compute Blade there, by whom it could be read, and when.** This page is a
record: where it says what has to change on a host, the doing is on [Acorns at
ps1](ps1.md). The reads of 2026-09-20, when all four blades were probed
together, are the dated entries in that page's first table; no fuller record
of that day is kept here.

On all four blades the JTAG pins are `--pins 2:3:4:14` (it has only answered on
pi20 at ps1) and the FPGA UART is `/dev/ttyAMA0` at GPIO14/15. All four ran Debian's
openFPGALoader 0.13.1, which has `--read-dna`, when probed. PCIe is through the blade's M.2 slot. On 2026-09-20
all four netbooted the trixie NFS root (arm64 then) with overlayroot, with `console=tty1` and
`serial-getty@ttyAMA0` inactive, so the [kernel console
crash](../wiring/compute-blade-host.md#kernel-console-on-the-fpga-uart) could not
happen. That no longer holds on pi16 at ps1 or pi20 at ps1 (their boot configuration, read on
2026-10-05, is below), and pi14 at ps1 and pi18 at ps1 have not been read since.

## pi16 at ps1 on 5 October 2026

Read over SSH as the visitor. Nothing was written to the host's storage or to
the Acorn; a report file in `/run` was made and removed, and GPIO2 and GPIO4,
left as outputs by a hand-run `openFPGALoader --detect`, were put back.

| | Read on pi16 at ps1, 2026-10-05 |
|---|---|
| Module | Compute Module 5 Lite Rev 1.0, 8 GB, MAC `2c:cf:67:fb:91:e5` |
| System | Raspbian 13 (trixie), 32-bit userspace on kernel `6.18.50+rpt-rpi-v8`; Debian's openFPGALoader 0.13.1 |
| Serial port | `enable_uart=1`, `console=serial0,115200`, and a serial getty active on `/dev/ttyAMA0` |
| Card | `1e24:0101` at `0001:01:00.0`: SQRL's factory image, not converted |
| `fpgas-verify` 0.0.post1100 | `pcie-link` (5.0 GT/s, x1) and `rp1-pio` pass; `jtag` cannot run; the tests that need the fpgas.online design are not run on a factory image, and `p2-gpio` is not run because J5 and H5 are not wired on a blade |

Two things follow from the serial port being on:

- **JTAG cannot run.** TMS is GPIO14, which is also the serial port's TX pin.
  The kernel's serial driver holds it (`pin gpio14 already requested by
  1f00030000.serial; cannot claim`), this kernel does not lend a held pin, and
  the serial driver has no `unbind` file and is the kernel console, so it
  cannot be detached from the running system. openFPGALoader 0.13.1
  then stops on a libgpiod assertion instead of saying so. Tracked in
  [test-designs issue
  #127](https://github.com/fpgas-online/fpgas.online-test-designs/issues/127).
  So whether pi16 at ps1's P1 cable is mated cannot be told from a scan today; the
  "P1 unmated" in the table is the pull-up reading of 2026-09-20.
- **The kernel console is on the FPGA's UART**, which the [wiring
  page](../wiring/compute-blade-host.md#kernel-console-on-the-fpga-uart) warns
  against: a design that drives serial TX can reboot or crash the host. It must
  be moved (`console=tty1`, no serial getty) before such a design is loaded.

Moving the console does not free JTAG. With `enable_uart=1` the serial driver
holds GPIO14 whether or not a console or a getty uses the port. For JTAG the
header's serial port itself has to be off at boot (`enable_uart=0`, and no
`console=serial0` word), and in that boot the tests of the P2 serial pair
cannot run. **Not yet run by us on this hardware.** The same applies to any
blade on this kernel with the serial port on, pi20 at ps1 included (next section).

## pi20 at ps1 on 5 October 2026

Read over SSH as the visitor, without sudo; nothing was installed, copied or
changed.

| | Read on pi20 at ps1, 2026-10-05 |
|---|---|
| Module | Compute Module 5 Lite Rev 1.0, 8 GB, MAC `2c:cf:67:fd:1e:be` |
| System | Raspbian 13 (trixie), 32-bit userspace on kernel `6.18.50+rpt-rpi-v8`; Debian's openFPGALoader 0.13.1 |
| Serial port | `enable_uart=1`, `console=ttyAMA0,115200` on the kernel command line, and `serial-getty@ttyAMA0` active: the same boot settings as pi16 at ps1 |
| Card | `10ee:7011` at `0001:01:00.0`: the ID of Xilinx's XDMA sample design (`fpgas-verify` would report it as unconverted); not SQRL's factory image and not the fpgas.online design. Which image it is beyond that ID was not read |
| `fpgas-verify` | not installed, so it has not run here |

pi20 at ps1's JTAG answered on 2026-09-20 under kernel 6.12.75. On 2026-10-05 it ran
the same kernel as pi16 at ps1 with the same serial-port settings, so its JTAG is
**expected not to run** for the same reason (the serial driver holds GPIO14).
**Not tried:** no JTAG command was run on pi20 at ps1 that day.

## Where a blade's boot configuration is

Read on pi16 at ps1 and pi20 at ps1 themselves on 2026-10-05, not on the gateway: on both,
the kernel command line has `nfsroot=10.21.0.1:/srv/nfs/rpi/trixie/root` and
`console=ttyAMA0,115200`, and `/boot/firmware/config.txt` has `enable_uart=1`
under `[all]` and no overlay for the UART. On pi16 at ps1 `/boot/firmware/cmdline.txt`
holds the same line with `console=serial0,115200`; that file was not read on
pi20 at ps1.

The settings to change for JTAG (`enable_uart` in `config.txt`, and the
`console=serial0` word in `cmdline.txt`) are in those two files, and their
master copy is on the site's gateway: `/srv/nfs/rpi/trixie/boot/`. The
gateway's TFTP root has one entry for each host's serial number, and every one
of them points at that one directory (read on the ps1 gateway, 6 October 2026).
So one copy serves every netbooted host at ps1, a change applies to all of
them, and it takes effect at a host's next boot. The bootloader's boot order on
both blades ends with the network (`BOOT_ORDER=0xf2461`) and the label read saw
no storage device on either module.
