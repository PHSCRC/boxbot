import asyncio

class DriveMotorControl:
    def __init__(self, left=0, right=1):
        self.loop = asyncio.get_event_loop()
        left = open("/var/run/motor{}".format(left),"w")
        right = open("/var/run/motor{}".format(right),"w")
        self.__left = 0
        self.__right = 0
        self._left, lpr = self.loop.connect_write_pipe(asyncio.Protocol, left)
        self._right, rpr = self.loop.connect_write_pipe(asyncio.Protocol, right)

    @property
    def left(self):
        return self.__left

    @left.setter
    def setleft(self, val):
        self.__left = val
        self._left.write("{}\n".format(val))
    
    @property
    def right(self):
        return self.__right

    @right.setter
    def setright(self, val):
        self.__right = val
        self._right.write("{}\n".format(val))
        
    def stop(self):
        self.left = 0
        self.right = 0
        
    def forward(self):
        self.left = 1
        self.right = -1

    def turnright(self):
        self.right = 1
        self.left = 1
        self.call_later(1, self.stop)

    def turnleft(self):
        self.right = -1
        self.left = -1
        self.call_later(1, self.stop)
