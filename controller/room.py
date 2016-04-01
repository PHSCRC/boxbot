import asyncio

CLEAR_THRESHOLD = 2500

class RoomBorderProtocol(asyncio.Protocol):
    def __init__(self, up):
        self.up = up

    def data_received(self, data):
        text = data.decode().strip().split()[-1]
        rgbc = tuple([int(i) for i in text.split(",")])
        up._received(rgbc)

class RoomEntryDetection:
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.cb = None
        self.data = (0,0,0,0)
        self.state = False
        self.__handle = None
        self.loop.run_until_complete(self.connect)

    @asyncio.coroutine
    def connect(self):
        yield from self.loop.connect_read_pipe(
            lambda up=self: RoomBorderProtocol(up), open("/var/run/color0"))

    def register(self, cb):
        self.cb = cb
        
    def _received(self, rgbc):
        self.data = rgbc
        newstate = rgbc[3] > CLEAR_THRESHOLD
        if newstate != self.state:
            self.state = newstate
            if self.cb:
                if self.__handle: self.__handle.cancel()
                self.__handle = self.loop.call_after(0.05, cb, newstate)
