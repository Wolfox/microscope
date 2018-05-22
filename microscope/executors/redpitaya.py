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

    def get_digital(self, digitalPin):
        return self.connection.readDigital(digitalPin)

    def set_digital(self, digitalPin, value):
        self.connection.writeDigital(digitalPin, value)

    def get_analog(self, analogOutput):
        return self.connection.readAnalog(analogOutput)

    def set_analog(self, analogOutput, value):
        self.connection.writeAnalog(analogOutput, value)

    def executeTable(self, name, table, setup = None, startIndex = 0,
        stopIndex = None, numReps = 0, repDuration = 0):
        prevIndex = startIndex
        lastIndex = stopIndex if stopIndex else len(table)
        for i in range(prevIndex, lastIndex):
            if table[i][2] < 0:
                table[prevIndex:i]
                table[prevIndex:i] = sorted(table[prevIndex:i])
                if table[i][0] < table[i-1][0]:
                    table[i][0] = table[i-1][0]
                prevIndex = i+1
        if prevIndex < lastIndex:
            table[prevIndex:lastIndex] = sorted(table[prevIndex:lastIndex])

        baseTime = table[startIndex] if startIndex else 0
        for line in table[startIndex:stopIndex]:
            line[0] -= baseTime
            if line[2] < 0:
                break

        self.connection.setProfile(table[startIndex:stopIndex], setup)
        self.connection.downloadProfile()
        self.connection.trigCollect()

        for i in range(numReps):
            time.sleep(repDuration)
            self.connection.trigCollect()
