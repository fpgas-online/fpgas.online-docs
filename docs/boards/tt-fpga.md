# Tiny Tapeout FPGA demo board

The Tiny Tapeout (TT) FPGA demo board is a Lattice iCE40UP5K "FabricFox" FPGA
breakout plugged into a Tiny Tapeout demo PCB, in place of the Tiny Tapeout ASIC
the demo PCB was designed for. The FPGA presents the same `ui_in` / `uo_out` /
`uio` interface as a real Tiny Tapeout chip, so a design can be emulated on real
hardware before — or instead of — silicon. Eight boards exist in the fleet: four
running at Welland and four pending deployment at PS1.

This page covers the board itself, how it is wired and programmed, the test
infrastructure built around it, the workarounds its firmware needs, and the
measured [pin mapping](#pin-mapping) from iCE40 ball through PMOD HAT to
Raspberry Pi GPIO. Before running anything against a deployed board, read
[Serial port ownership](#serial-port-ownership) — a daemon holds the port open
and the board is on a public web site while you work.

## Where they are

Eight TT FPGA demo boards across two sites. Four are deployed at Welland on
S3300 ports 33–36 (Tim's rule for that switch: port N carries Tiny Tapeout board
N; the FPGA emulation boards take the 33–36 block). The Welland four are the
public **fpga-1 … fpga-4** boards on
[tinytapeout.fpgas.online](https://tinytapeout.fpgas.online), live since
2026-08-24 and probed live 2026-09-03. Their hosts, IP addresses, MACs, RP2350
serials, switch ports and old `piNN` names are in
[Tiny Tapeout FPGA demo boards](../sites/welland.md#tiny-tapeout-fpga-demo-boards)
on the Welland page, which also carries the gateway and the per-port VLAN scheme
that gives each Pi `10.21.<switch>.<port>`.

The other four are pending deployment at [PS1](../sites/ps1.md), whose flat
`10.21.0.0/24` network and gateway are on that page. See the
[deployment checklist](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/docs/hardware/deployment-checklist.md)
in the test-designs repository for the steps to bring the PS1 boards up.

Each RPi connects to a TT FPGA board via USB-C, has a Digilent
[Pmod HAT](pmod/rpi-hat.md) for GPIO-level control of the TT I/O pins, and an
ov5647 camera publishing a live feed of the board. RPis are powered and
networked through PoE switches at each site. Each board's `status.json` (for
example `https://tinytapeout.fpgas.online/board/fpga-1/status.json`) reports the
Pi daemon's `/health` plus `reachable`, and is the quickest liveness check.

## Key Specifications

| Parameter | Value |
|-----------|-------|
| FPGA | Lattice iCE40UP5K (on FPGA breakout board) |
| Logic cells | 5,280 LUT4s |
| SPRAM | 128 KB (4 x 32 KB blocks) |
| DPRAM (EBR) | 120 Kbit (15 x 8 Kbit blocks) |
| Controller | RP2040 (dual-core Arm Cortex-M0+, on demo PCB) |
| USB | USB-C (via RP2040) |
| Display | 7-segment LED display |
| DIP switches | Configuration switches |
| PMOD headers | 2x standard PMOD (following Digilent spec) |
| Max clock | ~66 MHz |
| I/O voltage | 3.3V |

:::{note}
The controller row above is the generic Tiny Tapeout demo PCB specification,
which describes the RP2040-based demo board v2. Every board in this fleet is a
demo board **v3 (TTDBv3)** carrying an **RP2350B**, and the
[pin mapping](#pin-mapping) below is the v3 mapping. The two are *not*
interchangeable: [Tiny Tapeout PMOD layouts](pmod/tinytapeout.md) shows the
clock on GPIO0 for v2 against GPIO16 for v3, and a different GPIO block for
every signal group. Where the sources here say "RP2040" for a deployed board,
read RP2350.
:::

:::{todo}
The RP2040-specific facts inherited from that v2 specification have not been
re-verified on a v3 board: the ~66 MHz maximum clock in the table above, and
the PWM first-call bug the source calls an RP2040 bug while the deployed
workaround calls it an RP2350 bug (see [RP2350 PWM first-call
bug](#rp2350-pwm-first-call-bug)). Measure both on a TTDBv3 in the fleet and
record the date.
:::

:::{todo}
The two sources disagree on how the iCE40UP5K's block RAM is divided. The table
above says 15 × 8 Kbit EBR blocks; [FPGA Device](#fpga-device) under the pin
mapping says 30 EBR blocks. The totals agree (120 Kbit ≈ 15 KB), so one of the
block counts is wrong. Check against the Lattice datasheet and fix the loser.
:::

Source: [TinyTapeout PCB Specs](https://tinytapeout.com/specs/pcb/),
[TinyTapeout FPGA Breakout Guide](https://tinytapeout.com/guides/fpga-breakout/)

## Architecture

The TT FPGA demo board consists of two PCBs:

1. **TinyTapeout Demo PCB** (bottom): Contains the RP2040 microcontroller,
   USB-C connector, 7-segment display, DIP switches, and PMOD headers. This PCB
   is designed to interface with TinyTapeout ASICs but also accepts the FPGA
   breakout board.

2. **FPGA Breakout Board** (top): Contains the iCE40UP5K FPGA and SPI flash. It
   plugs into the demo PCB's chip socket, presenting the same interface as a
   TinyTapeout ASIC.

```text
┌──────────────────────────────┐
│    FPGA Breakout Board       │
│    (iCE40UP5K + SPI Flash)   │
│                              │
│    ┌────────────────────┐    │
│    │  Pin headers down  │    │
│    └────────────────────┘    │
└──────────────┬───────────────┘
               │ (plugs into)
┌──────────────┴───────────────┐
│    TinyTapeout Demo PCB      │
│                              │
│  [USB-C] [RP2040] [7-seg]   │
│  [DIP SW] [PMOD A] [PMOD B] │
└──────────────────────────────┘
```

The microcontroller programs the iCE40 over SPI and provides its 50 MHz clock.
After programming it releases its GPIO pins to high impedance so the Raspberry
Pi can talk to the FPGA directly through the PMOD HAT — the controller and the
PMOD headers share the same physical traces.

## TinyTapeout I/O Interface

The FPGA implements a TinyTapeout-compatible interface with the following
signals:

| Signal Group | Width | Direction | Description |
|-------------|-------|-----------|-------------|
| `ui_in[7:0]` | 8 bits | Input | User inputs (directly from DIP switches or RP2040) |
| `uo_out[7:0]` | 8 bits | Output | User outputs (directly to 7-segment display or RP2040) |
| `uio[7:0]` | 8 bits | Bidirectional | User bidirectional I/O |
| `ena` | 1 bit | Input | Enable signal |
| `clk` | 1 bit | Input | Clock (up to ~66 MHz) |
| `rst_n` | 1 bit | Input | Active-low reset |

Source: [TinyTapeout PCB Specs](https://tinytapeout.com/specs/pcb/)

## Serial Interface

The TT FPGA board supports UART communication through the TinyTapeout I/O pins.
Two serial pin configurations are available:

### Option 1 (Default TT UART)

| Signal | TT Pin | Direction (FPGA perspective) |
|--------|--------|------------------------------|
| RX | ui_in[3] | Input |
| TX | uo_out[4] | Output |

### Option 2 (Alternate)

| Signal | TT Pin | Direction (FPGA perspective) |
|--------|--------|------------------------------|
| RX | ui_in[7] | Input |
| TX | uo_out[0] | Output |

The RP2040 on the demo PCB can act as a USB-to-UART bridge, forwarding serial
data between the USB-C port and the FPGA's UART pins.

Source: [TinyTapeout PCB Specs](https://tinytapeout.com/specs/pcb/)

## PMOD Headers

The demo PCB has 2 standard PMOD headers following the
[Digilent specification](pmod/index.md):

- Each header is a 12-pin connector (8 signal + 2 GND + 2 VCC)
- Signal voltage: 3.3V
- The PMOD signals are routed through the TinyTapeout bidirectional I/O (`uio`)
  or directly to the FPGA breakout board

These PMOD headers can be used for loopback testing in the fpgas.online
infrastructure. The layouts Tiny Tapeout recommends for them are on
[Tiny Tapeout PMOD layouts](pmod/tinytapeout.md).

Source: [TinyTapeout PCB Specs](https://tinytapeout.com/specs/pcb/)

## Clock

The RP2350 (RP2040 on v2 boards) generates a 50 MHz clock via PWM on GPIO16
(`RP_PROJCLK`) — GPIO16 is the v3 pin. The
iCE40UP5K's internal PLL divides this down to a 12 MHz system clock for
LiteX SoC designs (see the
[clock and reset generator](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/designs/_shared/tt_fpga_crg.py)).

## 7-Segment Display

The demo PCB includes a 7-segment LED display connected to the `uo_out` pins.
This provides immediate visual feedback from the FPGA design:

| Segment | TT Output Pin |
|---------|--------------|
| a | uo_out[0] |
| b | uo_out[1] |
| c | uo_out[2] |
| d | uo_out[3] |
| e | uo_out[4] |
| f | uo_out[5] |
| g | uo_out[6] |
| dp | uo_out[7] |

Source: [TinyTapeout PCB Specs](https://tinytapeout.com/specs/pcb/)

## DIP Switches

The demo PCB has DIP switches connected to the `ui_in` pins, allowing manual
input to the FPGA design during development and testing.

## Programming

The RP2350 (RP2040 on v2 boards) programs the iCE40UP5K over SPI using the
`fabricfox` MicroPython module (PIO-accelerated or bitbang fallback).

```console
# The fpgas-tt daemon holds the serial port open; stop it before programming
# by hand, and start it again afterwards or the board drops off the public site.
$ sudo systemctl stop fpgas-tt
$ python3 designs/_host/tt_fpga_program.py /dev/ttyACM0 bitstream.bin
$ sudo systemctl start fpgas-tt
```

**Programming workflow:**

1. Upload `.bin` to `/bitstreams/custom.bin` on the RP2350 (RP2040 on v2
   boards) via `mpremote`. The
   [UART test wrapper](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/designs/_host/tt_test_wrapper.py) additionally calls
   its `reset_rp2350()` (Ctrl-C to break any stuck MicroPython script) and
   retries after a USB power cycle.
2. Enter raw REPL and execute a MicroPython script that:
   - Asserts `CRESET` (GPIO1) to reset the FPGA
   - Transfers the bitstream over SPI (SCK=GPIO6, MOSI=GPIO3, SS=GPIO5 — the
     v3 values, hardcoded as `TTDBv3` in the programming script)
   - Releases `CRESET` and waits for FPGA `CDONE`
   - Starts the 50 MHz clock on GPIO16
3. For PMOD tests: release all GPIO pins to high-Z (`--gpio-release`). All
   `ui_in`, `uo_out` and `uio` pins are set to `Pin.IN`. This is critical: the
   controller shares the same physical traces as the PMOD headers, so without
   releasing them its output drivers contend with the RPi's GPIO signals coming
   through the PMOD HAT.

After step 3 the RPi has clean access to the FPGA through the PMOD HAT, and
tests run the same way as on any other board — UART and PMOD tests work
identically to Arty and Fomu once the FPGA is programmed. Programming is the
only TT-specific step.

**SPI Flash:** The breakout board also has SPI flash (CS_N=pin 16, CLK=pin 15,
MOSI=pin 14, MISO=pin 17) for persistent bitstream storage, used by
the SPI Flash ID test.

## LiteX Integration

| Property | Value |
|----------|-------|
| FPGA | iCE40UP5K (same as Fomu) |
| Toolchain | Yosys + nextpnr-ice40 (open source, IceStorm flow) |

The TT FPGA board does not have a dedicated LiteX platform file in litex-boards.
Designs target the iCE40UP5K with a custom pin constraint file matching the
TinyTapeout I/O interface.

## Board firmware

**2026-08-23:** all four Welland boards were reflashed to TT SDK **3.1.0** (the
shipped `ttdbv3` build stalled at boot). With 3.1.0 the SDK's `tt` object comes
up as `Shuttle FPGA` and the Commander connects. The custom bitstreams that were
on the boards (`custom.bin`, `fabfox_mirror.bin`, …) were backed up to tweed
`/root/fpgas-tt-setup/fpga-backup/<host>/` and pushed back.

## Serial port ownership

**USB device:** `/dev/ttyACM0` (VID:PID `2e8a:0005` — MicroPython Board in FS
mode), with a udev symlink **`/dev/ttboard`** that the Pi daemon opens.

**The serial port has a permanent owner.** Every TT host runs the
[`fpgas-tt`](https://github.com/fpgas-online/fpgas.online-tt) daemon
(`fpgas-online-tt` 0.0.post52, reports version 0.1.0), which holds
`/dev/ttboard` open at 115200 baud and fans it out as a WebSocket on port 8765
(`WS /serial`, `GET /health`, reachable only from the gateway thanks to the
per-port VLANs). Verified 2026-09-03: `fuser /dev/ttyACM0` shows the daemon's
python3 process on all ten TT hosts. Consequences for the test tooling:

- `mpremote` and the
  [bitstream programming script](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/designs/_host/tt_fpga_program.py)
  cannot open `/dev/ttyACM0` while the daemon runs. Stop it first
  (`sudo systemctl stop fpgas-tt`) and start it again afterwards, or drive the
  board through the daemon's `/serial` socket.
- The bitstream-loading and design-listing features now live in the daemon
  (`/designs`, `/bitstream`, demos via the `fpgas-online-tt-demos` package),
  which is what the public site uses.

How the daemon is installed and configured is on
[The Tiny Tapeout stack](../setup/tinytapeout.md).

## Test Infrastructure

The RP2040 provides bitstream loading, clock generation, and USB-to-UART
bridging. Three host-side wrapper scripts handle the RP2040 interaction:

| Script | Purpose |
|--------|---------|
| [`tt_fpga_program.py`](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/designs/_host/tt_fpga_program.py) | Upload and program bitstream via mpremote |
| [`tt_test_wrapper.py`](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/designs/_host/tt_test_wrapper.py) | Program + UART bridge (PTY) + run test |
| [`tt_pmod_wrapper.py`](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/designs/_host/tt_pmod_wrapper.py) | Program + release GPIOs + hand off to RPi GPIO test |

### Available Tests

| Test | Bitstream | Wrapper | What it verifies |
|------|-----------|---------|------------------|
| UART echo | [`uart/.../tt_fpga_platform.bin`](https://github.com/fpgas-online/fpgas.online-test-designs/tree/main/designs/uart/) | [`tt_test_wrapper.py`](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/designs/_host/tt_test_wrapper.py) | Serial TX/RX via RP2040 bridge |
| SPI Flash ID | [`spi-flash-id/.../tt_fpga_platform.bin`](https://github.com/fpgas-online/fpgas.online-test-designs/tree/main/designs/spi-flash-id/) | [`tt_test_wrapper.py`](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/designs/_host/tt_test_wrapper.py) | JEDEC ID readback from on-board flash |
| PMOD loopback | [`pmod-loopback/.../top.bin`](https://github.com/fpgas-online/fpgas.online-test-designs/tree/main/designs/pmod-loopback/) | [`tt_pmod_wrapper.py`](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/designs/_host/tt_pmod_wrapper.py) | GPIO inversion across wired pin pairs |
| PMOD pin ID | [`pmod-pin-id/.../top.bin`](https://github.com/fpgas-online/fpgas.online-test-designs/tree/main/designs/pmod-pin-id/) | [`tt_pmod_wrapper.py`](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/designs/_host/tt_pmod_wrapper.py) | UART TX on each GPIO pin |

The pin ID test and how to read its output are described on
[Pin identification](pin-id.md).

### Test Execution

Tests are orchestrated by the
[hardware verification script](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/verify_hardware.py),
which uploads the wrapper scripts and bitstreams to the RPi, then runs the
appropriate test:

The Pis are not routable from outside tweed, so reaching one to stop its daemon
means jumping through the gateway; the form is in
[Gateway: tweed](../sites/welland.md#gateway-tweed) on the Welland page.

```console
# <host-ip> is the current address of the board, from the Welland host table.
# The wrapper opens the serial port on the target host, so fpgas-tt has to be
# stopped -- and started again after, or the board drops off the public site.
$ ssh -o ProxyCommand='ssh -W %h:%p ansible@10.99.21.2' pi@<host-ip> sudo systemctl stop fpgas-tt
$ uv run python verify_hardware.py --board tt --host welland-pi33
$ ssh -o ProxyCommand='ssh -W %h:%p ansible@10.99.21.2' pi@<host-ip> sudo systemctl start fpgas-tt
```

:::{todo}
`verify_hardware.py`'s `HOSTS` table still carries the pre-2026-08-23 names and
`10.21.0.1xx` addresses (`welland-pi27` … `welland-pi33`); the boards are now
`pi-sw2-p33` … `pi-sw2-p36` at `10.21.2.33` … `10.21.2.36`. The table itself
is tracked on [Verifying a deployment](../setup/verification.md#running-the-hardware-tests);
what is specific to this board is that the wrapper also needs to stop and
restart the `fpgas-tt` daemon around a run
(see [Serial port ownership](#serial-port-ownership)).
:::

## Known Workarounds

### GPIOMap firmware mismatch

Observed on the firmware the boards shipped with: it loaded `GPIOMapTT04`, but
the TTDBv3 hardware uses different GPIO assignments, so `pin_indices()`
returned wrong pin numbers. **Workaround:** all host scripts hardcode the
correct GPIO pins (SPI: SCK=6, MOSI=3, SS=5, CRESET=1; UART: TX=GPIO20,
RX=GPIO37). Not re-checked since the 2026-08-23 reflash to SDK 3.1.0; the
hardcoded pins are correct either way.

### DemoBoard() hang on boot

The stock RP2350 (RP2040 on v2 boards) `main.py` calls `DemoBoard()` which
probes I2C and can
hang permanently, making the board unrecoverable without a physical reset.
The shipped `ttdbv3` firmware did exactly this on all four boards; SDK 3.1.0
boots cleanly and all four report `board present` as of 2026-09-03.

:::{warning}
**Do not install a no-op `main.py` on the deployed boards any more.**
The
[UART test wrapper](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/designs/_host/tt_test_wrapper.py)
still does this after each run as a workaround, but the public site (and the
`fpgas-tt` daemon's design list) depends on the SDK booting into
`DemoBoard()`, so a no-op `main.py` takes the board off
tinytapeout.fpgas.online until the SDK files are restored.
:::

If a board does hang, a PoE cycle of its switch port (the S3300 write community
is in gdoc2netcfg) resets it; the RP2's mass-storage bootloader path stalls on
Pi 3B+ hosts, so reflashing from a Pi 3B+ needs the PICOBOOT path rather than
MSC (no TT FPGA host is a Pi 3B+ today; all four are Pi 4).

### RP2350 PWM first-call bug

The first `PWM()` call on GPIO16 produces a stuck-HIGH output instead of
oscillation. The source text calls this an RP2040 bug, but the
[programming script](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/designs/_host/tt_fpga_program.py) that carries the
workaround labels it "Workaround for RP2350 PWM bug", and every deployed board
is an RP2350B. **Workaround:** deinit and recreate the PWM object:

```python
clk = PWM(Pin(16))
clk.deinit()
utime.sleep_ms(1)
clk = PWM(Pin(16))  # Second call oscillates correctly
```

### SPI kernel module conflict

RPi GPIO7-11 overlap with the SPI0 bus and conflict with PMOD HAT pins
(JA/JB pins 2-4). **Workaround:** unload `spidev` and `spi_bcm2835`
kernel modules before running PMOD tests.

```console
# Nothing else on the Pi may be using SPI0 -- this takes the bus away from it.
$ sudo rmmod spidev spi_bcm2835
```

## Pin mapping

Pin mapping for the TinyTapeout FPGA demo board v3 (TTDBv3) as connected in the
fpgas.online test infrastructure, measured on the four Welland hosts. The
spec-derived RP2350 map on
[Tiny Tapeout PMOD layouts](pmod/tinytapeout.md#rp2350-gpio-mapping-demo-board-v3-tt09)
and the measured mapping below agree: `ui_in[0:7]` on GPIO17–24, `uio[0:7]` on
GPIO25–32 and `uo_out[0:7]` on GPIO33–40, with each PMOD connector wired
straight through (bit 0 → pin 1, bit 7 → pin 10).

The TTDBv3 consists of two boards: the **FPGA breakout board** (iCE40UP5K + SPI
flash + clock oscillator) and the **TT demo PCB** (RP2350B controller, PMOD
headers, 7-segment display, DIP switches). The demo PCB carries three PMOD
headers, one per signal group — [Key Specifications](#key-specifications)
counts only the two the Tiny Tapeout PCB spec calls standard, and the third is
the bidirectional (`uio`) one.

Cabling, from the
[loopback test's board config](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/designs/pmod-loopback/host/test_pmod_loopback.py):
HAT **JC** → TT `ui_in`, HAT **JA** → TT `uo_out`, and (per the mapping below)
HAT **JB** → TT `uio`.

:::{note}
The shipped RP2350 firmware loaded `GPIOMapTT04` instead of `GPIOMapTTDBv3`,
returning incorrect GPIO numbers. All pin numbers in this section are the
correct TTDBv3 values (empirically confirmed), not the firmware-reported ones.
:::

### FPGA Device

| Parameter | Value                                  |
| --------- | -------------------------------------- |
| FPGA      | Lattice iCE40UP5K-SG48                 |
| Package   | SG48 (48-pin QFN)                      |
| Clock     | 50 MHz from RP2350 PWM (GPIO16)        |
| Block RAM | 30 EBR blocks (15 KB total)            |
| SPRAM     | 128 KB (4 × 32 KB)                     |
| Toolchain | icestorm / nextpnr-ice40 (open source) |

Source: the
[TT FPGA LiteX platform definition](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/designs/_shared/tt_fpga_platform.py)

### Programming Interface

The iCE40 is programmed via the RP2350 over USB CDC, not directly from the RPi.

| Parameter      | Value                                                 |
| -------------- | ----------------------------------------------------- |
| Interface      | RP2350 PIO SPI → iCE40 SPI configuration port         |
| USB device     | `/dev/ttyACM0` (MicroPython REPL)                     |
| USB VID:PID    | `2e8a:0005` (MicroPython Board in FS mode)            |
| Tool           | `python3 tt_fpga_program.py /dev/ttyACM0 <bitstream>` |
| Bitstream type | `.bin` (volatile SRAM load)                           |

#### RP2350 SPI programming pins

| Signal   | RP2350 GPIO | Function                  |
| -------- | ----------- | ------------------------- |
| SCK      | GPIO6       | SPI clock                 |
| MOSI     | GPIO3       | SPI data out              |
| SS       | GPIO5       | SPI chip select           |
| CRESET_B | GPIO1       | iCE40 configuration reset |

#### Programming flow

1. Upload bitstream to RP2350 filesystem via `mpremote`
2. Execute MicroPython script via raw REPL:
   - Assert CRESET_B low, then high (reset iCE40 into config mode)
   - Stream bitstream via PIO SPI at 1 MHz
   - Start 50 MHz PWM clock on GPIO16
3. Release all shared GPIOs to high-Z (input mode)

#### openFPGALoader support (work in progress)

Direct programming of the iCE40 via openFPGALoader (bypassing the MicroPython
REPL) is being developed. This would allow faster, more reliable programming
without needing `mpremote` or the RP2350 filesystem. The work is in the
[tt-fpga-support branch of mithro/openFPGALoader](https://github.com/mithro/openFPGALoader/tree/tt-fpga-support).

#### RP2350 considerations

- The boards run TT SDK 3.1.0 since 2026-08-23 (the shipped build hung in
  `DemoBoard()`); the public site depends on the SDK booting, so do **not**
  replace `main.py` with a no-op on deployed boards (see
  [Known Workarounds](#known-workarounds)).
- The `fpgas-tt` daemon owns `/dev/ttboard` (→ `/dev/ttyACM0`) on every deployed
  host; stop it before using `mpremote` directly (see
  [Serial port ownership](#serial-port-ownership)).
- If the RP2350 is unresponsive, USB power cycle via `uhubctl` or PoE reset can
  recover it.

### ui_in

8-bit input bus. The RPi drives these through the PMOD HAT; the FPGA reads them.

| Bit      | iCE40 Pin | RP2350 GPIO | PMOD HAT Pin | RPi GPIO | Verified |
| -------- | --------- | ----------- | ------------ | -------- | -------- |
| ui_in[0] | 13        | 17          | JC1          | 16       | pin-id   |
| ui_in[1] | 19        | 18          | JC2          | 14       | pin-id   |
| ui_in[2] | 18        | 19          | JC3          | 15       | pin-id   |
| ui_in[3] | 21        | 20          | JC4          | 17       | pin-id   |
| ui_in[4] | 23        | 21          | JC7          | 4        | pin-id   |
| ui_in[5] | 25        | 22          | JC8          | 12       | (*)      |
| ui_in[6] | 26        | 23          | JC9          | 5        | (*)      |
| ui_in[7] | 27        | 24          | JC10         | 6        | pin-id   |

(\*) ui_in[5] and ui_in[6] were not decoded (initial=0, decoder sync issue).
Positions inferred from the pattern — the JC connector pin numbering matches the
TT bit ordering straight through (bit 0 → pin 1, bit 7 → pin 10).

### uo_out

8-bit output bus. The FPGA drives these; the RPi reads them through the PMOD
HAT.

| Bit       | iCE40 Pin | RP2350 GPIO | PMOD HAT Pin | RPi GPIO | Verified |
| --------- | --------- | ----------- | ------------ | -------- | -------- |
| uo_out[0] | 38        | 33          | JA1          | 8        | pin-id   |
| uo_out[1] | 42        | 34          | JA2          | 10       | (**)     |
| uo_out[2] | 43        | 35          | JA3          | 9        | (**)     |
| uo_out[3] | 44        | 36          | JA4          | 11       | (**)     |
| uo_out[4] | 45        | 37          | JA7          | 19       | pin-id   |
| uo_out[5] | 46        | 38          | JA8          | 21       | pin-id   |
| uo_out[6] | 47        | 39          | JA9          | 20       | pin-id   |
| uo_out[7] | 48        | 40          | JA10         | 18       | pin-id   |

(\*\*) uo_out[1:3] are on JA pins 2-4 which share RPi GPIOs with JB pins 2-4
(see the JA/JB pin sharing warning under [uio](#uio) below).
The pin-id decode on these GPIOs is corrupted by JA/JB contention. Positions
inferred from the pattern — the JA connector pin numbering matches the TT bit
ordering straight through (bit 0 → pin 1, bit 7 → pin 10).

:::{todo}
**Two live sources disagree about this permutation, and neither is stale.** The
tables above are the measured TTDBv3 mapping. The
[hardware verification walkthrough](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/docs/verify-hardware.md) and the `tt` entry in the
[loopback test's board config](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/designs/pmod-loopback/host/test_pmod_loopback.py) on `main` both carry a different one:

```python
"tt": {
    #   ui_in[0:7] drive GPIOs: JC10, JC8, JC1, JC9, JC4, JC7, JC2, JC3
    #   uo_out[0:7] read GPIOs: JA10, JA8, JA1, JA9, JA4, JA7, JA2, JA3
    "drive_pins": [6, 12, 16, 5, 17, 4, 14, 15],
    "read_pins": [18, 21, 8, 20, 11, 19, 10, 9],
```

The iCE40 pin numbers agree in every row, and both mappings use the same eight
JC pins for `ui_in` and the same eight JA pins for `uo_out` — only the bit
order differs. Under the tables above `ui_in[0]` is JC1/GPIO16 and `uo_out[0]`
is JA1/GPIO8; under `test_pmod_loopback.py` `ui_in[0]` is JC10/GPIO6 and
`uo_out[0]` is JA10/GPIO18.

`verify-hardware.md` adds a **third, separately wrong** set of numbers. Only its
GPIO column agrees with the loopback config; its PMOD HAT port labels
(`ui_in` on JA1/JA7/JA8/JB1/JC1/JC3/JC4/JC9, `uo_out` on
JC2/JA10/JB8/JA9/JB2/JA3/JB4/JB3) contradict
[Raspberry Pi PMOD HAT](pmod/rpi-hat.md) in every row — JA1 is GPIO8 there, not
GPIO6; JA7 is GPIO19, not GPIO12; JB1 is GPIO7, not GPIO5. The GPIOs it lists
for `ui_in` are in fact all JC pins and the ones it lists for `uo_out` are all
JA pins, exactly as `test_pmod_loopback.py` labels them, so the port column in
`verify-hardware.md` can be discarded outright; the disagreement worth
resolving is the bit order.

**The loopback test cannot arbitrate this.** It drives `drive_pins` and reads
`read_pins` position by position, and the FPGA returns `uo_out = ~ui_in` bit
for bit, so any permutation that is consistent between the two lists passes.
The "empirically confirmed (4-transition verification on pi33)" claim therefore
confirms that the cables are connected, not that the bit order is right.

**The pin-ID design does arbitrate.** It transmits a distinct identifier on
each pin, so the decode names the bit at each GPIO. Run `designs/pmod-pin-id`
through
[`tt_pmod_wrapper.py`](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/designs/_host/tt_pmod_wrapper.py) on `pi-sw2-p33`,
read the decode (see [Pin identification](pin-id.md)), then correct whichever
of the three copies loses: the tables on this page, the mapping in
`verify-hardware.md`, or `drive_pins`/`read_pins` in `test_pmod_loopback.py`.
Everything on this page that quotes RPi GPIO numbers — the
[UART Interface](#uart-interface) rows and the loopback pre-test note — depends
on the answer.
:::

### uio

8-bit bidirectional bus. Connected through the TT board's third PMOD header to
PMOD HAT port JB.

| Bit    | iCE40 Pin | RP2350 GPIO | PMOD HAT Pin | RPi GPIO |
| ------ | --------- | ----------- | ------------ | -------- |
| uio[0] | 2         | 25          | JB1          | 7        |
| uio[1] | 4         | 26          | JB2          | 10       |
| uio[2] | 3         | 27          | JB3          | 9        |
| uio[3] | 6         | 28          | JB4          | 11       |
| uio[4] | 9         | 29          | JB7          | 26       |
| uio[5] | 10        | 30          | JB8          | 13       |
| uio[6] | 11        | 31          | JB9          | 3        |
| uio[7] | 12        | 32          | JB10         | 2        |

RP2350 GPIO numbers follow the sequential pattern (ui_in=17-24, uio=25-32,
uo_out=33-40).

:::{warning}
**JA/JB pin sharing conflict.** HAT JB pins 2-4 and HAT JA pins 2-4 are the
[same RPi GPIO lines](pmod/rpi-hat.md) (GPIO10, GPIO9, GPIO11 — the shared SPI0
bus). This means 3 uo_out signals and 3 uio signals are electrically connected
at the RPi side:

| RPi GPIO | HAT JA Pin | TT Signal (uo_out) | HAT JB Pin | TT Signal (uio) | Conflict |
| -------- | ---------- | ------------------ | ---------- | --------------- | -------- |
| GPIO10   | JA2        | uo_out[1]          | JB2        | uio[1]          | Shorted  |
| GPIO9    | JA3        | uo_out[2]          | JB3        | uio[2]          | Shorted  |
| GPIO11   | JA4        | uo_out[3]          | JB4        | uio[3]          | Shorted  |

When the FPGA drives uo_out[1,2,3] and uio[1,2,3] simultaneously with different
values, the two FPGA outputs will fight each other through the shared RPi GPIO.
:::

That conflict has several consequences:

- **GPIO loopback test**: Works because the test only drives ui_in (JC) and
  reads uo_out (JA). The uio pins (JB) are not driven during this test, so no
  conflict occurs.
- **Bidirectional I/O test**: Cannot independently test uio[1,2,3] because they
  are shorted to uo_out[1,2,3] respectively. If the FPGA drives both buses, the
  conflicting outputs may cause contention or incorrect readings.
- **SPI kernel modules**: Must be unloaded (`rmmod spidev spi_bcm2835`) since
  GPIO7-11 overlap with HAT JA pins 1-4 and JB pins 1-4.

The 5 unaffected uio bits (uio[0], uio[4:7]) on JB pins 1 and 7-10 use unique
RPi GPIOs and work correctly.

### UART Interface

The TT standard UART uses ui_in[3] (RX) and uo_out[4] (TX), following the
[TinyTapeout UART0 convention](pmod/tinytapeout.md#uart-via-rp2040rp2350-built-in-usb-bridge-no-pmod-needed).

| Signal                    | iCE40 Pin | TT Signal | RP2350 GPIO | PMOD HAT Pin | RPi GPIO |
| ------------------------- | --------- | --------- | ----------- | ------------ | -------- |
| Serial RX (FPGA receives) | 21        | ui_in[3]  | GPIO20      | JC9          | 5        |
| Serial TX (FPGA sends)    | 45        | uo_out[4] | GPIO37      | JA4          | 11       |

:::{note}
These GPIO numbers follow the mapping in `verify-hardware.md` and
`test_pmod_loopback.py`, which differs from the measured tables above; see
the todo under [Pin mapping](#pin-mapping).
:::

Under the tables above the same two signals land on JC4/GPIO17 and JA7/GPIO19
instead. The iCE40 pins (21, 45), the TT signals and the RP2350 GPIOs (20, 37)
are the same either way; only the PMOD HAT pin and RPi GPIO move.

#### Access via the RP2350 USB bridge (recommended)

The RP2350 connects to the same FPGA pins via GPIO20/GPIO37 and can bridge UART
data to the USB CDC serial port (`/dev/ttyACM0`). This is the recommended
approach since:

- RPi GPIO5/11 are **not hardware UART pins** — the BCM2711 has no UART
  peripheral assignable to this GPIO pair. If the measured tables are the right
  ones the pair is GPIO17/19 instead, which is no better: GPIO17 is RTS0 and
  GPIO19 is PCM_FS, so neither is a UART data pin. The conclusion holds
  whichever mapping wins, but the specific pin argument below has to be redone
  against the surviving one.
- The NFS boot image has no device tree overlay files, and the root filesystem
  is read-only.
- Software bit-bang UART at 115200 baud is unreliable under a non-RT Linux
  kernel.
- The RP2350 has hardware UART peripherals that can be configured for these
  pins.

| Parameter | Value                                                   |
| --------- | ------------------------------------------------------- |
| Device    | `/dev/ttyACM0` (via RP2350 USB CDC)                     |
| Baud rate | 115200                                                  |
| Test args | `--port /dev/ttyACM0 --board tt --skip-banner`          |
| Requires  | RP2350 firmware configured to bridge UART0 on GPIO20/37 |

#### Access via RPi GPIO (not currently feasible)

RPi GPIO5 and GPIO11 are not assignable to any BCM2711 hardware UART as a pair.
The BCM2711 UART3 uses GPIO4/5 (TX/RX), and no UART uses GPIO11 for TX. Without
hardware UART support, these pins cannot reliably serve as a serial port at
115200 baud.

### PMOD Loopback

The GPIO loopback test uses all 8 ui_in pins (drive) and all 8 uo_out pins
(read). The FPGA computes `uo_out = ~ui_in`.

All 8 pairs are **empirically confirmed** (4-transition verification on pi33 —
now `pi-sw2-p36`). See the ui_in and uo_out tables above for the full mapping.

Before running the test:

- `rmmod spidev spi_bcm2835` — SPI kernel modules claim GPIO7-11 (overlap with
  HAT JA pins 1-4 and JB pin 1, used by uo_out[2], uo_out[4], uo_out[6],
  uo_out[7])
- RP2350 GPIOs must be released to high-Z after FPGA programming (the
  programming wrapper handles this automatically)

:::{note}
These GPIO numbers follow the mapping in `verify-hardware.md` and
`test_pmod_loopback.py`, which differs from the measured tables above; see
the todo under [Pin mapping](#pin-mapping).
:::

Under the tables above GPIO7-11 carry JB1/`uio[0]` and JA1-4/`uo_out[0:3]`
instead. Either way the same five RPi GPIOs are contended and the `rmmod` is
required; only the names of the signals on them change.

### SPI Flash

Dedicated iCE40 SPI pins on the FPGA breakout board (not shared with PMOD).

| Signal | iCE40 Pin |
| ------ | --------- |
| CS_N   | 16        |
| CLK    | 15        |
| MISO   | 17        |
| MOSI   | 14        |

### 7-segment display pins

The TT demo PCB has a 7-segment LED display connected to uo_out[0:6]. These
share the same PMOD traces — when the RPi is driving GPIO tests, the display
reflects the test patterns.

| Segment | TT Signal | iCE40 Pin |
| ------- | --------- | --------- |
| a       | uo_out[0] | 38        |
| b       | uo_out[1] | 42        |
| c       | uo_out[2] | 43        |
| d       | uo_out[3] | 44        |
| e       | uo_out[4] | 45        |
| f       | uo_out[5] | 46        |
| g       | uo_out[6] | 47        |

### Other Signals

| Signal     | iCE40 Pin | Function                            |
| ---------- | --------- | ----------------------------------- |
| clk_rp2040 | 20        | 50 MHz clock from RP2350 PWM GPIO16 |
| rst_n      | 37        | Reset (active low)                  |
| RGB LED R  | 39        | Accent LED (active low)             |
| RGB LED G  | 40        | Accent LED (active low)             |
| RGB LED B  | 41        | Accent LED (active low)             |

## References

- TinyTapeout Demo PCB design: <https://github.com/TinyTapeout/tt-demo-pcb>
- TinyTapeout PCB specifications: <https://tinytapeout.com/specs/pcb/>
- TinyTapeout FPGA Breakout Guide: <https://tinytapeout.com/guides/fpga-breakout/>
- TT FPGA Demo repository: <https://github.com/efabless/tt-fpga-demo>
- TinyTapeout main site: <https://tinytapeout.com>
- [TT FPGA LiteX platform definition](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/designs/_shared/tt_fpga_platform.py)
- PMOD Interface Specification: [PMOD interface](pmod/index.md)
- TinyTapeout PMOD Connector Standards:
  [Tiny Tapeout PMOD layouts](pmod/tinytapeout.md)
- PMOD HAT Adapter (RPi): [Raspberry Pi PMOD HAT](pmod/rpi-hat.md)
