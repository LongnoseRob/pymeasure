#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2022 PyMeasure Developers
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
import logging
import math
from enum import IntFlag,Enum
# from pymeasure.instruments.hp.hplegacyinstrument import HPLegacyInstrument, StatusBitsBase
from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set, strict_range


log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

c_uint8 = ctypes.c_uint8


# class SRQ(ctypes.BigEndianStructure):
#     """Support class for the SRQ handling
#     """
#     _fields_ = [
#         ("power_on", c_uint8, 1),
#         ("not_assigned_1", c_uint8, 1),
#         ("calibration", c_uint8, 1),
#         ("front_panel_button", c_uint8, 1),
#         ("internal_error", c_uint8, 1),
#         ("syntax_error", c_uint8, 1),
#         ("not_assigned_2", c_uint8, 1),
#         ("data_ready", c_uint8, 1),
#     ]

#     def __str__(self):
#         """
#         Returns a pretty formatted string showing the status of the instrument

#         """
#         ret_str = ""
#         for field in self._fields_:
#             ret_str = ret_str + f"{field[0]}: {hex(getattr(self, field[0]))}\n"

#         return ret_str


# class Status(StatusBitsBase):
#     """
#     Support-Class with the bit assignments for the 5 status byte of the HP3478A
#     """

#     _fields_ = [
#         # Byte 1: Function, Range and Number of Digits
#         ("function", c_uint8, 3),  # bit 5..7
#         ("range", c_uint8, 3),  # bit 2..4
#         ("digits", c_uint8, 2),  # bit 0..1
#         # Byte 2: Status Bits
#         ("res1", c_uint8, 1),
#         ("ext_trig", c_uint8, 1),
#         ("cal_enable", c_uint8, 1),
#         ("front_rear", c_uint8, 1),
#         ("fifty_hz", c_uint8, 1),
#         ("auto_zero", c_uint8, 1),
#         ("auto_range", c_uint8, 1),
#         ("int_trig", c_uint8, 1),
#         # Byte 3: Serial Poll Mask (SRQ)
#         # ("SRQ_PON", c_uint8, 1),
#         # ("res3", c_uint8, 1),
#         # ("SRQ_cal_error", c_uint8, 1),
#         # ("SRQ_front_panel", c_uint8, 1),
#         # ("SRQ_internal_error", c_uint8, 1),
#         # ("SRQ_syntax_error", c_uint8, 1),
#         # ("res2", c_uint8, 1),
#         # ("SRQ_data_rdy", c_uint8, 1),
#         ("SRQ", SRQ),
#         # Byte 4: Error Information
#         # ("res5", c_uint8, 1),
#         # ("res4", c_uint8, 1),
#         # ("ERR_AD_Link", c_uint8, 1),
#         # ("ERR_AD", c_uint8, 1),
#         # ("ERR_slope", c_uint8, 1),
#         # ("ERR_ROM", c_uint8, 1),
#         # ("ERR_RAM", c_uint8, 1),
#         # ("ERR_cal", c_uint8, 1),
#         (        "Error_Status", c_uint8, 8),
#         # Byte 5: DAC Value
#         ("DAC_value", c_uint8, 8),
#     ]


class HP3314A(Instrument):
    """ Represents the Hewlett Packard 3314A function generator
    and provides a high-level interface for interacting
    with the instrument.
    """
    # status_desc = Status

    def __init__(self, adapter, **kwargs):
        kwargs.setdefault('read_termination', '\r\n')
        kwargs.setdefault('write_termination', '\r\n')
        kwargs.setdefault('send_end', True)
        super().__init__(
            adapter,
            "Hewlett-Packard HP3314A",
            includeSCPI=False,
            **kwargs,
        )


    # overlaoding the read-fcn for now, until GPIBG issue fixed
    # Problem is theat normal read() will run into timeout, even with proper temchar

    def read(self):
        rec_data = self.adapter.connection.read_bytes(30)
        return rec_data.rstrip()

    AM_enabled = Instrument.control(
       "QAM", "AM%d",
       """
       this property controls the featrue of amplitude modulation (AM) of the unit

       ...

       """,
       validator=strict_discrete_set,
       values={False: 0, True: 1},
       map_values=True)

    FM_enabled = Instrument.control(
       "QFM", "DM%d",
       """
       this property controls the featrue of frequency modulation (FM) of the unit

       ...

       """,
       validator=strict_discrete_set,
       values={False: 0, True: 1},
       map_values=True)

    func = Instrument.control(
       "QFR", "FR %d",
       """
       this property controls the function (output mode) of the unit

       ...

       """,
       validator=strict_discrete_set,
       values={"off": 0,
               "Sine": 1,
               "Square": 2,
               "Trig": 3,
               },
       map_values=True)

    frequency = Instrument.control(
        "QFR",
        "FR%fHZ",
        """
        This Property controls the frequency of the unit.

        """,
        validator=strict_range,
        values=[0.001, 20000000])

    start_frequency = Instrument.control(
        "QST",
        "ST%fHZ",
        """
        This Property controls the frequency of the unit.

        """,
        validator=strict_range,
        values=[0.001, 20000000])

    stop_frequency = Instrument.control(
        "QSP",
        "SP%fHZ",
        """
        This Property controls the frequency of the unit.

        """,
        validator=strict_range,
        values=[0.001, 20000000])

    mode = Instrument.control(
       "QMO", "MO%d",
       """
       this property controls the mode of the unit

       ...

       """,
       validator=strict_discrete_set,
       values={"Free_Run": 1,
               "Gated": 2,
               "n_cycle": 3,
               "half_cycle": 4,
               "fin_N_X": 5,
               "fin_X_div_N": 6
               },
       map_values=True)

    sweep = Instrument.control(
       "QSW", "SW %d",
       """
       this property controls the sweep-mode of the unit

       ...

       """,
       validator=strict_discrete_set,
       values={"off": 0,
               "lin": 1,
               "log": 2,
               },
       map_values=True)

    time_intervall = Instrument.control(
        "QTI",
        "TI%fSN",
        """
        This Property controls the sweep-tim / trigger time intervall of the unit.

        """,
        validator=strict_range,
        values=[0.000001, 10000])

    def reset(self):
        """
        Initatiates a reset (like a power-on reset) of the HP3478A

        """
        self.adapter.connection.clear()

    def shutdown(self):
        """
        provides a way to gracefully close the connection to the HP3478A

        """
        self.adapter.connection.clear()
        self.adapter.connection.close()
        super().shutdown()

