#!/usr/bin/env python3

from adafruit.i2c import Adafruit_I2C

try:
    from .component import *
except SystemError as err:
    from component import *

class Melexis(LoopedComponent, I2CComponent):
    _mswait = 50
    _FN = "temp"
    
    def init(self, fahrenheit=False):
        super().init()
        self._i2c = Adafruit_I2C(0x5A)
        self.mode = fahrenheit
        self._set_init()

    def readAmbient(self):
        return self._readTemp(0x06)
    
    def readObject(self):
        return self._readTemp(0x07)

    def readObject2(self):
        return self._readTemp(0x08)

    def getDifference(self):
        """Returns how much warmer the object is than the ambient
        temperature."""
        return self.readObject() - self.readAmbient()
    
    def _readTemp(self, reg):
        temp = self._i2c.readS16(reg)
        temp = temp * .02 - 273.15
        if self.mode:
            return (temp * 9 / 5) + 32
        else:
            return temp

    def tick(self):
        self.writedata((self.readObject(),
                        self.readAmbient()))
    
if __name__ == "__main__":
    sensor = Melexis(fahrenheit=True)
    import time
    with sensor:
        while True:
            print("Object: {}ºF ({}ºF warmer than ambient)".format(
                round(sensor.readObject(), 3),
                round(sensor.getDifference(), 3)))
            time.sleep(0.5)
