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


class BuzzerTestDriver(Razbase):
    """
    This is a test driver for the buzzer

    """

    def __init__(self, back_plane_ip_address=None, subscriber_port='43125', publisher_port='43124', process_name=None):
        """
        :param back_plane_ip_address: Ip address of the backplane
        :param subscriber_port: backplane subscriber port address
        :param publisher_port: backplane publisher port address
        """

        self.subscriber_topic = 'no_subscriber'
        self.publisher_topic = 'user_buzzer_command'

        # initialize the base class
        super().__init__(back_plane_ip_address, subscriber_port, publisher_port, process_name=process_name)

        # wait for connection
        time.sleep(.03)
        # turn on led for 3 seconds
        payload = {'command': 'tone', 'frequency': 1000, 'duration': 1000}
        self.publish_payload(payload, self.publisher_topic)

        time.sleep(3)

        payload = {'command': 'tone', 'frequency': 500, 'duration': 500}
        self.publish_payload(payload, self.publisher_topic)


def buzzer_test_driver():
    # noinspection PyShadowingNames

    parser = argparse.ArgumentParser()
    parser.add_argument("-b", dest="back_plane_ip_address", default="None",
                        help="None or IP address used by Back Plane")
    parser.add_argument("-n", dest="process_name", default="Buzzer Test Driver", help="Set process name in banner")

    args = parser.parse_args()
    kw_options = {}

    if args.back_plane_ip_address != 'None':
        kw_options['back_plane_ip_address'] = args.back_plane_ip_address

    kw_options['process_name'] = args.process_name

    my_buzzer_test_driver = BuzzerTestDriver(**kw_options)

    # signal handler function called when Control-C occurs
    # noinspection PyShadowingNames,PyUnusedLocal,PyUnusedLocal
    def signal_handler(signal, frame):
        print('Control-C detected. See you soon.')

        my_buzzer_test_driver.clean_up()
        sys.exit(0)

    # listen for SIGINT
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


if __name__ == '__main__':
    buzzer_test_driver()
