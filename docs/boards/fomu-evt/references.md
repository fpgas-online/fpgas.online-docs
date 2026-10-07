# Fomu EVT: references

**You want the sources behind these pages.**

## References

- LiteX platform file:
  <https://github.com/litex-hub/litex-boards/blob/master/litex_boards/platforms/kosagi_fomu_evt.py>
- Fomu Workshop (getting started guide): <https://workshop.fomu.im>
- Fomu hardware design files: <https://github.com/im-tomu/fomu-hardware>, with
  the [EVT PCB](https://github.com/im-tomu/fomu-hardware/tree/evt/hardware/pcb)
  on the `evt` branch
- Crowd Supply campaign: <https://www.crowdsupply.com/sutajio-kosagi/fomu>
- [Raspberry Pi PMOD HAT](../pmod/rpi-hat.md), referenced by the pin-mapping notes.
  The Fomu is not fitted with one — it sits on the GPIO header directly — so the
  HAT page is background for the PMOD signalling only.
- [Hardware verification script](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/verify_hardware.py)
  (`verify_hardware.py` in the test-designs repository), which drives
  programming and the PoE reset recovery.
