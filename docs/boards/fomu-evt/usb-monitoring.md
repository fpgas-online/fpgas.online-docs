# Fomu EVT: USB monitoring

**You want to watch a Fomu's USB traffic with the analyser inline on its host.**

## USB monitoring

Each Fomu host has an inline USB protocol analyser between the Fomu and the Pi's
USB port, so the Fomu's native USB traffic — DFU programming, CDC-ACM serial,
custom USB protocols — can be captured and analysed without modifying the FPGA
design or the host software. Which analyser is on which host, along with the
hosts' addresses and the Fomu's `1209:5bf0` VID:PID and DFU version, is in the
[Fomu EVT host table](../../sites/welland.md#fomu-evt).

### OpenVizsla (pi17)

The [OpenVizsla](https://github.com/openvizsla/ov_ftdi) is an open-source USB
protocol analyser. It captures USB traffic between the Fomu and the RPi host for
debugging and test verification.

### Cythion/LUNA (pi21)

The [Cythion](https://greatscottgadgets.com/cythion/) (from Great Scott Gadgets)
is a USB multitool running the [LUNA](https://github.com/greatscottgadgets/luna)
USB framework. It provides USB protocol analysis, traffic capture, and can also
act as a USB host or device for testing. It is connected inline between the Fomu
and the RPi host.

:::{note}
The host names `pi17` and `pi21` here are the flat `piNN` names used before the
2026-08-23 renumbering, and neither host has been re-probed since the survey.
The old addresses no longer resolve; derive the current name and address of each
host from its switch port using the
[Fomu EVT host table](../../sites/welland.md#fomu-evt). The Welland
[Known faults](../../sites/welland.md#known-faults) also record pi21's Cythion/LUNA
and its Fomu as offline at that survey.
:::

Source: dnsmasq `pibs.conf` on tweed, verified 2026-03-17.
