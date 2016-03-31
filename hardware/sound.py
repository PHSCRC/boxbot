
try:
    from .component import *
except SystemError:
    from component import *

import RPi.GPIO as gpio
    
PIN = 21
    
class SoundDetect(GPIOComponent):
    def __init__(self, pin=PIN):
        self.__pin = pin
        super().__init__(inpins=(pin,), fn="sound")

    def __handle(self, channel):
        self.writedata(int(gpio.input(self.__pin)))
        
    def init(self):
        super().init()
        gpio.add_event_detect(self.__pin, gpio.BOTH,
                              bouncetime=200, callback=self.__handle)

    def cleanup(self):
        gpio.remove_event_detect(self.__pin)
        super().cleanup()
