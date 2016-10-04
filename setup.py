from setuptools import setup

setup(
    name='razmq',
    version='0.1.0',
    packages=['razmq', 'razmq.data_files.lunch', 'razmq.i2c', 'razmq.i2c.validators', 'razmq.i2c.accelerometers',
              'razmq.i2c.a2d', 'razmq.encoders.validators',
              'razmq.led', 'razmq.led.validators', 'razmq.utils', 'razmq.buzzer', 'razmq.buzzer.validators',
              'razmq.led.validators', 'razmq.utils', 'razmq.buzzer', 'razmq.buzzer.validators', 'razmq.motors',
              'razmq.motors.validators', 'razmq.razbase', 'razmq.encoders', 'razmq.backplane', 'razmq.switches',
              'razmq.gui', 'razmq.gui.kivy', 'razmq.gui.kivy.knob', 'razmq.gui.kivy.img'
              ],
    install_requires=['pyzmq',
                      'u-msgpack-python',
                      ],
    package_data={'razmq.data_files.lunch': ['*.txt'],
                  'razmq.gui.kivy': ['*.kv'],
                  'razmq.gui.kivy.img': ['*.png'],
                  },
    data_files=[('/usr/local/bin/img', ['razmq/gui/kivy/img/bline.png', 'razmq/gui/kivy/img/knob_metal.png'])],

    entry_points={
            'console_scripts': [
                'backplane = razmq.backplane.backplane:bp',
                'monitor = razmq.utils.monitor:monitor',
                'lunch_config=razmq.utils.lunch_config:lunch_config',
                'buzzer = razmq.buzzer.buzzer:buzzer',
                'buzzer_pigpio = razmq.buzzer.buzzer_pigpio:buzzer_pigpio',
                'encoders_pigpio = razmq.encoders.encoders_pigpio:encoders_pigpio',
                'i2c_pigpio = razmq.i2c.i2c_pigpio:i2c_pigpio',
                'i2c_pcf8591 = razmq.i2c.a2d.i2c_pcf8591:i2c_pcf8591',
                'i2c_adxl345 = razmq.i2c.accelerometers.i2c_adxl345:i2c_adxl345',
                'led = razmq.led.led:led',
                'led_pigpio = razmq.led.led_pigpio:led_pigpio',
                'motors = razmq.motors.motors:motors',
                'motors_pigpio = razmq.motors.motors_pigpio:motors_pigpio',
                'switches_gpio = razmq.switches.switches_pigpio:switches_pigpio',
                'razkv = razmq.gui.kivy.main:razmq_control_app'
            ]
        },
    url='https://github.com/MrYsLab/razmq',
    license='GNU General Public License v3 (GPLv3)',
    author='Alan Yorinks',
    author_email='MisterYsLab@gmail.com',
    description='A Non-Blocking Event Driven Robotics Framework',
    keywords=['Raspberry Pi', 'ZeroMQ', 'MessagePack', 'RedBot', ],
        classifiers=[
            'Development Status :: 4 - Beta',
            'Environment :: Other Environment',
            'Intended Audience :: Education',
            'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 3.4',
            'Topic :: Education',
            'Topic :: Software Development',
            'Topic :: Home Automation',
            'Topic :: System :: Hardware'
        ],
)
