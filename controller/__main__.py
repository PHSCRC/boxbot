from .maze import *

import asyncio, atexit

loop = asyncio.get_event_loop()

@atexit.register
def quit():
    pled.on = False
    loop.run_until_complete(asyncio.sleep(1))

loop.run_forever()

from .navigation import Navigator
from .start import SoundDetect
from .status import LED

pled = LED(2)
pled.on = True

led = LED(1)

def go():
    led.on = True
    loop.stop()

s = SoundDetect()
s.register(go)
loop.run_forever()

n = Navigator()
loop.run_forever()
