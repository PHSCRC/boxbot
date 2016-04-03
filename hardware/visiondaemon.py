
import atexit, time, sys, os

from .visionpipe import *

COMPONENTS = (
    Vision(),
    VisionController()
)

@atexit.register
def cleaner():
    for i in COMPONENTS:
        i.cleanup()

for i in COMPONENTS:
    i.init()

def main():
    for i in COMPONENTS:
        if hasattr(i, "start"):
            i.start()
    while True:
        time.sleep(1)

main()
