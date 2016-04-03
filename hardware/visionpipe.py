try:
    from .vision import *
except SystemError as err:
    from vision import *

try:
    from .component import *
except SystemError as err:
    from component import *

_ticking = False
    
class VisionController(LoopedComponent, Component):
    _mswait = 50
    _FN = "visioncontrol"

    def tick(self):
        global _ticking
        val = self.readdata()
        if not (val is None):
            if int(val) == 0:
                _ticking = False
            elif int(val) == 1:
                _ticking = True
    
class Vision(LoopedComponent, Component):
    _mswait = 10
    _FN = 'vision'

    def init(self):
        super().init()
        self._tester = Tester()
        self._tester.init()
        self._set_init()

    def cleanup(self):
        self._tester.close()
        super().cleanup()

    def __detect(self):
        result = self._tester.test_candle(quantity=1)
        self._tester.clear_pics()
        return result

    def tick(self):
        if _ticking:
            self.writedata(self.__detect())
