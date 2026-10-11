% This page is copied from https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/docs/verify.md
% by tools/sync_repos.py. Do not edit it here: change it in test-designs.

# fpgas-verify: checking an FPGA board from its Raspberry Pi

**You use fpgas-verify, or look after Pis that run it, and want the page for what you are doing.**

`fpgas-verify` answers one question per Pi: **is this Pi and its FPGA board ready for users?** It finds the
board, tests the board and its wiring to the Pi, and gives one result, pass or fail, with every fault it found.

* The code: [`verify/`](https://github.com/fpgas-online/fpgas.online-test-designs/tree/main/verify).
* `verify_hardware.py` ([verify_hardware.py — How the Hardware Verification Script Works](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/docs/verify-hardware.md)) is a different tool: a developer's script
  that loads freshly built bitstreams from a workstation over SSH.

This page lists the pages for [using verify](#using-verify-as-a-standalone-tool): installing, running, reading
the result, and what each board's check tests.

---

## Using verify as a standalone tool

One page for each task, in this order:

(installing)=

* [Installing](installing.md#installing): for you if you have a Pi with an FPGA board and want to install the check for it.

(running-it)=

* [Running it](running.md#running-it): for you if you have installed it and want to run the check, part of it, or set how the host runs it.

(identity-and-labels)=

* [Identity and labels](identity-and-labels.md#identity-and-labels): for you if you want to print who the board is, or make its labels with rpi-hwid.

(reading-the-result)=

* [Reading the result](reading-the-result.md#reading-the-result): for you if you have run the check and want to know what its result and summary mean.

* [More results](more-results.md): for you if you want to compare your summary with more failing and missing results.

(help)=

* [`--help`](help.md#the-help-of-each-tool): for you if you want the options and commands of each tool without installing it.

(what-each-board-s-check-tests)=

(what-each-boards-check-tests)=

(arty-netv2-fomu-and-tt-fpga)=

* [What the check tests on each board](tests.md#what-the-check-tests-on-each-board): for you if you have an Arty, NeTV2, Fomu or TT FPGA and want to know what each test does.

(which-tiny-tapeout-board-it-is)=

(what-the-tt-fpga-is-left-running)=

(the-sdk-test)=

(tt-fpga-identity)=

* [The Tiny Tapeout demo boards](tt-fpga.md): for you if you have a Tiny Tapeout demo board and want to know how it is told apart, what it is left running, its `sdk` test and its identity.

(acorn)=

* [What an Acorn check tests](acorn.md#acorn): for you if you have an Acorn and want to know what its check does.

(the-acorn-s-power-cycle-check-opt-in)=

(the-acorns-power-cycle-check-opt-in)=

* [The Acorn's power-cycle check](acorn-power-cycle.md#the-acorn-power-cycle-check-opt-in): for you if you have an Acorn and want to know how its opt-in power-cycle check works, and the details of its `ddr` test.

(the-jtag-idcode)=

(the-device-dna)=

* [The JTAG IDCODE and the device DNA](idcode-and-dna.md): for you if you have an Acorn, Arty or NeTV2 and want to know how its IDCODE and DNA are read and judged.

(checking-an-acorn-s-wiring)=

(checking-an-acorns-wiring)=

* [Checking an Acorn's wiring](acorn-wiring.md#checking-the-wiring-of-an-acorn): for you if you have built an Acorn's cables and want the page that checks them.

(common-failures)=

* [Common failures](common-failures.md#common-failures): for you if you have a result that is not `pass` and want to know what to do.

(the-report-and-the-recorded-state)=

* [The report and the recorded state](report-and-state.md#the-report-and-the-recorded-state): for you if you want to read the JSON report, or know when a board is `changed`.

```{toctree}
:hidden:

Installing <installing>
Running it <running>
Identity and labels <identity-and-labels>
Reading the result <reading-the-result>
Reading the result: more <more-results>
--help <help>
What each check tests <tests>
TT FPGA <tt-fpga>
Acorn <acorn>
Acorn: power-cycle check <acorn-power-cycle>
JTAG IDCODE and DNA <idcode-and-dna>
Checking an Acorn's wiring <acorn-wiring>
Common failures <common-failures>
The report and state <report-and-state>
```
