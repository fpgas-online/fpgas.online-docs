# Acorn PCIe programming and multiboot

How to program the Acorn CLE-215+ / LiteFury FPGA via PCIe, and how to use
Xilinx 7-series multiboot for safe recovery from bad bitstreams. See [SQRL Acorn
and LiteFury](index.md) for the board itself and [Acorn wiring](wiring.md) for
the GPIO JTAG wiring every JTAG command below assumes.

:::{danger}
**Corrected 2026-09-20, after the first LiteX PCIe design was run on hardware
(pi20 at PS1). Three things this page used to say were wrong:**

- **The `pcie-enumeration_acorn-*` bitstreams in the prebuilt release never
  link.** Their I/O reports put the PCIe lane on package pins D9/D7 (GTP channel
  X0Y7, M.2 lane 3), not on B10/B6 (X0Y6, M.2 lane 0): the Xilinx PCIe IP's own
  XDC pins a x1 core's transceiver and silently beats the port constraints. On
  a x1 host the core sits in Detect forever. **Do not use them as a golden image
  or for recovery.** The fix is in the `acorn-pcie` SoC ([test-designs
  `acorn-pcie/01-soc`](https://github.com/fpgas-online/fpgas.online-test-designs/tree/acorn-pcie/01-soc)),
  whose build now fails if any port is not on the pin it was constrained to.
- **`10ee:7011` is not a LiteX design.** LitePCIe's default ID for a x1 core is
  `10ee:7021` (`7020 + lanes`). pi20's `10ee:7011` is the vendor (RHS Research)
  XDMA sample image: x4-capable, two BARs. pi-sw2-p44 shows the same ID and has
  not been re-checked.
- **A PCIe rescan is not always enough after a JTAG load of a LiteX design.** It
  was not on the CM5 blade pi20; it was on the Pi 5 pi-sw2-p48 (2026-09-21). See
  [Bring the endpoint back after a JTAG
  load](#bring-the-endpoint-back-after-a-jtag-load).

Nothing on this page that goes through `litepcie_util` has been run on
fpgas.online hardware yet. The first board was installed on 2026-09-21 with
`spi_flash.py` instead: see [First install, as actually
done](#first-install-as-actually-done).
:::

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
# then bring it back: see the next section
```

The rule is the root complex's, not the Acorn's: it applies to any PCIe FPGA
on a Pi 5, the NeTV2 on `rpi5-netv2` included ([PCIe
detection](../netv2.md#pcie-detection-rpi5-netv2)).

Every Welland Pi 5 host uses `0001:01:00.0` ([SQRL Acorn
CLE-215+](../../sites/welland.md#sqrl-acorn-cle-215)). At PS1 the address
differs per host — `0000:01:00.0` on pi14, `0001:01:00.0` on pi16 and pi20 — so
read it from the `PCIe Bus` column in [Compute
blades](../../sites/ps1.md#compute-blades).

Every `openFPGALoader … <bitstream>` invocation on this page assumes that
detach has been done. Read-only operations (`--detect`, and `--read-dna` /
`--read-xadc` on openFPGALoader ≥ 0.13) do not reconfigure the device and are
safe on a live endpoint.

### Bring the endpoint back after a JTAG load

Measured on pi20 (CM5 on a Compute Blade, kernel 6.12.75, 2026-09-20):

| Design loaded over JTAG | `echo 1 > /sys/bus/pci/rescan` | Root-complex re-probe |
|---|---|---|
| Vendor XDMA image (reloaded from flash with `openFPGALoader --reset`) | re-links at 5 GT/s x1 and enumerates | works |
| LiteX `acorn-pcie` SoC | nothing: the core's LTSSM sits at `0x2d`, root-port retrain and secondary-bus reset change nothing | **links at 5 GT/s x1, enumerates as `10ee:7021`** |

So on the blade a LiteX design needs PERST# toggled, which means unbinding and
rebinding the slot's root complex. That touches only the FPGA's PCI domain: the
RP1 southbridge (Ethernet, USB, GPIO) hangs off a different platform device.

```console
# Which platform device is behind the FPGA slot? (pi20: 1000110000.pcie, PCI domain 0001)
$ readlink -f /sys/bus/pci/devices/0001:00:00.0 | grep -o '[0-9a-f]*\.pcie'
1000110000.pcie
$ echo 1000110000.pcie | sudo tee /sys/bus/platform/drivers/brcm-pcie/unbind
$ echo 1000110000.pcie | sudo tee /sys/bus/platform/drivers/brcm-pcie/bind
$ lspci -nn -s 0001:01:00.0
0001:01:00.0 Memory controller [0580]: Xilinx Corporation Device [10ee:7021]
```

If the link is down when `bind` runs, the driver logs `link down`, `bind` fails
with `No such device`, and the root port `0001:00:00.0` disappears until a later
`bind` succeeds. That is recoverable: load a design that links (or
`openFPGALoader --reset` to reload the flash image) and `bind` again.

Measured on pi-sw2-p48 (Raspberry Pi 5 with an M.2 HAT, kernel 6.12.96,
2026-09-21), the same steps behave differently:

| Design loaded over JTAG | `echo 1 > /sys/bus/pci/rescan` | Root-complex re-probe |
|---|---|---|
| LiteX `acorn-pcie` SoC (CLE-215+) | **enough**: the link is already up (LTSSM `0x16`, L0, 5 GT/s x1) as soon as the load finishes, and the rescan enumerates `10ee:7021` | not needed, not tried |

So try the rescan first and fall back to the re-probe only when `lspci` still
shows nothing. The platform device behind the FPGA slot has the same name on
both hosts (`1000110000.pcie`). Why the CM5 blade needs PERST# and the Pi 5 does
not is not yet understood.

### Prebuilt Vivado bitstreams

:::{warning}
The `pcie-enumeration_acorn-*` assets in this release are built on the wrong
PCIe lane and cannot link on any fpgas.online host (see the box at the top of
this page). The other designs in the release are unaffected.
:::

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
boot the factory SQRL cryptocurrency mining firmware `1e24:021f`; pi-sw2-p44
shows `10ee:7011`, which on pi20 turned out to be the vendor XDMA sample image,
not a LiteX design (2026-09-20). p44 has not been re-checked.

Factory firmware characteristics:

- PCI vendor:device `1e24:021f` (Squirrels Research Labs)
- BAR0: 128 KB — repeating mining parameter pattern, no LiteX CSRs
- **Not a LiteX design** — `litepcie_util` cannot communicate with this firmware

To enable PCIe→Flash programming, the factory firmware must be replaced with a
**LiteX Acorn PCIe SoC** bitstream (`10ee:7021`) that includes PCIe+DMA, SPI
Flash controller, and ICAP. Building this bitstream requires **Vivado** (the
XC7A200T is too large for the openXC7 open source toolchain). The
`pcie-enumeration_acorn-cle-215p_*_{fallback,operational}.bin` files in the
prebuilt release are **not** usable for this: they never link.

The litepcie kernel module and `litepcie_util` were built on the host then
called pi2 (now pi-sw2-p48) — they just need a matching LiteX bitstream to bind
to. Because the Pi root is `overlayroot=tmpfs`, anything built on a Pi is lost
at reboot unless it is baked into the NFS root.

### First install, as actually done

pi-sw2-p48 (RPi MAC `88:a2:9e:45:85:77`, Device DNA `0x0054b48664b04854`) was the
first board moved to the fpgas.online images, on 2026-09-21. It used
[`designs/acorn-pcie/host/spi_flash.py`](https://github.com/fpgas-online/fpgas.online-test-designs/pull/27),
which drives the SoC's flash core through PCIe BAR0 from Python and needs no
kernel module, rather than `litepcie_util`:

| Step | Result |
|---|---|
| Load the operational SoC into SRAM over JTAG (openocd `linuxgpiod`, endpoint detached first) | 24 s; PCIe rescan enumerates `10ee:7021` |
| `spi_flash.py id` | S25FL256S, RDID `01 02 19 4d 01 80`, 32 MiB, QUAD bit set |
| `spi_flash.py dump` of the factory contents, twice | 58 s each, identical SHA-256; kept as the backup |
| `spi_flash.py write …_operational.bin 0x400000` | erased, programmed and verified in 19 s |
| ICAP warm boot to `0x400000` (endpoint detached, triggered over the UART bridge) | operational image runs from flash, `BOOTSTS = 0x105`: no fallback, no error |
| Load the golden design into SRAM and check it | UART, PCIe and flash access all work |
| `spi_flash.py write …_fallback.bin 0x0 --i-know-this-writes-golden`, run from the golden design | 20 s; both slots verified again |
| ICAP warm boot to `0x0` | golden chain-loads operational |
| PoE power cycle | `10ee:7021` enumerated at kernel t = 2.0 s, 5 GT/s x1, operational ident; UART, PCIe, P2 GPIO and flash checks pass |
| Reset the SoC's CPU and drain the BIOS log from the crossover UART through BAR0 | DDR3 1 GiB at 800 MT/s: read leveling clean on both modules, `Memtest OK`, 35.1 MiB/s write, 46.8 MiB/s read |

Three things learned on the way:

- **The factory image is itself a multiboot pair.** Its header at `0x0` sets
  `WBSTAR = 0x680000` and issues `IPROG`, so the mining design lives at
  `0x680000`. Writing our operational image at `0x400000` did not disturb it.
- **The first SPI transfer after every configuration is lost.** `STARTUPE2`
  does not pass the first three `USRCCLKO` edges to the flash clock pin, so the
  first command arrives three clocks short and reads back as all ones.
  `spi_flash.py` spends them with the flash deselected.
- **The SoC resets `flash_cs_n` to 0**, so the flash sits selected after
  configuration until a host deselects it. Harmless so far; to be changed to
  reset high in the SoC.

- **BAR0 answers only aligned 32-bit accesses.** Reading the SoC's registers
  from Python through `/sys/bus/pci/devices/<bdf>/resource0`, a 4-byte slice of
  the `mmap` (`struct.unpack("<I", m[off:off + 4])`) returns the register; a
  byte-wise slice of the same window returns `0xff` for every byte (found by
  the rpi-hwid probe on pi-sw2-p48, 2026-09-21). Enable memory decoding first:
  `setpci -s <bdf> COMMAND=0002:0002`.

What that state means for programming, on any board:

- JTAG can always load a bitstream into SRAM (volatile), but it is lost on power cycle
- The only way to write to SPI flash (persistent) is via PCIe, with `spi_flash.py` (proven) or `litepcie_util` (not yet run here)
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
2026-09-03: none of them runs a LiteX design (pi-sw2-p44's `10ee:7011` is most
likely the vendor sample image, and it is one of the boards with no JTAG
recovery), so none can be reached by `litepcie_util` until a LiteX bitstream is
loaded.
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

After reload the PCIe link has to be brought back. A plain rescan was not enough
for a LiteX design after a JTAG load on pi20; whether it is after an ICAP reload
has not been tested. See [Bring the endpoint back after a JTAG
load](#bring-the-endpoint-back-after-a-jtag-load).

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
`pcie-enumeration_acorn-cle-215p_*_fallback.*` was meant to be the golden image
and `pcie-enumeration_acorn-cle-215p_*_operational.*` its operational partner,
but **those release files never link** (top of this page). Use the `acorn-pcie`
SoC's golden and operational builds instead.

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
   # Re-probe the root complex of the FPGA slot (see Bring the endpoint back after a JTAG load)
   $ echo 1000110000.pcie | sudo tee /sys/bus/platform/drivers/brcm-pcie/unbind
   $ echo 1000110000.pcie | sudo tee /sys/bus/platform/drivers/brcm-pcie/bind
   $ lspci -nn -s 0001:01:00.0
   # Expected: Memory controller [0580]: Xilinx Corporation Device [10ee:7021]
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
   `lspci -nn -s 0001:01:00.0` afterwards: `10ee:7021` again, this time without
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
   # Re-probe the root complex of the FPGA slot (see Bring the endpoint back after a JTAG load)
   $ echo 1000110000.pcie | sudo tee /sys/bus/platform/drivers/brcm-pcie/unbind
   $ echo 1000110000.pcie | sudo tee /sys/bus/platform/drivers/brcm-pcie/bind
   $ lspci -nn -s 0001:01:00.0
   # Expected: Memory controller [0580]: Xilinx Corporation Device [10ee:7021]
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
   # Bring the endpoint back (root-complex re-probe, see above) and check what enumerated
   $ echo 1000110000.pcie | sudo tee /sys/bus/platform/drivers/brcm-pcie/unbind
   $ echo 1000110000.pcie | sudo tee /sys/bus/platform/drivers/brcm-pcie/bind
   $ lspci -nn -s 0001:01:00.0
   # Expected: the loaded design; a LiteX x1 PCIe design shows [10ee:7021]
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
