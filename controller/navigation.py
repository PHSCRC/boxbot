import asyncio, atexit

from .position import *
from .drive import DriveMotors, TURN_TIME
from .room import RoomEntryDetection
from .status import LED
from .firefighting import *

from collections import defaultdict

L = "L"
R = "R"
S = "S"
X = "X"

DELAY_TIME = 1.2

VISION_NOTHING = 1
VISION_POSSIBLE = 3
VISION_LIKELY = 4

class Navigator:
    def __init__(self, start_in_room=True):
        self.loop = asyncio.get_event_loop()
        self.ir = IRPositioning()
        self.driver = DriveMotors()
        self.room = RoomEntryDetection()
        self.flamedetect = FlameDetect()
        self.flamedetect.on = True
        self.extinguisher = Extinguisher()
        
        self.flameled = LED(0)
        self.videoled = LED(1)
        self.readyled = LED(2)
        self.roomled = LED(3)
        self.flameled.on = 0

        self.__turning = False
        self.__turn_handles = defaultdict(bool)
        
        self.__inroom = not start_in_room
        self.__initial_room = start_in_room
        self.__toggle_room(True)
        self.__turning = None # "INITIAL_ORIENT"

        self.__steps = [X]
        self.__going_backwards = False
        self.__fourway = None
        self.__orientation = 0 # N, E, S, W
        self.__initial_orient = 0
        
        for i in (L_OPENING, R_OPENING, FRONT_WALL_DETECT, FOUR_WAY_DETECT):
            self.ir.register(i, self.perform_turn)
        self.ir.register(NOT_PARALLEL, self.parallel_correct)
        self.ir.register(OFF_CENTER, self.center_correct)
        self.flamedetect.register(self.vision)
        self.room.register(self.toggle_room)

        atexit.register(self.driver.stop)
        self.loop.call_soon(self.driver.forward) #self.driver.turnleft(None)
        #self.loop.call_later(0.1, self.initial_orient)

    def initial_orient(self):
        print(abs(self.ir.data[5] - self.ir.data[4]))
        turn_time = TURN_TIME / 5
        if abs(self.ir.data[5] - self.ir.data[4]) < 6 and self.ir.data[5]:
            self.__initial_orient += 1
            turn_time = 0.5
            self.driver.stop()
            print("STOPPED")
        else:
            self.__initial_orient = 0
            self.driver.turnleft(None)
            print("TURNING")
        if self.__initial_orient < 4:
            self.loop.call_later(turn_time, self.initial_orient)
        else:
            print("DONE ORIENTING")
            self.driver.cancel()
            self.loop.call_soon(self.driver.forward)
            self.loop.call_later(0.1, self.end_turn)
            print(self.driver.left, self.driver.right)

    def scan_room(self):
        self.__scan_start = self.loop.time()
        self.__giving_up = self.loop.call_later(TURN_TIME * 15, self.give_up)
        self.driver.right = 0.04
        self.driver.left = 0.04

    def give_up(self):
        print("GIVING UP")
        self.driver.forward()
        
    def vision(self, state, deg):
        print(repr(state), VISION_LIKELY, deg)
        if state == VISION_LIKELY:
            if deg < 0:
                self.driver.right = -0.03
                self.driver.left = -0.03
            elif deg > 0:
                self.driver.right = 0.03
                self.driver.left = 0.03
            if abs(deg) < 15:
                self.flameled.on = True
                self.driver.stop()
                self.__back_time = self.loop.time()
                self.extinguisher.go()
                self.__giving_up.cancel()
                self.loop.call_soon(self.approach)
                self.loop.call_later(1, self.extinguish)
                #self.loop.call_later(1, self.go_home)

    def approach(self):
        print((self.ir.data[4] + self.ir.data[5]) / 2)
        if (self.ir.data[4] + self.ir.data[5]) / 2 > 25:
            self.driver.forward()
            self.loop.call_later(0.1, self.approach)
        else:
            self.driver.stop()
            
    def extinguish(self):
        if self.flamedetect.laststate != 1:
            self.extinguisher.go()
            self.loop.call_later(1, self.extinguish)
        else:
            exit()
            
    def parallel_correct(self, name, state):
        self.readyled.on = state
        if self.__turning:
            return False
        if not (self.ir.state[NOT_PARALLEL] or
                self.ir.state[OFF_CENTER]):
            if not self.__inroom:
                self.driver.forward()
        elif state:
            direction = [0, 0] # left, right
            print(self.ir.data)
            if self.ir.data[0] < 30 and self.ir.data[1] < 30:
                direction[int(self.ir.data[0] < self.ir.data[1])] += 1
            if self.ir.data[2] < 30 and self.ir.data[3] < 30:
                direction[int(self.ir.data[2] < self.ir.data[3])] += 1
            if self.ir.data[5] < 30 and self.ir.data[4] < 30:
                direction[int(self.ir.data[5] < self.ir.data[4])] += 1
            print(direction, abs(self.ir.data[0] - self.ir.data[1]),
                  abs(self.ir.data[2] - self.ir.data[3]),
                  abs(self.ir.data[5] - self.ir.data[4]))
            if sum(direction) > 0 and sum(direction) != 2:
                if direction[0] < direction[1]:
                    if self.__initial_room or not self.__inroom:
                        self.driver.slightleft(False)
                else:
                    if self.__initial_room or not self.__inroom:
                        self.driver.slightright(False)
            #self.loop.call_later(1, self.parallel_correct, name, state)
        
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
        if not GO and name == FRONT_WALL_DETECT:
            self.videoled.on = state
        elif not GO:
            if self.__turn_handles[name]:
                if not state:
                    pass
                    #print("CANCELLING TURN")
                    #self.__turn_handles[name].cancel()
            self.__turn_handles[name] = self.loop.call_later(
                0.3, self.perform_turn, name, state, True)
            return False
        #else:
        #   print("Executing", name, state)
        if self.__initial_room and name == FRONT_WALL_DETECT and not self.__turning:
            print("LEFT TURN")
            self.__turning = "LEFT"
            self.driver.turnleft()
            self.loop.call_later(TURN_TIME, self.end_turn)
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
            self.__fourway = (len(self.__steps), self.__orientation)
        elif (self.ir.state[L_OPENING] and not (self.__going_backwards and
                                                self.__steps[-1] == R)):
            self.__turning = name
            d = L
        elif (self.ir.state[R_OPENING] and not (self.__going_backwards and
                                                self.__steps[-1] == L)):
            self.__turning = name
            d = R
        elif not self.ir.state[FRONT_WALL_DETECT]:
            self.__turning = name
            print(self.ir.state)
            d = S
        else:
            if self.__going_backwards:
                self.__turning = name
                d = R if self.__steps[-1] == L else L
            else:
                print("TURNING AROUND")
                self.__turning = "AROUND"
                self.turn_around()
                self.loop.call_later(TURN_TIME * 2, self.end_turn)
        self.decision(d)
            
    def decision(self, d):
        print(d)
        if self.__going_backwards:
            if ((self.__steps[-1] == R and d == L) or
                (self.__steps[-1] == L and d == R)):
                self.__steps.pop()
            else:
                self.__going_backwards = False
        if not self.__going_backwards:
            self.__steps.append(d)
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
        self.flamedetect.on = self.__inroom and not self.__initial_room
        print(self.flamedetect.on)
        if self.__inroom and not manual:
            self.driver.turnleft(False)
            self.loop.call_later(TURN_TIME * 1.25, self.scan_room)
        self.roomled.on = self.__inroom
            
    def toggle_room(self, state):
        self.__initial_room = False
        if state:
            self.loop.call_later(DELAY_TIME, self.__toggle_room)

    def turn_around(self):
        self.driver.turnright()
        self.loop.call_later(TURN_TIME, self.driver.turnright)
        self.__orientation += 2
        self.__orientation %= 4
        self.__going_backwards = True
