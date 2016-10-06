
import remi.gui as gui
from remi.gui import *
from remi import start, App
import zmq
import umsgpack
import sys
import socket

import signal
import time


class MyApp(App):
    publisher = None
    subscriber = None
    subscriber_port = '43125'
    publisher_port = '43124'
    subscriber_topic = 'left_encoder_tick'
    context = None
    inches_label = None
    distance = 0.000
    forward_btn= None
    left_btn = None
    stop_btn = None
    speed = 90
    back_plane_ip_address = None


    def __init__(self, *args):
        super(MyApp, self).__init__(*args, static_paths=('./res/',))
    
    def idle(self):
        #idle function called every update cycle
        data = None
        try:
            data = self.subscriber.recv_multipart(zmq.NOBLOCK)
            self.incoming_message_processing(data[0].decode(), umsgpack.unpackb(data[1]))
        except zmq.error.Again:
            pass
        except KeyboardInterrupt:
            self.clean_up()
    
    def main(self):
        self.context = zmq.Context()
        # noinspection PyUnresolvedReferences
        self.subscriber = self.context.socket(zmq.SUB)
        self.subscriber.setsockopt(zmq.SUBSCRIBE, self.subscriber_topic.encode())
        #
        connect_string = "tcp://" + '192.168.2.199' + ':' + self.subscriber_port
        self.subscriber.connect(connect_string)
        #
        # noinspection PyUnresolvedReferences
        self.publisher = self.context.socket(zmq.PUB)
        connect_string = "tcp://" + '192.168.2.199' + ':' + self.publisher_port
        self.publisher.connect(connect_string)
        #
        print('\n**************************************')
        print('Remi')
        print('Using Back Plane IP address: ' + '192.168.2.199')
        print('**************************************')

        return MyApp.construct_ui(self)

    def on_stop_button_pressed(self):
        topic = 'user_motor_command'
        payload = {'command': 'left_motor_coast'}
        self.publish_payload(payload, topic)
        payload = {'command': 'right_motor_coast'}
        self.publish_payload(payload, topic)

    def on_forward_button_pressed(self):
        topic = 'user_motor_command'
        payload = {'command': 'left_motor_forward', 'speed': self.speed}
        self.publish_payload(payload, topic)
        payload = {'command': 'right_motor_forward', 'speed': self.speed}
        self.publish_payload(payload, topic)

    def on_clear_distance(self):
        self.inches_label.set_text('0.000')
        self.distance = 0.000
        
    @staticmethod
    def construct_ui(self):
        mainContainer = Widget()
        mainContainer.attributes['editor_baseclass'] = "Widget"
        mainContainer.attributes['class'] = "Widget"
        mainContainer.attributes['editor_constructor'] = "()"
        mainContainer.attributes['editor_newclass'] = "False"
        mainContainer.attributes['editor_varname'] = "mainContainer"
        mainContainer.attributes['editor_tag_type'] = "widget"
        mainContainer.style['border-style'] = "none"
        mainContainer.style['left'] = "279px"
        mainContainer.style['display'] = "block"
        mainContainer.style['top'] = "114px"
        mainContainer.style['overflow'] = "auto"
        mainContainer.style['height'] = "404px"
        mainContainer.style['width'] = "590px"
        mainContainer.style['margin'] = "0px auto"
        mainContainer.style['position'] = "absolute"
        mainContainer.style['background-color'] = "#ffffff"
        distance1_label = Label('Robot Distance Traveled In Inches: ')
        distance1_label.attributes['editor_baseclass'] = "Label"
        distance1_label.attributes['class'] = "Label"
        distance1_label.attributes['editor_constructor'] = "('Robot Distance Traveled In Inches: ')"
        distance1_label.attributes['editor_newclass'] = "False"
        distance1_label.attributes['editor_varname'] = "distance1_label"
        distance1_label.attributes['editor_tag_type'] = "widget"
        distance1_label.style['left'] = "126px"
        distance1_label.style['display'] = "block"
        distance1_label.style['top'] = "43px"
        distance1_label.style['overflow'] = "auto"
        distance1_label.style['font-weight'] = "bold"
        distance1_label.style['height'] = "80px"
        distance1_label.style['width'] = "229px"
        distance1_label.style['margin'] = "0px auto"
        distance1_label.style['position'] = "absolute"
        distance1_label.style['color'] = "#060606"
        mainContainer.append(distance1_label,'distance1_label')
        left_button = Button('Left')
        self.left_btn = left_button
        left_button.attributes['editor_baseclass'] = "Button"
        left_button.attributes['class'] = "Button"
        left_button.attributes['editor_constructor'] = "('Left')"
        left_button.attributes['editor_newclass'] = "False"
        left_button.attributes['editor_varname'] = "left_button"
        left_button.attributes['editor_tag_type'] = "widget"
        left_button.style['left'] = "103px"
        left_button.style['display'] = "block"
        left_button.style['top'] = "188px"
        left_button.style['overflow'] = "auto"
        left_button.style['height'] = "30px"
        left_button.style['width'] = "100px"
        left_button.style['margin'] = "0px auto"
        left_button.style['position'] = "absolute"
        mainContainer.append(left_button,'left_button')
        forward_button = Button('Forward')
        self.forward_btn = forward_button

        forward_button.attributes['editor_baseclass'] = "Button"
        forward_button.attributes['class'] = "Button"
        forward_button.attributes['editor_constructor'] = "('Forward')"
        forward_button.attributes['editor_newclass'] = "False"
        forward_button.attributes['editor_varname'] = "forward_button"
        forward_button.attributes['editor_tag_type'] = "widget"
        forward_button.style['left'] = "233px"
        forward_button.style['display'] = "block"
        forward_button.style['top'] = "134px"
        forward_button.style['overflow'] = "auto"
        forward_button.style['height'] = "30px"
        forward_button.style['width'] = "100px"
        forward_button.style['margin'] = "0px auto"
        forward_button.style['position'] = "absolute"
        mainContainer.append(forward_button,'forward_button')
        stop_button = Button('STOP')
        self.stop_btn = stop_button

        stop_button.attributes['editor_baseclass'] = "Button"
        stop_button.attributes['class'] = "Button"
        stop_button.attributes['editor_constructor'] = "('STOP')"
        stop_button.attributes['editor_newclass'] = "False"
        stop_button.attributes['editor_varname'] = "stop_button"
        stop_button.attributes['editor_tag_type'] = "widget"
        stop_button.style['left'] = "233px"
        stop_button.style['display'] = "block"
        stop_button.style['top'] = "185px"
        stop_button.style['overflow'] = "auto"
        stop_button.style['height'] = "30px"
        stop_button.style['width'] = "100px"
        stop_button.style['margin'] = "0px auto"
        stop_button.style['position'] = "absolute"
        stop_button.style['background-color'] = "#f50825"
        right_button = Button('Right')
        right_button.attributes['editor_baseclass'] = "Button"
        right_button.attributes['class'] = "Button"
        right_button.attributes['editor_constructor'] = "('Right')"
        right_button.attributes['editor_newclass'] = "False"
        right_button.attributes['editor_varname'] = "right_button"
        right_button.attributes['editor_tag_type'] = "widget"
        right_button.style['left'] = "361px"
        right_button.style['display'] = "block"
        right_button.style['top'] = "185px"
        right_button.style['overflow'] = "auto"
        right_button.style['height'] = "30px"
        right_button.style['width'] = "100px"
        right_button.style['margin'] = "0px auto"
        right_button.style['position'] = "absolute"
        stop_button.append(right_button,'right_button')
        mainContainer.append(stop_button,'stop_button')
        speed_slider = Slider('0',60,255,1)
        speed_slider.attributes['editor_baseclass'] = "Slider"
        speed_slider.attributes['editor_newclass'] = "False"
        speed_slider.attributes['autocomplete'] = "off"
        speed_slider.attributes['value'] = "126"
        speed_slider.attributes['type'] = "range"
        speed_slider.attributes['class'] = "range"
        speed_slider.attributes['editor_constructor'] = "('0',60,255,1)"
        speed_slider.attributes['max'] = "255"
        speed_slider.attributes['editor_varname'] = "speed_slider"
        speed_slider.attributes['step'] = "1"
        speed_slider.attributes['editor_tag_type'] = "widget"
        speed_slider.attributes['min'] = "60"
        speed_slider.style['left'] = "245px"
        speed_slider.style['display'] = "block"
        speed_slider.style['top'] = "336px"
        speed_slider.style['overflow'] = "auto"
        speed_slider.style['font-weight'] = "bold"
        speed_slider.style['height'] = "30px"
        speed_slider.style['width'] = "100px"
        speed_slider.style['margin'] = "0px auto"
        speed_slider.style['position'] = "absolute"
        speed_slider.style['background-color'] = "#ffffff"
        mainContainer.append(speed_slider,'speed_slider')
        reverse_button = Button('Reverse')
        reverse_button.attributes['editor_baseclass'] = "Button"
        reverse_button.attributes['class'] = "Button"
        reverse_button.attributes['editor_constructor'] = "('Reverse')"
        reverse_button.attributes['editor_newclass'] = "False"
        reverse_button.attributes['editor_varname'] = "reverse_button"
        reverse_button.attributes['editor_tag_type'] = "widget"
        reverse_button.style['left'] = "233px"
        reverse_button.style['display'] = "block"
        reverse_button.style['top'] = "242px"
        reverse_button.style['overflow'] = "auto"
        reverse_button.style['height'] = "30px"
        reverse_button.style['width'] = "100px"
        reverse_button.style['margin'] = "0px auto"
        reverse_button.style['position'] = "absolute"
        mainContainer.append(reverse_button,'reverse_button')
        inches = Label('0.000')
        inches.attributes['editor_baseclass'] = "Label"
        inches.attributes['class'] = "Label"
        inches.attributes['editor_constructor'] = "('0.000')"
        inches.attributes['editor_newclass'] = "False"
        inches.attributes['editor_varname'] = "inches"
        inches.attributes['editor_tag_type'] = "widget"
        inches.style['left'] = "351px"
        inches.style['display'] = "block"
        inches.style['top'] = "45px"
        inches.style['overflow'] = "auto"
        inches.style['font-weight'] = "bold"
        inches.style['height'] = "30px"
        inches.style['width'] = "100px"
        inches.style['margin'] = "0px auto"
        inches.style['position'] = "absolute"
        inches.style['color'] = "#e85810"
        self.inches_label = inches
        mainContainer.append(inches,'inches')
        speed_label = Label('Speed')
        speed_label.attributes['editor_baseclass'] = "Label"
        speed_label.attributes['class'] = "Label"
        speed_label.attributes['editor_constructor'] = "('Speed')"
        speed_label.attributes['editor_newclass'] = "False"
        speed_label.attributes['editor_varname'] = "speed_label"
        speed_label.attributes['editor_tag_type'] = "widget"
        speed_label.style['left'] = "274px"
        speed_label.style['display'] = "block"
        speed_label.style['top'] = "306px"
        speed_label.style['overflow'] = "auto"
        speed_label.style['font-weight'] = "bold"
        speed_label.style['height'] = "30px"
        speed_label.style['width'] = "100px"
        speed_label.style['margin'] = "0px auto"
        speed_label.style['position'] = "absolute"
        speed_label.style['border-style'] = "none"
        mainContainer.append(speed_label,'speed_label')
        

        self.mainContainer = mainContainer
        self.stop_btn.set_on_click_listener(self, 'on_stop_button_pressed')
        self.forward_btn.set_on_click_listener(self, 'on_forward_button_pressed')
        # self.inches_label.set_on_click_listener(self, 'on_clear_distance')
        # self.left_btn.set_on_click_listener(self, 'on_clear_distance')
        self.inches_label.set_on_mouseout_listener(self, 'on_clear_distance')



        return self.mainContainer
    
    def clean_up(self):
        """
        Clean up before exiting - override if additional cleanup is necessary

        :return:
        """
        self.publisher.close()
        self.subscriber.close()
        self.context.term()
        # self.stop()
        # sys.exit(0)


    def incoming_message_processing(self, topic, payload):
        """
        Override this method with a message processor for the application

        :param topic: Message Topic string
        :param payload: Message Data
        :return:
        """
        if topic == 'left_encoder_tick':
            self.distance += 0.125
        distance_traveled_string = '{0: >#0.3f}'. format(float(self.distance))

        self.inches_label.set_text(str(distance_traveled_string))

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

def razremi():
    if len(sys.argv) > 1:
        MyApp.back_plane_ip_address = sys.argv[1]
    # argument, so just use the local host
    else:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # use the google dns
        s.connect(('8.8.8.8', 0))
        MyApp.back_plane_ip_address = s.getsockname()[0]

    # signal handler function called when Control-C occurs
    # noinspection PyShadowingNames,PyUnusedLocal,PyUnusedLocal
    def signal_handler(signal, frame):
        print('Control-C detected. See you soon.')


        sys.exit(0)

    # listen for SIGINT
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    start(MyApp, debug=True, address=MyApp.back_plane_ip_address, update_interval=.00001)




#Configuration
configuration = {'config_enable_file_cache': True, 'config_resourcepath': './res/', 'config_multiple_instance': True, 'config_project_name': 'untitled', 'config_start_browser': True, 'config_port': 8081, 'config_address': '0.0.0.0'}

if __name__ == "__main__":
    # start(MyApp,address='127.0.0.1', port=8081, multiple_instance=False,enable_file_cache=True, update_interval=0.1, start_browser=True)
    # start(untitled, address=configuration['config_address'], port=configuration['config_port'],
    #                     multiple_instance=configuration['config_multiple_instance'],
    #                     enable_file_cache=configuration['config_enable_file_cache'],
    #                     start_browser=configuration['config_start_browser'])

    # start(MyApp, debug=True, address='192.168.2.199', update_interval=.00001)
    razremi()

