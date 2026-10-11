---
type: how-to
owner: documentation maintainers
reader: someone building the golden and operational flavours of a design by hand
review: 2026-11-10
---

# How to generate multiboot bitstreams by hand

You have a design other than the fpgas.online Acorn design and want its golden and operational flavours for an Acorn's flash. The fpgas.online Acorn design's own build produces both flavours, so this page is not needed for it. It does not cover writing the images, which is [How to install the fpgas.online images on an Acorn](install-images.md).

This procedure is waiting for its run: [test-designs issue #226](https://github.com/fpgas-online/fpgas.online-test-designs/issues/226).

## What you need

- Vivado, with the design open as `current_design`.
- Vivado for the golden image: openXC7 does not support `NEXT_CONFIG_ADDR`.

## Steps

1. In Vivado, build the golden image, which chain-loads the operational slot.

```tcl
# Golden: chain-load the operational slot
set_property BITSTREAM.CONFIG.NEXT_CONFIG_ADDR 0x00400000 [current_design]
write_bitstream -force golden.bit
write_cfgmem -force -format bin -interface spix4 -size 16 -loadbit "up 0x0 golden.bit" -file golden.bin
```

2. In the same Vivado session, clear step 1's chain-load, then build the operational image, which has the watchdog and the fallback.

```tcl
# Operational: no chain-load, then the watchdog and the fallback
reset_property BITSTREAM.CONFIG.NEXT_CONFIG_ADDR [current_design]
set_property BITSTREAM.CONFIG.TIMER_CFG 0x0001fbd0 [current_design]
set_property BITSTREAM.CONFIG.CONFIGFALLBACK Enable [current_design]
write_bitstream -force operational.bit
write_cfgmem -force -format bin -interface spix4 -size 16 -loadbit "up 0x0 operational.bit" -file operational.bin
```

## Check

The working directory holds `golden.bit`, `golden.bin`, `operational.bit` and `operational.bin`. The images are checked when they are written: `fpgas-acorn-flash write` checks each one against its slot before it erases anything.

## If it fails

- **`fpgas-acorn-flash` refuses `operational.bin`: "this image chain-loads another one (the golden flavour)".** Step 1's `NEXT_CONFIG_ADDR` was still set when step 2 wrote it. Run step 2 again, with its `reset_property` line.

## Next

- [How to install the fpgas.online images on an Acorn](install-images.md)
- [How to update the operational image of an Acorn](update-operational-image.md)
