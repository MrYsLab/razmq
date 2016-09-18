#!/usr/bin/env python

# 2014-08-26 PCF8591.py

import time

import pigpio

# sudo pigpiod
# ./PCF8591.py

# Connect Pi 3V3 - VCC, Ground - Ground, SDA - SDA, SCL - SCL.

YL_40 = 0x48

pi = pigpio.pi()  # Connect to local Pi.

handle = pi.i2c_open(1, YL_40, 0)

aout = 0

try:
    while True:

        for a in range(0, 4):
            aout = aout + 1
            pi.i2c_write_byte_data(handle, 0x40 | ((a + 1) & 0x03), aout & 0xFF)
            v = pi.i2c_read_byte(handle)
            v = pi.i2c_read_byte(handle)
            print('a: ', a, v)

        time.sleep(0.04)


except:
    pass

pi.i2c_close(handle)
pi.stop()

