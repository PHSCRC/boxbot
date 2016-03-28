
try:
    from .adc import *
except SystemError:
    from adc import *

class InterpolatedDistance(ADC4):
