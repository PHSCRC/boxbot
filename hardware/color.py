from adafruit import TCS34725

try:
    from .component import *
except SystemError:
    from component import *

class ColorSensor(I2CComponent):
    def init(self):
        super().init()
        self.tcs = TCS34725(integrationTime=0xEB, gain=0x01)
        self._set_init()

    def readColor(self):
        rgb = tcs.getRawData(True)
        self._lastRGB = rgb

    def getColorTemp(self):
        return tcs.calculateColorTemperature(self._lastRGB)

    def getLux(self):
        return tcs.calculateLux(self._lastRGB)
        
    def cleanup(self):
        self.tcs.disable()
        del self.tcs
