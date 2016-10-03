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


class Adxl3451DisableTester(Razbase):
    """
    This is a test driver

    This tester will send enable/disable commands to the pfc8591
    """

    def __init__(self,back_plane_ip_address=None, subscriber_port='43125', publisher_port='43124', enable=True,
                 process_name=None):
        """
        :paramback_plaine_ip_address:
        :param subscriber_port:
        :param publisher_port:
        """

        self.subscriber_topic = 'no_subscriber'
        self.publisher_topic = 'adxl345'

        # initialize the base class
        super().__init__(back_plane_ip_address, subscriber_port, publisher_port, process_name=process_name)

        # wait for connection
        time.sleep(.03)
        # turn on led for 3 seconds
        if enable:
            payload = {'command': 'enable'}
            self.publish_payload(payload, self.publisher_topic)

        else:
            payload = {'command': 'disable'}
            self.publish_payload(payload, self.publisher_topic)


def adxl3451_disable_tester():
    # noinspection PyShadowingNames

    parser = argparse.ArgumentParser()
    parser.add_argument("-b", dest="back_plane_ip_address", default="None",
                        help="None or IP address used by Back Plane")
    parser.add_argument("-n", dest="process_name", default="ADXL345 Disable Tester", help="Set process name in banner")

    args = parser.parse_args()
    kw_options = {}

    if args.back_plane_ip_address != 'None':
        kw_options['back_plane_ip_address'] = args.back_plane_ip_address

    kw_options['process_name'] = args.process_name

    my_tester = Adxl3451DisableTester(**kw_options)

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
    adxl3451_disable_tester()
