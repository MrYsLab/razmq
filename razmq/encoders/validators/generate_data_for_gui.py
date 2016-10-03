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
import zmq
import umsgpack
import argparse

from razmq.razbase.razbase import Razbase

class GenerateEncoderData(Razbase):
    """
    This class generates data to simulate the data coming from the Rpi. It is intended to test the GUI
    """

    def __init__(self, back_plane_ip_address=None, subscriber_port='43125', publisher_port='43124', process_name=None,
                 delay=1):
        """

        :param back_plane_ip_address: ip address of the backplane
        :param subscriber_port: backplane subscriber ort
        :param publisher_port: backplane publisher port

        """
        # initialize the base class
        self.delay = delay
        super().__init__(back_plane_ip_address, subscriber_port, publisher_port, process_name=process_name)

        # allow time for connection
        time.sleep(.03)

        # receive loop is defined in the base class
        self.receive_loop()

    def receive_loop(self):
        """
        This is the receive loop for zmq messages.

        It is assumed that this method will be overwritten to meet the needs of the application and to handle
        received messages.
        :return:
        """
        while True:
            try:
                data = self.subscriber.recv_multipart(zmq.NOBLOCK)
                self.incoming_message_processing(data[0].decode(), umsgpack.unpackb(data[1]))
                # time.sleep(.001)
            except zmq.error.Again:
                try:
                    time.sleep(self.delay)
                    payload = {'report': 'left_encoder_tick', 'pin': 4, 'level': 0, 'tick': 1234}
                    self.publish_payload(payload, 'left_encoder_tick' )
                except KeyboardInterrupt:
                    self.clean_up()


def generate_encoder_data():
    # noinspection PyShadowingNames

    parser = argparse.ArgumentParser()
    parser.add_argument("-b", dest="back_plane_ip_address", default="None", help="None or IP address used by Back Plane")
    parser.add_argument("-n", dest="process_name", default="encoder emulator", help="Set process name in banner")
    parser.add_argument("-d", dest="delay", default=".01", help="Delay between messages")


    args = parser.parse_args()
    kw_options = {}

    if args.back_plane_ip_address != 'None':
        kw_options['back_plane_ip_address'] = args.back_plane_ip_address

    kw_options['process_name'] = args.process_name


    kw_options['delay'] = float(args.delay)

    # signal handler function called when Control-C occurs
    # noinspection PyShadowingNames,PyUnusedLocal,PyUnusedLocal
    def signal_handler(signal, frame):
        print("Control-C detected. See you soon.")
        sys.exit(0)

    # listen for SIGINT
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    data_gen = GenerateEncoderData(**kw_options)

    # signal handler function called when Control-C occurs
    # noinspection PyShadowingNames,PyUnusedLocal,PyUnusedLocal
    def signal_handler(signal, frame):
        print('Control-C detected. See you soon.')

        data_gen.clean_up()
        sys.exit(0)

    # listen for SIGINT
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


if __name__ == '__main__':
    generate_encoder_data()
