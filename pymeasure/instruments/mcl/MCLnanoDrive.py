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
import numpy as np

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
        self.tolerance = {1: 0.0125, 2: 0.05, 3: 0.025}
        self.offsets = {1: 0.06, 2: 0.03, 3: 0.02}


        self.mcl_error_codes = {
            0: '(0) MCL_SUCCESS',
            -1: '(-1) MCL_GENERAL_ERROR:\n-- generally occurs due to an internal sanity check failing.',
            -2: '(-2) MCL_DEV_ERROR:\n-- problem occurred when transferring data to the Nano-Drive.  It is likely that Nano-Drive will have to be 	 power cycled to correct these errors.',
            -3: '(-3) MCL_DEV_NOT_ATTACHED:\n-- Nano-Drive not attached.',
            -4: '(-4) MCL_USAGE_ERROR:\n-- Using a function from the library which the Nano-Drive does not support.',
            -5: '(-5) MCL_DEV_NOT_READY:\n-- Nano-Drive currently completing or waiting to complete another task.',
            -6: '(-6) MCL_ARGUMENT_ERROR:\n-- argument is out of range or a required pointer is equal to NULL.',
            -7: '(-7) MCL_INVALID_AXIS:\n-- Attempting an operation on an axis that does not exist in the Nano-Drive.',
            -8: '(-8) MCL_INVALID_HANDLE:\n-- The handle is not valid in this instance of the DLL.'
            }

        self.mcldll = ctypes.CDLL("C:/Program Files/Mad City Labs/NanoDrive/Madlib.dll")


        self.mcldll.MCL_InitHandleOrGetExisting.restype = ctypes.c_int
        self.handle = self.mcldll.MCL_InitHandleOrGetExisting() # this is better than MCL_InitHandle because it can handle an unreleased instance.

        self.mcldll.MCL_GetCalibration.restype = ctypes.c_double
        self.mcldll.MCL_SingleReadN.restype = ctypes.c_double
        self.mcldll.MCL_SingleWriteN.restype = ctypes.c_int
        self.mcldll.MCL_MonitorN.restype = ctypes.c_double

        if self.handle == 0:
            log.warning(f"Error: NanoDrive could not initialize handle..... Exiting")
            return
        else:
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
                log.info(f"ADC resolution: {pi.ADC_resolution}")
                log.info(f"DAC resolution: {pi.DAC_resolution}")
                log.info(f"Product ID: {pi.Product_id}")
                log.info(f"Firmware Version {pi.FirmwareVersion}")
                log.info(f"Firmware Profile {pi.FirmwareProfile}")
                for i_, ax_ in self.axis_mapping.items():
                    self.calibration[i_] = self.mcldll.MCL_GetCalibration(i_, self.handle)
                    log.info(f"Calibration is on axis {ax_} is {self.calibration[i_]} μm / volt")
                    self.position[i_] = self.get_position(i_)
                log.info(f"Initial position: {self.position} μm")

    def disconnect(self):
        self.mcldll.MCL_ReleaseHandle(self.handle) # be sure to release handle anytime before returning
        log.info(f"Finished disconnecting down {self.name}")


################################################################
    def get_position(self, i_axis, n=1):

        pos = []

        for i_ in range(n):
            pos.append(self.mcldll.MCL_SingleReadN(i_axis, self.handle))
            time.sleep(0.001)
            self.position[i_axis] = np.mean(pos)
        return self.position[i_axis]   
    
    def set_position(self, i_axis, new_position):

        new_position_ = new_position + self.offsets[i_axis]

        if not 0 <= float(new_position_) <= self.calibration[i_axis]:
            raise ValueError(f'Position must be between 0 and {self.calibration[i_axis]} μm')
        else:
            err = self.mcldll.MCL_SingleWriteN(ctypes.c_double(new_position_), i_axis, self.handle)
            if err != 0:
                log.info(f"Error: NanoDrive could not set position. Error Code: {err} = {self.mcl_error_codes[err]}")

            # i_while = 0
            # while (abs(new_position_ - self.position[i_axis]) > self.tolerance[i_axis]) and (i_while < 10):
            #     time.sleep(0.01)
            #     self.position[i_axis] = self.get_position(i_axis, n)
            #     i_while += 1
            #     if i_while > 10:
            #         log.warning(f"Error: NanoDrive could not achieve {new_position_} on {self.axis_mapping[i_axis]} after {i_while} attempts in set_position")
            
        return err
        
    def set_verify_position(self, i_axis, new_position, n=1):

        new_position_ = new_position + self.offsets[i_axis]

        if not 0 <= float(new_position_) <= self.calibration[i_axis]:
            raise ValueError(f'Position must be between 0 and {self.calibration[i_axis]} μm')
        else:
            pos_err = self.mcldll.MCL_MonitorN(ctypes.c_double(new_position_), i_axis, self.handle)
            if pos_err < 0:
                log.warning(f"Error: NanoDrive could not set position. Error Code: {pos_err} = {self.mcl_error_codes[int(pos_err)]}")
                return pos_err
            else:
                self.position[i_axis] = pos_err
                if n > 1:
                    self.position[i_axis] = ((n-1)*self.get_position(i_axis, n) + pos_err)/n
                
                i_while = 0                    
                while (abs(new_position_ - pos_err) > self.tolerance[i_axis]) and (i_while < 10):
                    time.sleep(0.01)
                    pos_err = self.mcldll.MCL_MonitorN(ctypes.c_double(new_position), i_axis, self.handle)
                    if pos_err < 0:
                        log.warning(f"Error: NanoDrive could not set position. Error Code: {pos_err} = {self.mcl_error_codes[int(pos_err)]}")
                        return pos_err
                    else:
                        self.position[i_axis] = pos_err
                        if n > 1:
                            self.position[i_axis] = ((n-1)*self.get_position(i_axis, n) + pos_err)/n
                    i_while += 1
                    if i_while > 10:
                        log.warning(f"Error: NanoDrive could not achieve {new_position_} on {self.axis_mapping[i_axis]} after {i_while} attempts in set_verify_position")

        return pos_err
################################################################

        


