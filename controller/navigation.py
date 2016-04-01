import asyncio

class DriveMotorControl:
    def __init__(self, left=0, right=1):
        self.loop = asyncio.get_event_loop()
        self._left = open("/var/run/motor{}".format(left),"w")
        self._right = open("/var/run/motor{}".format(right),"w")
        self.__left = 0
        self.__right = 0
        self.loop.run_until_complete(self.connect())

    @asyncio.coroutine
    def connect(self):
        self._left, lpr = yield from self.loop.connect_write_pipe(asyncio.Protocol, self._left)
        self._right, rpr = yield from self.loop.connect_write_pipe(asyncio.Protocol, self._right)

    @property
    def left(self):
        return self.__left

    @left.setter
    def left(self, val):
        self.__left = val
        self._left.write("{}\n".format(val).encode())
    
    @property
    def right(self):
        return self.__right

    @right.setter
    def right(self, val):
        self.__right = val
        self._right.write("{}\n".format(val).encode())
        
    def stop(self):
        self.left = 0
        self.right = 0
        
    def forward(self):
        self.left = 1
        self.right = -1

    def turnright(self):
        self.right = 1
        self.left = 1
        return self.loop.call_later(1, self.stop)

    def turnleft(self):
        self.right = -1
        self.left = -1
        return self.loop.call_later(1, self.stop)
