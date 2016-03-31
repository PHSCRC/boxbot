from adafruit import TCS34725

try:
    from .component import *
except SystemError:
    from component import *

class ColorSensor(LoopedComponent, I2CComponent):
    _mswait = 20
    _FN = "color"
    
    def init(self):
        super().init()
        self.tcs = TCS34725(integrationTime=0xEB, gain=0x01)
        self._set_init()

    def readColor(self):
        rgb = self.tcs.getRawData()
        self._lastRGB = rgb
        return rgb

    def getColorTemp(self):
        return self.tcs.calculateColorTemperature(self._lastRGB)

    def getLux(self):
        return self.tcs.calculateLux(self._lastRGB)
        
    def cleanup(self):
        self.tcs.disable()

    def tick(self):
        rgbc = self.readColor()
        self.writedata((rgbc["r"], rgbc["g"], rgbc["b"], rgbc["c"]))
