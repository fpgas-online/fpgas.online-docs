# Tiny Tapeout FPGA board on a Raspberry Pi: verifying 1, install and run the check

**You have a Tiny Tapeout FPGA demo board fitted to a Raspberry Pi with a Pmod HAT, and want to install the
fpgas.online packages for it, run the check and know whether the board and its wiring pass.**

Log in to the Raspberry Pi first. At welland, the board's page on <https://welland.fpgas.online/fpgas/> shows
its ssh command under "Use your own ssh client".

**Before you run it, on a board that is on the public site:** the check stops the `fpgas-tt` daemon for its
tests and starts it again when its report is written, so the board is off
[tinytapeout.fpgas.online](https://tinytapeout.fpgas.online) while the check runs, and whatever design the FPGA held is replaced by the check's.

```{include} ../generated/tt-fpga-pins-other.md
:start-after: "### Loading the FPGA: its configuration pins"
:end-before: "The FPGA breakout has no SPI flash"
```

```{include} ../../generated/install-tt-fpga.md
```

## Reading what it says

- One result, `pass` or one kind of fail: [Reading the result](../../../verify/fpgas-verify.md#reading-the-result).
- What the check tests on this board, in order (`sdk`, `pin-id`, `uart`), and the design it leaves running:
  [what each board's check tests](../../../verify/fpgas-verify.md#arty-netv2-fomu-and-tt-fpga).
- A line that says `fail` or `error`: [verifying 2](verifying-2.md).
