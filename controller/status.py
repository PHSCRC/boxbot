import asyncio

class LED:
    def __init__(self, led):
        self.loop = asyncio.get_event_loop()
        self._fd = open("/var/run/led{}".format(led),"w")
        self.loop.run_until_complete(self.connect())

    @asyncio.coroutine
    def connect(self):
        self._led, pr = yield from self.loop.connect_write_pipe(asyncio.Protocol, self._fd)

    @property
    def on(self):
        return None

    @on.setter
    def on(self, val):
        self._led.write("{}\n".format(int(bool(val))).encode())
