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
        self.__given_up = False

        self.__steps = [X, X]
        self.__going_backwards = False
        self.__fourway = None
        self.__orientation = 0 # N, E, S, W
        self.__initial_orient = 0
        
        for i in (L_OPENING, R_OPENING, FRONT_WALL_DETECT, FOUR_WAY_DETECT):
            self.ir.register(i, self.perform_turn)
        self.ir.register(FRONT_STUCK, self.front_stuck)
        self.ir.register(NOT_PARALLEL, self.parallel_correct)
        self.ir.register(OFF_CENTER, self.center_correct)
        self.flamedetect.register(self.vision)
        self.room.register(self.toggle_room)

        atexit.register(self.driver.stop)
        self.loop.call_soon(self.initial_movement) #self.driver.turnleft(None)
        #self.loop.call_later(0.1, self.initial_orient)

    def front_stuck(self, name, state):
        if not self.__inroom:
            if state:
                self.ir.blocked = True
                self.driver.left = -0.09
                self.driver.right = 1
                self.loop.call_later(0.7, self.unstuck)
            else:
                self.driver.forward()

    def unstuck(self):
        self.ir.blocked = False
        
    def initial_movement(self):
        self.driver.left = 0.099
        self.driver.right = -1
        
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
        self.__given_up = False
        self.__giving_up = self.loop.call_later(TURN_TIME * 18.5, self.give_up)
        self.driver.right = 0.03
        self.driver.left = 0.03

    def give_up(self):
        print("GIVING UP")
        self.__given_up = True
        self.__orientation += 2
        self.__orientation %= 4
        self.__going_backwards = True
        self.driver.turnright()
        self.loop.call_later(TURN_TIME, self.driver.forward)
        
    def vision(self, state, deg):
        print(state, deg)
        if state == VISION_LIKELY:
            if deg < 0:
                self.driver.right = 0.03
                self.driver.left = 0.03
            elif deg > 0:
                self.driver.right = -0.03
                self.driver.left = -0.03
            if abs(deg) < 10:
                self.flameled.on = True
                self.driver.stop()
                self.__back_time = self.loop.time()
                self.extinguisher.go()
                self.__giving_up.cancel()
                self.loop.call_soon(self.approach, deg < 0)
                self.loop.call_later(1, self.extinguish)
                #self.loop.call_later(1, self.go_home)
        elif state < 3 or state == 5:
            if not self.__given_up:
                self.driver.right = 0.03
                self.driver.left = 0.03

    def approach(self, left=False):
        #print((self.ir.data[4] + self.ir.data[5]) / 2)
        if (self.ir.data[4] + self.ir.data[5]) / 2 > 25:
            if left:
                self.driver.right = 0.06
                self.driver.left = -0.055
            else:
                self.driver.right = -0.055
                self.driver.left = 0.06
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
            MAX_DISTANCE_P = 36
            if self.ir.data[0] and self.ir.data[1] and self.ir.data[0] < MAX_DISTANCE_P and self.ir.data[1] < MAX_DISTANCE_P:
                direction[int(self.ir.data[0] < self.ir.data[1])] += 1
            if self.ir.data[2] and self.ir.data[3] and self.ir.data[2] < MAX_DISTANCE_P and self.ir.data[3] < MAX_DISTANCE_P:
                direction[int(self.ir.data[2] < self.ir.data[3])] += 1
            if self.ir.data[5] and self.ir.data[4] and self.ir.data[5] < MAX_DISTANCE_P and self.ir.data[4] < MAX_DISTANCE_P:
                direction[int(self.ir.data[5] < self.ir.data[4])] += 1
            print(direction, abs(self.ir.data[0] - self.ir.data[1]),
                  abs(self.ir.data[2] - self.ir.data[3]),
                  abs(self.ir.data[5] - self.ir.data[4]))
            if sum(direction) > 0 and sum(direction) != 2:
                if direction[0] < direction[1]:
                    if self.__initial_room: # or not self.__inroom:
                        self.driver.slightleft(False)
                else:
                    if self.__initial_room: # or not self.__inroom:
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
        print("ENDING_TURN")
        self.__turning = False
        self.ir.blocked = False
        if self.__initial_room:
            self.loop.call_soon(self.check_turn)

    def check_turn(self):
        print(self.ir.state[FRONT_WALL_DETECT])
        if self.ir.state[FRONT_WALL_DETECT]:
            self.loop.call_soon(self.perform_turn, FRONT_WALL_DETECT, True, True)
                        
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
                1, self.perform_turn, name, state, True)
            return False
        #else:
        #   print("Executing", name, state)
        if self.__initial_room and name == FRONT_WALL_DETECT and not self.__turning:
            if self.ir.data[0] > self.ir.data[3] or self.ir.data[1] > self.ir.data[2]:
                print("RIGHT TURN")
                self.__turning = "RIGHT"
                self.driver.turnright()
            else:
                print("LEFT TURN")
                self.__turning = "LEFT"
                self.driver.turnleft()
            #self.ir.blocked = True
            self.__initial_turn_handle = self.loop.call_later(TURN_TIME, self.end_turn)
            return False
        if (self.__turning and state) or self.__inroom:
            return False
        elif not state:
            if name == self.__turning:
                print("End TURN")
                self.loop.call_later(TURN_TIME + DELAY_TIME, self.end_turn)
            return False
        fourway = False
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
            if self.__fourway and (
                    (self.orientation + 1) % 4 == self.__fourway[1]):
                while len(self.__steps) > self.__fourway[0]:
                    self.__steps.pop()
                self.__going_backwards = True
                fourway = True
            if not self.__fourway:
                self.__fourway = (len(self.__steps), self.__orientation)
        elif (self.ir.state[L_OPENING]
              and not ((self.__going_backwards and self.__steps[-1] == R)
                       or (self.__steps[-1] == self.__steps[-2] == L))):
            self.__turning = name
            self.parallelize(L)
            return
        elif (self.ir.state[R_OPENING]
              and not ((self.__going_backwards and self.__steps[-1] == L)
                       or (self.__steps[-1] == self.__steps[-2] == R))):
            self.__turning = name
            self.parallelize(R)
            return
        elif not self.ir.state[FRONT_WALL_DETECT]:
            self.__turning = name
            print(self.ir.state)
            d = S
        else:
            if self.__going_backwards:
                self.__turning = name
                d = R if self.__steps[-1] == L else L
            else:
                print(self.__steps, self.__going_backwards, self.ir.state, self.ir.data)
                print("TURNING AROUND")
                self.__turning = "AROUND"
                self.turn_around()
                self.loop.call_later(TURN_TIME * 2, self.end_turn)
                return
        self.decision(d, fourway)

    def parallelize(self, d):
        if self.ir.state[NOT_PARALLEL] and False:
            print("PARALLELIZING")
            closest = sorted(enumerate(self.ir.data), key=lambda x: x[1])[0][0]
            if closest in (0, 1):
                direction = self.ir.data[0] < self.ir.data[1]
            if closest in (2, 3):
                direction = self.ir.data[2] < self.ir.data[3]
            if closest in (4, 5):
                direction = self.ir.data[5] < self.ir.data[4]
            self.driver.stop()
            if direction:
                self.loop.call_later(1, self.driver.slightright)
            else:
                self.loop.call_later(1, self.driver.slightleft)
            self.loop.call_later(0.05, self.parallelize, d)
        else:
            self.decision(d)
        
    def decision(self, d, fourway=False):
        print("Decision:", d)
        if self.__going_backwards:
            if ((self.__steps[-1] == R and d == L) or
                (self.__steps[-1] == L and d == R)):
                self.__steps.pop()
            elif fourway:
                pass
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
        if self.__inroom:
            if not manual:
                self.driver.turnleft(False)
                self.loop.call_later(TURN_TIME * 1.25, self.scan_room)
        else:
            self.driver.forward()
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
