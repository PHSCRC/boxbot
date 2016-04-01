
import os, math

try:
    from .adc import *
except SystemError:
    from adc import *

from bisect import bisect_right, bisect_left
    
class InterpolatedDistance(ADC4):
    def __init__(self, profiles, addr, **kwargs):
        super().__init__(addr, fn="distance", **kwargs)
        self.__mm = []
        self.__v = []
        for i in profiles:
            i.sort(key=lambda x: -x[0])
            repacked = tuple(zip(*i))
            self.__mm.append(repacked[0])
            self.__v.append(repacked[1])
        
    def process_reading(self, reading, pin):
        v = super().process_reading(reading, pin)
        v = v + 0.6255 * math.log(v) + 0.6249
        index = bisect_right(self.__v[pin], v)
        mm = self.__mm[pin]
        return mm[min(max(index, 0), len(mm) - 1)] / 10

    @classmethod
    def from_files(cls, addr, *args, base_path=None, **kwargs):
        profiles = []
        for fn in args:
            fd = open(os.path.join(base_path,fn) if base_path else fn)
            lines = fd.readlines()
            fd.close()
            data = []
            for i in lines:
                line = i.strip().split(",")
                data.append((int(line[0]), float(line[1])))
            profiles.append(data)
        return cls(profiles, addr, **kwargs)
