import asyncio

PARALLEL_TOLERANCE_MAX = 4
PARALLEL_TOLERANCE_LIMIT = 12
HALLWAY_LIMIT = 30
CENTER_OFFSET_LIMIT = 8

NOT_PARALLEL = "NOT_PARALLEL"
OFF_CENTER = "OFF_CENTER"
OPENING_BEGINS = "OPENING_BEGINS"
OPENING_FULL = "OPENING_FULL"

VERTICAL_PAIRS = {
    0: 1,
    1: 0,
    2: 3,
    3: 2
}

HORIZONTAL_PAIRS = {
    0: 3,
    3: 0,
    1: 2,
    2: 1
}
FORWARD_IR = (0, 3)

from collections import defaultdict

class IRProtocol(asyncio.Protocol):
    def __init__(self, i, positioner):
        self.i = i
        self.up = positioner
        
    def data_received(data):
        val = self.data.decode().strip().split()[-1]
        self.up._received(self.i, float(val))
        
class IRPositioning:
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.data = list([0 for i in range(8)])
        self.loop.run_until_complete(self.connect())
        self.cbs = defaultdict(lambda: self.echo)
        self.state = defaultdict(bool)

        def echo(self, *args):
            print(self.state, self.data)

    @asyncio.coroutine
    def connect(self):
        for i in range(8):
            fd = open("/var/run/distance{}".format(i))
            yield from self.loop.connect_read_pipe(
                lambda i=i, up=self: IRProtocol(i, up), fd)

    def register_cb(self, name, func):
        self.cbs[name] = func

    def get(self, i):
        return self.data[i]

    def _set(self, name, state, *args):
        if self.state[name] == state:
            return False
        self.state[name] = state
        self.call_soon(self.cbs[name], state, *args)
    
    def _received(self, i, val):
        self.data[i] = val
        vdiff = abs(self.data[VERTICAL_PAIRS[i]] - val)
        hdiff = abs(self.data[HORIZONTAL_PAIRS[i]] - val)
        if i < 6:
            self._set(NOT_PARALLEL,
                      PARALLEL_TOLERANCE_LIMIT > vdiff >
                      PARALLEL_TOLERANCE_MAX)
            self._set(OFF_CENTER, hdiff > CENTER_OFFSET_LIMIT)
            if i in FORWARD_IR:
                self._set(OPENING_BEGINS, val > HALLWAY_LIMIT)
            else:
                self._set(OPENING_FULL, val > HALLWAY_LIMIT)
