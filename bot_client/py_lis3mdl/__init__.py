# -*- coding: utf-8 -*-
"""
Python driver for the LIS3MDL Magnetic Sensor.

you will get three 16 bit signed integers, representing the values
of the magnetic sensor on axis X, Y and Z, e.g. [-1257, 940, -4970].
"""

import logging
import math
import time
import smbus2

DFLT_BUS = 1
DFLT_ADDRESS = 0x1E

REG_XOUT_LSB = 0x28  # Output Data Registers for magnetic sensor.
REG_XOUT_MSB = 0x29
REG_YOUT_LSB = 0x2A
REG_YOUT_MSB = 0x2B
REG_ZOUT_LSB = 0x2C
REG_ZOUT_MSB = 0x2D
REG_STATUS_1 = 0x27  # Status Register.
REG_TOUT_LSB = 0x2E  # Output Data Registers for temperature.
REG_TOUT_MSB = 0x2F
REG_CONTROL_1 = 0x20  # Control Register #1.
REG_CONTROL_2 = 0x21  # Control Register #2.
REG_CONTROL_3 = 0x22  # Control Register #3.
REG_RST_PERIOD = 0x0B  # SET/RESET Period Register.
REG_CHIP_ID = 0x0F  # Chip ID register.

REG_REBOOT = 0x08

# Flags for Status Register #1.
STAT_DRDY = 0b00001111  # Data Ready.
STAT_OVL = 0b11110000  # Overflow flag.

# Flags for Control Register 1.
ODR_10HZ = 0b00010000  # Output Data Rate Hz.
ODR_20HZ = 0b00010100
ODR_40HZ = 0b00011000
ODR_80HZ = 0b00011100
LO_PWR = 0b00000000  # Operating mode
MED_PWR = 0b00100000
HI_PWR = 0b01000000


class LIS3MDL(object):
    """Interface for the LIS3MDL 3-Axis Magnetic Sensor."""

    def __init__(
        self,
        i2c_bus=DFLT_BUS,
        address=DFLT_ADDRESS,
        output_data_rate=ODR_80HZ,
        operating_mode=LO_PWR,
        fast_ODR=1,
    ):

        self.address = address
        self.bus = smbus2.SMBus(i2c_bus)
        self.output_data_rate = output_data_rate
        self.operating_mode = operating_mode
        self.fast_ODR = fast_ODR
        self._declination = -10.10
        self._calibration = [
            [1.419921036152277, -0.029949764313015315, -659.2571999858343],
            [-0.029949764313015315, 1.0021360882289305, 1390.9391316004956],
            [0.0, 0.0, 1.0],
        ]
        chip_id = self._read_byte(REG_CHIP_ID)
        if chip_id != 0x3D:
            msg = "Chip ID returned 0x%x instead of 0x3d; is the wrong chip?"
            logging.warning(msg, chip_id)
        self._write_byte(REG_CONTROL_1, operating_mode | output_data_rate | fast_ODR)

    def __del__(self):
        self._write_byte(REG_CONTROL_2, REG_REBOOT)

    def mode_continuous(self):
        self._write_byte(REG_CONTROL_3, 0x00)  # Set operation mode.

    def _write_byte(self, registry, value):
        self.bus.write_byte_data(self.address, registry, value)
        time.sleep(0.01)

    def _read_byte(self, registry):
        return self.bus.read_byte_data(self.address, registry)

    def _read_word(self, registry):
        """Read a two bytes value stored as LSB and MSB."""
        low = self.bus.read_byte_data(self.address, registry)
        high = self.bus.read_byte_data(self.address, registry + 1)
        val = (high << 8) + low
        return val

    def _read_word_2c(self, registry):
        """Calculate the 2's complement of a two bytes value."""
        val = self._read_word(registry)
        if val >= 0x8000:  # 32768
            return val - 0x10000  # 65536
        else:
            return val

    def get_data(self):
        """Read data from magnetic and temperature data registers."""
        i = 0
        [x, y, z, t] = [None, None, None, None]
        while i < 20:  # Timeout after about 0.20 seconds.
            status = self._read_byte(REG_STATUS_1)
            if status & STAT_OVL:
                # Some values have reached an overflow.
                msg = "Magnetic sensor overflow."
                # logging.warning(msg)
            if status & STAT_DRDY:
                # Data is ready to read.
                x = self._read_word_2c(REG_XOUT_LSB)
                y = self._read_word_2c(REG_YOUT_LSB)
                z = self._read_word_2c(REG_ZOUT_LSB)
                t = self._read_word_2c(REG_TOUT_LSB)
                break
            else:
                # Waiting for DRDY.
                time.sleep(0.01)
                i += 1
        return [x, y, z, t]

    def get_magnet_raw(self):
        """Get the 3 axis values from magnetic sensor."""
        [x, y, z, t] = self.get_data()
        return [x, y, z]

    def get_magnet(self):
        """Return the horizontal magnetic sensor vector with (x, y) calibration applied."""
        [x, y, z] = self.get_magnet_raw()
        if x is None or y is None:
            [x1, y1] = [x, y]
        else:
            c = self._calibration
            x1 = x * c[0][0] + y * c[0][1] + c[0][2]
            y1 = x * c[1][0] + y * c[1][1] + c[1][2]
        return [x1, y1]

    def get_bearing_raw(self):
        """Horizontal bearing (in degrees) from magnetic value X and Y."""
        [x, y, z] = self.get_magnet_raw()
        if x is None or y is None:
            return None
        else:
            b = math.degrees(math.atan2(y, x))
            if b < 0:
                b += 360.0
            return b

    def get_bearing(self):
        """Horizontal bearing, adjusted by calibration and declination."""
        [x, y] = self.get_magnet()
        if x is None or y is None:
            return None
        else:
            b = math.degrees(math.atan2(y, x))
            if b < 0:
                b += 360.0
            b += self._declination
            if b < 0.0:
                b += 360.0
            elif b >= 360.0:
                b -= 360.0
        return b

    def get_temp(self):
        """Raw (uncalibrated) data from temperature sensor."""
        [x, y, z, t] = self.get_data()
        return t

    def set_declination(self, value):
        """Set the magnetic declination, in degrees."""
        try:
            d = float(value)
            if d < -180.0 or d > 180.0:
                logging.error("Declination must be >= -180 and <= 180.")
            else:
                self._declination = d
        except:
            logging.error("Declination must be a float value.")

    def get_declination(self):
        """Return the current set value of magnetic declination."""
        return self._declination

    def set_calibration(self, value):
        """Set the 3x3 matrix for horizontal (x, y) magnetic vector calibration."""
        c = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
        try:
            for i in range(0, 3):
                for j in range(0, 3):
                    c[i][j] = float(value[i][j])
            self._calibration = c
        except:
            logging.error("Calibration must be a 3x3 float matrix.")

    def get_calibration(self):
        """Return the current set value of the calibration matrix."""
        return self._calibration

    declination = property(
        fget=get_declination,
        fset=set_declination,
        doc="Magnetic declination to adjust bearing.",
    )

    calibration = property(
        fget=get_calibration,
        fset=set_calibration,
        doc="Transformation matrix to adjust (x, y) magnetic vector.",
    )
