---
type: how-to
owner: documentation maintainers
reader: someone building the golden and operational flavours of a design by hand
review: 2026-11-10
---

# How to generate multiboot bitstreams by hand

You have a design other than the fpgas.online Acorn design and want its golden and operational flavours for an Acorn's flash. The fpgas.online Acorn design's own build produces both flavours, so this page is not needed for it. It does not cover writing the images, which is [How to install the fpgas.online images on an Acorn](install-images.md).

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

2. In Vivado, build the operational image, which has the watchdog and the fallback.

```tcl
# Operational: watchdog and fallback
set_property BITSTREAM.CONFIG.TIMER_CFG 0x0001fbd0 [current_design]
set_property BITSTREAM.CONFIG.CONFIGFALLBACK Enable [current_design]
write_bitstream -force operational.bit
write_cfgmem -force -format bin -interface spix4 -size 16 -loadbit "up 0x0 operational.bit" -file operational.bin
```

## Check

The working directory holds `golden.bit`, `golden.bin`, `operational.bit` and `operational.bin`.

## If it fails

- **The golden image is built with openXC7.** openXC7 does not support `NEXT_CONFIG_ADDR`. Build golden images with Vivado, which suits an image written once and rarely changed.

## Next

- [How to install the fpgas.online images on an Acorn](install-images.md)
- [How to update the operational image of an Acorn](update-operational-image.md)
