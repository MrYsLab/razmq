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


class Buzzer(Razbase):
    """
    This is the user side interface for the buzzer.

    A user may create a tone {'command': 'tone', 'frequency': FREQUENCY, 'duration': DURATION}
    """

    def __init__(self, back_plane_ip_address=None, subscriber_port='43125', publisher_port='43124', process_name=None):
        """

        :param back_plane_ip_address: ip address of the backplane
        :param subscriber_port: backplane subscriber port
        :param publisher_port: backplane publisher port

        """

        # initialize the base class
        super().__init__(back_plane_ip_address, subscriber_port, publisher_port, process_name=process_name)

        # allow time for connection
        time.sleep(.03)
        self.set_subscriber_topic('user_buzzer_command')
        self.publisher_topic = 'system_buzzer_command'

        # receive loop is defined in the base class
        self.receive_loop()

    # noinspection PyMethodMayBeStatic
    def incoming_message_processing(self, topic, payload):
        """

        :param topic: Message Topic string
        :param payload: Message Data
        :return:
        """
        try:
            command = payload['command']
            if command == 'tone':
                payload = {'command': 'tone', 'frequency': payload['frequency'], 'duration': payload['duration']}
                self.publish_payload(payload, self.publisher_topic)
            else:
                raise ValueError

        except ValueError:
            print('buzzer topic: ' + topic + '  payload: ' + payload)
            raise


def buzzer():
    # noinspection PyShadowingNames

    parser = argparse.ArgumentParser()
    parser.add_argument("-b", dest="back_plane_ip_address", default="None",
                        help="None or IP address used by Back Plane")
    parser.add_argument("-n", dest="process_name", default="Buzzer Front End", help="Set process name in banner")

    args = parser.parse_args()
    kw_options = {}

    if args.back_plane_ip_address != 'None':
        kw_options['back_plane_ip_address'] = args.back_plane_ip_address

    kw_options['process_name'] = args.process_name

    my_buzzer = Buzzer(**kw_options)

    # signal handler function called when Control-C occurs
    # noinspection PyShadowingNames,PyUnusedLocal,PyUnusedLocal
    def signal_handler(signal, frame):

        print('Control-C detected. See you soon.')

        my_buzzer.clean_up()
        sys.exit(0)

    # listen for SIGINT
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

if __name__ == '__main__':
    buzzer()

