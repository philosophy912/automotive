# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        uiautomator2_client.py
# @Author:      lizhe
# @Created:     2021/5/1 - 23:49
# --------------------------------------------------------
import uiautomator2 as u2
import time
import cv2

from selenium.common.exceptions import NoSuchElementException
from uiautomator2 import UiObject, Device
from automotive.logger import logger

from .api import ElementAttributeEnum, SwipeDirectorEnum, DirectorEnum, BaseAndroid


class UiAutomator2Client(BaseAndroid):
    """
    AndroidService类用于构建一个uiautomator2(简称u2)和appium都能够用到的统一接口

    详细的使用可以通过driver使用原生的uiautomator2

    参考网站https://github.com/openatx/uiautomator2
    """
    DEFAULT_TIME_OUT = 3

    def __wait_until(self, element: (Device, UiObject), locator: dict, timeout: float) -> UiObject:
        """
        等待元素出现

        :param element: UiObject或者Device对象

        :param locator: 定位符

        :param timeout: 超时时间

        :return: UiObject元素
        """
        selectors = list(map(lambda x: x.lower(), self._UISELECTORS))
        device_locator = dict()
        for key, value in locator.items():
            key = key.lower().replace("-", "")
            if key not in selectors:
                raise KeyError(f"key [{key}] is not support, only support {self._UISELECTORS}")
            else:
                # 因为大小写的原因，转换如classname到_UISELECTORS支持的className
                device_locator[self._UISELECTORS[selectors.index(key)]] = value
        if timeout:
            end_time = time.time() + timeout
            logger.debug(f"locator is {device_locator}")
            while True:
                if isinstance(element, Device):
                    logger.trace(f"find element in driver")
                    ui_object = element(**device_locator)
                else:
                    logger.trace(f"find element in element")
                    ui_object = element.child(**device_locator)
                if ui_object.exists:
                    return ui_object
                time.sleep(0.5)
                if time.time() > end_time:
                    break
        else:
            if isinstance(element, Device):
                logger.trace(f"find element in driver")
                ui_object = element(**device_locator)
            else:
                logger.trace(f"find element in element")
                ui_object = element.child(**device_locator)
            if ui_object.exists:
                return ui_object
        raise NoSuchElementException(f"no found locator[{device_locator} in device")

    def __get_click_point(self, element: UiObject, position: DirectorEnum = DirectorEnum.CENTER) -> tuple:
        """
        根据position确定需要点击的范围

        :param element: 要点击元素对象

        :param position: 要点击的位置

        :return: 坐标点x, y
        """
        start_x, start_y, width, height = self.get_location(element)
        return self.get_point(start_x, start_y, width, height, position)

    def connect(self, device_id: str, capability: dict = None, url: str = "http://localhost:4723/wd/hub"):
        self._driver = u2.connect(device_id)

    def open_app(self, package: str, activity: str):
        self._driver.app_start(package, activity)

    def close_app(self, package: str = None):
        if package:
            self._driver.app_stop(package)
        else:
            self._driver.app_stop_all()

    def get_element(self, locator: (str, dict, UiObject), timeout: float = DEFAULT_TIME_OUT) -> UiObject:
        self._check_instance(locator, (str, dict, UiObject))
        if isinstance(locator, UiObject):
            return locator
        else:
            if isinstance(locator, (str, dict)):
                locator = self._convert_locator(locator)
            return self.__wait_until(self._driver, locator, timeout)

    def get_elements(self, locator: (str, dict), timeout: float = DEFAULT_TIME_OUT) -> list:
        self._check_instance(locator, (str, dict))
        elements = []
        element = self.get_element(locator, timeout)
        for i in range(element.count):
            elements.append(element[i])
        return elements

    def get_child_element(self, parent: (dict, UiObject), locator: (str, dict),
                          timeout: float = DEFAULT_TIME_OUT) -> UiObject:
        self._check_instance(parent, (dict, UiObject))
        self._check_instance(locator, (str, dict))
        parent = self.get_element(parent, timeout)
        if isinstance(locator, (str, dict)):
            locator = self._convert_locator(locator)
        return self.__wait_until(parent, locator, timeout)

    def get_child_elements(self, parent: (dict, UiObject), locator: (str, dict),
                           timeout: float = DEFAULT_TIME_OUT) -> list:
        self._check_instance(parent, (dict, UiObject))
        self._check_instance(locator, (str, dict))
        elements = []
        element = self.get_child_element(parent, locator, timeout)
        for i in range(element.count):
            elements.append(element[i])
        return elements

    def get_element_attribute(self, locator: (str, dict, UiObject), timeout: float = DEFAULT_TIME_OUT) -> dict:
        self._check_instance(locator, (str, dict, UiObject))
        attributes = dict()
        element = self.get_element(locator, timeout)
        info = element.info
        for key, item in ElementAttributeEnum.__members__.items():
            # display不支持，所以暂时要抛弃这个，貌似appium支持
            if key.lower() != ElementAttributeEnum.DISPLAYED.value:
                attributes[item] = info[item.value]
            if key.lower() == ElementAttributeEnum.TEXT.value:
                attributes[item] = element.get_text()
            else:
                logger.debug(f"due to no attribute in uiautomator2 so default value is True")
                attributes[item] = True
        return attributes

    def scroll_get_element(self, element: (dict, UiObject), locator: dict, text: str, exact_match: bool = True,
                           duration: float = None, direct: SwipeDirectorEnum = SwipeDirectorEnum.UP,
                           swipe_time: int = None, swipe_percent: float = 0.8,
                           timeout: float = DEFAULT_TIME_OUT) -> UiObject:
        self._check_instance(locator, (dict, UiObject))
        self._check_instance(locator, dict)
        start_x, start_y, end_x, end_y, duration = self._get_swipe_param(element, direct, duration, swipe_percent)
        return self._scroll_element(start_x, start_y, end_x, end_y, duration, direct, element, locator, text,
                                    exact_match, timeout, swipe_time)

    def get_location(self, locator: (str, dict, UiObject), timeout: float = DEFAULT_TIME_OUT) -> tuple:
        self._check_instance(locator, (str, dict, UiObject))
        info = self.get_element(locator, timeout).info
        bounds = info["bounds"]
        bottom, left, right, top = bounds["bottom"], bounds["left"], bounds["right"], bounds["top"]
        return left, top, (right - left), (bottom - top)

    def get_device_id(self) -> str:
        return self._driver.serial

    def click(self, locator: (tuple, str, dict, UiObject), timeout: float = DEFAULT_TIME_OUT):
        self._check_instance(locator, (tuple, str, dict, UiObject))
        x, y = self._get_element_location(locator, DirectorEnum.CENTER, timeout)
        self._driver.click(x, y)

    def double_click(self, locator: (tuple, str, dict, UiObject), timeout: float = DEFAULT_TIME_OUT,
                     duration: float = 0.1):
        self._check_instance(locator, (tuple, str, dict, UiObject))
        x, y = self._get_element_location(locator, DirectorEnum.CENTER, timeout)
        self._driver.double_click(x, y, duration)

    def press(self, locator: (tuple, str, dict, UiObject), duration: float, timeout: float = DEFAULT_TIME_OUT):
        self._check_instance(locator, (tuple, str, dict, UiObject))
        self._check_instance(duration, float)
        x, y = self._get_element_location(locator, DirectorEnum.CENTER, timeout)
        self._driver.long_click(x, y, duration)

    def drag(self, start_x: int, start_y: int, end_x: int, end_y: int):
        raise RuntimeError(f"uiautomator2 not support drag point")

    def drag_element_to(self, locator1: (str, dict, UiObject), locator2: (str, dict, UiObject),
                        timeout: float = DEFAULT_TIME_OUT):
        self._check_instance(locator1, (str, dict, UiObject))
        self._check_instance(locator2, (str, dict, UiObject))
        x, y = self._get_element_location(locator2, DirectorEnum.CENTER, timeout)
        self.drag_to(locator1, x, y, timeout)

    def drag_to(self, locator: (str, dict, UiObject), x: int, y: int, timeout: float = DEFAULT_TIME_OUT):
        self._check_instance(locator, (str, dict, UiObject))
        self._check_instance(x, int)
        self._check_instance(y, int)
        element = self.get_element(locator, timeout)
        element.drag_to(x=x, y=y)

    def swipe_element(self, from_element: (str, dict, UiObject), to_element: (str, dict, UiObject),
                      duration: float = None, timeout: float = DEFAULT_TIME_OUT):
        self._check_instance(from_element, (str, dict, UiObject))
        self._check_instance(to_element, (str, dict, UiObject))
        x1, y1 = self.__get_click_point(self.get_element(from_element))
        x2, y2 = self.__get_click_point(self.get_element(to_element))
        self._driver.swipe(x1, y2, x2, y2, duration)

    def swipe(self, swipe_element: (dict, UiObject), locator: dict, duration: float = None,
              direction: SwipeDirectorEnum = SwipeDirectorEnum.UP, swipe_time: int = None, wait_time: float = None,
              timeout: float = DEFAULT_TIME_OUT, swipe_percent: float = 0.8):
        self._check_instance(swipe_element, (dict, UiObject))
        self._check_instance(locator, dict)
        logger.debug(f"swipe_element is {swipe_element}")
        # 首先获取locator定位的元素， 并判断该元素是否可滑动，若不可滑动则发出警告信息
        swipe_element = self.get_element(swipe_element, timeout)
        if not self.get_element_attribute(swipe_element, timeout)[ElementAttributeEnum.SCROLLABLE]:
            logger.warning(f"element is not scrollable")
        # 其次，根据方向确定start_x, start_y, end_x, end_y
        x, y, width, height = self.get_location(swipe_element)
        start_x, start_y, end_x, end_y = self._get_swipe_point(x, y, width, height, direction, swipe_percent)
        logger.debug(f"swipe from {start_x}, {start_y} to {end_x}, {end_y}")
        # 若swipe_time为None，表示滑动到顶
        self._scroll_element(start_x, start_y, end_x, end_y, duration, direction, swipe_element, locator,
                             timeout=timeout, swipe_time=swipe_time, wait_time=wait_time)

    def get_text(self, locator: (str, dict, UiObject), timeout: float = DEFAULT_TIME_OUT) -> str:
        self._check_instance(locator, (str, dict, UiObject))
        return self.get_element(locator, timeout).get_text()

    def input_text(self, locator: (str, dict, UiObject), text: str, timeout: float = DEFAULT_TIME_OUT):
        self._check_instance(locator, (str, dict, UiObject))
        self._check_instance(text, str)
        self.get_element(locator, timeout).set_text(text)

    def clear_text(self, locator: (str, dict, UiObject), timeout: float = DEFAULT_TIME_OUT):
        self._check_instance(locator, (str, dict, UiObject))
        self.get_element(locator, timeout).clear_text()

    def screen_shot(self, file: str):
        image = self._driver.screenshot(format="opencv")
        cv2.imwrite(file, image)

    def get_xml_struct(self) -> str:
        return self._driver.dump_hierarchy()
