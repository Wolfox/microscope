#!/usr/bin/env python
# -*- coding: utf-8 -*-

## Copyright (C) 2018 Tiago Susano Pinto <tiagosusanopito@gmail.com>
##
## Microscope is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## Microscope is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Microscope.  If not, see <http://www.gnu.org/licenses/>.

import Pyro4
import time
from microscope import devices

class RedPitaya(devices.ExecutorDevice):
    def __init__(self, uri=None, timeout=0, **kwargs):
        super(RedPitaya, self).__init__()
        try:
            self.connection = Pyro4.Proxy(uri)
            self.connection._pyroTimeout = timeout
            self.connection.abort()
        except Exception as e:
            self.connection = None
            print(e)

    def get_digital(self, digital_line):
        return self.connection.readDigital(digital_line)

    def set_digital(self, digital_line, value):
        self.connection.writeDigital(digital_line, value)

    def get_analog(self, analog_output):
        return self.connection.readAnalog(analog_output)

    def set_analog(self, analog_output, value):
        self.connection.writeAnalog(analog_output, value)

    def execute_table(self, table, name = None, setup = None, start_index = 0,
        stop_index = None, repeats = 0, interval = 0):
        baseTime = table[start_index] if start_index else 0
        actionTable = []
        for time, handler, action in table[start_index:stop_index]:
            actionTable.append([time, handler, action])

        prev_index = 0
        for i in range(1, len(actionTable)):
            if actionTable[i][1] >= 0 and actionTable[i][2] < 0:
                actionTable[prev_index:i]
                actionTable[prev_index:i] = sorted(actionTable[prev_index:i])
                if actionTable[i][0] < actionTable[i-1][0]:
                    actionTable[i][0] = actionTable[i-1][0]
                prev_index = i+1
        if prev_index < len(actionTable):
            actionTable[prev_index:] = sorted(actionTable[prev_index:])

        baseTime = actionTable[0] if start_index else 0
        for line in actionTable:
            line[0] -= baseTime
            if line[1] >= 0 and line[2] < 0:
                break

        self.connection.setProfile(actionTable, setup)
        self.connection.downloadProfile(name)
        self.connection.trigCollect()

        for i in range(repeats):
            time.sleep(interval)
            self.connection.trigCollect()
