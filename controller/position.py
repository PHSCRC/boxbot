import asyncio

PARALLEL_TOLERANCE_MAX = 4
PARALLEL_TOLERANCE_LIMIT = 30
HALLWAY_LIMIT = 28
CENTER_OFFSET_LIMIT = 6
WALL_PROXIMITY_LIMIT = 30

STEADY_WAIT = 0.05 # seconds

NOT_PARALLEL = "NOT_PARALLEL"
OFF_CENTER = "OFF_CENTER"
L_OPENING_START = "L_OPENING_BEGINS"
L_OPENING_END = "L_OPENING_END"
R_OPENING_START = "R_OPENING_BEGINS"
R_OPENING_END = "R_OPENING_END"
L_OPENING = "L_OPENING_BOTH"
R_OPENING = "R_OPENING_BOTH"
FRONT_WALL_DETECT = "FRONT_WALL_PROXIMITY"
FOUR_WAY_DETECT = "4WAY_DETECT"

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
    def __init__(self, debug=False):
        self._debug = debug
        self.loop = asyncio.get_event_loop()
        self.data = list([None for i in range(8)])
        self.cbs = defaultdict(lambda self=self: self.echo)
        self.__handles = defaultdict(bool)
        self.state = defaultdict(bool)
        self.__blocked = False
        self.loop.run_until_complete(self.connect())

    @property
    def blocked(self):
        return self.__blocked

    @blocked.setter
    def blocked(self, val):
        self.__blocked = val
        
    def echo(self, *args):
        if self._debug:
            print("\t".join([str(i[0]) for i in self.state.items() if i[1]]),
                  self.data, sep="\n", end="\n\n")

    @asyncio.coroutine
    def connect(self):
        for i in range(8):
            fd = open("/var/run/distance{}".format(i))
            yield from self.loop.connect_read_pipe(
                lambda i=i, up=self: IRProtocol(i, up), fd)

    def register(self, name, func):
        self.cbs[name] = func

    def get(self, i):
        return self.data[i]

    def _set(self, name, state, *args):
        if self.state[name] == state:
            return False
        if self.__blocked:
            return None
        self.state[name] = state
        if self.__handles[name]: self.__handles[name].cancel()
        self.__handles[name] = self.loop.call_later(
            STEADY_WAIT, self.cbs[name], name, state, *args)
        
    def _received(self, i, val):
        self.data[i] = val
        if i < 6:
            vdiff = abs(self.data[VERTICAL_PAIRS[i]] - val)
            if val < PARALLEL_TOLERANCE_LIMIT:
                self._set(NOT_PARALLEL, PARALLEL_TOLERANCE_MAX < vdiff)
        if i < 4:
            hdiff = abs(self.data[HORIZONTAL_PAIRS[i]] - val)
            self._set(OPENINGS[i], val > HALLWAY_LIMIT)
            self._set(R_OPENING, (self.state[OPENINGS[0]] and
                                  self.state[OPENINGS[1]]))
            self._set(L_OPENING, (self.state[OPENINGS[2]] and
                                  self.state[OPENINGS[3]]))
            self._set(OFF_CENTER, hdiff > CENTER_OFFSET_LIMIT and
                      (val < HALLWAY_LIMIT and
                       self.data[HORIZONTAL_PAIRS[i]] < HALLWAY_LIMIT))
        front_avg = sum(self.data[4:6]) / 2
        if 3 < i < 6:
            self._set(FRONT_WALL_DETECT, self.data[4] < WALL_PROXIMITY_LIMIT
                      or self.data[5] < WALL_PROXIMITY_LIMIT)
        self._set(FOUR_WAY_DETECT,
                  all([self.state[i] for i in OPENINGS.values()]) and
                  front_avg > HALLWAY_LIMIT)

__all__ = ["IRPositioning", "NOT_PARALLEL", "OFF_CENTER", "FRONT_WALL_DETECT",
           "L_OPENING_START", "L_OPENING_END", "R_OPENING_START",
           "R_OPENING_END", "FOUR_WAY_DETECT", "L_OPENING", "R_OPENING"]
