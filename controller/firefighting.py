import asyncio

class Extinguisher:
    def __init__(self, channel=8):
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

    def _reverse(self):
        self.speed = 1
        self.loop.call_later(0.02, self._stop)
        
    def go(self):
        self.speed = -2
        self.loop.call_later(0.5, self._reverse)

class VisionProtocol(asyncio.Protocol):
    def __init__(self, up):
        self.up = up

    def data_received(self, data):
        text = data.decode().strip().split()[-1]
        state, deg = [float(i) for i in text.split(",")]
        self.up._received(state, deg)

class FlameDetect:
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self._fd = open("/var/run/visioncontrol0","w")
        self.__on = None
        self.cb = None
        self.laststate = None
        self.loop.run_until_complete(self.connect())

    @asyncio.coroutine
    def connect(self):
        self._controller, pr = yield from self.loop.connect_write_pipe(asyncio.Protocol, self._fd)
        yield from self.loop.connect_read_pipe(lambda up=self: VisionProtocol(up), open("/var/run/vision0"))

    def register(self, cb):
        self.cb = cb

    def _received(self, state, deg):
        if self.laststate != state or state in (3, 4):
            if self.cb and self.__on:
                self.cb(state, deg)
                self.laststate = state
        
    @property
    def on(self):
        return self.__on

    @on.setter
    def on(self, val):
        self.__on = val
        self._controller.write("{}\n".format(int(bool(val))).encode())
