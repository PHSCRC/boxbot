import math
import pickle

import cv2
import numpy as np

RUNNING_ON_MAC = __name__ == '__main__'
if RUNNING_ON_MAC:
    pass
else:
    import picamera.array  # order of these imports is important, no idea why
    import picamera

_CANDLE_FLAME_SHAPE = pickle.loads(b'\x80\x03]q\x00cnumpy.core.multiarray\n'
                                   b'_reconstruct\nq\x01cnumpy\nndarra'
                                   b'y\nq\x02K\x00\x85q\x03C\x01bq\x04\x87q'
                                   b'\x05Rq\x06(K\x01K\x9cK\x01K'
                                   b'\x02\x87q\x07cnumpy\ndtype\nq\x08X'
                                   b'\x02\x00\x00\x00i4q\tK\x00K\x01\x87q\nR'
                                   b'q\x0b(K\x03X\x01\x00\x00\x00<q\x0cNNN'
                                   b'J\xff\xff\xff\xffJ\xff\xff\xff\xffK\x00'
                                   b'tq\rb\x89B\xe0\x04\x00\x00G\x02'
                                   b'\x00\x00\xe2\x02\x00\x00C\x02'
                                   b'\x00\x00\xe6\x02\x00\x00C\x02'
                                   b'\x00\x00\xe7\x02\x00\x00B\x02'
                                   b'\x00\x00\xe8\x02\x00\x00B\x02'
                                   b'\x00\x00\xe9\x02\x00\x00A\x02'
                                   b'\x00\x00\xea\x02\x00\x00A\x02'
                                   b'\x00\x00\xeb\x02\x00\x00@\x02'
                                   b'\x00\x00\xec\x02\x00\x00@\x02'
                                   b'\x00\x00\xed\x02\x00\x00?\x02'
                                   b'\x00\x00\xee\x02\x00\x00?\x02'
                                   b'\x00\x00\xf0\x02\x00\x00>\x02'
                                   b'\x00\x00\xf1\x02\x00\x00>\x02'
                                   b'\x00\x00\xf2\x02\x00\x00=\x02'
                                   b'\x00\x00\xf3\x02\x00\x00=\x02'
                                   b'\x00\x00\xf5\x02\x00\x00<\x02'
                                   b'\x00\x00\xf6\x02\x00\x00<\x02'
                                   b'\x00\x00\xf7\x02\x00\x00;\x02'
                                   b'\x00\x00\xf8\x02\x00\x00;\x02'
                                   b'\x00\x00\xfa\x02\x00\x00:\x02'
                                   b'\x00\x00\xfb\x02\x00\x00:\x02'
                                   b'\x00\x00\xfd\x02\x00\x009\x02'
                                   b'\x00\x00\xfe\x02\x00\x009\x02'
                                   b'\x00\x00\x01\x03\x00\x008\x02'
                                   b'\x00\x00\x02\x03\x00\x008\x02'
                                   b'\x00\x00\x04\x03\x00\x007\x02'
                                   b'\x00\x00\x05\x03\x00\x007\x02'
                                   b'\x00\x00\x07\x03\x00\x006\x02'
                                   b'\x00\x00\x08\x03\x00\x006\x02'
                                   b'\x00\x00\n\x03\x00\x005\x02'
                                   b'\x00\x00\x0b\x03\x00\x005\x02'
                                   b'\x00\x00\x0f\x03\x00\x004\x02'
                                   b'\x00\x00\x10\x03\x00\x004\x02'
                                   b'\x00\x00\x12\x03\x00\x003\x02'
                                   b'\x00\x00\x13\x03\x00\x003\x02'
                                   b'\x00\x00\x16\x03\x00\x002\x02'
                                   b'\x00\x00\x17\x03\x00\x002\x02'
                                   b'\x00\x00\x1a\x03\x00\x001\x02'
                                   b'\x00\x00\x1b\x03\x00\x001\x02'
                                   b'\x00\x00!\x03\x00\x000\x02\x00\x00"\x03'
                                   b'\x00\x000\x02\x00\x00(\x03\x00\x00/\x02'
                                   b'\x00\x00)\x03\x00\x00/\x02\x00\x00N\x03'
                                   b'\x00\x000\x02\x00\x00O\x03\x00\x000\x02'
                                   b'\x00\x00W\x03\x00\x001\x02\x00\x00X\x03'
                                   b'\x00\x001\x02\x00\x00b\x03\x00\x002\x02'
                                   b'\x00\x00c\x03\x00\x002\x02\x00\x00g\x03'
                                   b'\x00\x003\x02\x00\x00h\x03\x00\x003\x02'
                                   b'\x00\x00o\x03\x00\x004\x02\x00\x00p\x03'
                                   b'\x00\x004\x02\x00\x00s\x03\x00\x005\x02'
                                   b'\x00\x00t\x03\x00\x005\x02\x00\x00w\x03'
                                   b'\x00\x006\x02\x00\x00x\x03\x00\x006\x02'
                                   b'\x00\x00{\x03\x00\x007\x02\x00\x00|\x03'
                                   b'\x00\x007\x02\x00\x00~\x03\x00\x008\x02'
                                   b'\x00\x00\x7f\x03\x00\x008\x02'
                                   b'\x00\x00\x80\x03\x00\x009\x02'
                                   b'\x00\x00\x81\x03\x00\x009\x02'
                                   b'\x00\x00\x82\x03\x00\x00;\x02'
                                   b'\x00\x00\x82\x03\x00\x00;\x02'
                                   b'\x00\x00\x80\x03\x00\x00<\x02'
                                   b'\x00\x00\x7f\x03\x00\x00<\x02'
                                   b'\x00\x00|\x03\x00\x00=\x02\x00\x00{\x03'
                                   b'\x00\x00=\x02\x00\x00w\x03\x00\x00>\x02'
                                   b'\x00\x00v\x03\x00\x00>\x02\x00\x00s\x03'
                                   b'\x00\x00?\x02\x00\x00r\x03\x00\x00?\x02'
                                   b'\x00\x00q\x03\x00\x00@\x02\x00\x00p\x03'
                                   b'\x00\x00@\x02\x00\x00o\x03\x00\x00A\x02'
                                   b'\x00\x00n\x03\x00\x00A\x02\x00\x00m\x03'
                                   b'\x00\x00B\x02\x00\x00l\x03\x00\x00B\x02'
                                   b'\x00\x00k\x03\x00\x00G\x02\x00\x00f\x03'
                                   b'\x00\x00H\x02\x00\x00f\x03\x00\x00I\x02'
                                   b'\x00\x00e\x03\x00\x00N\x02\x00\x00e\x03'
                                   b'\x00\x00O\x02\x00\x00f\x03\x00\x00Q\x02'
                                   b'\x00\x00f\x03\x00\x00X\x02\x00\x00m\x03'
                                   b'\x00\x00X\x02\x00\x00o\x03\x00\x00Y\x02'
                                   b'\x00\x00p\x03\x00\x00Y\x02\x00\x00q\x03'
                                   b'\x00\x00Z\x02\x00\x00r\x03\x00\x00Z\x02'
                                   b'\x00\x00s\x03\x00\x00[\x02\x00\x00t\x03'
                                   b'\x00\x00[\x02\x00\x00v\x03'
                                   b'\x00\x00\\\x02\x00\x00w\x03'
                                   b'\x00\x00\\\x02\x00\x00y\x03'
                                   b'\x00\x00]\x02\x00\x00z\x03\x00\x00]\x02'
                                   b'\x00\x00}\x03\x00\x00^\x02\x00\x00~\x03'
                                   b'\x00\x00^\x02\x00\x00\x80\x03'
                                   b'\x00\x00_\x02\x00\x00\x81\x03'
                                   b'\x00\x00_\x02\x00\x00\x82\x03'
                                   b'\x00\x00a\x02\x00\x00\x82\x03'
                                   b'\x00\x00a\x02\x00\x00\x81\x03'
                                   b'\x00\x00b\x02\x00\x00\x80\x03'
                                   b'\x00\x00b\x02\x00\x00~\x03\x00\x00c\x02'
                                   b'\x00\x00}\x03\x00\x00c\x02\x00\x00y\x03'
                                   b'\x00\x00d\x02\x00\x00x\x03\x00\x00d\x02'
                                   b'\x00\x00s\x03\x00\x00e\x02\x00\x00r\x03'
                                   b'\x00\x00e\x02\x00\x00g\x03\x00\x00f\x02'
                                   b'\x00\x00f\x03\x00\x00f\x02\x00\x00]\x03'
                                   b'\x00\x00g\x02\x00\x00\\\x03'
                                   b'\x00\x00g\x02\x00\x00/\x03\x00\x00f\x02'
                                   b'\x00\x00.\x03\x00\x00f\x02\x00\x00*\x03'
                                   b'\x00\x00e\x02\x00\x00)\x03\x00\x00e\x02'
                                   b'\x00\x00 \x03\x00\x00d\x02'
                                   b'\x00\x00\x1f\x03\x00\x00d\x02'
                                   b'\x00\x00\x1b\x03\x00\x00c\x02'
                                   b'\x00\x00\x1a\x03\x00\x00c\x02'
                                   b'\x00\x00\x15\x03\x00\x00b\x02'
                                   b'\x00\x00\x14\x03\x00\x00b\x02'
                                   b'\x00\x00\x12\x03\x00\x00a\x02'
                                   b'\x00\x00\x11\x03\x00\x00a\x02'
                                   b'\x00\x00\x0e\x03\x00\x00`\x02'
                                   b'\x00\x00\r\x03\x00\x00`\x02'
                                   b'\x00\x00\x0b\x03\x00\x00_\x02'
                                   b'\x00\x00\n\x03\x00\x00_\x02'
                                   b'\x00\x00\x06\x03\x00\x00^\x02'
                                   b'\x00\x00\x05\x03\x00\x00^\x02'
                                   b'\x00\x00\x04\x03\x00\x00]\x02'
                                   b'\x00\x00\x03\x03\x00\x00]\x02'
                                   b'\x00\x00\x00\x03\x00\x00\\\x02'
                                   b'\x00\x00\xff\x02\x00\x00\\\x02'
                                   b'\x00\x00\xfe\x02\x00\x00[\x02'
                                   b'\x00\x00\xfd\x02\x00\x00[\x02'
                                   b'\x00\x00\xfa\x02\x00\x00Z\x02'
                                   b'\x00\x00\xf9\x02\x00\x00Z\x02'
                                   b'\x00\x00\xf7\x02\x00\x00Y\x02'
                                   b'\x00\x00\xf6\x02\x00\x00Y\x02'
                                   b'\x00\x00\xf4\x02\x00\x00X\x02'
                                   b'\x00\x00\xf3\x02\x00\x00X\x02'
                                   b'\x00\x00\xf2\x02\x00\x00W\x02'
                                   b'\x00\x00\xf1\x02\x00\x00W\x02'
                                   b'\x00\x00\xf0\x02\x00\x00V\x02'
                                   b'\x00\x00\xef\x02\x00\x00V\x02'
                                   b'\x00\x00\xee\x02\x00\x00U\x02'
                                   b'\x00\x00\xed\x02\x00\x00U\x02'
                                   b'\x00\x00\xec\x02\x00\x00T\x02'
                                   b'\x00\x00\xeb\x02\x00\x00T\x02'
                                   b'\x00\x00\xea\x02\x00\x00S\x02'
                                   b'\x00\x00\xe9\x02\x00\x00S\x02'
                                   b'\x00\x00\xe8\x02\x00\x00M\x02'
                                   b'\x00\x00\xe2\x02\x00\x00q\x0etq'
                                   b'\x0fba.')[0]


class Camera(object):
    def __init__(self):
        self.__initialized = False

    def _is_init(self, raise_error=True):
        if raise_error and not self.__initialized:
            raise RuntimeError(
                "This {} object has not been initialized.".format(
                    self.__class__.__name__))
        return self.__initialized

    def init(self):
        if not RUNNING_ON_MAC:
            self.cam = picamera.PiCamera()
            self.cam.vflip = True
            self.cam.hflip = True
            self.array = picamera.array.PiRGBArray(self.cam)
        self.__initialized = True

    def close(self):
        if not RUNNING_ON_MAC:
            self.array.close()
            self.cam.close()
        self.__initialized = False

    def take_picture(self):
        self._is_init()
        if RUNNING_ON_MAC:
            return Picture(cv2.imread(input('Image file: ')))
        self.cam.capture(self.array, format='bgr')
        img = Picture(self.array.array)
        self.array.truncate(0)
        return img

    def __enter__(self):
        self.init()
        return self

    def __exit__(self, type, value, traceback):
        self.close()


class Picture(object):
    def __init__(self, img):
        self.__img = img
        self.width, self.height = tuple(img.shape[1::-1])

    @property
    def img(self):
        return self.__img.copy()


class Tester(object):
    NOTHING_DETECTED = 1
    TEST_AGAIN = 2
    POSSIBLY = 3
    HIGHLY_LIKELY = 4
    TOO_MUCH_DEVIATION = 5
    SAFETY_ZONE_DETECTED = 6

    __LOWER_BLUE = np.array([110, 50, 50])
    __UPPER_BLUE = np.array([130, 255, 255])

    __LOWER = (90, 90, 0)  # lower = (90, 50, 50)  #(,90,0)
    __UPPER = (135, 255, 255)
    __LOWER1 = (0, 50, 50)
    __UPPER1 = (8, 255, 255)
    __LOWER2 = (165, 50, 50)
    __UPPER2 = (179, 255, 255)

    def __init__(self):
        self.__initialized = False
        self.cam = Camera()
        self.pics = []

    def _is_init(self, raise_error=True):
        if raise_error and not self.__initialized:
            raise RuntimeError(
                "This {} object has not been initialized.".format(
                    self.__class__.__name__))
        return self.__initialized

    def init(self):
        self.cam.init()
        self.__initialized = True

    def close(self):
        self.cam.close()
        self.__initialized = False

    def take_pics(self, n=3):
        self._is_init()
        for i in range(0, n):
            self.pics.append(self.cam.take_picture())

    def clear_pics(self):
        self.pics = []

    def __get_pics(self, n):
        self._is_init()
        to_return = []
        if n < len(self.pics):
            to_return.extend(self.pics[::-1][:n])
            return to_return
        else:
            to_return.extend(self.pics)
            for i in range(len(self.pics), n):
                pic = self.cam.take_picture()
                to_return.append(pic)
                self.pics.append(pic)
        return to_return

    @staticmethod
    def __pyth(one, two, pixels):
        return math.sqrt(
            (one[0] - two[0]) ** 2 + (one[1] - two[1]) ** 2) > pixels

    @staticmethod
    def __check_shift(coords, pic, percent):
        pixels = max(pic.width, pic.height) * percent
        for i in range(len(coords)):
            for j in range(i + 1, len(coords)):
                if Tester.__pyth(coords[i], coords[j], pixels):
                    return False
        return True

    @staticmethod
    def __turn_amount_horiz(coord, pic):
        mid = pic.width // 2
        x = coord[0]
        return (x - mid) / pic.width * 53

    @staticmethod
    def __turn_amount_vert(coord, pic):
        mid = pic.height // 2
        y = coord[1]
        return (y - mid) / pic.height * 40

    @staticmethod
    def __center_of_contour(contour):
        moments = cv2.moments(contour)
        return moments['m10'] / moments['m00'], moments['m01'] / moments['m00']

    @staticmethod
    def __biggest_child(contours):
        maxmatch = contours[0]
        for i in range(1, len(contours)):
            if cv2.contourArea(contours[i]) > cv2.contourArea(maxmatch):
                maxmatch = contours[i]
        return maxmatch

    @staticmethod
    def is_point_red(point, image):
        if point[0] >= image.shape[1] or point[1] >= image.shape[0]:
            return False
        h = image.item(point[1], point[0], 0)
        s = image.item(point[1], point[0], 1)
        v = image.item(point[1], point[0], 2)
        # print(image.item(point[1], point[0], 0))
        # print(image.item(point[1], point[0], 1))
        # print(image.item(point[1], point[0], 2))
        return ((Tester.__LOWER1[0] <= h <= Tester.__UPPER1[1]) or (
            Tester.__LOWER2[0] <= h <= Tester.__UPPER2[1])) and (
               s >= Tester.__LOWER1[1] and v >= Tester.__LOWER1[2])

    @staticmethod
    def __get_children(hier, parent, contours):
        children = []
        child = hier[0][parent][2]
        while child != -1:
            children.append(contours[child])
            child = hier[0][child][0]
        return children

    @staticmethod
    def __sort_by_match(tosort):
        for i in range(0, len(tosort) - 1):
            minmatch = i
            for j in range(i + 1, len(tosort)):
                if tosort[j][2] < tosort[minmatch][2]:
                    minmatch = j

            if minmatch != i:
                temp = tosort[minmatch]
                tosort[minmatch] = tosort[i]
                tosort[i] = temp
        return tosort

    @staticmethod
    def __test_candle_pic(pic):
        image = cv2.cvtColor(pic.img, cv2.COLOR_BGR2GRAY)
        image = cv2.GaussianBlur(image, (5, 5), 0)

        # consider selecting threshold using min max avg
        image = cv2.threshold(image, 230, 255, cv2.THRESH_BINARY)[1]

        # consider using RETR_LIST
        contours = cv2.findContours(image.copy(), cv2.RETR_EXTERNAL,
                                    cv2.CHAIN_APPROX_SIMPLE)

        contours = contours[1]
        cont_moreinfo = []
        for c in contours:
            if cv2.contourArea(c) < 200:
                continue
            moment = cv2.moments(c)
            if moment['m00'] == 0:
                continue
            x = int(moment['m10'] / moment['m00'])
            y = int(moment['m01'] / moment['m00'])
            match = cv2.matchShapes(c, _CANDLE_FLAME_SHAPE, 1, 0)
            cont_moreinfo.append((c, (x, y), match))
            if RUNNING_ON_MAC:
                disp_image = pic.img.copy()
                cv2.drawContours(disp_image, [c], -1, (0, 255, 0), 3)
                cv2.circle(disp_image, (x, y), 3, (255, 0, 0), -1)
                print(x, y)
                # print(Tester.__turn_amount_horiz((x, y), pic), 'degrees')
                print(match)

        if RUNNING_ON_MAC:
            print()
            cv2.imshow('Test', disp_image)
            cv2.waitKey(1000)

        if len(cont_moreinfo) < 1:
            return 0, []
        elif len(cont_moreinfo) == 1:
            return 1, [cont_moreinfo[0]]
        else:
            return len(cont_moreinfo), Tester.__sort_by_match(cont_moreinfo)

    def test_candle(self, quantity=3, deviation_allowed=0.05):
        self._is_init()
        candlepics = self.__get_pics(quantity)
        responses = []
        allsame = True
        last = None
        for pic in candlepics:
            response = Tester.__test_candle_pic(pic)
            if last is None:
                last = response[0]
            elif response[0] != last:
                allsame = False
                break
            responses.append(response)
        if not allsame:
            return Tester.TEST_AGAIN, 0.0
        elif responses[0][0] == 0:
            return Tester.NOTHING_DETECTED, 0.0
        else:
            coords = []
            for i in responses:
                coords.append(i[1][1])
            if Tester.__check_shift(coords, candlepics[0], deviation_allowed):
                if responses[0][0] == 1:
                    return Tester.HIGHLY_LIKELY, Tester.__turn_amount_horiz(
                        responses[0][1][0])
                else:
                    return Tester.POSSIBLY, Tester.__turn_amount_horiz(
                        responses[0][1][0])
            else:
                if responses[0][0] == 1:
                    return Tester.TOO_MUCH_DEVIATION, 0.0
                else:
                    return Tester.TEST_AGAIN, 0.0

    @staticmethod
    def __test_safety_zone_pic(pic):
        hsv = cv2.cvtColor(pic.img, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, Tester.__LOWER, Tester.__UPPER)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.GaussianBlur(mask, (1, 1), 0)

        contours, hierarchy = cv2.findContours(mask.copy(), cv2.RETR_TREE,
                                               cv2.CHAIN_APPROX_SIMPLE)[1:3]

        i = -1
        for c in contours:
            i += 1
            perimeter = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.03 * perimeter, True)
            if hierarchy[0][i][3] != -1 or cv2.contourArea(
                    c) < 200 or not cv2.isContourConvex(approx):
                continue
            if len(approx) == 4:
                children = Tester.__get_children(hierarchy, i, contours)
                if len(children) > 0:
                    bigchild = Tester.__biggest_child(children)
                    cv2.drawContours(frame, [bigchild], -1, (0, 255, 0), 10)
                    blurred = cv2.GaussianBlur(hsv, (5, 5), 0)
                    centerpt = Tester.__center_of_contour(bigchild)
                    if Tester.__is_point_red(centerpt, blurred):
                        perimeterchild = cv2.arcLength(bigchild, True)
                        approxchild = cv2.approxPolyDP(bigchild,
                                                       0.01 * perimeter,
                                                       True)
                        if len(approxchild) > 6:
                            return Tester.SAFETY_ZONE_DETECTED, centerpt
        return Tester.NOTHING_DETECTED, (0, 0)

    def test_safety_zone(self, quantity=3, deviation_allowed=0.2):
        self._is_init()
        zonepics = self.__get_pics(quantity)
        responses = []
        coords = []
        required = math.ceil(quantity / 2)
        for pic in zonepics:
            response = Tester.__test_safety_zone_pic(pic)
            responses.append(response)
            if response[0] == Tester.SAFETY_ZONE_DETECTED:
                coords.append(response[1])
        if len(coords) >= required and Tester.__check_shift(coords, pic, deviation_allowed):
            return Tester.SAFETY_ZONE_DETECTED, Tester.__turn_amount_horiz(coords[0])
        return Tester.NOTHING_DETECTED, 0.0

    @staticmethod
    def __test_blue_led_pic(pic):
        pass

    def test_blue_led(self):
        pass

    def __enter__(self):
        self.init()
        return self

    def __exit__(self, type, value, traceback):
        self.close()


if RUNNING_ON_MAC:
    with Tester() as test:
        print(test.test_candle())
