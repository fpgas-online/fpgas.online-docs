# Taking pi20 at ps1's old serial wiring off

**You are about to fit the guide's P2 cable on pi20 at ps1 and need its old serial wiring off without losing
its P1 (JTAG) cable.** What each blade still needs is on [Acorns at ps1](ps1.md).

Its serial pair is wired straight to GPIO14 (J2) and
GPIO15 (K2), with no resistor: read with the pin-ID design on 31 August 2026, when a design driving J2 stopped
JTAG until a PoE cycle, so J2 and P1's TMS share GPIO14 (fpgas.online-test-designs issue 4, the comment of
2026-08-31). GPIO14 is on Extension Port pin 9 and on UART header pin 3 (Uptime Lab's GPIO guide). Which of
these pins the old serial wires sit on, and whether J2 shares a terminal or a housing with P1's TMS wire, is
not recorded by us. Build a new P2 cable by the guide ([UART connector
1](../building/compute-blade/uart-connector-1.md) and 2) first. Then, with the blade powered off (unplug its PoE
cable, and a USB-C cable if one is plugged in), look at Extension Port pins 9 and 10 and UART header pins 3 and 4, and
note which housing sits where:

1. If the serial wires are in a housing of their own, take that housing off the blade and the old cable off
   the card, and leave P1's housing in place.
2. If a serial wire shares a housing, a terminal or a splice with P1's TMS wire, do not cut or pull it: take
   P1's cable off too, and build a new P1 cable by the guide ([JTAG connector
   1](../building/compute-blade/jtag-connector-1.md) and 2).
3. If P1's housing came off or moved, take the card out and the P1 plug out of its socket. Check with the meter,
   as [JTAG connector 2](../building/compute-blade/jtag-connector-2.md) step 2 does, that the plug's contact 4
   (TMS) beeps to the housing cavity over Extension Port pin 9 and to no other cavity. If it does not, or the
   housing is not the guide's 2×5, build a new P1 cable.
4. Fit the new P2 cable as [Fitting](../building/compute-blade/fitting.md) does: with the card out, its plug into
   the card's socket P2, the card back in, its housing on the UART header. Then run the [bench
   check](../building/compute-blade/bench-check.md) before power-on: it is what shows the P2 housing is not
   turned round. Whether P1's TMS works is shown only by the check's `jtag` test, in
   a boot with the header's serial port off ([verifying 3](../building/compute-blade/verifying-3.md)); the meter
   cannot reach it with the card fitted.
