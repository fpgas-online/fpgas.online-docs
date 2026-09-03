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
Reconfiguring the FPGA over JTAG while its endpoint is enumerated is a PCIe
surprise removal. The Pi 5's BCM2712 root complex does not survive it: on
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

The endpoint is `0001:01:00.0` on the Welland Pi 5 hosts and on PS1's pi16 and
pi20, but `0000:01:00.0` on pi14; take the address from the host's own row in
[Compute blades](../../sites/ps1.md#compute-blades).

Every `openFPGALoader … <bitstream>` invocation on this page assumes that
detach has been done. Read-only operations (`--detect`, and `--read-dna` /
`--read-xadc` on openFPGALoader ≥ 0.13) do not reconfigure the device and are
safe on a live endpoint.

### Prebuilt Vivado bitstreams

There is no need to build locally. GitHub release
[`vivado-bitstreams-v0.0-496-gf162f60`](https://github.com/fpgas-online/fpgas.online-test-designs/releases/tag/vivado-bitstreams-v0.0-496-gf162f60)
(Vivado 2025.2, published 2026-04-17) carries every test design × Acorn variant
(`cle-101`, `cle-215`, `cle-215p`), each as plain `.bit`/`.bin` plus the
`_fallback` and `_operational` multiboot variants described below, and a
`manifest.json` with a SHA-256 per file. For the Welland CLE-215+ boards use the
`*_acorn-cle-215p_*` files; their `.bit` header reads `7a200tfbg484`, matching
IDCODE `0x3636093`.

```console
$ gh release download vivado-bitstreams-v0.0-496-gf162f60 \
      --repo fpgas-online/fpgas.online-test-designs \
      --pattern 'pmod-pin-id_acorn-cle-215p_vivado-vivado_sqrl_acorn.bit'
```

:::{note}
The `pmod-pin-id` design in that release predates [test-designs
PR #10](https://github.com/fpgas-online/fpgas.online-test-designs/pull/10)
(2026-08-31), which gave the Acorn pin-ID design a real clock; the release build
of *that one design* configures but never toggles a pin. The fixed design must
be rebuilt with Vivado until a newer release is cut.
:::

### Flash-via-JTAG is not currently working

**`openFPGALoader --write-flash` does not currently work on the Acorn.** JTAG
can only load bitstreams to volatile SRAM. This has important implications for
the recovery strategy below.

### Current flash state

What each board's flash actually holds is on the site pages: the [SQRL Acorn
CLE-215+](../../sites/welland.md#sqrl-acorn-cle-215) table at Welland gives the
`lspci -nn` reading for all six boards on 2026-09-03 — five still boot the
factory SQRL cryptocurrency mining firmware `1e24:021f` and only pi-sw2-p44 has
a LiteX/Vivado design `10ee:7011` in flash.

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

The longer-term intent (Tim, 2026-08-31) is to flash every board with a LiteX
design carrying PCIe + UART + GPIO that supports FPGA updates over PCIe, and to
add JTAG/PCIe/UART/GPIO self-verification to the Pi boot checks.

What that state means for programming, on any board:

- JTAG can always load a bitstream into SRAM (volatile), but it is lost on power cycle
- The only way to write to SPI flash (persistent) is via PCIe using `litepcie_util`
- PCIe→Flash requires a LiteX bitstream (not the factory Sqrl firmware)
- The golden bitstream at flash address 0x0 is **irreplaceable without PCIe** — if it is corrupted, recovery requires the SRAM bootstrap procedure (see below)

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
working, recovery uses a **two-stage SRAM bootstrap**:

1. **Load a PCIe-capable bitstream to SRAM via JTAG** (volatile — lost on power cycle):

   ```console
   # Detach anything that is enumerated before reconfiguring
   $ echo 1 | sudo tee /sys/bus/pci/devices/0001:01:00.0/remove
   # Free the SPI0 pins — Pi 0-4 only
   $ sudo rmmod spidev spi_bcm2835
   $ openFPGALoader --cable libgpiod --pins 10:9:11:8 golden.bit
   ```

2. **PCIe comes up from the SRAM-loaded bitstream**. Load the litepcie kernel module:

   ```console
   $ modprobe litepcie
   ```

3. **Write a new golden image to flash at address 0x0 via PCIe**:

   ```console
   $ litepcie_util flash_write golden.bin 0x0
   ```

4. **Write the operational bitstream to 0x400000**:

   ```console
   $ litepcie_util flash_write operational.bin 0x400000
   ```

5. **Power cycle** the board. The FPGA boots from the new golden image in flash, chain-loads operational, and PCIe comes up persistently.

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

## Initial setup (new board)

Since flash-via-JTAG is not working, initial multiboot setup uses the SRAM
bootstrap method:

1. **Build a golden bitstream** with Vivado (LiteX SoC with PCIe + SPI Flash + ICAP + NEXT_CONFIG_ADDR)

2. **Load golden to SRAM via JTAG** (volatile):

   ```console
   # Detach the factory endpoint before reconfiguring
   $ echo 1 | sudo tee /sys/bus/pci/devices/0001:01:00.0/remove
   # Free the SPI0 pins — Pi 0-4 only
   $ sudo rmmod spidev spi_bcm2835
   $ openFPGALoader --cable libgpiod --pins 10:9:11:8 golden.bit
   ```

3. **PCIe comes up**. Load the kernel module and write golden to flash:

   ```console
   $ modprobe litepcie
   $ litepcie_util flash_write golden.bin 0x0
   ```

4. **Write operational bitstream** to flash:

   ```console
   $ litepcie_util flash_write operational.bin 0x400000
   ```

5. **Power cycle** — golden boots from flash, chain-loads operational, PCIe comes up persistently.

6. **Verify** multiboot works by intentionally writing a bad operational image, confirming watchdog fallback, then reprogramming:

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

:::{warning}
1. **NEVER write to flash address 0x0 via PCIe during normal operation.** The
   golden image is the recovery mechanism. Only write to 0x0 during initial
   setup or golden recovery. A wrapper script should validate the target
   address.

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
   $ openFPGALoader --cable libgpiod --pins 10:9:11:8 new_design.bit
   # Test it works, then write to flash via PCIe
   ```

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
