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


class SwitchesPigpio(Razbase):
    """
    This class monitors the push-button switch and left and right bumpers. It uses glitch filtering to do switch
    de-bounce. It uses a glitch value of 20 ms.

    It uses a separate callback for each switch
    """

    def __init__(self, back_plane_ip_address=None, subscriber_port='43125', publisher_port='43124', button_pin=9,
                 left_bumper_pin=5, right_bumper_pin=6, glitch_time=20000, process_name=None):
        """

        :param back_plane_ip_address:
        :param subscriber_port:
        :param publisher_port:
        :param button_pin:
        :param left_bumper_pin:
        :param right_bumper_pin:
        :param glitch_time:
        """

        # initialize the base class
        super().__init__(back_plane_ip_address, subscriber_port, publisher_port, process_name=process_name)

        # self.set_subscriber_topic('system_switch_bank_command')

        self.button_pin = button_pin
        self.left_bumper_pin = left_bumper_pin
        self.right_bumper_pin = right_bumper_pin

        # allow time for connection
        time.sleep(.03)

        # configure the gpio pins
        self.pi = pigpio.pi()

        # button
        self.pi.set_pull_up_down(self.button_pin, pigpio.PUD_UP)

        self.pi.set_glitch_filter(self.button_pin, glitch_time)
        self.pi.set_mode(self.button_pin, pigpio.INPUT)

        self.pi.callback(self.button_pin, pigpio.EITHER_EDGE, self.button_callback)

        # left_bumper
        self.pi.set_glitch_filter(self.left_bumper_pin, glitch_time)
        self.pi.set_mode(self.left_bumper_pin, pigpio.INPUT)

        self.pi.callback(self.left_bumper_pin, pigpio.EITHER_EDGE, self.left_bumper_callback)

        # right_bumper
        self.pi.set_glitch_filter(self.right_bumper_pin, glitch_time)
        self.pi.set_mode(self.right_bumper_pin, pigpio.INPUT)

        self.pi.callback(self.right_bumper_pin, pigpio.EITHER_EDGE, self.right_bumper_callback)

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
        print('SwitchBankPigpio: unexpected incoming message ' + topic + ' ' + payload)

    def button_callback(self, pin, level, tick):
        payload = {'report': 'button_state_change', 'pin': pin, 'level': level, 'tick': tick}
        self.publish_payload(payload, 'button_state_change')

    def left_bumper_callback(self, pin, level, tick):
        payload = {'report': 'left_bumper_state_change', 'pin': pin, 'level': level, 'tick': tick}
        self.publish_payload(payload, 'left_bumper_state_change')

    def right_bumper_callback(self, pin, level, tick):
        payload = {'report': 'right_bumper_state_change', 'pin': pin, 'level': level, 'tick': tick}
        self.publish_payload(payload, 'right_bumper_state_change')


def switches_pigpio():
    # noinspection PyShadowingNames

    parser = argparse.ArgumentParser()
    parser.add_argument("-b", dest="back_plane_ip_address", default="None",
                        help="None or IP address used by Back Plane")
    parser.add_argument("-n", dest="process_name", default="Switches Back End", help="Set process name in banner")

    args = parser.parse_args()
    kw_options = {}

    if args.back_plane_ip_address != 'None':
        kw_options['back_plane_ip_address'] = args.back_plane_ip_address

    kw_options['process_name'] = args.process_name

    my_switches = SwitchesPigpio(**kw_options)

    # signal handler function called when Control-C occurs
    # noinspection PyShadowingNames,PyUnusedLocal,PyUnusedLocal
    def signal_handler(signal, frame):
        print('Control-C detected. See you soon.')

        my_switches.clean_up()
        sys.exit(0)

    # listen for SIGINT
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


if __name__ == '__main__':
    switches_pigpio()

