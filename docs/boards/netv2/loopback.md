# NeTV2: PMOD / GPIO Loopback

**You want to check the GPIO wiring between a NeTV2 and its Raspberry Pi with the loopback test, and need the pins it uses.**

The NeTV2 GPIO loopback uses FPGA pins E13 (input) and E14 (output) — the same
pins as the primary UART. It is a 1-bit loopback through the RPi's GPIO14/15.

| Drive RPi GPIO | FPGA Pin (Input) | Read RPi GPIO | FPGA Pin (Output) |
| -------------- | ---------------- | ------------- | ----------------- |
| GPIO14         | E13              | GPIO15        | E14               |
