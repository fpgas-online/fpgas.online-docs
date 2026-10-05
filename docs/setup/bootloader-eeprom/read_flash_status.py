# SPDX-License-Identifier: Apache-2.0
"""Print the part and the status registers of a Pi 5's bootloader flash.

    sudo python3 read_flash_status.py

Read commands only (9Fh JEDEC id, 05h SR1, 35h SR2, 15h SR3):
nothing on the flash changes.
"""
import array
import ctypes
import fcntl
import os
import struct


def xfer(fd, tx):
    txb = ctypes.create_string_buffer(bytes(tx), len(tx))
    rxb = ctypes.create_string_buffer(len(tx))
    msg = struct.pack("QQIIHBBBBBB",
                      ctypes.addressof(txb), ctypes.addressof(rxb),
                      len(tx), 1000000, 0, 8, 0, 0, 0, 0, 0)
    # SPI_IOC_MESSAGE(1)
    fcntl.ioctl(fd, 0x40206B00, array.array("B", msg), True)
    return rxb.raw


fd = os.open("/dev/spidev10.0", os.O_RDWR)  # the Pi 5's bootloader flash
print("jedec", xfer(fd, [0x9F, 0, 0, 0])[1:].hex())
for name, cmd in (("SR1", 0x05), ("SR2", 0x35), ("SR3", 0x15)):
    print(name, hex(xfer(fd, [cmd, 0])[1]))
