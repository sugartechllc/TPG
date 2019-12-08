"""
BME280 (I2C) abstraction
"""
import Adafruit_BME280

# pylint: disable=C0103
# pylint: disable=C0325

class bme280(object):
    """
    Interface with an I2C connect BME280 sensor.
    """
    def __init__(self):
        self.sensor = Adafruit_BME280.BME280(t_mode=Adafruit_BME280.BME280_OSAMPLE_8,
                                             p_mode=Adafruit_BME280.BME280_OSAMPLE_8,
                                             h_mode=Adafruit_BME280.BME280_OSAMPLE_8)

    def reading(self):
        """
        Return a hash containing sensor readings.
        The hash will contain:
           temp_C
           press_mb
           rh
        """
        retval = {}
        retval["temp_C"] = "{:.2f}".format(self.sensor.read_temperature())
        retval["pres_mb"] = "{:.2f}".format(self.sensor.read_pressure()/100)
        retval["rh"] = "{:.2f}".format(self.sensor.read_humidity())

        return retval

if __name__ == '__main__':
    bme280 = bme280()
    print(bme280.reading())
