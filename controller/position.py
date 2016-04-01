import asyncio

PARALLEL_TOLERANCE_MAX = 8
PARALLEL_TOLERANCE_LIMIT = 30
HALLWAY_LIMIT = 60
CENTER_OFFSET_LIMIT = 16
WALL_PROXIMITY_LIMIT = 26

NOT_PARALLEL = "NOT_PARALLEL"
OFF_CENTER = "OFF_CENTER"
L_OPENING_START = "L_OPENING_BEGINS"
L_OPENING_END = "L_OPENING_FULL"
R_OPENING_START = "R_OPENING_BEGINS"
R_OPENING_END = "R_OPENING_FULL"
FRONT_WALL_DETECT = "FRONT_WALL_PROXIMITY"

OPENINGS = {
    0: R_OPENING_START,
    1: R_OPENING_END,
    2: L_OPENING_END,
    3: L_OPENING_START
}

VERTICAL_PAIRS = {
    0: 1,
    1: 0,
    2: 3,
    3: 2,
    4: 5,
    5: 4
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
        
    def data_received(self, data):
        val = data.decode().strip().split()[-1]
        try:
            self.up._received(self.i, float(val))
        except TypeError:
            pass
        
class IRPositioning:
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.data = list([None for i in range(8)])
        self.cbs = defaultdict(lambda self=self: self.echo)
        self.state = defaultdict(bool)
        self.loop.run_until_complete(self.connect())

    def echo(self, *args):
        print("\t".join([str(i[0]) for i in self.state.items() if i[1]]),
              self.data, sep="\n", end="\n\n")

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
        self.loop.call_soon(self.cbs[name], state, *args)
        
    def _received(self, i, val):
        self.data[i] = val
        if i < 6:
            vdiff = abs(self.data[VERTICAL_PAIRS[i]] - val)
            if val < PARALLEL_TOLERANCE_LIMIT:
                self._set(NOT_PARALLEL, PARALLEL_TOLERANCE_MAX < vdiff)
        if i < 4:
            hdiff = abs(self.data[HORIZONTAL_PAIRS[i]] - val)
            self._set(OPENINGS[i], val > HALLWAY_LIMIT)
            self._set(OFF_CENTER, hdiff > CENTER_OFFSET_LIMIT and
                      val < HALLWAY_LIMIT)
        if 3 < i < 6:
            self._set(FRONT_WALL_DETECT,
                      sum(self.data[4:6]) / 2 < WALL_PROXIMITY_LIMIT)
