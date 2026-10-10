---
type: explanation
owner: documentation maintainers
reader: someone who wants to know what a Fomu USB analyser is for
review: 2026-11-10
---

# USB analysers for the Fomu EVT

**You want to know what a USB analyser between a Fomu EVT and its Pi is for.** It does not cover capturing with one. The board's USB signals are on [Fomu EVT specifications](specifications.md#usb-interface).

An analyser sits inline between the Fomu and the Pi's USB port. The Fomu's native USB traffic can then be captured and analysed without modifying the FPGA design or the host software. That traffic is DFU programming, CDC-ACM serial and custom USB protocols. The Fomu enumerates as `1209:5bf0`.

## OpenVizsla

The [OpenVizsla](https://github.com/openvizsla/ov_ftdi) is an open-source USB protocol analyser. It captures USB traffic between the Fomu and the Raspberry Pi host. The captures serve debugging and test verification.

## Cythion with LUNA

The [Cythion](https://greatscottgadgets.com/cythion/), from Great Scott Gadgets, is a USB multitool that runs the [LUNA](https://github.com/greatscottgadgets/luna) USB framework. It provides USB protocol analysis and traffic capture. It can also act as a USB host or device for testing. It is connected inline between the Fomu and the Raspberry Pi host.
