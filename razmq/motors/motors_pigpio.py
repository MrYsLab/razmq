"""
Copyright (c) 2016 Alan Yorinks All right reserved.

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public
License as published by the Free Software Foundation; either
version 3 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""


import time
import signal
import sys
import argparse
import pigpio

from razmq.razbase.razbase import Razbase


class MotorsPigpio(Razbase):
    """
    This is the robot pigpio side interface for motor control.

    This is the user side interface for motor control


        Move left motor forward with a speed of 100:
        {'command': 'left_motor_forward', 'speed': 100 }

        Move left motor reverse with a speed of 100:
        {'command': 'left_motor_reverse', 'speed': 100 }


        Move left motor forward with a speed of 100:
        {'command': 'right_motor_forward', 'speed': 100 }

        Move left motor reverse with a speed of 100:
        {'command': 'right_motor_reverse', 'speed': 100 }

        Brake left motor
        {'command': 'left_motor_brake' }}

        Coast left motor
        {'command': 'left_motor_coast' }}

        Brake right motor
        {'command': 'right_motor_brake' }}

        Coast right motor
        {'command': 'right_motor_coast' }}


        Drive/coast or drive/brake operation with MODE=0 (IN/IN)
        xIN1	xIN2	xOUT1	xOUT2	operating mode
        0	    0	    OPEN	OPEN	coast (outputs off)
        PWM	    0	    PWM	    L	    forward at speed PWM %
        0	    PWM	    L	    PWM	    reverse at speed PWM %
        1	    1	    L	    L	    brake low (outputs shorted to ground)

    """

    def __init__(self, back_plane_ip_address=None, subscriber_port='43125', publisher_port='43124',
                 ain1=17, ain2=27, bin1=22, bin2=23, process_name=None):
        """

        :param back_plane_ip_address:
        :param subscriber_port:
        :param publisher_port:
        :param ain1:
        :param ain2:
        :param bin1:
        :param bin2:
        """

        # initialize the base class
        super().__init__(back_plane_ip_address, subscriber_port, publisher_port, process_name=process_name)

        self.set_subscriber_topic('system_motor_command')
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
        self.pi.write(bin1, 0)

        self.pi.set_mode(bin2, pigpio.OUTPUT)
        self.pi.write(bin2, 0)

        # allow time for connection
        time.sleep(.03)

        # this class does not publish any messages

        # receive loop is defined in the base class
        self.receive_loop()

    # noinspection PyMethodMayBeStatic
    def incoming_message_processing(self, topic, payload):
        """
        Override this method with a message processor for the application

        :param topic: Message Topic string
        :param payload: Message Data
        :return:
        """
        try:
            command = payload['command']
            if command == 'left_motor_forward':
                speed = payload['speed']
                self.pi.set_PWM_dutycycle(self.ain2, 0)
                self.pi.write(self.ain2, 0)
                self.pi.set_PWM_dutycycle(self.ain1, speed)

            elif command == 'left_motor_reverse':
                speed = payload['speed']
                self.pi.set_PWM_dutycycle(self.ain1, 0)
                self.pi.write(self.ain1, 0)
                self.pi.set_PWM_dutycycle(self.ain2, speed)

            elif command == 'left_motor_brake':
                self.pi.set_PWM_dutycycle(self.ain1, 0)
                self.pi.set_PWM_dutycycle(self.ain2, 0)
                self.pi.write(self.ain1, 1)
                self.pi.write(self.ain2, 1)

            elif command == 'left_motor_coast':
                self.pi.set_PWM_dutycycle(self.ain1, 0)
                self.pi.set_PWM_dutycycle(self.ain2, 0)
                self.pi.write(self.ain1, 0)
                self.pi.write(self.ain2, 0)

            elif command == 'right_motor_forward':
                speed = payload['speed']
                self.pi.set_PWM_dutycycle(self.bin2, 0)
                self.pi.write(self.bin2, 0)
                self.pi.set_PWM_dutycycle(self.bin1, speed)

            elif command == 'right_motor_reverse':
                speed = payload['speed']
                self.pi.set_PWM_dutycycle(self.bin1, 0)
                self.pi.write(self.bin1, 0)
                self.pi.set_PWM_dutycycle(self.bin2, speed)

            elif command == 'right_motor_brake':
                self.pi.set_PWM_dutycycle(self.bin1, 0)
                self.pi.set_PWM_dutycycle(self.bin2, 0)
                self.pi.write(self.bin1, 1)
                self.pi.write(self.bin2, 1)

            elif command == 'right_motor_coast':
                self.pi.set_PWM_dutycycle(self.bin1, 0)
                self.pi.set_PWM_dutycycle(self.bin2, 0)
                self.pi.write(self.bin1, 0)
                self.pi.write(self.bin2, 0)
            else:
                raise ValueError

        except ValueError:
            print('motor topic: ' + topic + '  payload: ' + payload)
            raise

    def shut_down_and_coast_motors(self):
        self.pi.set_PWM_dutycycle(self.ain1, 0)
        self.pi.set_PWM_dutycycle(self.ain2, 0)
        self.pi.write(self.ain1, 0)
        self.pi.write(self.ain2, 0)

        self.pi.set_PWM_dutycycle(self.bin1, 0)
        self.pi.set_PWM_dutycycle(self.bin2, 0)
        self.pi.write(self.bin1, 0)
        self.pi.write(self.bin2, 0)


def motors_pigpio():
    # noinspection PyShadowingNames

    parser = argparse.ArgumentParser()
    parser.add_argument("-b", dest="back_plane_ip_address", default="None",
                        help="None or IP address used by Back Plane")
    parser.add_argument("-n", dest="process_name", default="Motors Back End", help="Set process name in banner")

    args = parser.parse_args()
    kw_options = {}

    if args.back_plane_ip_address != 'None':
        kw_options['back_plane_ip_address'] = args.back_plane_ip_address

    kw_options['process_name'] = args.process_name

    my_motors_pigpio = MotorsPigpio(**kw_options)

    # signal handler function called when Control-C occurs
    # noinspection PyShadowingNames,PyUnusedLocal,PyUnusedLocal
    def signal_handler(signal, frame):
        print('Control-C detected. See you soon.')

        my_motors_pigpio.clean_up()
        sys.exit(0)

    # listen for SIGINT
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

if __name__ == '__main__':
    motors_pigpio()

