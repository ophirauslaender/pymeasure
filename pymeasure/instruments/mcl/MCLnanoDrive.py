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

class ProductInfo(ctypes.Structure):
        _fields_ = [("axis_bitmap", ctypes.c_ubyte),
                    ("ADC_resolution", ctypes.c_short),
                    ("DAC_resolution", ctypes.c_short),
                    ("Product_id", ctypes.c_short),
                    ("FirmwareVersion", ctypes.c_short),
                    ("FirmwareProfile", ctypes.c_short)]
        _pack_ = 1 # this is how it is packed in the Madlib dll

class MCLnanoDrive(Instrument):
    """Control a MCL (Mad City Labs) Nano-Drive."""

    def __init__(self, adapter, name="MCL nanoDrive", **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs
        )

        self.axis_mapping = {1: 'X', 2: 'Y', 3: 'Z'}
        self.calibration = {}
        self.position = {}
        self.mcl_error_codes = { 0: 'MCL_SUCCESS',
                                -1: 'MCL_GENERAL_ERROR',
                                -2: 'MCL_DEV_ERROR',
                                -3: 'MCL_DEV_NOT_ATTACHED',
                                -4: 'MCL_USAGE_ERROR',
                                -5: 'MCL_DEV_NOT_READY',
                                -6: 'MCL_ARGUMENT_ERROR',
                                -7: 'MCL_INVALID_AXIS',
                                -8: 'MCL_INVALID_HANDLE'}

        self.mcldll = ctypes.CDLL("C:/Program Files/Mad City Labs/NanoDrive/Madlib.dll")

        # Function prototype for MCL_InitHandle
        MCL_InitHandle = self.mcldll.MCL_InitHandle     
        MCL_InitHandle.argtypes = []
        MCL_InitHandle.restype = ctypes.c_int

        # Function prototype for MCL_GetCalibration
        MCL_GetCalibration = self.mcldll.MCL_GetCalibration
        MCL_GetCalibration.argtypes = [ctypes.c_uint, ctypes.c_int]
        MCL_GetCalibration.restype = ctypes.c_double

        self.handle = MCL_InitHandle()

        log.info(f"MCL handle initialized: handle = {self.handle}")

        pi = ProductInfo()
        ppi = ctypes.pointer(pi)

        err = self.mcldll.MCL_GetProductInfo(ppi, self.handle)
        if err != 0:
            log.info(f"Error: NanoDrive could not get productInformation. Error Code: {err} = {self.mcl_error_codes[err]}")
            log.info("Exiting")
            self.disconnect()
            return
        else:
            log.info("Information about the NanoDrive:")
#            log.info(f"axis bitmap: {pi.axis_bitmap}")
            log.info(f"ADC resolution: {pi.ADC_resolution}")
            log.info(f"DAC resolution: {pi.DAC_resolution}")
            log.info(f"Product ID: {pi.Product_id}")
            log.info(f"Firmware Version {pi.FirmwareVersion}")
            log.info(f"Firmware Profile {pi.FirmwareProfile}")
            for i_, ax_ in self.axis_mapping.items():
                self.calibration[i_] = self.mcldll.MCL_GetCalibration(i_, self.handle)
                log.info(f"Calibration is on axis {ax_} is {self.calibration[i_]} μm / volt")
                self.position[i_] = self.get_position(i_)
            # print(self._position)
            log.info(f"Initial position: {self.position}")

    def disconnect(self):
        # Function prototype for MCL_ReleaseHandle
        MCL_ReleaseHandle = self.mcldll.MCL_ReleaseHandle
        MCL_ReleaseHandle.argtypes = [ctypes.c_int]
        MCL_ReleaseHandle.restype = None

        self.mcldll.MCL_ReleaseHandle(self.handle) # be sure to release handle anytime before returning

################################################################
    def get_position(self, i_axis):
        # Function prototype for MCL_SingleReadN
        MCL_SingleReadN = self.mcldll.MCL_SingleReadN
        MCL_SingleReadN.argtypes = [ctypes.c_uint, ctypes.c_int]
        MCL_SingleReadN.restype = ctypes.c_double

        self.position[i_axis] = MCL_SingleReadN(i_axis, self.handle) 
        return self.position[i_axis]    
    
    def set_position(self, i_axis, new_position, tol=0.1):
        MCL_SingleWriteN = self.mcldll.MCL_SingleWriteN
        MCL_SingleWriteN.argtypes = [ctypes.c_double, ctypes.c_uint, ctypes.c_int]
        MCL_SingleWriteN.restype = ctypes.c_int

        if not 0 <= float(new_position) <= self.calibration[i_axis]:
            raise ValueError(f'Position must be between 0 and {self.calibration[i_axis]} μm')
        else:
            err = MCL_SingleWriteN(ctypes.c_double(new_position), ctypes.c_uint(i_axis), self.handle)
            while (abs(new_position - self.position[i_axis]) > tol):
                time.sleep(0.01)
                self.position[i_axis] = self.get_position(i_axis)
            
            return err
################################################################

        


