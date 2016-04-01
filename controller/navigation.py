import asyncio, atexit

from .position import *
from .drive import DriveMotors, TURN_TIME
from .room import RoomEntryDetection

from collections import defaultdict

L = "L"
R = "R"
S = "S"
X = "X"

DELAY_TIME = 1.7

class Navigator:
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.ir = IRPositioning()
        self.driver = DriveMotors()
        self.room = RoomEntryDetection()

        self.flameled = open("/var/run/led0","wb",0)
        self.videoled = open("/var/run/led1","wb",0)
        self.readyled = open("/var/run/led2","wb",0)
        self.roomled = open("/var/run/led3","wb",0)
        self.camcontrol = open("/var/run/camera0","wb",0)

        self.__turning = False
        self.__turn_handles = defaultdict(bool)
        
        self.__inroom = False
        self.__toggle_room(True)

        self.__steps = []
        self.__going_backwards = False
        self.__fourway = None
        self.__orientation = 0 # N, E, S, W
        
        for i in (L_OPENING_END, L_OPENING_START, R_OPENING_START,
                  R_OPENING_END, FRONT_WALL_DETECT, FOUR_WAY_DETECT):
            self.ir.register(i, self.perform_turn)
        self.ir.register(NOT_PARALLEL, self.parallel_correct)
        self.ir.register(OFF_CENTER, self.center_correct)
        self.room.register(self.toggle_room)

        atexit.register(self.driver.stop)
        self.loop.call_soon(self.driver.forward)
        self.readyled.write(b"1\n")

    def parallel_correct(self, name, state):
        return False
        if self.__turning:
            return False
        if not (self.ir.state[NOT_PARALLEL] or
                self.ir.state[OFF_CENTER]):
            self.driver.forward()
        elif state:
            direction = [0, 0] # left, right
            direction[int(self.ir.data[0] < self.ir.data[1])] += 1
            direction[int(self.ir.data[2] < self.ir.data[3])] += 1
            direction[int(self.ir.data[5] < self.ir.data[4])] += 1
            if direction[0] < direction[1]:
                #if not self.ir.state[L_OPENING_START]:
                self.driver.slightleft(False)
            else:
                #if not self.ir.state[R_OPENING_START]:
                self.driver.slightright(False)
            self.loop.call_later(1, self.parallel_correct, name, state)
        
    def center_correct(self, name, state):
        if self.__turning or self.__inroom:
            return False
        if not (self.ir.state[NOT_PARALLEL] or
                self.ir.state[OFF_CENTER]):
            self.driver.forward()
        elif state:
            if (self.ir.state[L_OPENING_START] or
                self.ir.state[R_OPENING_START]):
                if self.ir.data[1] > self.ir.data[2]:
                    self.driver.slightright(False)
                else:
                    self.driver.slightleft(False)
            else:
                if self.ir.data[0] > self.ir.data[3]:
                    self.driver.slightright(False)
                else:
                    self.driver.slightleft(False)
            #self.loop.call_later(1, self.center_correct, name, state)

    def end_turn(self):
        self.__turning = False
                        
    def perform_turn(self, name, state, GO=False):
        if not GO:
            if self.__turn_handles[name]:
                if not state:
                    print("CANCELLING TURN")
                    self.__turn_handles[name].cancel()
            else:
                self.__turn_handles[name] = self.loop.call_later(0.5, self.perform_turn, name, state, True)
            return False
        if (self.__turning and state) or self.__inroom:
            return False
        elif not state:
            if name == self.__turning:
                print("End TURN")
                self.loop.call_later(TURN_TIME + DELAY_TIME, self.end_turn)
            return False
        if self.ir.state[FOUR_WAY_DETECT]:
            print("4WAY")
            self.__turning = FOUR_WAY_DETECT
            """if self.__fourway:
                if self.__orientation % 2 == self.__fourway[1] % 2:
                    pass
                else:
                    d = L
            else:
                d = R"""
            d = L
            self.__fourway = (len(self.steps), self.__orientation)
        elif (self.ir.state[L_OPENING_START] and self.ir.state[L_OPENING_END]
              and self.steps[-1] != R):
            d = L
        elif (self.ir.state[R_OPENING_START] and self.ir.state[R_OPENING_END]
              and self.steps[-1] != L):
            d = R
        elif not self.ir.state[FRONT_WALL_DETECT]:
            d = S
        else:
            d = R if self.steps[-1] == L else L
        self.decision(d)
            
    def decision(self, d):
        if self.__going_backwards:
            if ((self.steps[-1] == R and d = L) or
                (self.steps[-1] == L and d = R)):
                self.steps.pop()
            else:
                self.__going_backwards = False
        if not self.__going_backwards:
            self.steps.append(d)
        if d == R:
            self.__orientation += 1
            self.driver.turnright()
        elif d == L:
            self.__orientation -= 1
            self.driver.turnleft()
        else:
            self.driver.forward()
        self.__orientation %= 4

    def __toggle_room(self, manual=False):
        self.__inroom = not self.__inroom
        self.ir.blocked = self.__inroom
        if self.__inroom and not manual:
            self.loop.call_later(0.5, self.turn_around)
        self.roomled.write("{}\n".format(int(self.__inroom)).encode())
            
    def toggle_room(self, state):
        if not state:
            self.camcontrol.write("{}\n".format(int(self.__inroom)).encode())
            self.loop.call_later(DELAY_TIME, self.__toggle_room)

    def turn_around(self):
        self.driver.turnright()
        self.loop.call_later(TURN_TIME, self.driver.turnright)
        self.__orientation += 2
        self.__orientation %= 4
        self.__going_backwards = True
