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

from razmq.razbase.razbase import Razbase


class LedTestDriver(Razbase):
    """
    This is a test driver

    A user may turn on an led {'led_on': 'system_led'}
    A user may turn off an led {'led_off': 'system_led'}
    A user may blink an led for a specified time {'led_blink': 'system_led',
                                                  'blink_rate_millisecs': 1000,
                                                  'blink_duration_millisecs' : 1000 }

    , turn off an led and blink an led at a specified rate for a specified
    time
    """

    def __init__(self, back_plane_ip_address=None, subscriber_port='43125', publisher_port='43124', process_name=None):
        """
        :param back_plane_id_address:
        :param subscriber_port:
        :param publisher_port:
        """

        self.subscriber_topic = 'no_subscriber'
        self.publisher_topic = 'user_led_command'

        # initialize the base class
        super().__init__(back_plane_ip_address, subscriber_port, publisher_port, process_name=process_name)

        # wait for connection
        time.sleep(.03)
        # turn on led for 3 seconds
        payload = {'command': 'led_on'}
        self.publish_payload(payload, self.publisher_topic)

        time.sleep(3)

        # turn off led for 1 second

        payload = {'command': 'led_off'}
        self.publish_payload(payload, self.publisher_topic)

        time.sleep(1)

        # blink led 5 times with 1 second duration

        payload = {'command': 'blink_led',
                   'blink_rate': 1,
                   'number_of_blinks': 5}
        self.publish_payload(payload, self.publisher_topic)

        # blink led 2 times with 3 second duration
        payload = {'command': 'blink_led',
                   'blink_rate': .5,
                   'number_of_blinks': 10}
        self.publish_payload(payload, self.publisher_topic)


def led_test_driver():
    # noinspection PyShadowingNames

    parser = argparse.ArgumentParser()
    parser.add_argument("-b", dest="back_plane_ip_address", default="None",
                        help="None or IP address used by Back Plane")
    parser.add_argument("-n", dest="process_name", default="PFC8591 Disable Tester", help="Set process name in banner")

    args = parser.parse_args()
    kw_options = {}

    if args.back_plane_ip_address != 'None':
        kw_options['back_plane_ip_address'] = args.back_plane_ip_address

    kw_options['process_name'] = args.process_name

    my_tester = LedTestDriver(**kw_options)

    # signal handler function called when Control-C occurs
    # noinspection PyShadowingNames,PyUnusedLocal,PyUnusedLocal
    def signal_handler(signal, frame):
        print('Control-C detected. See you soon.')

        my_tester.clean_up()
        sys.exit(0)

    # listen for SIGINT
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


if __name__ == '__main__':
    led_test_driver()
