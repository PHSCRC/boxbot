import asyncio, traceback

SLIGHT_TIME = 0.1
TURN_TIME = 0.75

class IMUProtocol(asyncio.Protocol):
    def __init__(self, up):
        self.up = up

    def data_received(self, data):
        text = data.decode().strip().split()[-1]
        rgbc = tuple([int(i) for i in text.split(",")])
        self.up._received(rgbc)

class IMU:
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.data = (0,0,0)
        self.initial = False
        self._mark = 0
        self.loop.run_until_complete(self.connect())

    @asyncio.coroutine
    def connect(self):
        yield from self.loop.connect_read_pipe(
            lambda up=self: IMUProtocol(up), open("/var/run/euler0"))
        
    def _received(self, euler):
        self.data = euler
        self.heading = euler[0]
        if not initial:
            self.initial = euler

    def mark(self):
        self._mark = self.heading
            
    @property
    def from_start(self):
        return self.heading - self.initial[0]
    @property
    def from_mark(self):
        return self.heading - self._mark

class DriveMotors:
    def __init__(self, left=0, right=1):
        self.loop = asyncio.get_event_loop()
        self._left = open("/var/run/motor{}".format(left),"w")
        self._right = open("/var/run/motor{}".format(right),"w")
        self.__left = 0
        self.__right = 0
        self.imu = IMU()
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
        #val = val * 0.999
        self.__left = val
        #if val == 0:
            #traceback.print_stack()
        self._left.write("{}\n".format(val).encode())
    
    @property
    def right(self):
        return self.__right

    @right.setter
    def right(self, val):
        self.cancel()
        #val = val * 0.9
        self.__right = val
        self._right.write("{}\n".format(val).encode())
        
    def cancel(self):
        if self.__handle: self.__handle.cancel()

    def __set(self, right, left, t=None):
        self.imu.mark()
        self.right = right
        self.left = left
        if t:
            self.__handle = self.loop.call_later(t, self.forward)
        
    def stop(self):
        self.__set(0, 0)
        
    def forward(self):
        self.__set(-1, 1)
        
    def backward(self, t=None):
        self.__set(1, -1, t)

    def turnright(self, t=TURN_TIME):
        self.__set(1, 1, t)

    def turnleft(self, t=TURN_TIME):
        self.__set(-1, -1, t)

    def slightright(self, t=SLIGHT_TIME):
        print("Slight right")
        self.__set(-0.09, 1, t)

    def slightleft(self, t=SLIGHT_TIME):
        print("Slight left")
        self.__set(-1, 0.09, t)

