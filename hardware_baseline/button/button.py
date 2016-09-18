import pigpio
import time

def button(pin, active):
    pi = pigpio.pi()

    pi.set_mode(pin, pigpio.INPUT)

    pi.set_pull_up_down(pin, pigpio.PUD_UP)

    while True:
        v = pi.read(pin)
        if not active:
            v = v ^ 1
        time.sleep(.1)
        print(v)



button(9, 0)