---
type: reference
owner: documentation maintainers
reader: someone looking for the test designs of the board
review: 2026-11-10
---

# Tiny Tapeout FPGA demo board test designs

**You want to know which test designs exist for the board, what each verifies, and which script loads it.**

The check that runs on the host is on [fpgas-verify: the Tiny Tapeout demo boards](../../../verify/tt-fpga.md).

The RP2350 provides bitstream loading, clock generation and USB-to-UART bridging. Three host-side wrapper scripts handle the RP2350 interaction. Script names the file in the test-designs repository, and Purpose what it does.

| Script | Purpose |
|--------|---------|
| [`tt_fpga_program.py`](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/designs/_host/tt_fpga_program.py) | Program a bitstream |
| [`tt_test_wrapper.py`](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/designs/_host/tt_test_wrapper.py) | Program + UART bridge (PTY) + run test |
| [`tt_pmod_wrapper.py`](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/designs/_host/tt_pmod_wrapper.py) | Program + release GPIOs + hand off to RPi GPIO test |

Test names the test, Bitstream its design, Wrapper the script that loads it, and What it verifies what a pass shows.

| Test | Bitstream | Wrapper | What it verifies |
|------|-----------|---------|------------------|
| UART echo | [`uart/.../tt_fpga_platform.bin`](https://github.com/fpgas-online/fpgas.online-test-designs/tree/main/designs/uart/) | `tt_test_wrapper.py` | Serial TX/RX via RP2350 bridge |
| SPI Flash ID | [`spi-flash-id/.../tt_fpga_platform.bin`](https://github.com/fpgas-online/fpgas.online-test-designs/tree/main/designs/spi-flash-id/) | `tt_test_wrapper.py` | JEDEC ID readback from on-board flash |
| PMOD loopback | [`pmod-loopback/.../top.bin`](https://github.com/fpgas-online/fpgas.online-test-designs/tree/main/designs/pmod-loopback/) | `tt_pmod_wrapper.py` | GPIO inversion across wired pin pairs |
| PMOD pin ID | [`pmod-pin-id/.../top.bin`](https://github.com/fpgas-online/fpgas.online-test-designs/tree/main/designs/pmod-pin-id/) | `tt_pmod_wrapper.py` | UART TX on each GPIO pin |

The pin ID test and how to read its output are on [Verifying wiring with the pin-id design](../../pin-id.md). The hardware verification script, [`verify_hardware.py`](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/verify_hardware.py), orchestrates the tests.
