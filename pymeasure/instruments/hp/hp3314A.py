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

# import ctypes
import logging
# import math
# from enum import IntFlag,Enum
# from pymeasure.instruments.hp.hplegacyinstrument import HPLegacyInstrument, StatusBitsBase
from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set, strict_range


log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


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

    # overlaoding the read-fcn for now, until GPIB issue fixed
    # Problem is the normal read() will run into timeout, even with proper temchar
    def read(self):
        rec_data = self.adapter.connection.read_bytes(30)
        return rec_data.rstrip()

    def values(self, command):
        self.write(command)
        return self.read()

    amplitude = Instrument.control(
        "QAP",
        "AP%fVO",
        """
        Control the Amplitude (referenced to 50 Ohms load(!)) of the unit.

        """,
        validator=strict_range,
        values=[1E-6, 10],
        get_process=lambda v: float(v.lstrip(b'AP').rstrip(b'VO')),
        )

    AM = Instrument.control(
       "QAM", "AM%d",
       """
       Control the status of amplitude modulation (AM)

       ======  =======
       Value   Amplitude modulation
       ======  =======
       False   OFF
       True    ON
       ======  =======

       .. Note::
           Signal source for modulation needs to be connected to the AM-connector on the front

       """,
       validator=strict_discrete_set,
       values={False: 0, True: 1},
       map_values=True,
       get_process=lambda v: int(v.lstrip(b'AM')),
       )

    # TODO: add ARB mode switching

    # TODO add Calubrate functions (CA,CD,CE,CF)

    def check_errors(self):
        pending_error = self.values("QER").lstrip(b"ER")
        if pending_error != b'00':
            log.warning(f"HP3314A {self.adapter.connection.resource_name}: Error {pending_error}")
            return pending_error

    data_transfer_buffered = Instrument.setting(
        "DM%d",
        """
        Control setting for  unbuffered (False) and buffered (True) data transfer mode.

        """,
        values={False: 1, True: 2},
        map_values=True,
        )

    # TODO: impleent delete_vector (DV) function

    external_trigger = Instrument.control(
       "QSR", "SR%d",
       """
       Control the trigger source selection

       ======  =======
       Value   Trigger source
       ======  =======
       False   Internal
       True    External
       ======  =======


       """,
       validator=strict_discrete_set,
       values={False: 1, True: 2},
       map_values=True,
       get_process=lambda v: int(v.lstrip(b'SR')),
       )

    FM = Instrument.control(
       "QFM", "FM%d",
       """
       Control the status of frequency modulation (FM)

       ======  =======
       Value   Frequency modulation
       ======  =======
       False   OFF
       True    ON
       ======  =======

       .. Note::
           Signal source for modulation needs to be connected to the FM/VCO-connector on the front

       """,
       validator=strict_discrete_set,
       values={False: 0, True: 1},
       map_values=True,
       get_process=lambda v: int(v.lstrip(b'FM')),
       )

    frequency = Instrument.control(
        "QFR",
        "FR%fHZ",
        """
        Control the output frequency.

        """,
        validator=strict_range,
        values=[0.001, 20000000],
        get_process=lambda v: float(v.lstrip(b'FR').rstrip(b'.HZ')),
        )

    func = Instrument.control(
       "QFU", "FU %d",
       """
       Control the function (output mode) of the unit.

       ========  =======
       Value     Output mode
       ========  =======
       "off"     Output disabled _Note_: DC offset is still output
       "Sine"    Sinewave
       "Square"  Square wave
       "Trig"    Trianglar (sawtooth)
       ========  =======

       """,
       validator=strict_discrete_set,
       values={"off": 0,
               "Sine": 1,
               "Square": 2,
               "Trig": 3,
               },
       map_values=True,
       get_process=lambda v: v.lstrip(b'FU'),
       )

    func_inverted = Instrument.control(
       "QFI", "FI%d",
       """
       Control the status of the the output-invert-function

       ======  =======
       Value   Output shape
       ======  =======
       False   normal
       True    inverted
       ======  =======

       """,
       validator=strict_discrete_set,
       values={False: 0, True: 1},
       map_values=True,
       get_process=lambda v: v.lstrip(b'FI'),
       )

    # TODO: implement insert vector

    manual_sweep_enabled = Instrument.control(
       "QMA", "MA%d",
       """
       Enable a manual sweep

       """,
       validator=strict_discrete_set,
       values={False: 0, True: 1},
       map_values=True,
       get_process=lambda v: v.lstrip(b'MA'),
       )

    marker_frequency = Instrument.control(
        "QMK",
        "MK%fHZ",
        """
        Control the marker frequency.

        """,
        validator=strict_range,
        values=[0.001, 20000000],
        get_process=lambda v: float(v.lstrip(b'MK').rstrip(b'HZ')),
        )

    mode = Instrument.control(
        "QMO", "MO%d",
        """
        Control the synchronization possibilities of the unit

        =============  =======
        Value          Selection
        =============  =======
        "Free_Run"     Free running (no sync applied)
        "Gated"        gated output
        "n_cycle"      output limited to n cycles
        "half_cycle"   output a half-cyle e.g. haversine
        "fin_N_X"      f_out is N times higher then frequency applied to sync terminal
        "fin_X_div_N"  f_out is 1/N of frequency applied to sync terminal
        =============  =======
        """,
        validator=strict_discrete_set,
        values={"Free_Run": 1,
                "Gated": 2,
                "n_cycle": 3,
                "half_cycle": 4,
                "fin_N_X": 5,
                "fin_X_div_N": 6
                },
        map_values=True,
        get_process=lambda v: v.lstrip(b'MO'),
        )

    n = Instrument.control(
        "QNM",
        "NM%dEN",
        """
        Control the number of cycles/events to be output.

        """,
        validator=strict_range,
        values=[1, 9999],
        get_process=lambda v: int(v.lstrip(b'NM').rstrip(b' EN')),
        )

    negative_trigger_slope = Instrument.control(
       "QSL", "SL%d",
       """
       Control the trigger slope selection:

       ======  =======
       Value   Trigger slope
       ======  =======
       False   positive (L --> H)
       True    negative (H --> L)
       ======  =======

       """,
       validator=strict_discrete_set,
       values={False: 1, True: 2},
       map_values=True,
       get_process=lambda v: v.lstrip(b'SL'),
       )

    offset = Instrument.control(
        "QOF",
        "OF%fVO",
        """
        Control the offset of the output signal in the range of -5..+5 V

        """,
        validator=strict_range,
        values=[-5, 5],
        get_process=lambda v: float(v.lstrip(b'OF').rstrip(b'VO')),
        )

    phase = Instrument.control(
        "QPH",
        "PH%fDG",
        """
        Control the phase of the output signal (0..360 degrees)

        """,
        validator=strict_range,
        values=[0, 360.0],
        get_process=lambda v: float(v.lstrip(b'PH').rstrip(b'DG')),
        )

    # TODO: add PLL mask

    def preset(self):
        """
        Set the device to a default state, refer to manaul for specifics

        """
        self.write("PR")

    # TODO: add range hold and range up/down

    recall_preset = Instrument.setting(
        "RC%d",
        """
        Get a user-defined setup.
        This instrument allows 6 setups [0..5]

        """,
        values=[0, 5],
        validator=strict_range,
        )

    recall_wave = Instrument.control(
        "QRW",
        "RW%f",
        """
        Control the waveform for the ARB functionality.
        When selecting a wavefowm (up to 5), this also enables the ARB-function

        """,
        validator=strict_range,
        values=[0, 5],
        get_process=lambda v: int(v.lstrip(b'PH')),
        )

    # TODO: add SRQ mask

    start_frequency = Instrument.control(
        "QST",
        "ST%fHZ",
        """
        Control the start-frequency for sweep-mode

        """,
        validator=strict_range,
        values=[0.001, 20000000],
        get_process=lambda v: float(v.lstrip(b'ST').rstrip(b'.HZ')),
        )

    stop_frequency = Instrument.control(
        "QSP",
        "SP%fHZ",
        """
        Control the stop-frequency for sweep-mode

        """,
        validator=strict_range,
        values=[0.001, 20000000],
        get_process=lambda v: float(v.lstrip(b'SP').rstrip(b'.HZ')),
        )

    store_preset = Instrument.setting(
        "SO%d",
        """
        Set the current configuration toa  a user-defined setup slot.
        6 slots avialable [0..5], with Slot 0 defining the power-on setup

        """,
        values=[0, 5],
        validator=strict_range,
        )

    sweep = Instrument.control(
       "QSW", "SW %d",
       """
       Control the sweep-mode of the unit

       ======  =======
       Value   Mode
       ======  =======
       "off"   no sweep
       "lin"   linear frequency sweep
       "log"   logarithmic frequency sweep
       ======  =======

       """,
       validator=strict_discrete_set,
       values={"off": 0,
               "lin": 1,
               "log": 2,
               },
       map_values=True,
       get_process=lambda v: v.lstrip(b'SW'),
       )

    symmetry = Instrument.control(
        "QSY",
        "SY%dPS",
        """
        Control the symmetry of the output signal.
        Allowed range is 1..99, representing 1..99%

        """,
        validator=strict_range,
        values=[1, 99],
        get_process=lambda v: int(v.lstrip(b'PH').rstrip(b'DG')),
        )

    time_intervall = Instrument.control(
        "QTI",
        "TI%fSN",
        """
        Control the sweep-time / trigger time intervall of the unit.

        """,
        validator=strict_range,
        values=[0.000001, 10000],
        get_process=lambda v: float(v.lstrip(b'TI').rstrip(b'SN')),
        )

    trigger_threshold = Instrument.control(
        "QLV", "LV%d",
        """
        Control the trigger threshold

        Possible selections "1V", "0V"

        """,
        validator=strict_discrete_set,
        values={"1V": 1,
                "0V": 2,
                },
        map_values=True,
        get_process=lambda v: v.lstrip(b'LV'),
        )

    VCO = Instrument.control(
       "QVC", "VC%d",
       """
       Control the VCO function

       ======  =======
       Value   VCO function
       ======  =======
       False   OFF
       True    ON
       ======  =======

       .. Note::
            Signal source needs to be connected to the FM/VCO-connector on the front
       """,
       validator=strict_discrete_set,
       values={False: 0, True: 1},
       map_values=True,
       get_process=lambda v: v.lstrip(b'VC'),
       )

    # TODO* Add vector commands

    def reset(self):
        """
        Initatiate a reset (like a power-on reset) of the HP3478A

        """
        self.adapter.connection.clear()

    def shutdown(self):
        """
        Provide a way to gracefully close the connection to the HP3314A

        """
        self.adapter.connection.clear()
        self.adapter.connection.close()
        super().shutdown()
