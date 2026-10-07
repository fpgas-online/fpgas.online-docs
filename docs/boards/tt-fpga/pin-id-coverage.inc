**How many wires pin-ID covers.** Measured so far: **18 of the 24** signal wires, every wire that has a
Raspberry Pi GPIO to itself ([sources](/boards/tt-fpga/wiring/sources.md)). The other six are on the three
GPIOs that HAT ports JA and JB share (`ui_in[1]` to `ui_in[3]`, `uio[1]` to `uio[3]`). Builds of the test
designs made after 0.0.post1151 send on those six in turns, so that each can be read (the change of
5 October 2026, [test-designs issue #142](https://github.com/fpgas-online/fpgas.online-test-designs/issues/142));
the check's documentation describes those builds, and says all 24. The check that passed on 5 October 2026 ran
bitstreams 0.0.post1119, which judged 18 of 24 (read on 5 October 2026). The root deployed at welland on
6 October 2026 carries 0.0.post1189 (our deploy record of that day); no result of a run of it is recorded
here yet.
