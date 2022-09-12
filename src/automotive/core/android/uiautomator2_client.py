# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        uiautomator2_client.py
# @Author:      lizhe
# @Created:     2021/5/1 - 23:49
# --------------------------------------------------------
from typing import Union, Sequence, Optional

import uiautomator2 as u2
import time
import cv2

from selenium.common.exceptions import NoSuchElementException
from uiautomator2 import UiObject, Device
from automotive.logger.logger import logger
from .common.constants import UISELECTORS

from .common.enums import ElementAttributeEnum, SwipeDirectorEnum, DirectorEnum
from .common.interfaces import BaseAndroid
from .common.typehints import Capability, U2LocatorElement, Locator, Attributes, ClickPosition, LocatorElement
from ...common.typehints import Position
from time import sleep


class UiAutomator2Client(BaseAndroid):
    """
    AndroidService类用于构建一个uiautomator2(简称u2)和appium都能够用到的统一接口

    详细的使用可以通过driver使用原生的uiautomator2

    参考网站https://github.com/openatx/uiautomator2
    """

    DEFAULT_TIME_OUT = 3

    @staticmethod
    def __wait_until(element: Union[Device, UiObject], locator: Locator, timeout: Optional[float]) -> UiObject:
        """
        等待元素出现

        :param element: UiObject或者Device对象

        :param locator: 定位符

        :param timeout: 超时时间

        :return: UiObject元素
        """
        selectors = list(map(lambda x: x.lower(), UISELECTORS))
        device_locator = dict()
        for key, value in locator.items():
            key = key.lower().replace("-", "")
            if key not in selectors:
                raise KeyError(f"key [{key}] is not support, only support {UISELECTORS}")
            else:
                # 因为大小写的原因，转换如classname到_UISELECTORS支持的className
                device_locator[UISELECTORS[selectors.index(key)]] = value
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

    def __get_click_point(self, element: UiObject, position: DirectorEnum = DirectorEnum.CENTER) -> ClickPosition:
        """
        根据position确定需要点击的范围

        :param element: 要点击元素对象

        :param position: 要点击的位置

        :return: 坐标点x, y
        """
        start_x, start_y, width, height = self.get_location(element)
        return self.get_point(start_x, start_y, width, height, position)

    def connect(self, device_id: str, capability: Optional[Capability] = None,
                url: str = "http://localhost:4723/wd/hub"):
        self._driver = u2.connect(device_id)

    def disconnect(self):
        self._driver = None

    def open_app(self, package: str, activity: str):
        self._driver.app_start(package, activity)

    def close_app(self, package: str = None):
        if package:
            self._driver.app_stop(package)
        else:
            self._driver.app_stop_all()

    def get_element(self, locator: U2LocatorElement, timeout: float = DEFAULT_TIME_OUT) -> UiObject:
        if isinstance(locator, UiObject):
            return locator
        else:
            if isinstance(locator, (str, dict)):
                locator = self._convert_locator(locator)
            return self.__wait_until(self._driver, locator, timeout)

    def get_elements(self, locator: Locator, timeout: float = DEFAULT_TIME_OUT) -> Sequence[UiObject]:
        elements = []
        element = self.get_element(locator, timeout)
        for i in range(element.count):
            elements.append(element[i])
        return elements

    def get_child_element(self,
                          parent: U2LocatorElement,
                          locator: Locator,
                          timeout: float = DEFAULT_TIME_OUT) -> UiObject:
        parent = self.get_element(parent, timeout)
        if isinstance(locator, (str, dict)):
            locator = self._convert_locator(locator)
        return self.__wait_until(parent, locator, timeout)

    def get_child_elements(self,
                           parent: U2LocatorElement,
                           locator: Locator,
                           timeout: float = DEFAULT_TIME_OUT) -> Sequence[UiObject]:
        elements = []
        element = self.get_child_element(parent, locator, timeout)
        for i in range(element.count):
            elements.append(element[i])
        return elements

    def get_element_attribute(self,
                              locator: U2LocatorElement,
                              timeout: float = DEFAULT_TIME_OUT) -> Attributes:
        attributes = dict()
        element = self.get_element(locator, timeout)
        info = element.info
        logger.debug(f"info is {info}")
        for key, item in ElementAttributeEnum.__members__.items():
            # display不支持，所以暂时要抛弃这个，貌似appium支持
            if key.lower() == ElementAttributeEnum.DISPLAYED.value:
                attributes[item] = True
                attributes[item.value] = True
            elif key.lower() == ElementAttributeEnum.TEXT.value:
                attributes[item] = element.get_text()
                attributes[item.value] = element.get_text()
            else:
                logger.debug(f"key is {key} and item is {item} and value is {info[item.value]}")
                attributes[item] = info[item.value]
                attributes[item.value] = info[item.value]
        return attributes

    def scroll_get_element(self,
                           element: U2LocatorElement,
                           locator: Locator, text: str,
                           exact_match: bool = True,
                           duration: Optional[float] = None,
                           direct: SwipeDirectorEnum = SwipeDirectorEnum.UP,
                           swipe_time: Optional[int] = None,
                           swipe_percent: float = 0.8,
                           timeout: float = DEFAULT_TIME_OUT,
                           wait_time: Optional[float] = None) -> UiObject:
        start_x, start_y, end_x, end_y, duration = self._get_swipe_param(element, direct, duration, swipe_percent)
        return self._scroll_element(start_x, start_y, end_x, end_y, duration, direct, element, locator, text,
                                    exact_match, timeout, swipe_time, wait_time)

    def get_location(self, locator: U2LocatorElement, timeout: float = DEFAULT_TIME_OUT) -> Position:
        info = self.get_element(locator, timeout).info
        bounds = info["bounds"]
        bottom, left, right, top = bounds["bottom"], bounds["left"], bounds["right"], bounds["top"]
        return left, top, (right - left), (bottom - top)

    def get_device_id(self) -> str:
        return self._driver.serial

    def click_if_attribute(self,
                           locator: Union[ClickPosition, U2LocatorElement],
                           element_attribute: ElementAttributeEnum,
                           status: bool,
                           timeout: float = DEFAULT_TIME_OUT):
        current_status = self.get_element_attribute(locator, timeout)[element_attribute]
        if current_status == status:
            self.click(locator, timeout)

    def click(self, locator: Union[ClickPosition, U2LocatorElement], timeout: float = DEFAULT_TIME_OUT):
        x, y = self._get_element_location(locator, DirectorEnum.CENTER, timeout)
        self._driver.click(x, y)

    def double_click(self, locator: Union[ClickPosition, U2LocatorElement],
                     timeout: float = DEFAULT_TIME_OUT,
                     duration: float = 0.1):
        x, y = self._get_element_location(locator, DirectorEnum.CENTER, timeout)
        self._driver.double_click(x, y, duration)

    def press(self,
              locator: Union[ClickPosition, U2LocatorElement],
              duration: float,
              timeout: float = DEFAULT_TIME_OUT):
        x, y = self._get_element_location(locator, DirectorEnum.CENTER, timeout)
        self._driver.long_click(x, y, duration)

    def drag(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: int = 1):
        self._driver.drag(start_x, start_y, end_x, end_y, duration)

    def drag_element_to(self, locator1: U2LocatorElement,
                        locator2: Locator,
                        duration: int = 1, timeout: float = DEFAULT_TIME_OUT):
        start_x, start_y = self._get_element_location(locator1, DirectorEnum.CENTER, timeout)
        end_x, end_y = self._get_element_location(locator2, DirectorEnum.CENTER, timeout)
        self.drag(start_x, start_y, end_x, end_y, duration)

    def drag_to(self, locator: U2LocatorElement, x: int, y: int, duration: int = 1,
                timeout: float = DEFAULT_TIME_OUT):
        start_x, start_y = self._get_element_location(locator, DirectorEnum.CENTER, timeout)
        self.drag(start_x, start_y, x, y, duration)

    def swipe_element(self,
                      from_element: U2LocatorElement,
                      to_element: U2LocatorElement,
                      duration: Optional[float] = None,
                      timeout: float = DEFAULT_TIME_OUT):
        x1, y1 = self.__get_click_point(self.get_element(from_element))
        x2, y2 = self.__get_click_point(self.get_element(to_element))
        self._driver.swipe(x1, y1, x2, y2, duration)

    def swipe(self,
              swipe_element: U2LocatorElement,
              locator: Locator,
              duration: Optional[float] = None,
              direction: SwipeDirectorEnum = SwipeDirectorEnum.UP,
              swipe_time: Optional[int] = None,
              wait_time: Optional[float] = None,
              timeout: float = DEFAULT_TIME_OUT,
              swipe_percent: float = 0.8):
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

    def get_text(self, locator: U2LocatorElement, timeout: float = DEFAULT_TIME_OUT) -> str:
        return self.get_element(locator, timeout).get_text()

    def input_text(self, locator: U2LocatorElement, text: str, timeout: float = DEFAULT_TIME_OUT):
        self.get_element(locator, timeout).set_text(text)

    def clear_text(self, locator: U2LocatorElement, timeout: float = DEFAULT_TIME_OUT):
        self.get_element(locator, timeout).clear_text()

    def screen_shot(self, file: str):
        image = self._driver.screenshot(format="opencv")
        cv2.imwrite(file, image)

    def get_xml_struct(self) -> str:
        return self._driver.dump_hierarchy()

    def swipe_point(self, start_point: ClickPosition, end_point: ClickPosition, swipe_time: int, duration: float):
        start_x = start_point[0]
        start_y = start_point[1]
        end_x = end_point[0]
        end_y = end_point[1]
        for i in range(swipe_time):
            self._driver.swipe(start_x, start_y, end_x, end_y)
            sleep(duration)

    def swipe_in_element(self, element: LocatorElement, swipe_time: int, duration: float, percent: float = 0.8,
                         director: SwipeDirectorEnum = SwipeDirectorEnum.UP):
        """
        滑动可滑动元素
        :param element: 可滑动的元素
        :param percent: 滑动幅度
        :param swipe_time: 滑动次数
        :param duration: 每次滑动持续时间
        :param director: 滑动方向
        """
        logger.debug(f"swipe_element is {element}")
        # 首先获取locator定位的元素， 并判断该元素是否可滑动，若不可滑动则发出警告信息
        swipe_element = self.get_element(element)
        if not self.get_element_attribute(swipe_element)[ElementAttributeEnum.SCROLLABLE]:
            logger.warning(f"element is not scrollable")
        # 其次，根据方向确定start_x, start_y, end_x, end_y
        x, y, width, height = self.get_location(swipe_element)
        start_x, start_y, end_x, end_y = self._get_swipe_point(x, y, width, height, director, percent)
        logger.debug(f"swipe from {start_x}, {start_y} to {end_x}, {end_y}")
        # 若swipe_time为None，表示滑动到顶
        for i in range(swipe_time):
            self._driver.swipe(start_x, start_y, end_x, end_y, duration)
            sleep(0.5)
