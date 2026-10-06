# Tiny Tapeout FPGA board: what the public site loads

**You are looking at a Tiny Tapeout FPGA board on
[tinytapeout.fpgas.online](https://tinytapeout.fpgas.online) and want to know which designs can be in its
FPGA and how each gets there: the bundled demos, a visitor's upload, and the design the boot check leaves
running.**

```{include} ../generated/tt-fpga-pins-other.md
:start-after: "### Loading the FPGA: its configuration pins"
:end-before: "The FPGA breakout has no SPI flash"
```

## The demos and visitors' uploads

On the public site users can run bundled demos or upload their own bitstream. The bitstream-loading and
design-listing features live in the `fpgas-tt` daemon on the board's Raspberry Pi (`/designs`, `/bitstream`,
demos via the `fpgas-online-tt-demos` package), which is what the public site uses.

- **Which demos there are and how they are built**: [Demo bitstreams](../../../setup/tinytapeout.md#demo-bitstreams).
- **The daemon's routes**: [FPGA-board routes](../../../setup/tinytapeout.md#fpga-board-routes).
- **How a design reaches the FPGA.** The daemon's own README (its `main` branch, read on 6 October 2026)
  says: "Nothing writes to the demo board's filesystem. Every design is a file on the Pi: the packaged demos
  (`--demos-dir`) and visitors' uploads (`--uploads-dir`). Loading one sends its bytes over the board's raw
  MicroPython REPL into a buffer in the RP2350's memory and has the SDK's own loader clock that buffer into
  the iCE40"
  ([fpgas.online-tt](https://github.com/fpgas-online/fpgas.online-tt/blob/main/README.md)). Whether the
  daemon running on each board today is that version is not verified by us here.
- **Boards from before October 2026 still hold old copies.** The same README: until then the daemon copied
  every demo and every upload to the board's `/bitstreams` and loaded from there; boards from that time still
  hold those files, and the daemon neither reads nor removes them.

## What the boot check leaves running

At every boot the check ends by streaming one more design, `tt-display`, so that the board's seven-segment
display moves and the board looks alive on its camera: one segment runs round the ring, the middle segment
changes at each lap, the dot blinks once a second. It lasts until the board's own SDK next starts, which
happens when a visitor's Commander connects or a design is run from the site. The whole account: [What the
TT FPGA is left running](../../../verify/fpgas-verify.md#what-the-tt-fpga-is-left-running).

## Is the board there?

Each board's `status.json` (for
example `https://tinytapeout.fpgas.online/board/fpga-1/status.json`) reports the
Pi daemon's `/health` plus `reachable`, and is the quickest liveness check.
