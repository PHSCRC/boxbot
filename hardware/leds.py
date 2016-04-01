
try:
    from .component import *
except SystemError:
    from component import *

import RPi.GPIO as gpio

RED = 16
GREEN = 19
BLUE = 26
YELLOW = 20

class LEDController(LoopedComponent, GPIOComponent):
    _FN = "led"
    _mswait = 100
    
    def __init__(self, red=RED, green=GREEN, blue=BLUE, yellow=YELLOW):
        self.__pins = (red, green, blue, yellow)
        super().__init__(self.__pins,numchannels=4)

    def tick(self):
        for i in range(4):
            val = self.readdata(i)
            if not (val is None):
                gpio.output(self.__pins[i], bool(val))
