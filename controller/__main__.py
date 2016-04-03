from .navigation import Navigator
from .start import SoundDetect
from .status import LED

import asyncio, atexit

pled = LED(2)
pled.on = True

loop = asyncio.get_event_loop()

led = LED(1)

@atexit.register
def quit():
    pled.on = False
    loop.run_until_complete(asyncio.sleep(1))

def go():
    led.on = True
    loop.stop()

s = SoundDetect()
s.register(go)
loop.run_forever()

n = Navigator()
loop.run_forever()
