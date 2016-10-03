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

# The next line will be enabled when we build for Android using Buildozer
# __version__ = "1.0"

import socket
import sys
import time

import umsgpack
import zmq
from kivy.app import App
from kivy.clock import Clock
from kivy.properties import StringProperty
from kivy.uix.widget import Widget
# noinspection PyUnresolvedReferences
from razmq.gui.kivy.knob import Knob


class MainWidget(Widget):
    robot_distance = StringProperty()

    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
        self.robot_distance = '0.00'

    def update_robot_distance(self, dt):
        # self.random_number = str(random.randint(1, 100))
        self.robot_distance = dt
        pass


class RazmqControlApp(App):
    back_plane_ip_address = None
    subscriber_port = '43125'
    publisher_port = '43124'

    def __init__(self):
        # print('control init')
        super().__init__()

        self.distance_traveled = 0.0
        self.stop_time = 0
        self.speed = 90

        print('\n**************************************')
        print('GUI')
        print('Using Back Plane IP address: ' + self.back_plane_ip_address)
        print('**************************************')

        # establish the zeriomq sub and pub sockets
        self.context = zmq.Context()
        # noinspection PyUnresolvedReferences
        self.subscriber = self.context.socket(zmq.SUB)
        connect_string = "tcp://" + self.back_plane_ip_address + ':' + self.subscriber_port
        self.subscriber.connect(connect_string)

        # noinspection PyUnresolvedReferences
        self.publisher = self.context.socket(zmq.PUB)
        connect_string = "tcp://" + self.back_plane_ip_address+ ':' + self.publisher_port
        self.publisher.connect(connect_string)

        self.set_subscriber_topic('left_encoder_tick')


        Clock.schedule_interval(self._zmq_read, .00001)
        # Clock.ClockBaseInterrupt(self.zmq_read, .2)

    def _zmq_read(self, dt):
        data = None
        # print(time.time())
        try:
            data = self.subscriber.recv_multipart(zmq.NOBLOCK)
            self.incoming_message_processing(data[0].decode(), umsgpack.unpackb(data[1]))
            Clock.schedule_once(self._zmq_read, .00001)
        except zmq.error.Again:
            if self.stop_time:
                if self.root.ids.stop_button.state == 'down':
                    current_time = time.time()
                    if current_time - self.stop_time > 2:
                        sys.exit(0)
                else:
                    self.stop_time = 0
            Clock.schedule_once(self._zmq_read, .00001)
        except KeyboardInterrupt:
            self.clean_up()

    def publish_payload(self, payload, topic=''):
        """
        This method will publish a payload with the specified topic.

        :param payload: A dictionary of items
        :param topic: A string value
        :return:
        """
        if not type(topic) is str:
            raise TypeError('Publish topic must be a string', 'topic')

        # create a message pack payload
        message = umsgpack.packb(payload)

        pub_envelope = topic.encode()
        self.publisher.send_multipart([pub_envelope, message])


    def incoming_message_processing(self, topic, payload):
        """
        Override this method with a message processor for the application

        :param topic: Message Topic string
        :param payload: Message Data
        :return:
        """
        self.distance_traveled += 0.125
        distance_traveled_string = '{0: >#0.3f}'. format(float(self.distance_traveled))
        self.root.update_robot_distance(distance_traveled_string)

    def set_subscriber_topic(self, topic):
        """
        This method sets the subscriber topic.

        You can subscribe to multiple topics by calling this method for
        each topic.
        :param topic: A topic string
        :return:
        """
        if not type(topic) is str:
            raise TypeError('Subscriber topic must be a string')

        self.subscriber.setsockopt(zmq.SUBSCRIBE, topic.encode())

    def reset_distance(self):
        self.distance_traveled= 0.0

    def clean_up(self):
        """
        Clean up before exiting - override if additional cleanup is necessary

        :return:
        """
        self.publisher.close()
        self.subscriber.close()
        self.context.term()
        self.stop()
        sys.exit(0)

    def build(self):
        self.title = 'Raspberry RedBot'
        return MainWidget()

    # gui user event handlers

    def forward_pressed(self, *args):
        if self.root.ids.forward_button.state == 'down':
            print('forward pressed')
            topic = 'user_motor_command'
            payload = {'command': 'left_motor_forward', 'speed': self.speed}
            self.publish_payload(payload, topic)
            payload = {'command': 'right_motor_forward', 'speed': self.speed}
            self.publish_payload(payload, topic)
            self.stop_time = 0

    def stop_pressed(self, *args):
        self.stop_time = time.time()
        topic = 'user_motor_command'
        payload = {'command': 'left_motor_coast'}
        self.publish_payload(payload, topic)
        payload = {'command': 'right_motor_coast'}
        self.publish_payload(payload, topic)

    def left_pressed(self, *args):
        print('left pressed')
        self.stop_time = 0
        pass

    def right_pressed(self, *args):
        print('right pressed')
        self.stop_time = 0
        pass

    def reverse_pressed(self, *args):
        print('reverse pressed')
        self.stop_time = 0
        pass

    def right_spin_released(self, *args):
        self.stop_time = 0

        pass
        # print('right spin released')

    def speed_value_change(self, value):
        self.speed = int(value)
        if self.root.ids.forward_button.state == 'down':
            topic = 'user_motor_command'
            payload = {'command': 'left_motor_forward', 'speed': self.speed}
            self.publish_payload(payload, topic)
            payload = {'command': 'right_motor_forward', 'speed': self.speed}
            self.publish_payload(payload, topic)
            self.stop_time = 0

    def turn_speed_value_change(self, value):
        print(value)

def razmq_control_app():
    # we can't use argparse here because of inheritance.
    # if user wants to explicitly set the ip address: main 192.168.1.ANYTHING YOU LIKE
    if len(sys.argv) > 1:
        RazmqControlApp.back_plane_ip_address = sys.argv[1]
    # argument, so just use the local host
    else:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # use the google dns
        s.connect(('8.8.8.8', 0))
        RazmqControlApp.back_plane_ip_address = s.getsockname()[0]

    RazmqControlApp().run()

if __name__ == '__main__':
    razmq_control_app()
