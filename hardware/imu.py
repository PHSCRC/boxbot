from Adafruit_BNO055 import BNO055

try:
    from .component import *
except SystemError:
    from component import *

class IMU(object):
    bno = None

    @classmethod
    def getIMU(cls):
        if not cls.bno:
            cls.bno = BNO055.BNO055()
            cls.bno.begin()
        return cls.bno

class IMUComponent(LoopedComponent, Component):
    def init(self):
        super().init()
        self.bno = IMU.getIMU()
        self._set_init()

    def cleanup(self):
        super().cleanup()
    
class Gyroscope(IMUComponent):
    _mswait = 30
    _FN = 'gyro'
    
    def tick(self):
        self.writedata(self.bno.read_gyroscope())  # x,y,z degrees per sec


class Accelerometer(IMUComponent):
    _mswait = 30
    _FN = 'accel'

    def tick(self):
        self.writedata(self.bno.read_accelerometer())  # x,y,z meters per sec

class Euler(IMUComponent):
    _mswait = 30
    _FN = 'euler'

    def tick(self):
        self.writedata(self.bno.read_euler())  # heading, roll, pitch degrees
