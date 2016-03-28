from adafruit import PWM

try:
    from .component import *
except SystemError:
    from component import *

class MotorDriver(I2CComponent):
    def init(self):
        super().init()
        self.pwm = PWM(self._address) # 0x40
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
        pwm.setPWM(channel, 0, pulse)

