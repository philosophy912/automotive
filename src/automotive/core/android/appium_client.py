# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        appium_client.py
# @Author:      lizhe
# @Created:     2021/5/1 - 23:48
# --------------------------------------------------------
import time
from typing import Dict, Union, Tuple, List, Optional

from appium import webdriver
from appium.webdriver import WebElement
from appium.webdriver.common.touch_action import TouchAction
from appium.webdriver.webdriver import WebDriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from automotive.logger.logger import logger
from .common.constants import UISELECTORS, LOCATORS, DEFAULT_TIME_OUT

from .common.enums import ElementAttributeEnum, SwipeDirectorEnum, DirectorEnum
from .common.interfaces import BaseAndroid
from .common.typehints import AppiumLocatorElement, Locator, Attributes, ClickPosition, LocatorElement
from ...common.typehints import Position
from time import sleep


class AppiumClient(BaseAndroid):

    def __init__(self):
        super().__init__()
        self._driver = None
        self._actions = None

    @staticmethod
    def __get_key_value(locator: dict) -> Tuple[str, str]:
        """
        获取key, value
        :param locator: 字典，长度为1
        :return: key value
        """
        for key, item in locator.items():
            return key, item

    @staticmethod
    def __get_xpath_text(text: str) -> str:
        """
        设置获取的text的xpath地址

        :param text: 要获取的text名字

        :return: xpath的text地址
        """
        return "//*[@text=\"" + text + "\"]"

    @staticmethod
    def __get_attribute(element: WebElement) -> Attributes:
        """
        获取控件的属性值

        :param element: 控件

        :return:  字典对象，如{"checkable": True}
        """
        attribute = Attributes()
        for attr in ElementAttributeEnum:
            result = element.get_attribute(attr.value)
            logger.debug(f"the {attr.value} value is {result}")
            attribute[attr] = True if result == "true" else False
        return attribute

    @staticmethod
    def __get_by_type(by_type: str) -> str:
        """
        将类型变成appium方式支持的类型

        :param by_type: 目前支持下列5种类型

            resourceId, className, xpath, text, description

        :return:
            除了description返回str外，其他返回By
        """
        if by_type not in LOCATORS:
            raise TypeError(f"by_type[{by_type}] is not support, only support {LOCATORS}")
        if by_type == "resourceId":
            return By.ID
        elif by_type == "className":
            return By.CLASS_NAME
        elif by_type == "xpath":
            return By.XPATH
        elif by_type == "text":
            return By.NAME
        elif by_type == "description":
            return "description"

    @staticmethod
    def __get_ui_selector(locator: Locator) -> str:
        """
        根据locator来获取selector

        :param locator: 多个定位符

        :return: Uiautomator方式的字符串
        """
        selector = ""
        for key, value in locator.items():
            if key not in UISELECTORS:
                raise ValueError(f"locator type[{key}] not support, only support[{UISELECTORS}]")
            selector = f"{selector}.{key}(\"{value}\")"
        # 需要去掉第一个的点[.]
        return selector[1:].replace("True", "true").replace("False", "false")

    @staticmethod
    def __wait_until(element: Union[WebDriver, WebElement],
                     locator: Union[str, Tuple[str, str]],
                     function_name: str,
                     timeout: Optional[float]) -> Union[WebElement, List[WebElement]]:
        """
        等待元素出现

        :param element: 从element开始查找

        :param locator: 定位符

        :param timeout: 超时时间

        :param function_name: 要执行的函数名

        :return: WebElement元素
        """
        if timeout:
            end_time = time.time() + timeout
            logger.trace(f"locator is {locator}")
            while True:
                logger.trace(f"element type is{type(element)} and function name is [{function_name}]")
                logger.trace(f"param is [{locator}]")
                try:
                    if isinstance(locator, tuple):
                        find_type, value = locator
                        logger.trace(f"find_type = {find_type}, value = {value}")
                        return getattr(element, function_name)(*locator)
                    else:
                        return getattr(element, function_name)(locator)
                except NoSuchElementException:
                    time.sleep(0.5)
                    if time.time() > end_time:
                        break
            raise NoSuchElementException(f"no found locator[{locator} by method {function_name}]")
        else:
            if isinstance(locator, tuple):
                find_type, value = locator
                logger.trace(f"find_type = {find_type}, value = {value}")
                return getattr(element, function_name)(find_type, value)
            else:
                return getattr(element, function_name)(locator)

    def __find_element_by_ui_selector(self,
                                      element: Union[WebDriver, WebElement],
                                      locator: str,
                                      timeout: Optional[float]) -> WebElement:
        """
        通过uiselector方式查找element

        :param element: 从element开始查找

        :param locator: uiselector的定位字符串

        :return: WebElement元素
        """
        return self.__wait_until(element, locator, "find_element_by_android_uiautomator", timeout)

    def __find_elements_by_ui_selector(self,
                                       element: Union[WebDriver, WebElement],
                                       locator: str,
                                       timeout: Optional[float]) -> List[WebElement]:
        """
        通过uiselector方式查找elements

        :param element: 从element开始查找

        :param locator: uiselector的定位字符串

        :return: WebElement元素列表
        """
        return self.__wait_until(element, locator, "find_elements_by_android_uiautomator", timeout)

    def __get_element(self,
                      element: Union[WebDriver, WebElement],
                      locator: Locator,
                      timeout: Optional[float]) -> WebElement:
        """
        查找element下面的locator定位的元素, 只支持一种定位方式，即len(locator) = 1

        :param element:  从那个element去查找

        :param locator:  定位符

        :param timeout: 超时时间

        :return: WebElement元素
        """
        if isinstance(locator, (str, dict)):
            locator = self._convert_locator(locator)
        for key, value in locator.items():
            logger.trace(f"key is {key}")
            if key in LOCATORS:
                by_type = self.__get_by_type(key)
                if by_type == "description":
                    return self.__wait_until(element, (by_type, value), "find_element_by_accessibility_id", timeout)
                elif by_type == By.NAME:
                    by_type = By.XPATH
                    value = self.__get_xpath_text(value)
                    return self.__wait_until(element, (by_type, value), "find_element", timeout)
                else:
                    return self.__wait_until(element, (by_type, value), "find_element", timeout)
            elif key in UISELECTORS:
                locator = self.__get_ui_selector(locator)
                return self.__find_element_by_ui_selector(element, locator, timeout)
            else:
                raise TypeError(f"key[{key}] is not support and only support {UISELECTORS} and {LOCATORS}")

    def __get_elements(self, element: Union[WebDriver, WebElement], locator: Dict[str, str],
                       timeout: Optional[float]) -> List[WebElement]:
        """
        查找element下面的locator定位所在的元素列表, 只支持一种定位方式，即len(locator) = 1

        :param element:  从那个element去查找

        :param locator:  定位符

        :param timeout: 超时时间

        :return: WebElement元素列表
        """
        if isinstance(locator, (str, dict)):
            locator = self._convert_locator(locator)
        for key, value in locator.items():
            logger.trace(f"key is {key}")
            if key in LOCATORS:
                by_type = self.__get_by_type(key)
                if by_type == "description":
                    return self.__wait_until(element, (by_type, value), "find_elements_by_accessibility_id", timeout)
                elif by_type == By.NAME:
                    by_type = By.XPATH
                    value = self.__get_xpath_text(value)
                    return self.__wait_until(element, (by_type, value), "find_elements", timeout)
                else:
                    return self.__wait_until(element, (by_type, value), "find_elements", timeout)
            elif key in UISELECTORS:
                locator = self.__get_ui_selector(locator)
                return self.__find_elements_by_ui_selector(element, locator, timeout)
            else:
                raise TypeError(f"key[{key}] is not support and only support {UISELECTORS} and {LOCATORS}")

    def __get_click_point(self, element: WebElement, position: DirectorEnum = DirectorEnum.CENTER) -> ClickPosition:
        """
        根据position确定需要点击的范围

        :param element: 要点击元素对象

        :param position: 要点击的位置

        :return: 坐标点x, y
        """
        start_x, start_y, width, height = self.get_location(element)
        return self.get_point(start_x, start_y, width, height, position)

    def __click_point(self, x: int, y: int, count: int = 1):
        """
        点击坐标点

        由于传入的单位是秒，需要转换成毫秒

        :param x: 坐标点X

        :param y: 坐标点Y

        :param count: 点击次数
        """
        self._actions.tap(x=x, y=y, count=count).perform()

    def __press_point(self, x: int, y: int, duration: float):
        """
        按下坐标点

        :param x: 坐标点X

        :param y: 坐标点Y

        :param duration: 持续时间
        """
        duration = int(duration * 1000)
        self._actions.long_press(x=x, y=y, duration=duration).wait(duration).perform()

    def connect(self, device_id: str, capability: Dict[str, str] = None, url: str = "http://localhost:4723/wd/hub"):
        capability["deviceName"] = device_id
        self._driver = webdriver.Remote(url, capability)
        self._actions = TouchAction(self._driver)

    def disconnect(self):
        self._driver = None
        self._actions = None

    def open_app(self, package: str, activity: str):
        self._driver.start_activity(package, activity)

    def close_app(self, package: str = None):
        self._driver.quit()

    def get_element(self, locator: AppiumLocatorElement, timeout: float = DEFAULT_TIME_OUT) -> WebElement:
        if isinstance(locator, WebElement):
            return locator
        else:
            if isinstance(locator, (str, Locator)):
                locator = self._convert_locator(locator)
            if len(locator) == 1:
                key, value = self.__get_key_value(locator)
                # 当支持的key属于"resourceId", "className", "xpath", "text", "description"中的某一种的时候
                # 采用get_element方式定位
                if key in LOCATORS:
                    return self.__get_element(self._driver, locator, timeout)
                # 检查是否属于uiselector中的某一种定位方式
                elif key in UISELECTORS:
                    locator = self.__get_ui_selector(locator)
                    return self.__find_element_by_ui_selector(self._driver, locator, timeout)
                else:
                    raise KeyError(f"not support {key} method locator, please check it again")
            else:
                locator = self.__get_ui_selector(locator)
                return self.__find_element_by_ui_selector(self._driver, locator, timeout)

    def get_elements(self, locator: Locator, timeout: float = DEFAULT_TIME_OUT) -> List[WebElement]:
        if len(locator) == 1:
            locator = self._convert_locator(locator)
            key, value = self.__get_key_value(locator)
            # 当支持的key属于"resourceId", "className", "xpath", "text", "description"中的某一种的时候
            # 采用get_element方式定位
            if key in LOCATORS:
                return self.__get_elements(self._driver, locator, timeout)
            # 检查是否属于uiselector中的某一种定位方式
            elif key in UISELECTORS:
                locator = self.__get_ui_selector(locator)
                return self.__find_elements_by_ui_selector(self._driver, locator, timeout)
            else:
                raise KeyError(f"not support {key} method locator, please check it again")
        else:
            locator = self.__get_ui_selector(locator)
            return self.__find_elements_by_ui_selector(self._driver, locator, timeout)

    def get_child_element(self,
                          parent: AppiumLocatorElement,
                          locator: Locator,
                          timeout: float = DEFAULT_TIME_OUT) -> WebElement:
        element = self.get_element(parent, timeout)
        return self.__get_element(element, locator, timeout)

    def get_child_elements(self,
                           parent: AppiumLocatorElement,
                           locator: Locator,
                           timeout: float = DEFAULT_TIME_OUT) -> List[WebElement]:
        element = self.get_element(parent, timeout)
        return self.__get_elements(element, locator, timeout)

    def get_element_attribute(self,
                              locator: AppiumLocatorElement,
                              timeout: float = DEFAULT_TIME_OUT) -> Attributes:
        attributes = dict()
        element = self.get_element(locator, timeout)
        for attr in list(map(lambda x: x.value, ElementAttributeEnum.__members__.values())):
            if attr == "text":
                value = element.text
            else:
                value = element.get_attribute(attr)
            logger.trace(f"The {attr} attribute is {value}")
            attributes[ElementAttributeEnum.from_value(attr)] = True if value == "true" else False
            attributes[attr] = True if value == "true" else False
        return attributes

    def scroll_get_element(self,
                           element: AppiumLocatorElement,
                           locator: Locator,
                           text: str,
                           exact_match: bool = True,
                           duration: Optional[float] = None,
                           direct: SwipeDirectorEnum = SwipeDirectorEnum.UP,
                           swipe_time: Optional[int] = None,
                           swipe_percent: float = 0.8,
                           timeout: float = DEFAULT_TIME_OUT,
                           wait_time: Optional[float] = None) -> WebElement:
        start_x, start_y, end_x, end_y, duration = self._get_swipe_param(element, direct, duration, swipe_percent)
        return self._scroll_element(start_x, start_y, end_x, end_y, duration, direct, element, locator, text,
                                    exact_match, timeout, swipe_time, wait_time)

    def get_device_id(self) -> str:
        return self._driver.capabilities["deviceName"]

    def get_location(self, locator: AppiumLocatorElement, timeout: float = DEFAULT_TIME_OUT) -> Position:
        element = self.get_element(locator, timeout)
        location = element.location
        size = element.size
        x, y = location["x"], location["y"]
        width, height = size["width"], size["height"]
        logger.debug(f"x = [{x}], y = [{y}], width = {width}, height = {height}")
        return x, y, width, height

    def click_if_attribute(self,
                           locator: AppiumLocatorElement,
                           element_attribute: ElementAttributeEnum,
                           status: bool,
                           timeout: float = DEFAULT_TIME_OUT):
        current_status = self.get_element_attribute(locator, timeout)[element_attribute]
        if current_status == status:
            self.click(locator, timeout)

    def click(self, locator: Union[ClickPosition, AppiumLocatorElement],
              timeout: float = DEFAULT_TIME_OUT):
        x, y = self._get_element_location(locator, DirectorEnum.CENTER, timeout)
        logger.info(f"the point[{x}:{y}] will be click")
        self.__click_point(x, y)

    def double_click(self,
                     locator: Union[ClickPosition, AppiumLocatorElement],
                     timeout: float = DEFAULT_TIME_OUT,
                     duration: float = 0.1):
        x, y = self._get_element_location(locator, DirectorEnum.CENTER, timeout)
        logger.info(f"the point[{x}:{y}] will be click")
        self.__click_point(x, y, 2)

    def press(self,
              locator: Union[ClickPosition, AppiumLocatorElement],
              duration: Optional[float] = None,
              timeout: float = DEFAULT_TIME_OUT):
        x, y = self._get_element_location(locator, DirectorEnum.CENTER, timeout)
        logger.info(f"the point[{x}:{y}] will be click")
        self.__press_point(x, y, duration)

    def drag(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: int = 1):
        self._actions.long_press(x=start_x, y=start_y).move_to(x=end_x, y=end_y).wait(duration).release().perform()

    def drag_element_to(self,
                        locator1: AppiumLocatorElement,
                        locator2: AppiumLocatorElement,
                        duration: int = 1,
                        timeout: float = DEFAULT_TIME_OUT):
        x1, y1 = self.__get_click_point(self.get_element(locator1, timeout))
        x2, y2 = self.__get_click_point(self.get_element(locator2, timeout))
        self.drag(x1, y1, x2, y2, duration)

    def drag_to(self,
                locator: AppiumLocatorElement,
                x: int,
                y: int,
                duration: int = 1,
                timeout: float = DEFAULT_TIME_OUT):
        x1, y1 = self.__get_click_point(self.get_element(locator, timeout))
        self.drag(x1, y1, x, y, duration)

    def swipe_element(self,
                      from_element: Union[ClickPosition, AppiumLocatorElement],
                      to_element: Union[ClickPosition, AppiumLocatorElement],
                      duration: Optional[int] = None,
                      timeout: float = DEFAULT_TIME_OUT):
        start_x, start_y = self._get_element_location(from_element, DirectorEnum.CENTER, timeout)
        end_x, end_y = self._get_element_location(to_element, DirectorEnum.CENTER, timeout)
        logger.info(f"start from {start_x} : {start_y} to scroll to {end_x}: {end_y}")
        self._driver.swipe(start_x, start_y, end_x, end_y, duration)

    def swipe(self,
              swipe_element: AppiumLocatorElement,
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

    def get_text(self, locator: AppiumLocatorElement, timeout: float = DEFAULT_TIME_OUT) -> str:
        return self.get_element(locator, timeout).text

    def input_text(self, locator: AppiumLocatorElement, text: str, timeout: float = DEFAULT_TIME_OUT):
        element = self.get_element(locator, timeout)
        logger.debug(f"it will input text {text} to element")
        element.send_keys(text)

    def clear_text(self, locator: AppiumLocatorElement, timeout: float = DEFAULT_TIME_OUT):
        element = self.get_element(locator, timeout)
        logger.debug(f"it will clear text in element")
        element.clear()

    def screen_shot(self, file: str):
        self._driver.get_screenshot_as_file(file)

    def get_xml_struct(self) -> str:
        return self._driver.page_source

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