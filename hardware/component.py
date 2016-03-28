#
# Base classes for GPIO hardware
#

import RPi.GPIO as gpio
import time

from collections import defaultdict
from threading import Thread

from traceback import print_exc, format_exc

def delay(microseconds):
    time.sleep(microseconds/1000000)

def waitms(milliseconds):
    time.sleep(milliseconds/1000)

class Component:
    def __init__(self):
        super().__init__()
        self.__initialized = False

    def _checkInit(self,quiet=False):
        if quiet:
            return self.__initialized
        if not self.__initialized:
            raise RuntimeError("This {} has not been initialized yet!".format(
                    self.__class__.__name__))

    def _set_init(self):
        self.__initialized = True

    def init(self):
        pass

    def cleanup(self):
        self.__initialized = False

    def __enter__(self):
        self.init()
        return self

    def __exit__(self, type, value, tb):
        self.cleanup()

class GPIOComponent(Component):
    def __init__(self,outpins=(),inpins=()):
        super().__init__()
        self.__out_pins = outpins
        self.__in_pins = inpins

    def init(self):
        super().init()
        if self._checkInit(True):
            try:
                self.cleanup()
            finally:
                pass
            
        gpio.setmode(gpio.BOARD)

        for ch in self.__out_pins:
            gpio.setup(ch, gpio.OUT, initial=gpio.LOW)
        for ch in self.__in_pins:
            gpio.setup(ch, gpio.IN, initial=gpio.LOW)

        self._set_init()

    def cleanup(self):
        if not self._checkInit(True):
            return False
        super().cleanup()
        for ch in self.__out_pins + self.__in_pins:
            gpio.cleanup(ch)
        return True

class I2CComponent(Component):
    def __init__(self,addr):
        self._address = addr
        super().__init__()

class EventedInput:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__next_id = -1
        self.__handlers = defaultdict(dict)

    def _get_handlers(self,pin=None,generic=False):
        if (pin is None) and (not generic):
            raise TypeError("Must supply pin for non generic handler!")
        return self.__handlers["generic"] if generic else self.__handlers[pin]

    def add_handler(self,callback,pin=None,generic=False):
        self.__next_id += 1
        self._get_handlers(pin,generic)[self.__next_id] = callback
        return self.__next_id

    def remove_handler(self,hid,pin=None,generic=False):
        del self._get_handlers(pin,generic)[hid]

    def _handle_pin(self,pin):
        for i in (list(self._get_handlers(generic=True).values())
                  + list(self._get_handlers(pin).values())):
            try:
                i(pin)
            except Exception as e:
                print_exc()

class LoopedInput:
    def __init__(self, *args, **kwargs):        
        super().__init__(*args, **kwargs)
        self.thread = Thread(target=self.runloop)
        self.thread.daemon = True
        self.__started = False
        self.thread.start()

    def init(self, autostart=False):
        super().init()
        self._set_init()
        if autostart:
            self.start()
        
    def cleanup(self):
        if self.__started:
            self.stop()
        super().cleanup()

    def start(self):
        self._checkInit()
        self.__started = True

    def stop(self):
        self.__started = False

    def runloop(self):
        while True:
            if self.__started:
                self.tick()
            waitms(self._mswait)
