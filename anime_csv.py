#!/usr/bin/env python
#
# Read data from a csv file, and send it to the anime matrix over USB.
# Template.csv is provided with an outline of the matrix.
# The template has 61 rows, with up to 34 integers 0..255.
# It is more or less to scale, for easy manual composition.

import sys
import struct as st
import usb.core
import usb.util
import csv

# send one message to anime over USB 
def write(data: bytes) -> int:
    ret = dev.ctrl_transfer(
        bmRequestType=0x21,    # REQUEST_TYPE_CLASS | RECIPIENT_INTERFACE | ENDPOINT_OUT
        bRequest=0x9,          # SET_REPORT
        wValue=0x35e,          # Feature 0x5e('^')
        wIndex=0,
        data_or_wLength=data,  # 640 max
        timeout=500)
    return ret

# helper to write data chunks from large data array
def writeat(start: int, data: bytes) -> int:
    return write(b'^\xc0\x02' + st.pack('<HH', start, len(data)) + data)

path = sys.argv[1]
data = []
    
# read the csv LED data from the file
with open(path, 'r') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        for item in row:
            data.append(int(item))

# find our device
dev = usb.core.find(idVendor=0x0b05, idProduct=0x193b)

if dev is None:
    raise ValueError('Device not found')

# send the initialization data packets
write(b'^ASUS Tech.Inc.\0')
# boot off
write(b'^\xc3\x01\x80')
# commit
write(b'^\xc4\x01\x80')
# on
write(b'^\xc0\x04\x03')
# commit
write(b'^\xc4\x01\x80')

# write the 1449 data bytes 632 bytes at a time 
writeat(1, bytes(data[:632]))
writeat(1 + 632, bytes(data[632:2 * 632]))
writeat(1 + (2 * 632), bytes(data[2 * 632:]))
# flush
write(b'^\xc0\x03')

exit(0)
