"""
BME280 (I2C) abstraction
"""
from Adafruit_BME280 import *

# pylint: disable=C0103
# pylint: disable=C0325

class bme280(object):
    def __init__(self):
        self.sensor = BME280(t_mode=BME280_OSAMPLE_8, p_mode=BME280_OSAMPLE_8, h_mode=BME280_OSAMPLE_8)

    def reading(self):
        """
        Return a hash containing sensor readings.
        The hash will contain:
           temp_C
           press_mb
           rh
        """
        retval = {}
        retval["temp_C"] = self.sensor.read_temperature()
        retval["pres_mb"] = self.sensor.read_pressure()/100
        retval["rh"] = self.sensor.read_humidity()

        return retval

if __name__ == '__main__':
    bme280 = bme280()
    print(bme280.reading())
