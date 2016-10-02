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

import os
import sys
import signal
import shutil


class LunchConfig:
    """
    This class moves the lunch configuration file from the installation dirctory to the home directory as
    .lunchrc.

    Calling lunch_config will overwrite any changes you may have made to the .lunchrc file
    """
    def __init__(self):

        # find the path to the data files needed for operation
        path = sys.path

        base_path = None
        s_path = None

        # get the prefix
        prefix = sys.prefix
        for p in path:
            # make sure the prefix is in the path to avoid false positives
            if prefix in p:
                # look for the configuration directory
                s_path = p + '/razmq/data_files/lunch/'
                if os.path.isdir(s_path):
                    # found it, set the base path
                    base_path = p + '/razmq'
                    break

        if not base_path:
            print('Cannot locate lunch configuration directory.')
            sys.exit(0)
        else:
            home = os.path.expanduser('~')
            install_it = home + '/.lunchrc'
            lunch_config_file = s_path + 'lunchrc.txt'
            shutil.copy(lunch_config_file, install_it)
            print('.lunchrc installed: ' + install_it)


def lunch_config():
    # noinspection PyShadowingNames

    LunchConfig()

    # signal handler function called when Control-C occurs
    # noinspection PyShadowingNames,PyUnusedLocal,PyUnusedLocal
    def signal_handler(signal, frame):
        print('Control-C detected. See you soon.')

        # system_led.clean_up()
        sys.exit(0)

    # listen for SIGINT
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


if __name__ == '__main__':
    lunch_config()
