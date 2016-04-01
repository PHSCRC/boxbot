import asyncio

class Extinguisher:
    def __init__(self, channel=2):
        self.loop = asyncio.get_event_loop()
        self._fd = open("/var/run/motor{}".format(channel), "w")
        self.loop.run_until_complete(self.connect())
        self.__speed = 0

    @asyncio.coroutine
    def connect(self):
        self._motor, pr = yield from self.loop.connect_write_pipe(asyncio.Protocol, self._fd)

    @property
    def speed(self):
        return self.__speed

    @speed.setter
    def speed(self, val):
        self.__speed = val
        self._motor.write("{}\n".format(val).encode())

    def _stop(self):
        self.speed = 0
        
    def go(self):
        self.speed = 1
        self.loop.call_later(0.2, self._stop)
        
