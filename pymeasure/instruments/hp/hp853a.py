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

import logging
# import time
# import numpy as np
from enum import IntEnum
from pymeasure.instruments import Instrument
from pymeasure.instruments import Channel
from pymeasure.instruments.validators import strict_range, strict_discrete_set

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class trace(Channel):
    """This device supports two traces"""

    class TraceMode(IntEnum):
        """
        IntEnum controlling the trace mode

        ===========  ===============
        Value        Trace function
        ===========  ===============
        CLEAR_WRITE  resets trace w/ each write
        MAX_HOLD     maximum hold feature
        STORE_VIEW   stores last trace data
        STORE_BLANK  blank trace
        ===========  ===============
        """
        CLEAR_WRITE = 1
        MAX_HOLD = 2
        STORE_VIEW = 3
        STORE_BLANK = 4


    # TODO: Valiation of the sertting trace-part (481 values of -50..975 as ASCII string)
    trace = Channel.control(
        "T{ch}", "I{ch}%d",
        """Control the trace data""",
        )

    def clear(self):
        """Clear the trace memory to a blank state"""
        self.write("C{ch}")

    peak = Channel.measurement(
        "{ch}P",
        """Measure the X&Y coordinates of the peak on the current channel """,)

    mode = Channel.control(
        "FP", "{ch}C%d",
        """Control the operation mode of the channel""",
        map_values=True,
        values=TraceMode,
        # preprocess_reply=lambda v: v[2+v.find({ch}+"C")],
        )


class HP853A(Instrument):
    """ Represents the Hewlett-Packard 853A Spectrum analzyer digital storage mainframe
    and provides a high-level interface for interacting with the instrument.
    """

    def __init__(self, adapter, **kwargs):
        kwargs.setdefault('read_termination', '\r\n')
        kwargs.setdefault('write_termination', '\r\n')
        kwargs.setdefault('send_end', True)
        super().__init__(
            adapter,
            'Hewlett-Packard 853A',
            includeSCPI=False,
            **kwargs
        )

    channels = Instrument.ChannelCreator(trace, ("A", "B"))

    id = Instrument.measurement(
        "OI",
        """Return the ID of the instrument""",
        get_process=lambda v: f"HP,{v:.0f}A,n/a,n/a",
        )

    sweep_count = Instrument.setting(
        "TS%d",
        """Set the number of sweeps to be performed

        Allowed range = 1..63
        """,
        validator=strict_range,
        values=[1, 63],
        )

    normalize = Instrument.setting(
        "IC%d",
        """Set the nomalization function (Input - B --> A)

        Bool variable --> True - enabled, False - disabled
        """,
        map_values=True,
        validator=strict_discrete_set,
        values={False: 0, True: 1},
        )

    norm_offset = Instrument.setting(
        "OF%d",
        """Set the normalization offset,
        initial value is set by jumper position (400 (mid-screen) or 800 (top graticule line))

        allowed range 0..975""",
        validator=strict_range,
        values=[0, 975],
        )

    average_digitally = Instrument.setting(
        "DC%d",
        """Set the digital averaging mode

        Bool variable --> True - enabled, False - disabled
        """,
        map_values=True,
        validator=strict_discrete_set,
        values={False: 0, True: 1},
        )

    @property
    def sweeps_remaining(self):
        """ Return the number of remaining sweeps """
        return self.adapter.connection.read_stb()

    # @property
    # def status(self):
    #     """ Returns the status byte of the 8116A as an IntFlag-type enum. """
    #     return Status(self.adapter.connection.read_stb())

    def GPIB_trigger(self):
        """ Initate trigger via low-level GPIB-command (aka GET - group execute trigger).
        Note: Ideally the unit should be set to single trigger
        """
        self.adapter.connection.assert_trigger()

    def reset(self):
        """ Initatiate a reset (like a power-on reset) of the 853A. """
        self.adapter.connection.clear()

    def shutdown(self):
        """ Gracefully close the connection to the 853A. """
        self.adapter.connection.clear()
        self.adapter.connection.close()
        super().shutdown()

    # TODO: rrework, byte 5 of STB indicates syntax error
    def check_errors(self):
        """ Check for errors in the 853A.

        :return: list of error entries or empty list if no error occurred.
        """
        errors_response = self.ask('IERR', 100).split('\r\n')[0].strip(' ,\r\n')
        errors = errors_response.split('ERROR')[:-1]
        errors = [e.strip() + " ERROR" for e in errors]

        if errors[0] == 'NO ERROR':
            return []
        else:
            for error in errors:
                log.error(f'{self.name}: {error}')
            return errors
