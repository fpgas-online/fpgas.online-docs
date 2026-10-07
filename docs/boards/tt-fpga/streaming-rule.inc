**The rule: an FPGA on a demo board is loaded by streaming only**, and no code of ours may write, replace or
delete a file on a demo board. The loader and the tests in fpgas.online-test-designs do not: the demo board's
microcontroller reads the bitstream from the Raspberry Pi over the USB-C cable and passes it straight to the
FPGA.
