---
type: how-to
owner: documentation maintainers
reader: a visitor with an Arty A7's page open on welland.fpgas.online
review: 2026-11-10
---

# How to load a design onto an Arty A7 from its board page

**You have an Arty A7's page open on welland.fpgas.online and a `.bit` bitstream for it. You want the design to
run**. The load goes into the FPGA's SRAM, so a reset or a power cycle ends it. A reset or a reboot also empties
`/home/pi`, uploads included.

:::{admonition} Not in service today
:class: warning

No Arty A7 is in service at welland today, so there is no page to follow these steps on. The cause is open in
[infra issue #125](https://github.com/fpgas-online/fpgas.online-infra/issues/125) and, for ps1, in
[infra issue #272](https://github.com/fpgas-online/fpgas.online-infra/issues/272). The steps below are the ones for a
board that is back.
:::

## What you need

- An Arty A7's page, from [the welland list](https://welland.fpgas.online/fpgas/): a board whose label says Arty.
- A `.bit` file for the Arty A7, here `design.bit`.

## Steps

1. Upload the file with the page's **upload** button. It goes into `/home/pi/Uploads/` on the host.
2. In the page's terminal, load the design. The FPGA runs it from SRAM.

   ```console
   $ openFPGALoader -b arty Uploads/design.bit
   ```

## Check

- The load's last line ends with `done 1`. With `done 0` the FPGA is not configured, whatever the exit status; the
  STAT register printed under it says why.
- The board shows in the terminal as two `/dev/ttyUSB*` devices, the JTAG channel and the UART channel.

## If it fails

| What you see | Likely cause | Fix |
|---|---|---|
| no `/dev/ttyUSB*` device at all | the Arty's USB chip is not on the host's USB | run `lsusb` in the terminal. If it does not list `0403:6010`, the FT2232H, the host cannot reach the board: press Reset, as on [How to reset a board](../reset.md), and try again |
| `done 0` | the FPGA did not configure | read the STAT register printed under it, and check that the file was built for an Arty A7 |

More causes are on [How to load a design onto an Arty A7](../../../boards/arty-a7/setup/load-design.md#if-it-fails).

## Next

- [An Arty A7 on fpgas.online](about.md)
- [How to reset a board](../reset.md)
