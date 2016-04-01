import asyncio

from .position import *
from .drive import DriveMotors
from .room import RoomEntryDetection

class Navigator:
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.ir = IRPositioning()
        self.driver = DriveMotors()
        self.room = RoomEntryDetection()

        self.__steps = []
        self.__turning = False
        self.__inroom = True
        self.__fourway_right = False
        
        for i in (NOT_PARALLEL, OFF_CENTER):
            self.ir.register(i, self.course_correct)
        for i in (L_OPENING_END, R_OPENING_END, FRONT_WALL_DETECT):
            self.ir.register(i, self.perform_turn)
        self.ir.register(FOUR_WAY_DETECT, self.four_way)
        self.room.register(self.toggle_room)

        self.driver.forward()

    def course_correct(self, name, state):
        if self.__turning or self.__inroom:
            return False
        if not (self.ir.state[NOT_PARALLEL] or
                self.ir.state[OFF_CENTER]):
            self.driver.forward()
        elif state:
            if name == NOT_PARALLEL:
                direction = [0, 0] # left, right
                direction[int(self.ir.data[0] < self.ir.data[1])] += 1
                direction[int(self.ir.data[2] < self.ir.data[3])] += 1
                direction[int(self.ir.data[5] < self.ir.data[4])] += 1
                if direction[0] > direction[1]:
                    self.driver.slightleft(False)
                else:
                    self.driver.slightright(False)
            else:
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

    def perform_turn(self, name, state):
        self.__turning = True
        self.driver.stop()

    def four_way(self, name, state):
        self.__turning = True
        self.driver.stop()

    def toggle_room(self, state):
        self.__inroom = not self.__inroom
