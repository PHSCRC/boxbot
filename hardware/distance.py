
import os

try:
    from .adc import *
except SystemError:
    from adc import *

from bisect import bisect_right
    
class InterpolatedDistance(ADC4):
    def __init__(self, profiles, addr, *args, **kwargs):
        o = (addr - 0x48) * 4
        super().__init__("distance", *args, offset=o, addr=addr, **kwargs)
        self.__mm = []
        self.__v = []
        for i in profiles:
            i.sort(key=lambda x: -x[0])
            repacked = zip(*i)
            self.__mm.append(repacked[0])
            self.__v.append(repacked[1])
        
    def process_reading(self, reading, pin):
        v = super().process_reading(reading, pin)
        return self.__mm[pin][bisect_right(self.__v[pin], v)] / 10

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
        return cls(profiles, addr, *args, **kwargs)
