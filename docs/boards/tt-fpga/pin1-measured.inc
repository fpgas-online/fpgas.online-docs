**Pin 1, as measured on the boards at welland.** Cabled as they are, those boards read their wiring with the
pin identification design on 29 September and 4 October 2026, and one of them passed the whole check on
5 October 2026 (its `pin-id` included): iCE40 pin 13 (`ui_in[0]`) reaches GPIO8, which is Pmod HAT port JA
pin 1 ([sources](/boards/tt-fpga/wiring/sources.md)), and each of the 18 wires measured there joins pin n of
its header to pin n of its port. So on those boards the cables run pin 1 to pin 1. A measurement through the
wires cannot show which end of a socket pin 1 is, and says nothing of a cable you fit yourself: find pin 1 on
each connector.
