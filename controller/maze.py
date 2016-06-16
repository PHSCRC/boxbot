import asyncio, atexit, random

from .drive import DriveMotors

loop = asyncio.get_event_loop()
driver = DriveMotors()

driver.forward()

def do_turn():
    random.choice((driver.turnleft, driver.turnright))()
    loop.call_later(3, do_turn)

loop.call_later(1, do_turn)
