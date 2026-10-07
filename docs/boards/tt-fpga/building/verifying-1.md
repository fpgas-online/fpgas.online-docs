# Tiny Tapeout FPGA board on a Raspberry Pi: verifying 1, install and run the check

**You have a Tiny Tapeout FPGA demo board fitted to a Raspberry Pi with a Pmod HAT, and want to install the
fpgas.online packages for it, run the check and know whether the board and its wiring pass.**

**What this page cannot give you:** which position of the demo board's DIP switches is safe while the check
drives `ui_in` (step 4); it is not recorded, so the page says to leave them as you find them. The commands are written for Raspberry Pi OS or Debian **trixie**; on
**bookworm** one more line is needed (step 3).

The steps, each a section of this page:

1. Log in to the Raspberry Pi.
2. Add the fpgas.online apt repository.
3. Installing the TT FPGA Packages (with rpi-hwid, and on bookworm `mpremote`).
4. Before you run it.
5. Run it.

## 1. Log in to the Raspberry Pi

At welland the Pis are reached through the gateway: [Gateway: tweed](../../../sites/welland.md#gateway-tweed)
(another page, not in this set). On 3 September 2026 each Tiny Tapeout FPGA host at welland also had a page
on <https://welland.fpgas.online/fpgas/> (the site table of that date); whether that page gives the ssh
command for such a host is not verified by us.

On a Pi of the welland fleet the check already runs at every boot (below), so steps 2 and 3 (adding the
repository, installing the packages) are for a Pi of your own.

## 2. Add the fpgas.online apt repository

From [Checking a board: fpgas-verify](../../../verify/fpgas-verify.md#installing):

```{literalinclude} ../../../verify/fpgas-verify.md
:language: bash
:start-at: "# The fpgas.online apt repository"
:end-before: "# fpgas.online's openFPGALoader"
```

The same block on that page then adds fpgas.online's openFPGALoader repository. This board is loaded through
its microcontroller with `mpremote`, not with openFPGALoader, so it is left out here. Then:

```bash
sudo apt update
```

Step 3 is the next section.

```{include} ../../generated/install-tt-fpga.md
:end-before: "```bash"
```

(That repository is step 2 above.)

```{include} ../../generated/install-tt-fpga.md
:start-after: "then on the demo board's Pi:"
:end-before: "The check, at each boot:"
```

**`fpgas-tt-fpga-debug`**, which runs one test with its output live, is in `fpgas-online-tt-fpga-debug`
(the section below says so):

```bash
sudo apt install fpgas-online-tt-fpga-debug
```

**rpi-hwid is required.** Without it the check cannot ask the board what it is, and loads nothing (the
section below). It comes from its own signed apt repository. From rpi-hwid's README
(<https://github.com/mithro/rpi-hwid#install>, read on 7 October 2026), with your suite's name (`bookworm`
or `trixie`) in place of `trixie`:

```bash
sudo install -d -m0755 /etc/apt/keyrings
curl -fsSL https://mith.ro/rpi-hwid/rpi-hwid.gpg | sudo tee /etc/apt/keyrings/rpi-hwid.gpg > /dev/null
echo "deb [signed-by=/etc/apt/keyrings/rpi-hwid.gpg] https://mith.ro/rpi-hwid/trixie/ ./" \
  | sudo tee /etc/apt/sources.list.d/rpi-hwid.list
sudo apt update
sudo apt install python3-rpi-hwid      # provides the rpi-hwid command
```

The README gives the repository's signing key as `9C51 CAE0 CF1C 4C08 A63C  8A6A 2599 D5E0 285B 902F`
(`gpg --show-keys /etc/apt/keyrings/rpi-hwid.gpg` shows it).

**On bookworm only: `mpremote`.** The check needs `micropython-mpremote`, which bookworm has only in
bookworm-backports (the section below; without it the check reports an `error`). Debian's form for enabling
backports and installing from it (<https://backports.debian.org/Instructions/>), not run by us on this board:

```bash
echo "deb http://deb.debian.org/debian bookworm-backports main" \
  | sudo tee /etc/apt/sources.list.d/bookworm-backports.list
sudo apt update
sudo apt install -t bookworm-backports micropython-mpremote
```

## 4. Before you run it

1. **The three Pmod cables are on the right ports and the right way round**: INPUT to JA, BIDIR to JB,
   OUTPUT to JC, pin 1 to pin 1 ([fitting](fitting.md#3-the-three-pmod-cables-and-the-usb-c-cable)). The
   check drives the Pi's GPIOs into those cables.
2. **The DIP switches: leave them as you find them.** That is how the one board that has passed was checked
   (below). Which position leaves `ui_in` undriven is **not recorded** (asked of the boards' owner on
   7 October 2026). The switches are on the `ui_in` signals (Tiny Tapeout's specification; not verified by
   us), the check drives those same signals from the Pi, and two drivers on one signal fight. What is
   recorded: on 5 October 2026 the
   board with USB serial `4df39a7a6856f86f` passed `pin-id` with its switches as they were found, and with
   its SDK running and the microcontroller not driving `ui_in`, `ui_in` read `00001001`: `ui_in[0]` and
   `ui_in[3]` held high, by the switches or by the Pi, not decided (read on 5 October 2026). A camera still of
   a passing board's switches would record a setting that passes: not yet taken.
3. **On a board that is on the public site:** the check stops the `fpgas-tt` daemon for its tests and starts
   it again when its report is written, so the board is off
   [tinytapeout.fpgas.online](https://tinytapeout.fpgas.online) while the check runs, and whatever design the
   FPGA held is replaced by the check's. Look for a visitor first (the warning below).
4. **The debug tool and the serial port** (the warning below): needed before `fpgas-tt-fpga-debug`.

```{include} ../serial-port.inc
```

## 5. Run it

```{include} ../../generated/install-tt-fpga.md
:start-after: "#current-results)."
:end-before: "What the results mean"
```

## What the result means

From [Reading the result](../../../verify/fpgas-verify.md#reading-the-result):

```{include} ../../../verify/fpgas-verify.md
:start-after: "### Reading the result"
:end-before: "* The check goes on after a fault wherever it can"
```

- What the check tests on this board, in order (`sdk`, `pin-id`, `uart`), and the design it leaves running:
  the next section.
- A line that says `fail` or `error`: [verifying 2](verifying-2.md).

(the-report-and-the-recorded-state)=

- The report, `changed` and `--update`, and every other failing line are on another page, not in this set:
  [Checking a board: fpgas-verify](../../../verify/fpgas-verify.md#reading-the-result).

## What the check does

```{include} ../streaming-rule.inc
```

```{include} ../../generated/install-tt-fpga.md
:start-after: "`fpgas-online-tt` is a different package: the TT site's own."
:end-before: "**Check the board now**"
```
