#!/usr/bin/env python3
"""
Created on January 9 11:39:15 2016

@author: Alan Yorinks
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
import signal
import socket
import sys
import time

import zmq


# noinspection PyUnresolvedReferences,PyUnresolvedReferences
# PyUnresolvedReferences,PyUnresolvedReferences,PyUnresolvedReferences
class BackPlane:
    """
    This class instantiates a ZeroMQ forwarder that acts as a software backplane.
    All other components plug into the back plane using the IP address displayed when this process
    starts
    """

    def __init__(self, subscriber_port='43125', publisher_port='43124'):
        """
        This is the constructor for the razmq BackPlane class. The class must be instantiated
        before starting any other razmq modules
        :param subscriber_port: subscriber IP port number
        :param publisher_port: publisher IP port number
        """

        # get ip address of this machine
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # use the google dns
        s.connect(('8.8.8.8', 0))
        self.bp_ip_address = s.getsockname()[0]

        print('\n******************************************')
        print('RAZMQ BackPlane IP address: ' + self.bp_ip_address)
        print('Subscriber Port = ' + subscriber_port)
        print('Publisher  Port = ' + publisher_port)
        print('******************************************')

        self.bp = zmq.Context()
        # establish bp as a ZMQ FORWARDER Device

        # subscribe to any message that any entity publishes
        self.publish_to_bp = self.bp.socket(zmq.SUB)
        bind_string = 'tcp://' + self.bp_ip_address + ':' + publisher_port
        self.publish_to_bp.bind(bind_string)
        # Don't filter any incoming messages, just pass them through
        self.publish_to_bp.setsockopt_string(zmq.SUBSCRIBE, '')

        # publish these messages
        self.subscribe_to_bp = self.bp.socket(zmq.PUB)
        bind_string = 'tcp://' + self.bp_ip_address + ':' + subscriber_port
        self.subscribe_to_bp.bind(bind_string)

        # instantiate the forwarder device
        try:
            zmq.device(zmq.FORWARDER, self.publish_to_bp, self.subscribe_to_bp)
        except KeyboardInterrupt:
            self.clean_up()
            sys.exit()

    # noinspection PyMethodMayBeStatic
    def run_back_plane(self):
        """
        This method runs in a forever loop and just keeps the back plane alive.
        :return:
        """
        while True:
            try:
                time.sleep(.001)
            except KeyboardInterrupt:
                sys.exit(0)

    def clean_up(self):
        self.publish_to_bp.close()
        self.subscribe_to_bp.close()
        self.bp.term()


def bp():
    # noinspection PyShadowingNames

    bp = BackPlane()
    bp.run_back_plane()

    # signal handler function called when Control-C occurs
    # noinspection PyShadowingNames,PyUnusedLocal,PyUnusedLocal
    def signal_handler(signal, frame):
        print('Control-C detected. See you soon.')

        bp.clean_up()
        sys.exit(0)

    # listen for SIGINT
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

if __name__ == '__main__':
    bp()
