
import atexit, time, sys, os

BASE_PATH = "data/irdata/"

files1 = ("1-s.avg.csv","2-s.avg.csv","3-s.avg.csv","4-s.avg.csv")
files2 = ("5-s.avg.csv","6-s.avg.csv","1-m.avg.csv","2-m.avg.csv")

COMPONENTS = (
    ColorSensor(),
    Melexis(),
    InterpolatedDistance.from_files(0x48, *files1, base_path=BASE_PATH),
    InterpolatedDistance.from_files(0x49, *files2, base_path=BASE_PATH),
    LEDController(),
    Melexis(),
    MotorDriver(),
    SoundDetect()
)

for i in COMPONENTS:
    i.init()

@atexit.register
def cleaner():
    for i in COMPONENTS:
        i.cleanup()

for i in COMPONENTS:
    i.start()

while True:
    time.sleep(1)
