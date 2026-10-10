---
type: reference
owner: documentation maintainers
reader: someone who needs to know which controller and firmware a Tiny Tapeout shuttle's demo board has
review: 2026-11-10
---

# Tiny Tapeout shuttles and their demo boards

This page lists each Tiny Tapeout shuttle with the controller on its demo board, and the firmware each controller can run.
It does not say which boards are deployed; the public site for them is <https://tinytapeout.fpgas.online>.

## Shuttles and controllers

The demo PCB version is fixed by the shuttle: v2 (RP2040) carries TT06 to TT08 and v3 (RP2350) carries TT09 onwards.
Chip page is the shuttle's page on tinytapeout.com; a dash means there is none that opens.
Controller is the microcontroller on the demo PCB, with the demo PCB version where it is known.

| Shuttle | Chip page | Controller |
| ------- | --------- | ---------- |
| TT02 | [tt02](https://tinytapeout.com/chips/tt02/) | RP2040 |
| TT03 | [tt03](https://tinytapeout.com/chips/tt03/) | RP2040 |
| TT03p5 | — | RP2040 |
| TT04 | [tt04](https://tinytapeout.com/chips/tt04/) | RP2040 |
| TT05 | [tt05](https://tinytapeout.com/chips/tt05/) | RP2040 |
| TT06 | [tt06](https://tinytapeout.com/chips/tt06/) | RP2040 (v2) |
| TT07 | [tt07](https://tinytapeout.com/chips/tt07/) | RP2040 (v2) |
| TT08 | [tt08](https://tinytapeout.com/chips/tt08/) | RP2040 (v2) |
| TT09 | [tt09](https://tinytapeout.com/chips/tt09/) | RP2350 (v3) |

The table follows the demo board version rule for TT09.
The test-designs hardware README lists TT09 as `USB (RP2040)`; the disagreement is tracked in fpgas.online-docs [#7](https://github.com/fpgas-online/fpgas.online-docs/issues/7).
The page `tinytapeout.com/chips/tt03p5/` returns 404, which is why the TT03p5 row has no chip page.

## Firmware by controller

Firmware is the Tiny Tapeout MicroPython SDK flashed to the controller.
Which build a board can run depends on both the controller and the shuttle.

| Board | Firmware it can run |
| ----- | ------------------- |
| RP2040 | TT SDK **2.0.4**, the last RP2040 build |
| RP2350 | the TT SDK 3.x series, which is RP2350-only |
| TT03p5 (RP2040) | demo-board firmware **1.2.2**, the last release that supports the shuttle |

The TT03p5 chip is not supported by SDK 2.0 or later.
It has no chip ROM to identify itself from, so its board identifies the shuttle from `/shuttles/tt03p5.json` and `rom_fallback.txt` on its file system.
The web Commander does not support demo-board firmware 1.2.x: tt-commander-app [#9](https://github.com/fpgas-online/tt-commander-app/issues/9).
