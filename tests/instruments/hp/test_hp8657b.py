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


from pymeasure.test import expected_protocol

from pymeasure.instruments.hp import HP8657B


def test_frequency():
    with expected_protocol(
            HP8657B,
            [(b"FR 1234567890 HZ", None),
             (b"FR   12345678 HZ", None)],
    ) as instr:
        instr.frequency = 1.23456789e9
        instr.frequency = 1.2345678e7


def test_level():
    with expected_protocol(
            HP8657B,
            [(b"AP -123.4 DM", None)],
    ) as instr:
        instr.level = -123.4


def test_output():
    with expected_protocol(
            HP8657B,
            [(b"R3", None),
             (b"R2", None)],
    ) as instr:
        instr.output_enabled = True
        instr.output_enabled = False
