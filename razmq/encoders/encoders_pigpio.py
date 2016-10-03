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


class EncodersPigpio(Razbase):
    """
    This class publishes encoder ticks for each encoder
    It uses a separate callback for each wheel
    """

    def __init__(self, router_ip_address=None, subscriber_port='43125', publisher_port='43124',
                 left_encoder_pin=24, right_encoder_pin=25, edge_detect=pigpio.RISING_EDGE, process_name=None):

        """

        :param router_ip_address:
        :param subscriber_port:
        :param publisher_port:
        :param left_encoder_pin:
        :param right_encoder_pin:
        :param edge_detect:
        """
        # initialize the base class
        super().__init__(router_ip_address, subscriber_port, publisher_port, process_name=process_name)

        self.set_subscriber_topic('system_encoder_throttle_count')

        self.left_encoder_pin = left_encoder_pin
        self.right_encoder_pin = right_encoder_pin

        # allow time for connection
        time.sleep(.03)

        # configure the gpio pins
        self.pi = pigpio.pi()

        self.pi.set_mode(self.left_encoder_pin, pigpio.INPUT)
        self.pi.set_mode(self.right_encoder_pin, pigpio.INPUT)

        self.pi.set_pull_up_down(self.left_encoder_pin, pigpio.PUD_UP)
        self.pi.set_pull_up_down(self.right_encoder_pin, pigpio.PUD_UP)

        self.pi.callback(self.left_encoder_pin, edge_detect, self.left_encoder_callback)
        self.pi.callback(self.right_encoder_pin, edge_detect, self.right_encoder_callback)

        self.left_count = 0
        self.right_count = 0

        # only send a tick message for each .25 inches of wheel motion
        # the throttle count may be modified using the throttle count message - see incoming messages
        self.throttle_count = 6

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
        if topic == 'system_encoder_throttle_count':
            self.throttle_count = payload['throttle_count']
        else:
            print('EncoderPigpio: unexpected incoming message ' + topic + ' ' + payload)

    def left_encoder_callback(self, pin, level, tick):
        self.left_count += 1
        if self.left_count >= self.throttle_count:
            self.left_count = 0
            payload = {'report': 'left_encoder_tick', 'pin': pin, 'level': level, 'tick': tick}
            self.publish_payload(payload, 'left_encoder_tick')

    def right_encoder_callback(self, pin, level, tick):
        self.right_count += 1
        if self.right_count >= self.throttle_count:
            self.right_count = 0
            payload = {'report': 'right_encoder_tick', 'pin': pin, 'level': level, 'tick': tick}
            self.publish_payload(payload, 'right_encoder_tick')


def encoders_pigpio():
    # noinspection PyShadowingNames

    parser = argparse.ArgumentParser()
    parser.add_argument("-b", dest="back_plane_ip_address", default="None",
                        help="None or IP address used by Back Plane")
    parser.add_argument("-n", dest="process_name", default="Encoders Back End", help="Set process name in banner")

    args = parser.parse_args()
    kw_options = {}

    if args.back_plane_ip_address != 'None':
        kw_options['back_plane_ip_address'] = args.back_plane_ip_address

    kw_options['process_name'] = args.process_name

    my_encoders_pigpio = EncodersPigpio(**kw_options)

    # signal handler function called when Control-C occurs
    # noinspection PyShadowingNames,PyUnusedLocal,PyUnusedLocal
    def signal_handler(signal, frame):
        print('Control-C detected. See you soon.')

        my_encoders_pigpio.clean_up()
        sys.exit(0)

        # listen for SIGINT

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


if __name__ == '__main__':
    encoders_pigpio()

