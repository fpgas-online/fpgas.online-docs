The RP2350 provides bitstream loading, clock generation, and USB-to-UART
bridging. Three host-side wrapper scripts handle the RP2350 interaction:

| Script | Purpose |
|--------|---------|
| [`tt_fpga_program.py`](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/designs/_host/tt_fpga_program.py) | Program the iCE40 from the Pi via mpremote |
| [`tt_test_wrapper.py`](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/designs/_host/tt_test_wrapper.py) | Program + UART bridge (PTY) + run test |
| [`tt_pmod_wrapper.py`](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/designs/_host/tt_pmod_wrapper.py) | Program + release GPIOs + hand off to RPi GPIO test |
