# Verifying a deployment

This page covers adding **another device of a type the fleet already has** — a
sixth Arty A7 at PS1, a fifth Acorn at Welland — and then proving the new host
works. It is the test-designs repository's new-device deployment checklist,
with each of its file references pointed at the page that now holds the fact,
plus a summary of how the hardware verification script drives a board once it
is on the network.

Adding a **new device type** is out of scope, as the original checklist says:
that needs new gateware, new CI jobs, new test scripts and new documentation,
none of which this procedure produces.

## Adding a device of an existing type

Five things change, and a sixth from the original checklist has collapsed into
the second. Three of them still live in repositories rather than in these docs,
and are called out as such.

### 1. Gateway network configuration

**PS1 (val2)** — add a `dhcp-host` entry for the new Pi's MAC address to
`/etc/dnsmasq.d/pibs.conf` on the gateway, giving the hostname, the IP and a
comment naming the board type. PS1 still runs the legacy MAC table, so a Pi's
identity comes from its MAC and nothing is derived from the socket; see
[Gateway: val2](../sites/ps1.md#gateway-val2) for what that file is and which
range it hands out.

**Welland (tweed)** — nothing to add for the network. Since 2026-08-23 every
switch port is its own VLAN, and a Pi plugged into switch `s` port `p` becomes
`pi-sw<s>-p<p>` at `10.21.s.p` on its own, with no per-host configuration at
all ([Two addressing schemes](network.md#two-addressing-schemes)). Instead:

- Plug the board into the right port. The allocation rule on the S3300 is that
  port `N` carries Tiny Tapeout `N` for ports 1–10, the TT FPGA demo boards sit
  on 33–36, and the Acorns on 29 and 43–48. Which of those ports are actually
  occupied today is the
  [Welland host tables](../sites/welland.md#hosts-and-boards), not this rule.
- For a Tiny Tapeout board, add or enable its row in the `tt_boards` catalogue.
  That catalogue **stays in the infra repository**, in
  [`ansible/inventory/host_vars/fpgas.online.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/inventory/host_vars/fpgas.online.yml).
  Running `ansible/web.yml --tags ttsite` afterwards renders
  `/etc/fpgas-online/tt-boards.yaml` **on the gateway**, for the web tier; the
  Pi NFS root gets its own copy of the same file baked in by the `onpi` play,
  from the same template. The keys a row takes, and both render paths, are
  under [The board catalogue](tinytapeout.md#the-board-catalogue).
- For the `welland.fpgas.online` board list, update the packaged fixture. The
  fixture ships inside the `fpgas.online-site` package and is loaded by bare
  name, so it is changed in that repository and not in the infra inventory; see
  [Deployment](webapp.md#deployment).

:::{todo}
Two claims in the upstream checklist disagree with these docs.

Its port ranges are wider than the measured occupancy. The
[Welland host tables](../sites/welland.md#hosts-and-boards) put TT ASIC boards
on ports 3–8 only, with 9 and 10 reserved in the catalogue and nothing recorded
on 1 or 2; and the Acorns on p29, p43, p44, p46, p47 and p48, with no p45. Is
1–10 the standing allocation with four slots free, or has the range shrunk, and
what is on p45?

It also says the `ttsite` tag renders `/etc/fpgas-online/tt-boards.yaml` for the
Pi NFS root as well as for the gateway.
[The board catalogue](tinytapeout.md#the-board-catalogue) has the NFS root copy
baked in by `onpi/tasks/tt.yml` instead, from the same template — so a `ttsite`
run alone leaves the Pi copy stale until the `onpi` play runs. Confirm which,
and fix the checklist.
:::

### 2. Site host table

Add the new host to the right table on its site page —
[Welland hosts and boards](../sites/welland.md#hosts-and-boards) or
[PS1 hosts and boards](../sites/ps1.md#hosts-and-boards) — under the section
for that board type (Arty, NeTV2, Fomu, TT FPGA, Acorn, and so on).

Give hostname, switch port, IP, Pi model, board type or serial, and status.
The tables carry more columns than that (MAC, board serial, revision), so fill
what the section's own header row asks for.

The old checklist had a separate step for the board's own document — "if the
device doc has a host inventory section, add the new host". That step is gone,
not skipped: board pages no longer carry host inventories. Each one links to
the site page instead, so the site table is the only host list to edit.

### 3. Board counts

Update the deployed and pending counts in
[Boards at a glance](../boards/index.md#boards-at-a-glance) for that board type
and site. Deploying something that was pending means decrementing the pending
count and incrementing the deployed one.

### 4. Test runner configuration

This one **stays in the test-designs repository**. In
[`verify_hardware.py`](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/verify_hardware.py):

- Add the host to the `HOSTS` dict with its board type, gateway, target IP and
  any variant information.
- If the board type needs a programming command of its own, make sure
  `PROGRAM_CMD` (or `HOST_PROGRAM_CMD`, for a host that programs differently
  from others of the same board type) covers it.

### 5. PoE switch, physical

On the PoE switch, enable PoE on the new port if it is not already enabled,
then confirm the Pi netboots and gets an address. Power on that port is the
only remote power control there is
([PoE power control](network.md#poe-power-control)), and what the Pi does with
it is [the boot chain](netboot.md#the-boot-chain).

### Verification steps

After all of the above:

1. **Netboot.** Confirm the Pi boots over TFTP and NFS from the gateway. If it
   does not, work through
   [When a Pi does not boot](netboot.md#when-a-pi-does-not-boot).
2. **SSH access.** Confirm the double hop through the gateway reaches it.

   ```console
   $ ssh root@<gateway> 'ssh root@<new-host> hostname'
   ```

3. **FPGA detection.** Confirm the FPGA is visible — `lsusb` for USB-attached
   boards, `lspci` for the PCIe ones.
4. **Programming.** Program a test bitstream with `openFPGALoader`, or with
   whichever tool that board needs; the per-board commands are in
   [Programming commands](#programming-commands) below.
5. **Test.** Run `verify_hardware.py --host <new-host>` for the full suite.
6. **Commit.** Commit the documentation changes.

The order in which a test actually exercises the board — boot, program, open
the serial port, parse the result — is under
[From boot to result](#from-boot-to-result).

### Worked example: adding an Arty A7 at PS1

```
1. On val2: Add dhcp-host line to /etc/dnsmasq.d/pibs.conf
2. Edit docs/sites/ps1.md: Add row to the Arty A7 hosts table
3. Edit docs/boards/index.md: Increment PS1 (deployed) count for Arty A7
4. Edit verify_hardware.py: Add "ps1-piNN" to HOSTS dict
5. Power on the RPi, verify PXE boot, run verify_hardware.py
6. Commit and push
```

The original checklist suggests a commit message of the form "Add pi42 Arty A7
to Welland site".

:::{note}
`pi42` is the legacy naming form. It is still correct at PS1, where a host is
`pi<N>`, but at Welland a host has been `pi-sw<s>-p<p>` since 2026-08-23 — the
board on switch 2 port 42 is `pi-sw2-p42`. See
[Two addressing schemes](network.md#two-addressing-schemes).
:::

## Running the hardware tests

### From boot to result

End to end, whatever the board, a run is four steps:

1. **Boot.** The Pi PXE-boots from its site gateway over TFTP onto the shared
   read-only NFS root ([Netboot and the NFS root](netboot.md)).
2. **Program the FPGA.** openFPGALoader over USB FTDI JTAG (Arty), over GPIO
   bit-bang JTAG (NeTV2, and Acorn with the PCIe endpoint detached first), or
   over USB DFU (Fomu); RP2040 (TT ASIC) / RP2350 (TT FPGA), MicroPython, via
   `/dev/ttboard` (owned by the `fpgas-tt` daemon).
3. **Run the harness.** Open the serial port — `ttyUSB1`, `/dev/ttyAMA0` or
   `/dev/ttboard` — and drive the design.
4. **Collect results.** Parse the UART output for PASS/FAIL, check PCIe
   enumeration (NeTV2), verify the PMOD loopback signals (Arty).

### What the runner does per test

`verify_hardware.py` is the test orchestrator. It holds no state on the Pi: for
every test it uploads what it needs, prepares the host, programs the FPGA, runs
one test script and reads a single marker line out of the output.

Each of its steps, in order:

1. **Check connectivity.** `ssh_check_connectivity()` runs `echo ok`; an
   unreachable host fails the test immediately rather than timing out later.
2. **Upload.** The CI-built bitstream and the test script are piped through SSH
   stdin into `cat > <path>`, which sidesteps `scp` quoting across the double
   hop. TT FPGA hosts get extra helper scripts on top.
3. **Pre-test.** A board-specific shell command frees the serial port and the
   GPIOs — see [Pre-test commands](#pre-test-commands). It runs **before**
   programming, because the FPGA's BIOS starts talking the moment the bitstream
   loads and anything still holding the port corrupts that output.
4. **Program.** See [Programming commands](#programming-commands).
5. **Run.** `python3 ~/test_<design>.py <args>` on the Pi, with a 180-second
   timeout; stdout and stderr are both captured.
6. **Parse.** The last five lines are searched for `RESULT: PASS` or
   `RESULT: FAIL`.

Hosts and boards are declared separately and multiplied together. The `HOSTS`
dict gives each Pi an SSH type (through a gateway, or direct), a target
address, a board type, and optionally a `variant` (which FPGA is fitted, so the
matching bitstream is chosen — the NeTV2 hosts set `a7-35` or `a7-100`, and the
Acorn host sets `cle-215+`) and a `serial_port` (which UART device that Pi
model exposes). `DESIGNS` gives each test design a script and a
per-board artifact, arguments and pre-test command. `generate_tests()` takes
the cross product and keeps every pair whose board type the design supports, so
adding a host to `HOSTS` is enough to enrol it in every applicable test.

:::{todo}
The `HOSTS` dict in `verify_hardware.py` is stale. It carries the pre-2026-08-23
Welland names and flat addresses — `welland-pi3` at `10.21.0.103` through
`welland-pi33` at `10.21.0.133` (lines 41–75) — while those hosts are now
`pi-sw<s>-p<p>` at `10.21.s.p`
([Two addressing schemes](network.md#two-addressing-schemes)). The `GATEWAYS`
table (lines 29–32) still reaches Welland as `pi@tweed.welland.mithis.com`,
an account that went away with tweed's 2026-08-30 reinstall. Nothing in the
Welland half of the table can connect as written.
:::

### Pre-test commands

Each design's per-board configuration may carry a `pre_test` command, run over
SSH with a 30-second timeout before the FPGA is programmed. What each one is
for:

| Board | Designs | Pre-test command | Why |
| --- | --- | --- | --- |
| Arty | PMOD loopback | `rmmod spidev spi_bcm2835` | The SPI kernel modules claim GPIO 7–11, which overlap the PMOD HAT's JB pins. Unloading them frees the GPIOs for the loopback. |
| Arty | UART, DDR, Ethernet, SPI flash | none | The Arty's UART is on its own FTDI channel, so nothing on the Pi contends for it. |
| Fomu | UART | `systemctl mask serial-getty@ttyAMA0`, then `stop`, then `fuser -k /dev/serial0` and `chmod 666 /dev/serial0` | `stop` alone is not enough — systemd restarts the getty — so the unit is masked to `/dev/null` first. `fuser` clears anything else holding the port, and the permissions revert to root-only when the getty lets go. |
| Fomu | SPI flash | `systemctl stop 'serial-getty@*'`, `fuser -k`, `chmod 666`, then `pinctrl set 14 a4; pinctrl set 15 a4` if `pinctrl` exists | Same port cleanup, plus the Pi 5 GPIO fix below. |
| Fomu | PMOD loopback | `rmmod spidev spi_bcm2835` | Same GPIO 7–11 clash as the Arty. |
| NeTV2 | UART | `systemctl stop 'serial-getty@*'`; `pm2 stop all`; `pkill -f netv2-status`; `fuser -k`; `chmod 666`; `pinctrl set 14 a4; pinctrl set 15 a4` | Three different things hold the port: the serial login console, a pm2-managed `netv2-status.js` monitor that keeps sending `json on` to the FPGA BIOS, and whatever `fuser` finds left. On a Pi 5, GPIO 14/15 fall back to plain GPIO when the getty stops, so `pinctrl` puts them back on ALT4 (TXD0/RXD0); a Pi 3's mini-UART pins do not change function and need no such fix. |
| NeTV2 | DDR, Ethernet, SPI flash | `systemctl stop serial-getty@ttyAMA0` | Only the login console is in the way. |
| NeTV2 | PMOD loopback | none | The NeTV2 loopback is a one-bit serial loopback rather than a PMOD-HAT GPIO test, so it does not touch GPIO 7–11. |
| Acorn | UART, DDR, SPI flash | `systemctl stop serial-getty@ttyAMA0` | As above. |
| Acorn | PMOD loopback, PCIe enumeration | none | The loopback runs the NeTV2 one-bit serial path, and the PCIe test only reads the enumeration. |
| TT FPGA | PMOD loopback | `rmmod spidev spi_bcm2835` | The loopback drives the FPGA through the PMOD HAT, over the same GPIO 7–11 the SPI modules claim. |
| TT FPGA | UART, SPI flash | none | These go over the RP2350's USB CDC port, not the Pi's GPIO UART. |

A PoE cycle loses all of this: the mask, the unloaded modules and the pin
functions are all runtime state on a read-only NFS root, so the pre-test is
re-run after any power-cycle recovery.

### Programming commands

Programming is chosen in this order: a design's own per-board `program_cmd`
first, then a per-host override, then the board default.

| Board | Command | Path |
| --- | --- | --- |
| Arty | `openFPGALoader -b arty <bitstream>` | USB JTAG through the on-board FTDI. |
| Fomu | `openFPGALoader -b fomu <bitstream>` | USB DFU. |
| Acorn | `rmmod spidev spi_bcm2835 2>&1; openFPGALoader -c rp1pio --pins 10:9:11:8 <bitstream>` | GPIO bit-bang JTAG on the Pi's SPI0 pins, which is why the SPI modules come out first. openFPGALoader's pin order is TDI:TDO:TCK:TMS, so GPIO 10 (SPI0 MOSI) is TDI and GPIO 11 (SCLK) is TCK; see [Acorn wiring](../boards/acorn/wiring.md). As configured in the runner: the Welland NFS root on infra `main` still ships openFPGALoader 0.10.0 with no `rp1pio` cable until infra PR #48 lands, see [Packages](pi.md#packages). |
| TT FPGA | `python3 ~/tt_fpga_program.py /dev/ttyACM0 <bitstream>` | Through the RP2350 over USB CDC. The PMOD loopback design appends `--gpio-release`. |
| NeTV2 on `rpi5-netv2` | `sudo openFPGALoader -c rp1pio --pins 27:22:4:17 <bitstream>` | RP1 GPIO bit-bang JTAG on the 40-pin header, in openFPGALoader's TDI:TDO:TCK:TMS pin order; see [JTAG via RPi GPIO](../boards/netv2.md#jtag-via-rpi-gpio). As configured in the runner: the Welland NFS root on infra `main` still ships openFPGALoader 0.10.0 with no `rp1pio` cable until infra PR #48 lands, see [Packages](pi.md#packages). |
| NeTV2 on `rpi3-netv2` | `sudo openocd -f ~/netv2/alphamax-rpi.cfg -c 'init; pld load 0 <bitstream>; exit'` | BCM2835 GPIO bit-bang JTAG. `pld load 0` is OpenOCD 0.10.x syntax, device index 0. |
| NeTV2 on the Welland pool hosts | the same OpenOCD command **without** `sudo` | The gateway hop already lands as root on those Pis. |

OpenOCD does not expand `~`, so the runner rewrites the bitstream path to an
absolute one before handing it over, using the home directory of whichever
account that host is reached as.

Programming counts as successful if the command exits 0 **or** its output
contains `done 1` in any letter case — openFPGALoader prints the FPGA's DONE
status bit, while
`tt_fpga_program.py` only reports through its exit code.

Failure on a Fomu is treated as a DFU timeout rather than a fault. The EVT's
DFU bootloader gives up after roughly three minutes and loads the user
bitstream out of SPI flash, which usually has no USB at all, so the board
vanishes. The runner then power-cycles the host, waits for it to netboot,
re-uploads the bitstream and script (the tmpfs overlay is empty again), re-runs
the pre-test, and retries programming once.

### PoE reset

`poe_reset()` is the recovery path. It SSHes to the Welland gateway and runs
`poe.sh <port> 2` to cut power, polls connectivity until the host stops
answering — which is how it confirms the power actually went off — then runs
`poe.sh <port> 1` and polls until the host answers again, allowing for a Pi 3
netboot of about two minutes. Nothing waits a fixed time for the hardware:
both waits are bounded polls, the power-off loop polling on a half-second
interval and the boot loop on the connectivity check's own ten-second timeout.
The switch port comes from the host name.

:::{todo}
`poe_reset()` derives the switch port with `re.match(r"pi(\d+)$", host_name)`
(line 353), which only matches a bare `piNN`. Every key in the current `HOSTS`
dict is `welland-piNN`, `ps1-piNN`, `rpi5-netv2` or `rpi3-netv2` (lines 41–99),
so the match always fails, the function returns `False`, and the Fomu DFU
recovery at line 537 can never fire. The upstream
[verify-hardware.md](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/docs/verify-hardware.md)
describes the mapping as "pi27 → switch port 27", which was true before the
host keys were prefixed with a site name.
:::

### TT FPGA programming

The mechanism — the RP2350 taking the bitstream over `mpremote`, programming
the iCE40 over SPI and then releasing the shared pins to high-Z — is on the
[TT FPGA board page](../boards/tt-fpga.md#programming), with the pin numbers
under [Pin mapping](../boards/tt-fpga.md#pin-mapping) and the HAT side on
[Raspberry Pi PMOD HAT](../boards/pmod/rpi-hat.md).

What the runner does differently is which of the two entry points it calls. For
the PMOD loopback it programs in its own step, appending `--gpio-release` so
the RP2350 drops off the shared traces before the Pi drives them. For the UART
and SPI-flash designs it does not program separately at all: it calls
`tt_test_wrapper.py`, which programs the board, bridges its serial port and
runs the test in one invocation, with a 240-second timeout instead of the
120-second one that programming alone gets. Once the FPGA is configured the Pi
reaches it through the PMOD HAT exactly as it does an Arty or a Fomu, so
programming is the only board-specific step.

:::{note}
The upstream `verify-hardware.md` carries its own iCE40 ↔ PMOD HAT ↔ Pi GPIO pin
tables, and they do not agree with the measured tables on the board page. That
disagreement is tracked in the todo under
[Pin mapping](../boards/tt-fpga.md#pin-mapping); use the board page's tables.
:::

### Result detection and exit code

`check_test_result()` looks in the last five lines of the combined output for
`RESULT: PASS` or `RESULT: FAIL`. Every test script prints exactly one such
line, last, so the marker survives wrapper chatter and error text earlier in
the run. Failing that, a bare `PASS` in the tail together with exit code 0 is
accepted as a pass, and anything else is a fail.

The run ends with a summary table of pass, fail and skip per test, and exits 0
when nothing failed and 1 when anything did. A test whose bitstream is missing
from `artifacts/` is skipped, not failed, and does not change the exit code.
`--list` prints the generated tests without running them; `--test`, `--host`
and `--board` narrow the set; `--skip-upload` reuses whatever is already on the
Pi.

:::{todo}
The upstream
[verify-hardware.md](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/docs/verify-hardware.md)
has drifted from the script on six points. The code is what is described
above. (1) It documents `ssh_type: "tweed"` with a hard-wired tweed hop; the
code uses `ssh_type: "gateway"` with a `gateway` key selecting from a
`GATEWAYS` table that also holds PS1 (lines 29–32, 293–299). (2) It says
`EXTRA_UPLOADS` sends three helper scripts including `tt_pmod_wrapper.py`; the
code sends two, `tt_fpga_program.py` and `tt_test_wrapper.py` (lines 273–278).
(3) Its programming section has no Acorn entry, although `PROGRAM_CMD["acorn"]`
exists (line 108), gives the OpenOCD config as `alphamax-rpi.cfg` rather than
`~/netv2/alphamax-rpi.cfg`, and does not mention that the five Welland NeTV2
pool hosts run it without `sudo` (lines 113–122). (4) It does not mention the
PMOD design's `--gpio-release` programming override (line 253). (5) It calls
`variant` NeTV2-only; `welland-pi2` is an Acorn carrying `"variant": "cle-215+"`
(lines 68–71) and the variant-artifact selection at lines 407–413 is
board-agnostic. (6) It glosses the `--pins 27:22:4:17` string as TCK:TDO:TDI:TMS;
openFPGALoader's order is TDI:TDO:TCK:TMS, as
[JTAG via RPi GPIO](../boards/netv2.md#jtag-via-rpi-gpio) and
[Acorn wiring](../boards/acorn/wiring.md) both give it for the same pin strings,
and GPIO 10 is SPI0 MOSI (TDI) with GPIO 11 the clock. Line numbers are
`verify_hardware.py` on `main` as read on 2026-09-04.
:::

## Sources

fpgas.online-test-designs, `main`:

- [`docs/hardware/deployment-checklist.md`](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/docs/hardware/deployment-checklist.md)
  — the whole "Adding a device of an existing type" procedure: everything that
  changes, the six verification steps, and the PS1 Arty worked example.
- [`docs/verify-hardware.md`](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/docs/verify-hardware.md)
  — the reasoning behind each pre-test command, the Fomu DFU timeout and its
  recovery, the PoE reset sequence, and the RP2350 high-Z hand-off on the TT
  FPGA board.
- [`verify_hardware.py`](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/verify_hardware.py)
  — the authority for the pre-test and programming tables above, the
  `HOSTS` × `DESIGNS` expansion, the `done 1` success test, `check_test_result()`
  and the exit code.
