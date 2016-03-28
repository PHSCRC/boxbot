#!/usr/bin/env python3

from adafruit.ads1x15 import ADS1x15

from collections import deque

try:
    from .component import *
except SystemError:
    from component import *

IC = 0 # ADS1015 (12-bit ADC)
GAIN = 0x1000 # (+/- 4.096V for Rasberry Pi 3V3 supply)
SINGLE_SPS = SPS = 2400
WAITMS = 100

MILLIVOLTS = 1000

class ADC4(EventedInput, LoopedInput, I2CComponent):
    _mswait = 50

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.values = list([None for i in range(4)])
        self.__last_values = list([deque([0 for i in range(2)])
                                   for i in range(4)])

    def init(self, autostart=False):
        super().init()
        self.adc = ADS1x15(ic=IC, address=self._address)

    def cleanup(self):
        super().cleanup()
        del self.adc

    def get(self, pin):
        return self.values[pin]

    def read(self, pin):
        self._checkInit()
        return self.process_reading(
            self.adc.readADCSingleEnded(pin, GAIN, SINGLE_SPS))

    def process_reading(self, reading):
        return reading / MILLIVOLTS

    def tick(self):
        for i in range(4):
            v = self.read(i)
            try:
                self.__last_values[i].popleft()
            except IndexError:
                pass
            self.__last_values[i].append(v)
            val = (sum(self.__last_values[i]) /
                   len(self.__last_values[i]))
            if type(v) == int: val = int(val)
            #print(v, val, self.__last_values[i])
            if self.values[i] != val:
                self.values[i] = val
                self._handle_pin(i)
