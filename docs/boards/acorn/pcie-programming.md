# Acorn PCIe programming and multiboot

How to program the Acorn CLE-215+ / LiteFury FPGA via PCIe, and how to use
Xilinx 7-series multiboot for safe recovery from bad bitstreams. See [SQRL Acorn
and LiteFury](index.md) for the board itself and [Acorn wiring](wiring.md) for
the GPIO JTAG wiring every JTAG command below assumes.

## Programming paths

The Acorn has two working programming paths:

| Method | Speed | Persistent? | Requires | Notes |
|--------|-------|-------------|----------|-------|
| GPIO JTAG → SRAM | ~16 s for a 1.6 MB XC7A200T bitstream (bit-banged libgpiod, measured 2026-08-31) | No (lost on power cycle) | RPi GPIO wiring | Works with any/no bitstream loaded. **Detach the PCIe endpoint first** (below) |
| PCIe → SPI Flash | Fast (~seconds) | Yes | Working LiteX PCIe bitstream | Requires PCIe-capable bitstream already running |

### Detach the PCIe endpoint before any JTAG reconfiguration

:::{warning}
**Detach the PCIe endpoint before any JTAG reconfiguration.** Reconfiguring the
FPGA over JTAG while its endpoint is enumerated is a PCIe surprise removal. The
Pi 5's BCM2712 root complex does not survive it: on
2026-08-31 a JTAG load on pi-sw2-p47 killed the host outright ("Connection
closed by remote host", Pi rebooted). With the endpoint removed first, the same
load completed cleanly and the host was unaffected.
:::

```console
# Detach the endpoint first — before openFPGALoader
$ echo 1 | sudo tee /sys/bus/pci/devices/0001:01:00.0/remove
# ... load ...
# Restore it afterwards, or just reboot
$ echo 1 | sudo tee /sys/bus/pci/rescan
```

Every Welland Pi 5 host uses `0001:01:00.0`; the same rule and the same command
are on the site page under [PCIe and JTAG
interact](../../sites/welland.md#pcie-and-jtag-interact). At PS1 the address
differs per host — `0000:01:00.0` on pi14, `0001:01:00.0` on pi16 and pi20 — so
read it from the `PCIe Bus` column in [Compute
blades](../../sites/ps1.md#compute-blades).

Every `openFPGALoader … <bitstream>` invocation on this page assumes that
detach has been done. Read-only operations (`--detect`, and `--read-dna` /
`--read-xadc` on openFPGALoader ≥ 0.13) do not reconfigure the device and are
safe on a live endpoint.

### Prebuilt Vivado bitstreams

There is no need to build locally. GitHub release
[`vivado-bitstreams-v0.0-496-gf162f60`](https://github.com/fpgas-online/fpgas.online-test-designs/releases/tag/vivado-bitstreams-v0.0-496-gf162f60)
(Vivado 2025.2, published 2026-04-17) carries every test design × Acorn variant
(`cle-101`, `cle-215`, `cle-215p`). Each comes as plain `.bit`/`.bin` plus the
`_fallback` and `_operational` multiboot variants described below, alongside a
`manifest.json` with a SHA-256 per file. For the Welland CLE-215+ boards use the
`*_acorn-cle-215p_*` files; their `.bit` header reads `7a200tfbg484`, matching
IDCODE `0x3636093`.

```console
# The multiboot pair for a Welland CLE-215+ board.
# .bit is for a JTAG SRAM load, .bin for a flash write.
$ gh release download vivado-bitstreams-v0.0-496-gf162f60 \
      --repo fpgas-online/fpgas.online-test-designs \
      --pattern 'pcie-enumeration_acorn-cle-215p_*_fallback.*' \
      --pattern 'pcie-enumeration_acorn-cle-215p_*_operational.*'
```

:::{note}
The `pmod-pin-id` design in that release predates [test-designs
PR #10](https://github.com/fpgas-online/fpgas.online-test-designs/pull/10)
(2026-08-31), which gave the Acorn pin-ID design a real clock; the release build
of *that one design* configures but never toggles a pin. The fixed design must
be rebuilt with Vivado until a newer release is cut.
:::

:::{todo}
Two pages disagree about that one asset. [Measured P2 wiring on Raspberry Pi 5
hosts](wiring.md#measured-p2-wiring-on-raspberry-pi-5-hosts) says the survey
was read off with "the fixed pin-ID bitstream" and names exactly this release
asset, `pmod-pin-id_acorn-cle-215p_vivado-vivado_sqrl_acorn.bit`. This section
says that asset predates PR #10 and never toggles a pin. Either the release does
carry the fixed design, or the survey used a locally rebuilt file with the same
name. Confirm which before anyone downloads that asset expecting it to work.
:::

### Flash-via-JTAG is not currently working

**`openFPGALoader --write-flash` does not currently work over the GPIO JTAG
wiring** — the open-source spiOverJtag bridge never toggles CCLK after
configuration. Over that path JTAG can only load bitstreams into volatile SRAM.
That is what makes the recovery strategy below what it is.

### Current flash state

What each board's flash actually holds is on the site pages. The [SQRL Acorn
CLE-215+](../../sites/welland.md#sqrl-acorn-cle-215) table at Welland carries
the `lspci -nn` reading for all six boards, taken 2026-09-03. Five of them still
boot the factory SQRL cryptocurrency mining firmware `1e24:021f`; only
pi-sw2-p44 has a LiteX/Vivado design `10ee:7011` in flash.

Factory firmware characteristics:

- PCI vendor:device `1e24:021f` (Squirrels Research Labs)
- BAR0: 128 KB — repeating mining parameter pattern, no LiteX CSRs
- **Not a LiteX design** — `litepcie_util` cannot communicate with this firmware

To enable PCIe→Flash programming, the factory firmware must be replaced with a
**LiteX Acorn PCIe SoC** bitstream (vendor `10ee`) that includes PCIe+DMA, SPI
Flash controller, and ICAP. Building this bitstream requires **Vivado** (the
XC7A200T is too large for the openXC7 open source toolchain); the prebuilt
release above already contains
`pcie-enumeration_acorn-cle-215p_*_{fallback,operational}.bin`.

The litepcie kernel module and `litepcie_util` were built on the host then
called pi2 (now pi-sw2-p48) — they just need a matching LiteX bitstream to bind
to. Because the Pi root is `overlayroot=tmpfs`, anything built on a Pi is lost
at reboot unless it is baked into the NFS root.

What that state means for programming, on any board:

- JTAG can always load a bitstream into SRAM (volatile), but it is lost on power cycle
- The only way to write to SPI flash (persistent) is via PCIe using `litepcie_util`
- PCIe→Flash requires a LiteX bitstream (not the factory SQRL firmware)
- The golden bitstream at flash address 0x0 is **irreplaceable without PCIe** — if it is corrupted, recovery requires the SRAM bootstrap procedure (see below)

The longer-term intent (Tim, 2026-08-31) is to flash every board with a LiteX
design carrying PCIe + UART + GPIO that supports FPGA updates over PCIe, and to
add JTAG/PCIe/UART/GPIO self-verification to the Pi boot checks.

## SPI flash layout

The Acorn has a Spansion S25FL256S (256 Mbit = 32 MB) quad-SPI NOR flash.

```text
┌──────────────────────────────────────────────────┐
│ 0x00000000  Fallback bitstream (golden image)    │  ~4 MB
│             - Always boots first                 │
│             - Sets NEXT_CONFIG_ADDR = 0x400000   │
│             - Has PCIe + LiteX + SPI Flash       │
│             - PROTECTED — see safety rules       │
├──────────────────────────────────────────────────┤
│ 0x00400000  Operational bitstream (updatable)    │  ~4 MB
│             - Chain-loaded by fallback           │
│             - Has TIMER_CFG watchdog             │
│             - Updated via PCIe (litepcie_util)   │
│             - If broken, watchdog → fallback     │
├──────────────────────────────────────────────────┤
│ 0x00800000  Free space                           │  ~24 MB
│            (available for data/additional images)│
└──────────────────────────────────────────────────┘
```

## Multiboot mechanism

### How it works

1. **Power-on**: FPGA loads fallback bitstream from flash address 0x0
2. **Chain-load**: Fallback's `NEXT_CONFIG_ADDR` (0x400000) tells the FPGA to immediately load the operational bitstream
3. **Operational runs**: The operational bitstream runs the user's design with PCIe, UART, etc.
4. **If operational fails**: The `TIMER_CFG` watchdog detects configuration failure and triggers an automatic fallback to address 0x0
5. **Fallback recovers**: The golden image boots, PCIe comes up, and the host can reprogram the operational slot

### Watchdog timer

The operational bitstream must include `CONFIGFALLBACK` and `TIMER_CFG`
properties:

- `TIMER_CFG 0x0001fbd0` — watchdog timeout that triggers fallback if configuration stalls
- `CONFIGFALLBACK Enable` — enables the fallback mechanism

If the operational bitstream hangs during configuration (e.g. bad bitstream
data), the watchdog fires and the FPGA ignores `WBSTAR`, rebooting from address
0x0 (the golden image).

### ICAPE2 warm reboot

The ICAPE2 (Internal Configuration Access Port) primitive allows
software-triggered reconfiguration without a power cycle:

1. Write the target flash address to the `WBSTAR` (Warm Boot Start Address) register
2. Write the `IPROG` command to the ICAPE2 CMD register
3. The FPGA immediately begins reconfiguration from the specified address
4. PCIe link goes down momentarily and retrains after the new bitstream loads

LiteX exposes this via the `ICAP` core:

```python
from litex.soc.cores.icap import ICAP
self.icap = ICAP()
self.icap.add_reload()
```

## Programming via PCIe

:::{danger}
**Four of the nine deployed Acorns must not be flashed over PCIe today.**
pi-sw2-p43 and pi-sw2-p44 at Welland scan an empty JTAG chain, and PS1's pi14
and pi16 do not answer JTAG at all (2026-08-31). If a flash write leaves a bad
golden image on any of those four, nothing can rescue it — see [safety
rules](#safety-rules).

That leaves no Welland Acorn that can safely be flashed over PCIe as of
2026-09-03: pi-sw2-p44 is the only one running a LiteX design, and it is one of
the boards with no JTAG recovery. The other five cannot be reached over PCIe at
all until a LiteX bitstream is in their flash.
:::

### Prerequisites

- A working LiteX bitstream with PCIe support must already be running on the FPGA
- The `litepcie` kernel module must be loaded on the host
- `litepcie_util` must be built (auto-generated by LiteX build)

### Write operational bitstream

```console
# Write new operational bitstream to flash at 0x400000
$ litepcie_util flash_write operational.bin 0x400000
```

### Reload from flash

```console
# Trigger ICAP warm reboot — FPGA reloads from flash
$ litepcie_util flash_reload
```

After reload, the PCIe link retrains. The host must rescan the PCIe bus:

```console
$ echo 1 > /sys/bus/pci/rescan
```

### Full update sequence

```console
# 1. Write new operational bitstream
$ litepcie_util flash_write new_design.bin 0x400000
# 2. Trigger warm reboot
$ litepcie_util flash_reload
# 3. Wait for PCIe link to retrain (~2-5 seconds)
$ sleep 5
# 4. Rescan PCIe bus
$ echo 1 > /sys/bus/pci/rescan
# 5. Verify new bitstream is running
$ lspci -d 10ee: -vvv
```

## Recovery from bad bitstream

### Automatic recovery (watchdog) — operational bitstream bad

If the operational bitstream at 0x400000 is corrupted or fails to configure:

1. FPGA attempts to load operational bitstream
2. Configuration stalls or produces errors
3. `TIMER_CFG` watchdog fires
4. FPGA ignores `WBSTAR` and reloads from address 0x0 (fallback)
5. Golden image boots, PCIe comes up
6. Host can reprogram operational slot via `litepcie_util flash_write`

**No manual intervention required** — the system self-recovers.

### SRAM bootstrap recovery — golden bitstream bad

If the golden bitstream at address 0x0 is corrupted, PCIe will not come up on
boot and `litepcie_util` cannot be used. Since flash-via-JTAG is not currently
working, recovery uses a **two-stage SRAM bootstrap**.

You need the golden bitstream in both forms: `.bit` for the JTAG SRAM load, and
`.bin` for the flash write. Both are in the release described under [prebuilt
Vivado bitstreams](#prebuilt-vivado-bitstreams) —
`pcie-enumeration_acorn-cle-215p_*_fallback.*` is the golden image and
`pcie-enumeration_acorn-cle-215p_*_operational.*` its operational partner.

:::{warning}
Files staged under `/home/pi` do not survive a reboot: the Pi root is a
read-only NFS export with a tmpfs overlay (`overlayroot=tmpfs`), so a bitstream
that loaded a minute ago fails with `Open file … FAIL` after a reboot. Re-upload
it before each attempt; see [Acorn
wiring](wiring.md#step-2-test-jtag-programming).
:::

:::{note}
Step 0, the PCIe rescan and `lspci` check in step 2, and the expected outputs
were added on port, 2026-09-03; the source omitted them. They follow [Step
2](wiring.md#step-2-test-jtag-programming) and [Step
5](wiring.md#step-5-test-pcie-bitstream) of the wiring page.
:::

0. **Prove JTAG answers before touching anything.** `--detect` is read-only and
   safe on a live endpoint:

   ```console
   # Pi 5 with openFPGALoader 0.10.0: the 40-pin header is /dev/gpiochip15
   $ sudo ln -sfn /dev/gpiochip15 /dev/gpiochip0
   $ openFPGALoader --cable libgpiod --pins 10:9:11:8 --detect
   # Expected on a CLE-215+: idcode 0x3636093 (XC7A200T)
   # PS1 Compute Blades: --pins 2:3:4:14
   ```

   That IDCODE is the XC7A200T on a CLE-215+. A CLE-101 or LiteFury carries an
   XC7A100T and reports a different IDCODE; read the value off `--detect` on the
   board in hand rather than expecting `0x3636093` there.

   `found 0 devices` means this board cannot be rescued over JTAG at all. Stop
   here and read safety rule 4.

1. **Load a PCIe-capable bitstream to SRAM via JTAG** (volatile — lost on power cycle):

   ```console
   # Detach anything that is enumerated before reconfiguring. With a corrupt
   # golden image nothing enumerates, so this reports "No such file or
   # directory" — that is expected, carry on.
   $ echo 1 | sudo tee /sys/bus/pci/devices/0001:01:00.0/remove
   # Pi 0-4 hosts only. Not needed on the Pi 5 fleet, where GPIO8-11 are
   # unclaimed even with the modules loaded, but harmless there.
   $ sudo rmmod spidev spi_bcm2835
   # Pi 5 with openFPGALoader 0.10.0
   $ sudo ln -sfn /dev/gpiochip15 /dev/gpiochip0
   $ openFPGALoader --cable libgpiod --pins 10:9:11:8 golden.bit
   # Expected: about 16 s for a 1.6 MB XC7A200T bitstream, then "Done"
   # PS1 Compute Blades: --pins 2:3:4:14
   ```

2. **Bring the endpoint back and confirm the SRAM-loaded design enumerated**,
   then load the litepcie kernel module:

   ```console
   $ echo 1 | sudo tee /sys/bus/pci/rescan
   $ lspci -nn -s 0001:01:00.0
   # Expected: Xilinx Corporation 7-Series FPGA Hard PCIe block (AXI/debug) [10ee:7011]
   $ modprobe litepcie
   $ lspci -k -s 0001:01:00.0
   # Expected: Kernel driver in use: litepcie
   ```

   Still the SQRL ID `1e24:021f`, or no device at all, means the JTAG load did
   not take — go back to step 1 rather than writing flash.

3. **Write a new golden image to flash at address 0x0 via PCIe**:

   ```console
   $ litepcie_util flash_write golden.bin 0x0
   # Expected: the write and verify both report success before you continue
   ```

4. **Write the operational bitstream to 0x400000**:

   ```console
   $ litepcie_util flash_write operational.bin 0x400000
   ```

5. **Power cycle** the board. The FPGA boots from the new golden image in flash,
   chain-loads operational, and PCIe comes up persistently. Confirm with
   `lspci -nn -s 0001:01:00.0` afterwards: `10ee:7011` again, this time without
   any JTAG load.

   `sudo reboot` is not necessarily enough — it need not drop the M.2 rail, so
   the FPGA can keep its configuration across it. The reliable power cycle is a
   PoE cycle of the host's switch port, which takes a Pi 5 more than 90 s to
   come back; see [SQRL Acorn
   CLE-215+](../../sites/welland.md#sqrl-acorn-cle-215).

:::{warning}
Between steps 1 and 5 the board **must not lose power**. The SRAM-loaded
bitstream is volatile — if power is lost before step 3 completes, the flash
still has the corrupted golden image and you must restart from step 1.
:::

### Recovery summary

| Scenario | Golden OK? | Operational OK? | Recovery Method | Automatic? |
|----------|-----------|----------------|-----------------|------------|
| Bad operational | Yes | No | Watchdog fallback to golden, reprogram via PCIe | Yes |
| Bad operational (PCIe broken) | Yes | No | Golden boots, reprogram via PCIe | Yes |
| Bad golden | No | — | SRAM bootstrap: JTAG→SRAM, then PCIe→Flash | No (manual) |
| Bad golden + no JTAG wiring | No | — | **Bricked** — requires physical JTAG reconnection | No |

:::{danger}
The last row is not hypothetical. Four of the nine deployed Acorns are in it
today (2026-08-31): pi-sw2-p43 and pi-sw2-p44 at Welland scan an empty JTAG
chain, and PS1's pi14 and pi16 do not answer JTAG at all. A bad golden image on
any of those four bricks the board until its JTAG wiring is repaired.
:::

## Initial setup (new board)

Since flash-via-JTAG is not working, initial multiboot setup uses the SRAM
bootstrap method.

:::{note}
The `gpiochip0` symlink, the PCIe rescan and the `lspci` checks below were added
on port, 2026-09-03; the source omitted them. They follow [Step
2](wiring.md#step-2-test-jtag-programming) and [Step
5](wiring.md#step-5-test-pcie-bitstream) of the wiring page.
:::

1. **Build a golden bitstream** with Vivado (LiteX SoC with PCIe + SPI Flash + ICAP + NEXT_CONFIG_ADDR)

2. **Load golden to SRAM via JTAG** (volatile):

   ```console
   # Detach the factory endpoint before reconfiguring
   $ echo 1 | sudo tee /sys/bus/pci/devices/0001:01:00.0/remove
   # Free the SPI0 pins: Pi 0-4 hosts only. Not needed on the Pi 5 fleet, where
   # GPIO8-11 are unclaimed even with the modules loaded, but harmless there.
   $ sudo rmmod spidev spi_bcm2835
   # Pi 5 with openFPGALoader 0.10.0
   $ sudo ln -sfn /dev/gpiochip15 /dev/gpiochip0
   $ openFPGALoader --cable libgpiod --pins 10:9:11:8 golden.bit
   # Expected: about 16 s for a 1.6 MB XC7A200T bitstream, then "Done"
   # PS1 Compute Blades: --pins 2:3:4:14
   ```

3. **PCIe comes up**. Rescan, confirm the design enumerated, then load the
   kernel module and write golden to flash:

   ```console
   $ echo 1 | sudo tee /sys/bus/pci/rescan
   $ lspci -nn -s 0001:01:00.0
   # Expected: Xilinx Corporation 7-Series FPGA Hard PCIe block (AXI/debug) [10ee:7011]
   $ modprobe litepcie
   $ litepcie_util flash_write golden.bin 0x0
   ```

4. **Write operational bitstream** to flash:

   ```console
   $ litepcie_util flash_write operational.bin 0x400000
   ```

5. **Power cycle** — golden boots from flash, chain-loads operational, PCIe
   comes up persistently. Use a PoE cycle of the switch port, not `sudo reboot`,
   for the reason given in the SRAM bootstrap above.

6. **Verify** multiboot works by intentionally writing a bad operational image, confirming watchdog fallback, then reprogramming:

   :::{warning}
   This step deliberately writes random data to flash. Check the address on
   every command: `0x400000` is the operational slot and is recoverable,
   `0x0` is the golden image and is not. Do it only on a board whose JTAG
   answers, so the SRAM bootstrap is available if it goes wrong.
   :::

   ```console
   # Write garbage to the operational slot — never to 0x0
   $ dd if=/dev/urandom bs=1M count=4 of=/tmp/bad.bin
   $ litepcie_util flash_write /tmp/bad.bin 0x400000
   $ litepcie_util flash_reload
   # Wait — watchdog should fall back to golden
   $ sleep 10
   $ echo 1 > /sys/bus/pci/rescan
   # Verify golden is running (check ident string via UART), then
   # reprogram a good operational image
   $ litepcie_util flash_write operational.bin 0x400000
   $ litepcie_util flash_reload
   ```

From this point on, operational updates only need `litepcie_util flash_write` +
`flash_reload`.

## Generating multiboot bitstreams

### Fallback (golden) bitstream

The fallback bitstream must set `NEXT_CONFIG_ADDR` to point to the operational
slot.

Vivado TCL:

```tcl
set_property BITSTREAM.CONFIG.NEXT_CONFIG_ADDR 0x00400000 [current_design]
write_bitstream -force golden.bit
write_cfgmem -force -format bin -interface spix4 -size 16 -loadbit "up 0x0 golden.bit" -file golden.bin
```

LiteX (openXC7): the openXC7 toolchain does not currently support
`NEXT_CONFIG_ADDR` bitstream properties. Multiboot golden bitstreams must be
built with Vivado. This is acceptable since the golden image is written once and
rarely updated.

### Operational bitstream

The operational bitstream must enable the watchdog timer and fallback.

Vivado TCL:

```tcl
set_property BITSTREAM.CONFIG.TIMER_CFG 0x0001fbd0 [current_design]
set_property BITSTREAM.CONFIG.CONFIGFALLBACK Enable [current_design]
write_bitstream -force operational.bit
write_cfgmem -force -format bin -interface spix4 -size 16 -loadbit "up 0x0 operational.bit" -file operational.bin
```

## Safety rules

:::{danger}
**NEVER write to flash address 0x0 via PCIe during normal operation.** The
golden image at 0x0 is the recovery mechanism. Overwrite it and the only way
back is the SRAM bootstrap over JTAG — and on a board whose JTAG does not
answer, there is no way back at all. Write to 0x0 only during initial setup or
golden recovery. A wrapper script should validate the target address; no such
script exists today.
:::

All six rules:

:::{warning}
1. **NEVER write to flash address 0x0 via PCIe during normal operation** — see
   the box above.

2. **Always use 0x400000 for operational updates:**

   ```console
   # CORRECT — writes to the operational slot
   $ litepcie_util flash_write design.bin 0x400000
   # DANGEROUS — overwrites the golden image, DO NOT DO THIS
   # litepcie_util flash_write design.bin 0x0
   ```

3. **Always test new bitstreams via JTAG SRAM load first** before writing to
   flash. This validates the design without touching flash:

   ```console
   # Detach the endpoint first
   $ echo 1 | sudo tee /sys/bus/pci/devices/0001:01:00.0/remove
   # Pi 5 with openFPGALoader 0.10.0
   $ sudo ln -sfn /dev/gpiochip15 /dev/gpiochip0
   $ openFPGALoader --cable libgpiod --pins 10:9:11:8 new_design.bit
   # PS1 Compute Blades: --pins 2:3:4:14
   # Bring the endpoint back and check what enumerated
   $ echo 1 | sudo tee /sys/bus/pci/rescan
   $ lspci -nn -s 0001:01:00.0
   # Expected: the loaded design; a LiteX PCIe design shows [10ee:7011]
   # Test it works, then write to flash via PCIe
   ```

   The rescan and `lspci` check were added on port, 2026-09-03; the source
   stopped at the load.

4. **Keep JTAG wiring connected** on all deployed Acorn boards. Without JTAG, a
   corrupted golden image means the board is **permanently bricked** until JTAG
   is reconnected. As of 2026-08-31 pi-sw2-p43 and pi-sw2-p44 scan an empty JTAG
   chain and PS1's pi14/pi16 do not answer JTAG at all — those four are in
   exactly this state and must not be flashed over PCIe until JTAG is restored.

5. **Detach the PCIe endpoint before every JTAG load** (see [detach the PCIe
   endpoint before any JTAG
   reconfiguration](#detach-the-pcie-endpoint-before-any-jtag-reconfiguration)).
   A Pi 5 host crashes otherwise.

6. **The golden bitstream must be a minimal LiteX SoC** with only PCIe, SPI
   Flash, ICAP, and UART — no complex user logic that might fail.
:::

## Future: flash-via-JTAG support

When openFPGALoader gains working `--write-flash` support for the Acorn (via
GPIO JTAG), the recovery story simplifies significantly:

- Initial setup becomes a single JTAG flash write instead of the SRAM bootstrap
- Golden recovery no longer requires a volatile SRAM intermediate step
- The "bricked" scenario in the recovery table disappears — JTAG can always reflash

This is tracked as an openFPGALoader enhancement. The SRAM bootstrap procedure
documented above works reliably in the meantime.

## References

- Xilinx XAPP1247 — MultiBoot with SPI: <https://docs.amd.com/v/u/en-US/xapp1247-multiboot-spi>
- LiteX Acorn CLE-215 wiki: <https://github.com/enjoy-digital/litex/wiki/Use-LiteX-on-the-Acorn-CLE-215>
- LitePCIe: <https://github.com/enjoy-digital/litepcie>
- LiteX ICAP core: <https://github.com/enjoy-digital/litex/blob/master/litex/soc/cores/icap.py>
- Acorn board spec: [SQRL Acorn and LiteFury](index.md)
- Acorn pinmap and GPIO JTAG wiring: [Acorn wiring](wiring.md#p1-jtag-24-header--rpi-pins-19-26)
