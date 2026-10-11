---
type: how-to
owner: documentation maintainers
reader: a visitor with an iCE40 bitstream for a Tiny Tapeout FPGA demo board
review: 2026-11-10
---

# How to load your own bitstream

**You have a Tiny Tapeout design built for the FPGA demo board, and its board's page open on tinytapeout.fpgas.online.
You want your design to run on the board**.

## What you need

- A bitstream built for the iCE40UP5K with the FabricFox flow: yosys, then `nextpnr-ice40 --up5k --package sg48`, then
  `icepack`, with the top module `tt_fpga_top`. The [demo designs](https://github.com/fpgas-online/tinytapeout-fpga-demos)
  are worked examples of that build.
- The file as a `.bin` of at most 256 KiB.
- A name for it: lower-case letters, digits and `_`, up to 40, such as `tt_um_my_design`. It cannot be the name of a
  bundled design.

## Steps

1. Under **Upload your own bitstream**, type the name in **Name**.
2. Choose the `.bin` file in **Bitstream**.
3. Press **Upload & load**. The page shows `Uploaded <name> (<size> bytes)`, then loads it.

## Check

The page shows `<name> is running`, and your design is in **Designs on this board**, marked "upload", with its button
reading **Running**. Drive it from the Commander's **Interact** tab.

## If it fails

| What you see | Likely cause | Fix |
|---|---|---|
| `Bitstream too large` | the file is over 256 KiB | build it again for the iCE40UP5K; check it is the `.bin`, not another file |
| `not an iCE40 bitstream` | the file is not an iCE40 bitstream | upload the `.bin` that `icepack` wrote |
| `… is a demo name; pick another` | the name is a bundled design's | choose another name |
| `… is the daemon's own name for its idle display; pick another` | the name is the one the Pi uses for its idle design | choose another name |
| your upload is gone from the list | the Pi keeps 16 uploads, and it drops the oldest; a reboot of the Pi drops them all | upload it again |

## Next

- [How to run a bundled design](run-design.md)
- [The bundled designs](designs.md)
