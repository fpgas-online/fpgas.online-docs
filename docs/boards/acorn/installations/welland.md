# Acorns at welland

**You look after the Acorns at welland (the private test lab in South Australia) and want to know which
card is where, what state it is in, and what it still needs.** The site itself (the gateway, the switches,
the other boards) is on the [Welland site page](../../../sites/welland.md).

**The live state of each card is its board page on <https://welland.fpgas.online/fpgas/>.** The check
(`fpgas-verify`) is the authority on what is connected and whether it passes. The table below is a dated
snapshot.

## The cards

Each card is on a Raspberry Pi 5 with an M.2 HAT: the [Raspberry Pi 5 wiring](../wiring/rpi-5.md), with JTAG
on its own GPIOs (`--pins 10:9:11:8`) and both spare balls wired. A card is named by its label: its name
and its device DNA. A hostname at welland follows the switch port and the cards have been moved between
ports, so the Pi a card is on is named by its own label (model, memory, serial number) and its MAC, not by
a hostname.

```{rst-class} nowrap
```

| Card, by its label | On (last read) | Variant | What the card runs | Read on 4 October 2026 | Read on 6 October 2026 | What it still needs |
|---|---|---|---|---|---|---|
| `acorn-holly 0x00200c8664b04854` | `Pi 5 2 GB 285df3f84af242d0`, MAC `88:a2:9e:45:c6:87` (2026-10-04) | CLE-215+ | the fpgas.online golden and operational images, `10ee:7021`, subsystem `1e24:021f` | the boot check passes | the boot check passes, ten tests of ten, at 08:25; seen at sw2 p47 on 6 October 2026 | nothing recorded |
| `acorn-willow 0x0054b48664b04854` | `Pi 5 2 GB 0cd35697db04a4ab`, MAC `88:a2:9e:45:85:77` (2026-10-04) | CLE-215+ | the fpgas.online golden and operational images, `10ee:7021`, subsystem `1e24:021f`; cold boot proven 2026-09-21 ([how](../designs/install-images.md#installing-the-fpgasonline-images)) | the boot check passes | the boot check passes, ten tests of ten, at 08:25; seen at sw2 p46 on 6 October 2026 | nothing recorded |
| `acorn-sycamore 0x0058cc8664b04854` | `Pi 5 2 GB a01e40441f959c20`, MAC `88:a2:9e:45:dd:be` (2026-10-04) | CLE-215+ | the fpgas.online golden and operational images, converted from SQRL's factory image on 2026-10-04 | the boot check fails on `p2-gpio`: the J5 wire does not reach GPIO3 | rewired, its Pi's bootloader locked; the boot check passes, ten tests of ten, at 10:57; seen at sw2 p43 on 6 October 2026 | its label (none on 4 October 2026) |
| `acorn-olive 0x0054e48664b04854` | `Pi 5 1 GB c36b093f773d46b8`, MAC `98:fe:54:13:f5:75` (2026-10-04) | CLE-215+ | the fpgas.online golden and operational images, converted from SQRL's factory image on 2026-10-04 | the boot check fails on `p2-uart`, `p2-serial`, `scratch` and `p2-gpio`: both pairs of P2 are crossed | rewired, its Pi's bootloader locked; the boot check passes, ten tests of ten, at 10:12; seen at sw2 p44 on 6 October 2026 | its label (none on 4 October 2026) |
| Acorn CLE-215+, no label yet (device DNA not read) | the Pi with MAC `98:fe:54:13:e0:75` (2026-09-03) | CLE-215+ | SQRL factory firmware, `1e24:021f` (2026-09-03) | not seen; last read 2026-09-03: `--detect` finds an empty JTAG chain although PCIe enumerates | not seen | to be found; a physical check of its P1 cable |
| Acorn CLE-215+, no label yet (device DNA not read) | the Pi with MAC `98:fe:54:13:e0:f5` (2026-09-03) | CLE-215+ | `10ee:7011`, most likely the vendor XDMA sample image (2026-09-03) | not seen; last read 2026-09-03: `--detect` finds an empty JTAG chain although PCIe enumerates | not seen | to be found; a physical check of its P1 cable |

The four labelled rows were read by the fpgas.online team on 4 October 2026 and on 6 October 2026 (the boot
check, `fpgas-verify`, on each host; clock times in Australia/Adelaide). A port is where a card was seen on
that date, not where it lives. The two rows without a label are the cards' last measurement, of 3 September
2026, below.

Both cable faults read on 4 October 2026 were repaired by 6 October 2026, when both cards passed.

The two cable faults
read at Welland on 2026-10-04 were both of the kind the building guide's meter checks catch: on acorn-olive
both pairs of P2 were crossed with every wire conducting, and on acorn-sycamore
P2 wire 4 (J5) was open. A cable that passes the meter and is still wrong is
named, wire by wire, by the check: [verifying on a Raspberry Pi
5](../building/rpi-5/verifying-1.md).

## Reads of September 2026

These are the records of 3 and 21 September 2026, kept as they were written then, by the MAC of the Pi each
card was on. What has been read since is in the table above.

All six were unplugged and are being put back one at a time, and not into the
ports they had before. A hostname follows the switch port (`pi-sw2-p<port>`),
so each board is listed by its RPi MAC. A board without a switch port is
unplugged and waiting to go back in; its columns are its last measurement.

```{rst-class} nowrap
```

| RPi MAC | Then | RPi Model (rev) | FPGA Device DNA | In flash | JTAG | P2 (K2/J2/J5/H5) | Camera | Last checked |
| ------- | --- | --------------- | --------------- | -------- | ---- | ---------------- | ------ | ------------ |
| 88:a2:9e:45:85:77 | [pi-sw2-p48](https://welland.fpgas.online/fpgas/pi-sw2-p48.html) | RPi 5 Rev 1.1 2 GB (b04171) | `0x0054b48664b04854` | **fpgas.online golden + operational** (`10ee:7021`, subsystem `1e24:021f`), cold boot proven ([how](../designs/install-images.md#installing-the-fpgasonline-images)) | OK | OK, all four | **out of focus, not aimed at the board** | 2026-09-21 |
| 88:a2:9e:45:dd:be | unplugged | RPi 5 Rev 1.1 2 GB (b04171) | not read | SQRL factory firmware (`1e24:021f`) | OK | serial pair OK; **J5 wire open** | ov5647 | 2026-09-03 |
| 98:fe:54:13:e0:75 | unplugged | RPi 5 Rev 1.1 1 GB (a04171) | not read | SQRL factory firmware (`1e24:021f`) | **empty chain** | untestable | ov5647 | 2026-09-03 |
| 98:fe:54:13:e0:f5 | unplugged | RPi 5 Rev 1.1 1 GB (a04171) | not read | `10ee:7011`, most likely the vendor XDMA sample image | **empty chain** | untestable | ov5647 | 2026-09-03 |
| 98:fe:54:13:f5:75 | unplugged | RPi 5 Rev 1.1 1 GB (a04171) | not read | SQRL factory firmware (`1e24:021f`) | OK | **reversed** (K2↔J2 and J5↔H5) | ov5647 | 2026-09-03 |
| 88:a2:9e:45:c6:87 | unplugged | RPi 5 Rev 1.1 2 GB (b04171) | not read | SQRL factory firmware (`1e24:021f`) | OK | OK, all four | ov5647 | 2026-09-03 |

The SQRL factory firmware is a mining design, not LiteX, so `litepcie_util`
cannot talk to a board that boots it; `10ee:7011` is the vendor's XDMA sample
image, also not LiteX. See [PCIe programming](../designs/litex-soc.md#what-the-flash-holds).
The JTAG and P2 columns come from the [pin-ID
check](../designs/pin-id.md): GPIO15 decoded through
`/dev/ttyAMA0`, the other three lines from `gpiomon` edge timestamps.

All six ran the shared bookworm NFS root (`overlayroot=tmpfs`), with
`/dev/ttyAMA0` enabled by `[pi5] dtoverlay=uart0-pi5`, the kernel console on
`ttyAMA10` and `serial-getty@ttyAMA0` inactive. The root carries
`openfpgaloader-rp1pio` and `openocd-rp1pio` 0.0.post76 (openFPGALoader 1.1.1,
OpenOCD 0.12). openFPGALoader's `libgpiod` cable works once `/dev/gpiochip0` is
linked to `gpiochip15` ([how](../wiring/rpi-5-host.md#jtag-from-the-pi)); its `rp1pio`
cable needs `/dev/pio0`, which these hosts do not have (`rp1-pio: failed to
contact RP1 firmware`, bootloader `3c4fc886`). OpenOCD with `adapter driver
linuxgpiod` on `gpiochip15` works too, and loads the 2.3 MB fpgas.online SoC
bitstream in 24 s. A wedged Pi 5 draws about 0.4 W on PoE instead of about 8 W
and needs a PoE cycle, taking more than 90 s to come back.

Read since: On 2 October 2026 `/dev/pio0` was present, and the check's `rp1-pio` test passed, on the Acorn and Raspberry Pi 5 seen at welland's sw2 p47 that day.

Source: live probes (`/proc/device-tree/model`, `lspci -nn`, `/proc/cmdline`,
`openFPGALoader --detect`, the pin-ID check), the NFS root's package list on
tweed, and pi-sw2-p48's install record.

## Known faults, as recorded in September 2026

The two cable faults among these were read again on 4 October 2026 and repaired by 6 October 2026 (the table
at the top). On 2 October 2026 `/dev/pio0` was present, and the check's `rp1-pio` test passed, on the Acorn and Raspberry Pi 5 seen at welland's sw2 p47 that day. The others have
not been read again here.

- **Acorn 98:fe:54:13:e0:75 and 98:fe:54:13:e0:f5**: `openFPGALoader --detect`
  finds an empty JTAG chain although PCIe enumerates. The P1 cable needs a
  physical check; until then nothing can be loaded on them.
- **Acorn 98:fe:54:13:f5:75**: the P2 cable is reversed (K2↔J2 and J5↔H5).
  Transpose both pairs; turning the 2×3 housing round does not fix it, because
  that maps pin 5↔10 and 7↔8.
- **Acorn 88:a2:9e:45:dd:be**: the J5 (spare GPIO) conductor is open. The serial
  pair is fine.
- **All Acorn hosts**: openFPGALoader's `rp1pio` cable cannot run (no
  `/dev/pio0`), and its `libgpiod` cable needs the `gpiochip15 → gpiochip0`
  link on a Pi 5. See [P1: JTAG](../wiring/rpi-5-host.md#jtag-from-the-pi).
