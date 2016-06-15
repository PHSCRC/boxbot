from controller.drive import DriveMotors
from Adafruit_BNO055.BNO055 import BNO055
import curses
import threading
import time


W = ord('w')
A = ord('a')
S = ord('s')
D = ord('d')
Q = ord('q')
E = ord('e')
imu_cont_lock = threading.Lock()
imu_cont = True


def continue_imu_data():
    imu_cont_lock.acquire()
    status = imu_cont
    imu_cont_lock.release()
    return status


def set_imu_cont(val):
    global imu_cont
    imu_cont_lock.acquire()
    imu_cont = val
    imu_cont_lock.release()


def display_iterable(scr, iterable, start, x=10, name=None):
    sy, sx = curses.getsyx()
    if name:
        curses.setsyx(start, x)
        scr.clrtoeol()
        scr.addstr(start, x, name)
        start += 1
    for i in iterable:
        curses.setsyx(start, x)
        scr.clrtoeol()
        scr.addstr(start, x, str(i))
        start += 1
    curses.setsyx(sy, sx)
    scr.refresh()

    
def display_imu_data(scr, bno, startline=4):
    while continue_imu_data():
        start = startline
        for i in (('Euler', bno.read_euler()),
                  ('Gyroscope', bno.read_gyroscope()),
                  ('Accelerometer', bno.read_accelerometer())):
            display_iterable(scr, i[1], start, name=i[0])
            start += len(i[1]) + 2
        time.sleep(0.25)
            

def main():
    scr = curses.initscr()
    curses.cbreak()
    curses.setsyx(-1, -1)
    # scr.keypad(1)
    dm = DriveMotors()    
    bno = BNO055()
    bno.begin()

    scr.addstr(0, 10, 'debug_control.py: the ultimate boxbot controller')
    scr.addstr(2, 10, 'Press Q to exit.')
    scr.refresh()

    tdisp = threading.Thread(target=display_imu_data, args=(scr, bno))
    tdisp.start()
    
    while True:
        key = scr.getch()

        if key == Q:
            break
        
        {
            W: dm.forward,
            S: dm.backward,
            A: dm.turnleft,
            D: dm.turnright,
            E: dm.stop,
        }.get(key, dm.stop)()

    set_imu_cont(False)
    tdisp.join()
    curses.endwin()


if __name__ == '__main__':
    main()
