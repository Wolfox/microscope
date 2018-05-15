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
        return self.connection.readPosition(analogOutput)

    def set_analog(self, analogOutput, value):
        self.connection.moveAbsoluteADU(analogOutput, value)

        # numReps and repDuration not implemented
    def executeTable(self, name, table, startIndex = 0, stopIndex = None,
        numReps = 0, repDuration = 0):
        times = []
        pins = []
        values = []

        events = table[startIndex:stopIndex]
        baseTime = events[0][0]
        for time, handler, action in events:
            time = int(float(time) + .5)
            # if handler in self.handlerToDigitalLine:
            #     pins.append(self.handlerToDigitalLine[handler]);
            #     values.append(value);
            # elif handler in self.handlerToAnalogLine:
            #     pins.append(self.handlerToAnalogLine[handler]);
            #     values.append(self.convertMicronsToADUs(aline, action));
            # else:
            #     raise RuntimeError("Unhandled handler when generating DSP profile: %s" % handler.name)
            times.append(time - baseTime);
            pins.append(handler)
            values.append(action)

        self.connection.setProfile(times, pins, values)
        self.connection.downloadProfile()
        self.connection.trigCollect()

        return
