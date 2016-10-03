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


class Led(Razbase):
    """
    This is the user side interface for an Led control.

    A user may turn on an led {'led_on': 'system_led'}
    A user may turn off an led {'led_off': 'system_led'}
    A user may blink an led for a specified time {'led_blink': 'system_led',
                                                  'blink_on_duration_millisecs': 1000
                                                  'blink_off_duration_millisecs': 1000,
                                                  'number_of_blinks': 100}

    """

    def __init__(self, back_plane_ip_address=None, subscriber_port='43125', publisher_port='43124', process_name=None):
        """

        :param back_plane_ip_address:
        :param subscriber_port:
        :param publisher_port:

        """

        # initialize the base class
        super().__init__(back_plane_ip_address, subscriber_port, publisher_port, process_name=process_name)

        # allow time for connection
        time.sleep(.03)
        self.set_subscriber_topic('user_led_command')
        self.publisher_topic = 'system_led_command'

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
            if command == 'led_on':
                payload = {'command': 'led_on'}
                self.publish_payload(payload, self.publisher_topic)
            elif command == 'led_off':
                payload = {'command': 'led_off'}
                self.publish_payload(payload, self.publisher_topic)
            elif command == 'blink_led':
                blink_rate = payload['blink_rate']
                number_of_blinks = payload['number_of_blinks']
                for blinks in range(number_of_blinks):
                    payload = {'command': 'led_on'}
                    self.publish_payload(payload, self.publisher_topic)
                    time.sleep(blink_rate)
                    payload = {'command': 'led_off'}
                    self.publish_payload(payload, self.publisher_topic)
                    time.sleep(blink_rate)
            else:
                raise ValueError

        except ValueError:
            print('led topic: ' + topic + '  payload: ' + payload)
            raise


def led():
    # noinspection PyShadowingNames

    parser = argparse.ArgumentParser()
    parser.add_argument("-b", dest="back_plane_ip_address", default="None",
                        help="None or IP address used by Back Plane")
    parser.add_argument("-n", dest="process_name", default="LED Front End", help="Set process name in banner")

    args = parser.parse_args()
    kw_options = {}

    if args.back_plane_ip_address != 'None':
        kw_options['back_plane_ip_address'] = args.back_plane_ip_address

    kw_options['process_name'] = args.process_name

    my_led = Led(**kw_options)

    # signal handler function called when Control-C occurs
    # noinspection PyShadowingNames,PyUnusedLocal,PyUnusedLocal
    def signal_handler(signal, frame):
        print('Control-C detected. See you soon.')

        my_led.clean_up()
        sys.exit(0)

    # listen for SIGINT
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

if __name__ == '__main__':
    led()

