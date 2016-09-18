import pigpio
import time

def led(pin):
    pi = pigpio.pi()

    pi.set_mode(pin, pigpio.OUTPUT)


    while True:
        pi.write(pin, 1)
        time.sleep(1)
        pi.write(pin, 0)
        time.sleep(1)

led(11)