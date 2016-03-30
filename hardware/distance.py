
try:
    from .adc import *
except SystemError:
    from adc import *

from bisect import bisect_right
    
class InterpolatedDistance(ADC4):
    def __init__(self, profile, *args, **kwargs):
        super().__init__(*args, **kwargs)
        profile.sort(key=lambda x: -x[0])
        self.__mm, self.__v = zip(*profile)
        
    def process_reading(self, reading):
        v = super().process_reading(reading)
        return self.__mm[bisect_right(self.__v, v)] / 10

    @classmethod
    def from_file(cls, fn, *args, **kwargs):
        fd = open(fn)
        lines = fd.readlines()
        fd.close()
        data = []
        for i in lines:
            line = i.strip().split(",")
            data.append((int(line[0]), float(line[1])))
        return cls(data, *args, **kwargs)
