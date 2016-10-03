# !/usr/bin/env python3

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
import umsgpack
import zmq
import argparse

from razmq.razbase.razbase import Razbase


class I2CPcf8591(Razbase):
    """
    This class continuously reads the 3 A/D ports for line follower data_files. It may be stopped
    started by other processes that publish a pfc8591 topic message with a payload of enable or
    disable

    """

    def __init__(self, back_plane_ip_address=None, subscriber_port='43125', publisher_port='43124',
                 device_address=72, continuous_read=True, enabled=True, process_name=None):
        """

        :param back_plane_ip_address: Address of the backplane
        :param subscriber_port: Subscriber port of the backplane
        :param publisher_port: Publish port of the backplane
        :param device_address: This is i2c address of this device
        :param continuous_read: Default is to have the device automatically update
                                the IR sensor values.
        :param enabled: start or stop streaming via msgpack message described above
        """

        super().__init__(back_plane_ip_address, subscriber_port, publisher_port, process_name=process_name)
        self.set_subscriber_topic('I2C' + str(device_address))
        self.set_subscriber_topic('pfc8591')
        self.publisher_topic = 'i2c_backend' + str(device_address)

        self.continuous_read = continuous_read

        # this flag is used to determine when to send out next read request
        self.wait_for_data = False

        self.enabled = enabled
        self.device_address = device_address
        self.last_data = [0, 0, 0]
        self.atod_channel = 0x40
        self.atod_index = 0

        # this is a descriptor for the i2c commands to be sent to the i2c target device
        self.i2c_device = {
            "pcf8591": {
                "commands": {
                    "init": [
                        {
                            u"command": u"init",
                            u"device_address": device_address
                        }
                    ],
                    "read": [
                        {
                            u"command": u"write_byte",
                            u"device_address": device_address,
                            u"value": self.atod_channel
                        }, {
                            u"command": "read_byte",
                            u"device_address": device_address,
                            u"report": False,
                            u"tag": 0
                        }, {

                            u"command": "read_byte",
                            u"device_address": device_address,
                            u"report": True,
                            u'tag': self.atod_index

                        }]
                }
            }
        }

        # initialize the i2c device
        time.sleep(.3)

        self.initialize_device()
        time.sleep(.3)

        # kick off the receive loop
        self.receive_loop()

    def receive_loop(self):
        """
        This is the receive loop for zmq messages.

        :return:
        """
        while True:
            try:
                data = self.subscriber.recv_multipart(zmq.NOBLOCK)
                self.incoming_message_processing(data[0].decode(), umsgpack.unpackb(data[1]))
                # time.sleep(.001)
            except zmq.error.Again:
                try:
                    if not self.wait_for_data:
                        if self.enabled:
                            self.read_device()
                    time.sleep(.2)
                except KeyboardInterrupt:
                    self.clean_up()

    # noinspection PyMethodMayBeStatic
    def incoming_message_processing(self, topic, payload):
        """
        This method processes the incoming messages
        :param topic: Message Topic string
        :param payload: Message Data
        :return:
        """

        try:
            # this is from the RPi
            if topic == "I2C" + str(self.device_address):
                # data1 = payload[0]['data_files']
                # data2 = payload[1]['data_files']
                # data3 = payload[2]['data_files']
                # self.last_data = [data1, data2, data3]
                if payload['tag'] == 0:
                    self.last_data[0] = payload['data_files']
                if payload['tag'] == 1:
                    self.last_data[1] = payload['data_files']
                if payload['tag'] == 2:
                    self.last_data[2] = payload['data_files']

                if payload['tag'] == 2:
                    self.wait_for_data = False
            # this is from the user or gui
            elif topic == "pfc8591":
                if payload["command"] == 'enable':
                    self.enabled = True
                else:
                    self.enabled = False

        except ValueError:
            print('pcf8591 - Unexpected topic: ', topic)
            pass

    def initialize_device(self):
        """
        This method sends out the i2c initialization sequence to the MCUs.
        :return: None
        """
        msg = self.i2c_device['pcf8591']['commands']['init']
        self.publish_payload(msg, self.publisher_topic)

    def read_device(self):

        if not self.wait_for_data:
            self.wait_for_data = True
            for a in range(0, 3):
                msg = self.i2c_device['pcf8591']['commands']['read']
                msg[0]['value'] = a + 0x40
                msg[2]['tag'] = a
                self.publish_payload(msg, self.publisher_topic)

    def get_last_data(self):
        """
        This method retrieves the data_files retrieved from the last read - continuous or manual
        :return:
        """
        return self.last_data


def i2c_pcf8591():
    # noinspection PyShadowingNames

    parser = argparse.ArgumentParser()
    parser.add_argument("-b", dest="back_plane_ip_address", default="None",
                        help="None or IP address used by Back Plane")
    parser.add_argument("-n", dest="process_name", default="PCF8591 Front End", help="Set process name in banner")

    args = parser.parse_args()
    kw_options = {}

    if args.back_plane_ip_address != 'None':
        kw_options['back_plane_ip_address'] = args.back_plane_ip_address

    kw_options['process_name'] = args.process_name

    my_i2c_pcf8591 = I2CPcf8591(**kw_options)

    # signal handler function called when Control-C occurs
    # noinspection PyShadowingNames,PyUnusedLocal,PyUnusedLocal
    def signal_handler(signal, frame):

        print('Control-C detected. See you soon.')

        my_i2c_pcf8591.clean_up()
        sys.exit(0)

    # listen for SIGINT
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


if __name__ == '__main__':
    i2c_pcf8591()
