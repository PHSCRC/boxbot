#!/usr/bin/env python3

from adafruit.trellis import Adafruit_Trellis

try:
    from .component import *
except SystemError:
    from component import *

def str_to_bools(s):
    """Converts a string to an array of booleans. All characters
    excepts spaces becomes True."""
    out = []
    for i in s:
        out.append(False if i == " " else True)
    return out
    
class LEDKeypad(EventedInput, LoopedInput, I2CComponent):
    _mswait = 100

    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)

    def init(self, *args, **kwargs):
        self.trellis = Adafruit_Trellis()
        self.trellis.begin(self._address)
        super().init(*args, **kwargs)

    def cleanup(self):
        self.trellis.clear()
        self.trellis.writeDisplay()
        super().cleanup()
        del self.trellis

    def tick(self):
        self._checkInit()
        if self.trellis.readSwitches():
            for i in range(16):
                if self.trellis.justPressed(i):
                    self._handle_pin(i)

    def __led(self, val, index):
        getattr(self.trellis,"setLED" if val else "clrLED")(index)

    def insert(self, row, col, val):
        if not hasattr(val, "__iter__"):
            val = [val]
        for i in val:
            self.__led(i, row*4 + col)
            col += 1
            if col > 3:
                row += 1
                col = 0
            if row > 3:
                return False

    def flush(self):
        self.trellis.writeDisplay()
        
    def set_leds(self, leds={}):
        self._checkInit()
        for i, val in leds.items():
            self.__led(val, i)
        self.flush()
