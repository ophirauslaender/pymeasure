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

import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

from pymeasure.instruments import Instrument

class ProductInformation(ctypes.Structure):
    _fields_ = [("axis_bitmap", ctypes.c_uint),
                ("FirmwareProfile", ctypes.c_uint),
                ("Product_id", ctypes.c_uint)]

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
        
        # Function prototype for MCL_InitHandle
        MCL_InitHandle = instrument_dll.MCL_InitHandle
        MCL_InitHandle.argtypes = []
        MCL_InitHandle.restype = ctypes.c_int

        # Function prototype for MCL_PrintDeviceInfo
        MCL_PrintDeviceInfo = instrument_dll.MCL_PrintDeviceInfo
        MCL_PrintDeviceInfo.argtypes = [ctypes.c_int]
        MCL_PrintDeviceInfo.restype = None

        # Function prototype for MCL_GetProductInfo
        MCL_GetProductInfo = instrument_dll.MCL_GetProductInfo
        MCL_GetProductInfo.argtypes = [ctypes.POINTER(ProductInformation), ctypes.c_int]
        MCL_GetProductInfo.restype = None

        # Function prototype for MCL_SingleReadN
        MCL_SingleReadN = instrument_dll.MCL_SingleReadN
        MCL_SingleReadN.argtypes = [ctypes.c_uint, ctypes.c_int]
        MCL_SingleReadN.restype = ctypes.c_double

        # Function prototype for MCL_GetCalibration
        MCL_GetCalibration = instrument_dll.MCL_GetCalibration
        MCL_GetCalibration.argtypes = [ctypes.c_uint, ctypes.c_int]
        MCL_GetCalibration.restype = ctypes.c_double

        # Function prototype for MCL_ReleaseHandle
        MCL_ReleaseHandle = instrument_dll.MCL_ReleaseHandle
        MCL_ReleaseHandle.argtypes = [ctypes.c_int]
        MCL_ReleaseHandle.restype = None        

        self.handle = MCL_InitHandle()

        log.info(f"MCL handle initialized: {self.handle}")
#        log.info(f'Serial Number: {MCL_GetSerialNumber(self.handle)}')

#        for i_, ax_ in self.axis_mapping.items():
#               print(f'Axis {ax_} Calibration: {float(MCL_GetCalibration(i_, self.handle))}')
          

        MCL_PrintDeviceInfo(self.handle)





