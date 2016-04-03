#!/usr/bin/env python3

from adafruit import ADS1x15

from collections import deque

try:
    from .component import *
except SystemError:
    from component import *

IC = 1 # ADS1015 (16-bit ADC)
GAIN = 0x1000 # (+/- 4.096V for Rasberry Pi 3V3 supply)
SINGLE_SPS = 64
SPS = 250
WAITMS = 100

MILLIVOLTS = 1000

MOVING_AVERAGE_LIMIT = 4

class ADC4(LoopedComponent, I2CComponent):
    _mswait = 10

    def __init__(self, addr, fn="adc", **kwargs):
        o = (addr - 0x48) * 4
        super().__init__(addr, fn, 4, o, **kwargs)
        self.values = list([None for i in range(4)])
        self.__last_values = list([deque(
            [0 for i in range(MOVING_AVERAGE_LIMIT)])
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
            self.adc.readADCSingleEnded(pin, GAIN, SINGLE_SPS),
            pin)

    def process_reading(self, reading, channel):
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
                self.writedata(val, i)
