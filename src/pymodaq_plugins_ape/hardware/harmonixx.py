# -*- coding: utf-8 -*-

import numpy as np
import pyvisa

class Harmonixx():

    def __init__(self):
        self._cmd_from_axis = {
            "SHG": "SMS",
            "THG": "SMT",
            "DC": "SMD",
            "WP": "SMW",
            "WAVELENGTH": "NWL",
        }

        self._axis_index = {
            "SHG": 1,
            "THG": 2,
            "DC": 3,
            "WP": 4,
        }

    def open_communication(self, address):
        '''
            Opens VISA communication with Harmonixx harmonics generator

            Input:
                str : VISA address

            Output:
                None
        '''
        try:
            self._rm = pyvisa.ResourceManager()
            self._device = self._rm.open_resource(address)
            self._device.baud_rate = 38400
            self._device.timeout = 20000
            self._device.write_termination = ","
            self._device.read_termination = "\n"
            self._device.clear()
            initialized = True

        except:
            initialized = False

        return initialized

    def close_communication(self):
        '''
            Closes VISA communication with Chameleon laser source

            Input:
                None

            Output:
                None
        '''
        self._device.close()

    def get_pos(self, axis):
        '''
            Gets position of specified axis

            Input:
                axis : str

            Output:
                pos : int
        '''

        pos = float(self._device.query("GWL")[3:])*1e-9 if axis == "WAVELENGTH" \
            else float(self._device.query("GPS")[3:].split(" ")[self._axis_index[axis]])
        return pos

    def move_abs(self, axis, abs_pos):
        '''
            Moves axis to specified position (absolute)

            Input:
                axis : str
                abs_pos : int

            Output:
                None
        '''

        cmd = self._cmd_from_axis[axis]

        if axis == "WAVELENGTH":
            param = (4-len(str(int(abs_pos*1e9))))*'0'+"{}".format(int(abs_pos*1e9))
        else:
            rel_pos = abs_pos - self.get_pos(axis)
            sign = "+" if rel_pos>0 else "-"
            pos = abs(int(rel_pos))
            param = sign+(3-len(str(pos)))*'0'+"{}".format(pos)

        self._device.query("{}{}".format(cmd, param))

    def move_rel(self, axis, rel_pos):
        '''
            Moves axis to specified position (relative)

            Input:
                axis : str
                rel_pos : int

            Output:
                None
        '''

        cmd = self._cmd_from_axis[axis]

        if axis == "WAVELENGTH":
            abs_pos = self.get_pos("WAVELENGTH") + rel_pos
            param = (4-len(str(int(abs_pos*1e9))))*'0'+"{}".format(int(abs_pos*1e9))
        else:
            sign = "+" if rel_pos > 0 else "-"
            pos = abs(int(rel_pos))
            param = sign + (3 - len(str(pos))) * '0' + "{}".format(pos)

        self._device.query("{}{}".format(cmd, param))

    def calibrate(self, axis):
        '''
            Calibrates the specified axis

            Input:
                axis : str

            Output:
                None
        '''
        cmd = self._cmd_from_axis[axis]
        if axis == "WAVELENGTH":
            self._device.query("{}0800".format(cmd))
        else:
            self._device.query("{}+0".format(cmd))

    def abort(self):
        '''
            Stops movement of the stage

            Input:
                None

            Output:
                None
        '''
        self._device.query("BRK")