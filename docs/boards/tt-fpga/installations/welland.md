# Tiny Tapeout FPGA boards at welland

**You look after the Tiny Tapeout FPGA demo boards at welland (the private test lab in South Australia) and
want to know which boards exist, what was last read from each, and what each still needs.** The site itself
(the gateway, the switches, the other boards) is on the [Welland site page](../../../sites/welland.md).

**The live state of each board is its page on [tinytapeout.fpgas.online](https://tinytapeout.fpgas.online).**
By the project's rule the check (`fpgas-verify`) is the authority on what is connected and whether it passes.
The tables below are dated snapshots.

## The boards

These carry an **iCE40UP5K FPGA** (FabricFox breakout) that emulates Tiny
Tapeout designs, on a TT demo board **v3 (RP2350B)** running TT SDK **3.1.0**
(reflashed 2026-08-23). They are **not** ASIC boards. They have been public on tinytapeout.fpgas.online since
2026-08-24, where users can run
bundled demos or upload their own bitstream.

A board is named here by the USB serial number of its microcontroller, which is what the check records for
it. No label has been recorded for any of them yet. A hostname at welland follows the switch port and a
board can be moved, so a port is given only as where a board was seen on a date.

**Reaching a board's Pi.** A Pi's host name and address at welland follow the switch port it is plugged into
(`pi-sw<switch>-p<port>`, `10.21.<switch>.<port>`: [the per-port
scheme](../../../setup/network.md#two-addressing-schemes)), so they are not repeated here as facts about a
board. On 3 September 2026 each host below had a page on welland.fpgas.online, linked in the first table;
whether that page shows the host's ssh command is not verified by us. The Pis are reached through the
gateway: [Gateway: tweed](../../../sites/welland.md#gateway-tweed).

```{rst-class} nowrap
```

| Board, by its RP2350's USB serial | USB VID:PID | Seen at, on 3 September 2026 | Shown on the public site then as |
|---|---|---|---|
| `4df39a7a6856f86f` | `2e8a:0005` | sw2 p33 ([its host's page then](https://welland.fpgas.online/fpgas/pi-sw2-p33.html)) | [fpga-1](https://tinytapeout.fpgas.online/board/fpga-1/) |
| `fd1a167bd863a198` | `2e8a:0005` | sw2 p34 ([its host's page then](https://welland.fpgas.online/fpgas/pi-sw2-p34.html)) | [fpga-2](https://tinytapeout.fpgas.online/board/fpga-2/) |
| `8c46329b33590ecb` | `2e8a:0005` | sw2 p35 ([its host's page then](https://welland.fpgas.online/fpgas/pi-sw2-p35.html)) | [fpga-3](https://tinytapeout.fpgas.online/board/fpga-3/) |
| `a2961e5cac65b25f` | `2e8a:0005` | sw2 p36 ([its host's page then](https://welland.fpgas.online/fpgas/pi-sw2-p36.html)) | [fpga-4](https://tinytapeout.fpgas.online/board/fpga-4/) |

The Raspberry Pi each was on that day, by its model and MAC (no Pi serial number is recorded):

```{rst-class} nowrap
```

| Board | On, 3 September 2026 | The Pi's MAC | The host's name before 2026-08-23 |
|---|---|---|---|
| `4df39a7a6856f86f` | RPi 4 2 GB Rev 1.5 (b03115) | `e4:5f:01:97:0e:77` | pi27 |
| `fd1a167bd863a198` | RPi 4 2 GB Rev 1.5 (b03115) | `e4:5f:01:97:27:f2` | pi29 |
| `8c46329b33590ecb` | RPi 4 2 GB Rev 1.5 (b03115) | `e4:5f:01:97:0c:e3` | pi31 |
| `a2961e5cac65b25f` | RPi 4 8 GB Rev 1.5 (d03115) | `e4:5f:01:8e:02:27` | pi33 |

Each RPi connects to its board over USB-C, has a Digilent Pmod HAT for
GPIO-level control of the TT I/O pins, and an ov5647 camera publishing a live
feed. Like the ASIC boards they appear as "MicroPython Board in FS mode" with
the `/dev/ttboard` symlink, and the `fpgas-tt` daemon owns the port. Each
board's `status.json` (for example
`https://tinytapeout.fpgas.online/board/fpga-1/status.json`) reports the daemon's
`/health` plus `reachable`, and is the quickest liveness check.

Source: live probe 2026-09-03 (`lsusb`, `/dev/serial/by-id`, daemon `/health`).

## What has been read since

Each of these reads names a board by where it was seen that day; whether the board at a port was the same
board as on 3 September 2026 is not recorded.

- **29 September 2026.** The pin-ID design, on the boards seen at sw2 p33, p35 and p36; the host at sw2 p34
  was not powered. It read the cabling INPUT to JA, BIDIR to JB, OUTPUT to JC, and the wires that have a GPIO
  to themselves: [sources](../wiring/sources.md).
- **2 October 2026.** The boot check (`fpgas-online-verify` 0.0.post771) on the boards seen at sw2 p33, p35
  and p36; no Pi answered at sw2 p34. `uart` passed on each; `pin-id` and `spiflash` failed on each: [the
  results of that day](../../../verify/fpgas-verify.md#current-results).
- **4 October 2026.** The boot check's `pin-id`, on the boards seen at sw2 p33, p35 and p36; the host at
  sw2 p34 was not powered. It read the same cabling as on 29 September: [sources](../wiring/sources.md).

About the fails of 2 October 2026: the `spiflash` test was for a flash this board does not have and has since
been removed ([no SPI flash](../overview/device-info.md#no-spi-flash)). Why `pin-id` failed that day is not
recorded here; the pin-mapping page of that time had JA and JC the other way round from the measured cabling
([test-designs issue #58](https://github.com/fpgas-online/fpgas.online-test-designs/issues/58)). No result of
a later whole check is recorded on these pages.

## What each still needs

- **Each of them:** its label (none recorded); a whole boot check recorded since the fixes above; the answer
  about its Pmod cables and their 3.3 V pins (asked on 6 October 2026): [which cable goes
  where](../wiring/cables.md).
- **The board seen at sw2 p34 on 3 September 2026 (`fd1a167bd863a198`):** to be read. Its host was not
  powered on 29 September, 2 October or 4 October 2026; why is not recorded.

## Firmware

The firmware history of these boards and the workarounds: [firmware](../designs/firmware.md).
