---
type: reference
owner: documentation maintainers
reader: someone looking for the documents behind the Fomu EVT pages
review: 2026-11-10
---

# Fomu EVT references

**You want the documents and scripts behind the Fomu EVT pages.** Each line names one and says what it holds.

## Outside documents

- [Fomu Workshop](https://workshop.fomu.im): the getting-started guide.
- [Fomu hardware design files](https://github.com/im-tomu/fomu-hardware): the board's hardware repository, with the [EVT PCB](https://github.com/im-tomu/fomu-hardware/tree/evt/hardware/pcb) on the `evt` branch.
- [Crowd Supply campaign](https://www.crowdsupply.com/sutajio-kosagi/fomu): the board's campaign page.
- [Raspberry Pi PMOD HAT](../../pmod/rpi-hat.md): background for the PMOD signalling only, because the Fomu is not fitted with one and sits on the GPIO header directly.

## LiteX and scripts

- [LiteX platform file for the Fomu EVT](https://github.com/litex-hub/litex-boards/blob/master/litex_boards/platforms/kosagi_fomu_evt.py): the board's pins and resources.
- [Hardware verification script](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/verify_hardware.py): `verify_hardware.py` in the test-designs repository, which drives programming.
