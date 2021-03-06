import pigpio
import time

class RightEncoder:
    def __init__(self, pin=25):

        self.pi = pigpio.pi()
        self.pin = pin
        self.pi.set_mode(pin, pigpio.INPUT)
        self.pi.set_pull_up_down(pin, pigpio.PUD_UP)

        cb1 = self.pi.callback(pin, pigpio.EITHER_EDGE, self.cbf)
        self.tick = 0

    def cbf(self, gpio, level, tick):
        # print(gpio, level, tick)
        print(self.tick)
        self.tick += 1


e = RightEncoder()
while True:
    time.sleep(.01)