import pigpio
import time

class Motor:

    def __init__(self, ain1=17, ain2=27, bin1=22, bin2=23):
        self.ain1 = ain1
        self.ain2 = ain2
        self.bin1 = bin1
        self.bin2 = bin2

        self.pi = pigpio.pi()

        # setup all pins as outputs and set to low
        self.pi.set_mode(ain1, pigpio.OUTPUT)
        self.pi.write(ain1, 0)

        self.pi.set_mode(ain2, pigpio.OUTPUT)
        self.pi.write(ain2, 0)

        self.pi.set_mode(bin1, pigpio.OUTPUT)
        self.pi.write(ain1, 0)

        self.pi.set_mode(bin2, pigpio.OUTPUT)
        self.pi.write(ain2, 0)

        # left forward
        self.pi.set_PWM_dutycycle(ain1, 128)
        # time.sleep(2)
        self.pi.set_PWM_dutycycle(ain1, 0)
        self.pi.write(ain1, 0)

        time.sleep(5)

        # left reverse
        self.pi.write(ain2, 1)

        self.pi.set_PWM_dutycycle(ain2, 128)
        time.sleep(2)
        self.pi.set_PWM_dutycycle(ain2, 0)
        self.pi.write(ain1, 0)

        # right forward
        self.pi.set_PWM_dutycycle(bin1, 128)
        time.sleep(2)
        self.pi.set_PWM_dutycycle(bin1, 0)
        self.pi.write(bin2, 0)

        time.sleep(2)

        # right reverse
        self.pi.write(bin2, 1)

        self.pi.set_PWM_dutycycle(bin2, 128)
        time.sleep(2)
        self.pi.set_PWM_dutycycle(bin2, 0)
        self.pi.write(bin2, 0)



m = Motor()
print('done')