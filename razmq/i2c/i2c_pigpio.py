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

import signal
import sys
import argparse
import pigpio
import umsgpack

from razmq.razbase.razbase import Razbase


class I2cPigpio(Razbase):
    """
    This class directs i2c commands to the i2c pins using the i2c device address as a qualifier
    """

    def __init__(self, back_plane_ip_address=None, subscriber_port='43125', publisher_port='43124', board='1',
                 process_name=None):
        """

        :param back_plane_ip_address:
        :param subscriber_port:
        :param publisher_port:
        :param board:
        :param process_name:
        """
        super().__init__(back_plane_ip_address, subscriber_port, publisher_port, process_name=process_name)
        self.board_num = board
        self.pi = pigpio.pi()
        self.set_subscriber_topic('i2c')
        self.i2c_addr = None
        self.i2c_handle_dict = {}
        self.value = 0
        self.receive_loop()

    # noinspection PyMethodMayBeStatic
    def incoming_message_processing(self, topic, payload):
        """
        Override this method with a message processor for the application

        :param topic: Message Topic string
        :param payload: Message Data
        :return:
        """

        if 'i2c' in topic:
            # first item is always the device address, so extract it
            # iterate through everything in the list of commands
            for i in payload:
                command = i['command']
                self.i2c_addr = i['device_address']
                if command == 'init':
                    handle = self.pi.i2c_open(1, self.i2c_addr)
                    self.i2c_handle_dict.update({self.i2c_addr: handle})
                elif command == 'write_byte_data':
                    # get handle
                    value = i['value']
                    handle = self.i2c_handle_dict[self.i2c_addr]
                    register = i['register']
                    self.pi.i2c_write_byte_data(handle, register, value)
                elif command == 'write_byte':
                    # get handle
                    self.value = 0
                    self.value = i['value']
                    handle = self.i2c_handle_dict[self.i2c_addr]
                    self.pi.i2c_write_byte(handle, self.value)
                elif command == 'read_block':
                    num_bytes = i['num_bytes']
                    handle = self.i2c_handle_dict[self.i2c_addr]
                    register = i['register']
                    tag = i['tag']
                    data = self.pi.i2c_read_i2c_block_data(handle, register, num_bytes)
                    if i['report']:
                        self.report_i2c_block_data(data, tag)
                elif command == 'read_byte':
                    handle = self.i2c_handle_dict[self.i2c_addr]
                    tag = i['tag']
                    data = self.pi.i2c_read_byte(handle)
                    report = i['report']
                    if report:
                        self.report_i2c_byte_data(data, tag)
                else:
                    print('unknown command', i)

    def report_i2c_block_data(self, data, tag):
        # create a topic specific to the board number of this board
        envelope = ("I2C" + str(self.i2c_addr))

        # extract bytes from returned byte array and place in a list
        rdata = []
        for x in data[1]:
            rdata.append(x)

        msg = umsgpack.packb({u"command": "I2C_reply", u"board": self.board_num, u"data_files": rdata, u"tag": tag})

        self.publisher.send_multipart([envelope.encode(), msg])

    def report_i2c_byte_data(self, data, tag):
        # create a topic specific to the board number of this board
        envelope = ("I2C" + str(self.i2c_addr))
        msg = umsgpack.packb({u"command": "I2C_reply", u"board": self.board_num, u"data_files": data, u"tag": tag})
        self.publisher.send_multipart([envelope.encode(), msg])


def i2c_pigpio():
    # noinspection PyShadowingNames

    parser = argparse.ArgumentParser()
    parser.add_argument("-b", dest="back_plane_ip_address", default="None",
                        help="None or IP address used by Back Plane")
    parser.add_argument("-n", dest="process_name", default="I2C Back End", help="Set process name in banner")

    args = parser.parse_args()
    kw_options = {}

    if args.back_plane_ip_address != 'None':
        kw_options['back_plane_ip_address'] = args.back_plane_ip_address

    kw_options['process_name'] = args.process_name

    my_i2c_pigpio = I2cPigpio(**kw_options)

    # signal handler function called when Control-C occurs
    # noinspection PyShadowingNames,PyUnusedLocal,PyUnusedLocal
    def signal_handler(signal, frame):
        print('Control-C detected. See you soon.')

        my_i2c_pigpio.clean_up()
        sys.exit(0)

    # listen for SIGINT
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

if __name__ == '__main__':
    i2c_pigpio()


