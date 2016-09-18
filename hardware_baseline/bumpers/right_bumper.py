import time

import pigpio


class RightBumper:
    def __init__(self, pin=6):

        self.pi = pigpio.pi()

        self.pin = pin
        self.pi.set_mode(pin, pigpio.INPUT)
        #self.pi.set_pull_up_down(pin, pigpio.PUD_OFF)

    # cb1 = self.pi.callback(pin, pigpio.EITHER_EDGE, self.cbf)
        self.tick = 0

        while True:
            state = self.pi.read(pin)
            if state:
                pass
            else:
                print('right bump')
                time.sleep(.3)
                while not self.pi.read(pin):
                    pass
                print('right release')

    def cbf(self, gpio, level, tick):
        # print(gpio, level, tick)
        # print(self.tick)
        # self.tick += 1
        print('bump')
        time.sleep(.1)


e = RightBumper()
# while True:
#     time.sleep(.01)
