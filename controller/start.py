import asyncio

class SoundStartProtocol(asyncio.Protocol):
    def __init__(self, up):
        self.up = up

    def data_received(self, data):
        text = data.decode().strip().split()[-1]
        self.up._received(int(text))

class SoundDetect:
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.cb = None
        self.loop.run_until_complete(self.connect())

    @asyncio.coroutine
    def connect(self):
        yield from self.loop.connect_read_pipe(lambda up=self: SoundStartProtocol(up), open("/var/run/sound0"))

    def register(self, cb):
        self.cb = cb

    def _received(self, state):
        if state and self.cb:
            self.cb()
        
