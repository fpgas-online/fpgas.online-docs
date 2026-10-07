# Tiny Tapeout FPGA board on a Raspberry Pi: verifying 1, install and run the check

**You have a Tiny Tapeout FPGA demo board fitted to a Raspberry Pi with a Pmod HAT, and want to install the
fpgas.online packages for it, run the check and know whether the board and its wiring pass.**

## 1. Log in to the Raspberry Pi

At welland the Pis are reached through the gateway: [Gateway: tweed](../../../sites/welland.md#gateway-tweed).
On 3 September 2026 each Tiny Tapeout FPGA host at welland also had a page on
<https://welland.fpgas.online/fpgas/> (the site table of that date); whether that page gives the ssh command
for such a host is not verified by us.

On a Pi of the welland fleet the check already runs at every boot (below), so steps 2 and 3 (adding the
repository, installing the packages) are for a Pi of your own.

## 2. Add the fpgas.online apt repository

From [Checking a board: fpgas-verify](../../../verify/fpgas-verify.md#installing):

```{literalinclude} ../../../verify/fpgas-verify.md
:language: bash
:start-at: "# The fpgas.online apt repository"
:end-before: "sudo apt install fpgas-online-arty "
```

Then step 3, the section below, which installs the packages:

```{include} ../../generated/install-tt-fpga.md
:end-before: "The check, at each boot:"
```

`fpgas-tt-fpga-debug`, which runs one test with its output live, is in `fpgas-online-tt-fpga-debug` (the
section above, below its table):

```bash
sudo apt install fpgas-online-tt-fpga-debug
```

## 4. Before you run it

1. **The three Pmod cables are on the right ports and the right way round**: INPUT to JA, BIDIR to JB,
   OUTPUT to JC, pin 1 to pin 1 ([fitting](fitting.md#3-the-three-pmod-cables-and-the-usb-c-cable)). The
   check drives the Pi's GPIOs into those cables.
2. **On a board that is on the public site:** the check stops the `fpgas-tt` daemon for its tests and starts
   it again when its report is written, so the board is off
   [tinytapeout.fpgas.online](https://tinytapeout.fpgas.online) while the check runs, and whatever design the
   FPGA held is replaced by the check's.
3. **The debug tool and the serial port** (the warning below): needed before `fpgas-tt-fpga-debug`.

```{include} ../serial-port.inc
```

## 5. Run it

```{include} ../../generated/install-tt-fpga.md
:start-after: "#current-results)."
```

## What the check does

```{include} ../generated/tt-fpga-pins-other.md
:start-after: "### Loading the FPGA: its configuration pins"
:end-before: "The FPGA breakout has no SPI flash"
```

```{include} ../../generated/install-tt-fpga.md
:start-after: "`fpgas-online-tt` is a different package: the TT site's own."
:end-before: "**Check the board now**"
```

## Reading what it says

- One result, `pass` or one kind of fail: [Reading the result](../../../verify/fpgas-verify.md#reading-the-result).
- What the check tests on this board, in order (`sdk`, `pin-id`, `uart`), and the design it leaves running:
  [what each board's check tests](../../../verify/fpgas-verify.md#arty-netv2-fomu-and-tt-fpga).
- A line that says `fail` or `error`: [verifying 2](verifying-2.md).
