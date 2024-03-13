#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2023 PyMeasure Developers
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import ctypes

import time
import subprocess

import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

from pymeasure.instruments import Instrument

class MCLnanoDrive(Instrument):
    """Control a MCL (Mad City Labs) Nano-Drive."""

    def __init__(self, adapter, name="MCL nanoDrive", **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs
        )

        self.axis_mapping = {1: 'X', 2: 'Y', 3: 'Z'}

        instrument_dll = ctypes.CDLL("C:/Program Files/Mad City Labs/NanoDrive/Madlib.dll")

        self.handle = instrument_dll.MCL_InitHandle()

        log.info(f"MCL handle initialized: {self.handle}")
        log.info(f'Serial Number: {instrument_dll.MCL_GetSerialNumber(self.handle)}')

        for i_, ax_ in self.axis_mapping.items():
            print(f'Axis {ax_} Calibration: {float(instrument_dll.MCL_GetCalibration(i_, self.handle))}')
          

        instrument_dll.MCL_PrintDeviceInfo(self.handle)




