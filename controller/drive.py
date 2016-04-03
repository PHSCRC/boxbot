import asyncio

SLIGHT_TIME = 0.1
TURN_TIME = 0.75

class DriveMotors:
    def __init__(self, left=0, right=1):
        self.loop = asyncio.get_event_loop()
        self._left = open("/var/run/motor{}".format(left),"w")
        self._right = open("/var/run/motor{}".format(right),"w")
        self.__left = 0
        self.__right = 0
        self.loop.run_until_complete(self.connect())
        self.__handle = None

    @asyncio.coroutine
    def connect(self):
        self._left, lpr = yield from self.loop.connect_write_pipe(asyncio.Protocol, self._left)
        self._right, rpr = yield from self.loop.connect_write_pipe(asyncio.Protocol, self._right)

    @property
    def left(self):
        return self.__left

    @left.setter
    def left(self, val):
        self.cancel()
        val = val * 0.999
        self.__left = float(val)
        self._left.write("{}\n".format(val).encode())
    
    @property
    def right(self):
        return self.__right

    @right.setter
    def right(self, val):
        self.cancel()
        val = val * 0.9
        self.__right = val
        self._right.write("{}\n".format(val).encode())
        
    def cancel(self):
        if self.__handle: self.__handle.cancel()

    def stop(self):
        self.right = 0
        self.left = 0
        
    def forward(self):
        self.right = -1
        self.left = 1

    def turnright(self, t=TURN_TIME):
        self.right = 1
        self.left = 1
        if t:
            self.__handle = self.loop.call_later(t, self.forward)

    def turnleft(self, t=TURN_TIME):
        self.right = -1
        self.left = -1
        if t:
            self.__handle = self.loop.call_later(t, self.forward)

    def slightright(self, t=SLIGHT_TIME):
        print("Slight right")
        self.right = -0.09
        self.left = 1
        if t:
            self.__handle = self.loop.call_later(t, self.forward)

    def slightleft(self, t=SLIGHT_TIME):
        print("Slight left")
        self.right = -1
        self.left = 0.09
        if t:
            self.__handle = self.loop.call_later(t, self.forward)

