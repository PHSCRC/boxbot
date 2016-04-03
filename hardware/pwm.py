from adafruit import PWM

try:
    from .component import *
except SystemError:
    from component import *

PULSE_MAX = 550
PULSE_CENTER = 400

MAX_PULSE = PULSE_MAX - PULSE_CENTER

class MotorDriver(LoopedComponent, I2CComponent):
    _mswait = 10
    
    def __init__(self):
        super().__init__(0x40, "motor", 12)
        
    def init(self):
        super().init()
        self.pwm = PWM(self._address)
        # Note if you'd like more debug output you can instead run:
        #pwm = PWM(0x40, debug=True)

        self.pwm.setPWMFreq(60)
        servoMin = 150  # Min pulse length out of 4096
        servoMax = 600  # Max pulse length out of 4096
        self._set_init()

    def setServoPulse(self, channel, pulse):
        pulseLength = 1000000                   # 1,000,000 us per second
        pulseLength /= 60                       # 60 Hz
        print("%d us per period" % pulseLength)
        pulseLength /= 4096                     # 12 bits of resolution
        print("%d us per bit" % pulseLength)
        pulse *= 1000
        pulse /= pulseLength
        self.pwm.setPWM(channel, 0, pulse)

    def tick(self):
        for i in range(12):
            val = self.readdata(i)
            if not (val is None):
                self.pwm.setPWM(i, 0, round(val * MAX_PULSE) + PULSE_CENTER)
