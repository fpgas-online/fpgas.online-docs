# Tiny Tapeout FPGA boards at ps1

**You look after the boards at ps1 (Pumping Station: One, Chicago) and want to know whether any Tiny Tapeout
FPGA demo board is installed there, and what one would need.** The site itself (the ps1 gateway, its switch,
its other boards) is on the [PS1 site page](../../../sites/ps1.md).

## The boards

**None is installed at ps1.** Probed live 2026-09-03; the PS1 rows were still TBD at that probe. Tiny
Tapeout FPGA demo boards are allocated to PS1 and not yet installed. The source
inventory carried four identical rows for them — host, switch port, IP, RPi MAC
and RP2350 serial are all TBD, and there is no board page yet.

No board allocated to ps1 has a recorded USB serial number or label, so none can be named here.

Source: the deployment table in the board's page in fpgas.online-test-designs (probed live 2026-09-03) and
the board summary in its `site-ps1.md`.

## What an installation at ps1 would need

Not yet written for ps1, and not yet run by us at ps1. What is recorded:

- The hardware is the same as at welland: [the building guide](../building/index.md).
- ps1's network is flat and MAC-based, so a new Raspberry Pi at ps1 needs an entry on the ps1 gateway: the
  [deployment checklist](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/docs/hardware/deployment-checklist.md)
  in the test-designs repository has the steps to bring a ps1 board up.
- The public Tiny Tapeout site is served from welland. Whether a board at ps1 would appear on it is not
  recorded.
