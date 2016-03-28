
from warnings import warn

import os, sys
if os.environ.get("USE_DUMMY_MODULES"):
    sys.path.append(os.path.join(os.path.dirname(__file__),"../dummies"))

"""try:
    from .display import *
    from .rf import *
except ImportError as err:
    warn("Cannot import Display or RF modules, probably missing RPi.GPIO.",
         RuntimeWarning, 2)

try:
    from .adc import *
    from .keypad import *
except ImportError as err:
    warn("Cannot import ADC or Keypad modules, probably missing I2C support.",
         RuntimeWarning, 2)

from .app import *"""
