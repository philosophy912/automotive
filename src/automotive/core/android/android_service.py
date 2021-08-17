# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        android_service.py
# @Author:      lizhe
# @Created:     2021/5/1 - 23:48
# --------------------------------------------------------
from enum import Enum, unique
from typing import Union, Dict, List, Tuple

from appium.webdriver import WebElement
from appium.webdriver.common.touch_action import TouchAction
from appium.webdriver.webdriver import WebDriver
from selenium.common.exceptions import NoSuchElementException
from uiautomator2 import Device, UiObject

from .api import SwipeDirectorEnum, ElementAttributeEnum
from .uiautomator2_client import UiAutomator2Client
from .appium_client import AppiumClient
from automotive.core.singleton import Singleton
from automotive.logger.logger import logger
from .adb import ADB


@unique
class ToolTypeEnum(Enum):
    """
    安卓测试方式

    APPIUM、UIAUTOMATOR2
    """
    APPIUM = "appium"
    UIAUTOMATOR2 = "uiautomator2"

    @staticmethod
    def from_value(value: str):
        """
        从枚举的值获取枚举对象

        :param value: 枚举对象对应的值

        :return: 枚举对象本身
        """
        for key, item in ToolTypeEnum.__members__.items():
            if value.lower() == item.value.lower():
                return item
        raise ValueError(f"{value} can not be found in ToolTypeEnum")


class AndroidService(metaclass=Singleton):
    """
    Android 测试服务，实现主要的测试方式，同时兼容APPIUM和Uiautomator2两种框架，

    前者当前最流行的开源框架https://github.com/appium/appium， 后者则为python的自动化测试框架https://github.com/openatx/uiautomator2

    主要实现功能如:

    1、获取元素及元素列表

    2、获取子元素及子元素列表

    3、获取元素的所有属性

    4、获取元素的指定属性

    5、滑动可滑动空间并查找指定的文本，并可以进行相关的操作

    6、滑动空间滑动到头

    7、获取控件的相关位置属性，如起始点、长宽信息

    8、元素操作，如点击、双击、长按、拖动

    9、获取元素的文本信息

    10、文本框的输入和清除

    11、指定元素是否存在

    12、获取页面Activity的XML结构
    """
    _DEFAULT_TIME_OUT = 3

    def __init__(self, tool_type: ToolTypeEnum):
        self.adb = ADB()
        self.__type = tool_type
        if tool_type == ToolTypeEnum.APPIUM:
            self.__client = AppiumClient()
        elif tool_type == ToolTypeEnum.UIAUTOMATOR2:
            self.__client = UiAutomator2Client()
        else:
            raise TypeError(f"{tool_type} not support, only support APPIUM and UIAUTOMATOR2")

    @property
    def actions(self) -> TouchAction:
        if self.__type == ToolTypeEnum.UIAUTOMATOR2:
            raise TypeError(f"uiautomator2 is not support touch action")
        return self.__client.actions

    @property
    def driver(self) -> Union[WebDriver, Device]:
        return self.__client.driver

    def connect(self, device_id: str, capability: Dict[str, str] = None, url: str = "http://localhost:4723/wd/hub"):
        """
        连接Android设备

        appium: 连接Android设备并打开app

        u2: 连接Android设备，如果传入了package和activity，则需要打开app，否则不打开app

        :param url: appium的URL

        :param capability: appium相关的配置参数

        :param device_id 设备编号
        """
        self.__client.connect(device_id, capability, url)

    def disconnect(self):
        """
        断开连接，目前仅把driver置空
        """
        self.__client.disconnect()

    def open_app(self, package: str, activity: str):
        """
        打开应用。 由于u2连接的时候不会主动打开application，则需要调用该接口

        u2/appium: 打开某个应用

        :param package 应用的package

        :param activity 应用的activity
        """
        self.__client.open_app(package, activity)

    def close_app(self, package: str = None):
        """
        关闭应用

        appium: 只能关闭所有应用

        u2: 可以单独关闭某个应用，如果没有填则表示调用app_stop_all方法

        :param package: 应用的package
        """
        self.__client.close_app(package)

    def get_element(self, locator: Union[Dict[str, str], WebElement, UiObject],
                    timeout: float = _DEFAULT_TIME_OUT) -> Union[WebElement, UiObject]:
        """
        根据定位符获取元素

        :param timeout:  超时时间, 默认3秒

        :param locator:  定位符（只支持字典类型)

        :return:

            appium: 获取的是WebElement对象

            u2: 获取的是UiObject对象
        """
        return self.__client.get_element(locator, timeout)

    def get_elements(self, locator: Dict[str, str],
                     timeout: float = _DEFAULT_TIME_OUT) -> List[Union[WebElement, UiObject]]:
        """
        根据定位符获取元素列表

        :param locator:  定位符（只支持字典类型)

        :param timeout:  超时时间, 默认3秒

        :return: 元素列表集合

            appium: 获取的是WebElement对象列表

            u2: 获取的是UiObject对象列表
        """
        return self.__client.get_elements(locator, timeout)

    def get_child_element(self, parent: Union[Dict[str, str], WebElement, UiObject], locator: Dict[str, str],
                          timeout: float = _DEFAULT_TIME_OUT) -> Union[WebElement, UiObject]:
        """
        在父元素中查找子元素

        :param parent: 父元素

        :param locator: 子元素定位符

        :param timeout: 超时时间，默认3秒

        :return:

            appium: 获取的是WebElement对象列表

            u2: 获取的是UiObject对象列表
        """
        return self.__client.get_child_element(parent, locator, timeout)

    def get_child_elements(self, parent: Union[Dict[str, str], WebElement, UiObject], locator: Dict[str, str],
                           timeout: float = _DEFAULT_TIME_OUT) -> List[Union[WebElement, UiObject]]:
        """
        在父元素中查找子元素列表

        :param parent: 父元素

        :param locator: 子元素定位符

        :param timeout: 超时时间，默认3秒

        :return: 元素列表集合

            appium: 获取的是WebElement对象列表

            u2: 获取的是UiObject对象列表
        """
        return self.__client.get_child_elements(parent, locator, timeout)

    def get_element_attribute(self, locator: Union[Dict[str, str], WebElement, UiObject],
                              timeout: float = _DEFAULT_TIME_OUT) -> Dict[ElementAttributeEnum, bool]:
        """
        获取元素的属性，以列表方式返回

        :param locator: 子元素定位符

        :param timeout: 超时时间，默认3秒

        :return: 属性字典，键值对

            key: ElementAttribute

            value: bool类型，True or False
        """
        return self.__client.get_element_attribute(locator, timeout)

    def is_checkable(self, locator: Union[Dict[str, str], WebElement, UiObject],
                     timeout: float = _DEFAULT_TIME_OUT) -> bool:
        """
        元素是否可选择

        :param locator: 定位符

        :param timeout: 超时时间

        :return: 是/否
        """
        return self.__client.get_element_attribute(locator, timeout)[ElementAttributeEnum.CHECKABLE]

    def is_checked(self, locator: Union[Dict[str, str], WebElement, UiObject],
                   timeout: float = _DEFAULT_TIME_OUT) -> bool:
        """
        元素是否可选中

        :param locator: 定位符

        :param timeout: 超时时间

        :return: 是/否
        """
        return self.__client.get_element_attribute(locator, timeout)[ElementAttributeEnum.CHECKED]

    def is_clickable(self, locator: Union[Dict[str, str], WebElement, UiObject],
                     timeout: float = _DEFAULT_TIME_OUT) -> bool:
        """
        元素是否可点击

        :param locator: 定位符

        :param timeout: 超时时间

        :return: 是/否
        """
        return self.__client.get_element_attribute(locator, timeout)[ElementAttributeEnum.CLICKABLE]

    def is_enable(self, locator: Union[Dict[str, str], WebElement, UiObject],
                  timeout: float = _DEFAULT_TIME_OUT) -> bool:
        """
        元素是否可用

        :param locator: 定位符

        :param timeout: 超时时间

        :return: 是/否
        """
        return self.__client.get_element_attribute(locator, timeout)[ElementAttributeEnum.ENABLED]

    def is_focusable(self, locator: Union[Dict[str, str], WebElement, UiObject],
                     timeout: float = _DEFAULT_TIME_OUT) -> bool:
        """
        元素是否可以存在焦点

        :param locator: 定位符

        :param timeout: 超时时间

        :return: 是/否
        """
        return self.__client.get_element_attribute(locator, timeout)[ElementAttributeEnum.FOCUSABLE]

    def is_focused(self, locator: Union[Dict[str, str], WebElement, UiObject],
                   timeout: float = _DEFAULT_TIME_OUT) -> bool:
        """
        元素是否焦点中

        :param locator: 定位符

        :param timeout: 超时时间

        :return: 是/否
        """
        return self.__client.get_element_attribute(locator, timeout)[ElementAttributeEnum.FOCUSED]

    def is_scrollable(self, locator: Union[Dict[str, str], WebElement, UiObject],
                      timeout: float = _DEFAULT_TIME_OUT) -> bool:
        """
        元素是否可滑动

        :param locator: 定位符

        :param timeout: 超时时间

        :return: 是/否
        """
        return self.__client.get_element_attribute(locator, timeout)[ElementAttributeEnum.SCROLLABLE]

    def is_long_clickable(self, locator: Union[Dict[str, str], WebElement, UiObject],
                          timeout: float = _DEFAULT_TIME_OUT) -> bool:
        """
        元素是否可长按

        :param locator: 定位符

        :param timeout: 超时时间

        :return: 是/否
        """
        return self.__client.get_element_attribute(locator, timeout)[ElementAttributeEnum.LONG_CLICKABLE]

    def is_display(self, locator: Union[Dict[str, str], WebElement, UiObject],
                   timeout: float = _DEFAULT_TIME_OUT) -> bool:
        """
        元素是否可显示，对于uiautomator2来说，默认可显示，即不准

        :param locator: 定位符

        :param timeout: 超时时间

        :return: 是/否
        """
        return self.__client.get_element_attribute(locator, timeout)[ElementAttributeEnum.CHECKABLE]

    def is_selected(self, locator: Union[Dict[str, str], WebElement, UiObject],
                    timeout: float = _DEFAULT_TIME_OUT) -> bool:
        """
        元素是否可选择

        :param locator: 定位符

        :param timeout: 超时时间

        :return: 是/否
        """
        return self.__client.get_element_attribute(locator, timeout)[ElementAttributeEnum.SELECTED]

    def scroll_get_element(self, element: Union[Dict[str, str], WebElement, UiObject], locator: Dict[str, str],
                           text: str, exact_match: bool = False, duration: float = None,
                           direct: SwipeDirectorEnum = SwipeDirectorEnum.UP, swipe_time: int = None,
                           swipe_percent: float = 0.8,
                           timeout: float = _DEFAULT_TIME_OUT, wait_time: float = None) -> Union[WebElement, UiObject]:
        """
        在可滑动的空间中，查找文字所在的控件

        :param swipe_time: 滑动次数，默认为None，即滑动到头

        :param timeout: 超时时间

        :param text: 行/列控件中要查找的文字

        :param element: 可滑动的控件

        :param locator: 滑动控件中行/列控件，一般来说是一般来说是classname: android.widget.LinearLayout

        :param exact_match: 是否精确查找

        :param duration: 滑动持续时间

        :param direct: 滑动方向

        :param swipe_percent: 滑动的比例

        :param wait_time: 每次滑动等待时间

        :return:

            appium: 获取的是WebElement对象列表

            u2: 获取的是UiObject对象列表
        """
        return self.__client.scroll_get_element(element, locator, text, exact_match, duration, direct, swipe_time,
                                                swipe_percent, timeout,  wait_time)

    def scroll_get_element_and_click(self, element: Union[Dict[str, str], WebElement, UiObject],
                                     locator: Dict[str, str], text: str, exact_match: bool = False,
                                     duration: float = None, direct: SwipeDirectorEnum = SwipeDirectorEnum.UP,
                                     swipe_time: int = None, swipe_percent: float = 0.8,
                                     timeout: float = _DEFAULT_TIME_OUT):
        """
        在可滑动的空间中，查找文字所在的控件

        :param swipe_time: 滑动次数，默认为None，即滑动到头

        :param timeout: 超时时间

        :param text: 行/列控件中要查找的文字

        :param element: 可滑动的控件

        :param locator: 滑动控件中行/列控件，一般来说是一般来说是classname: android.widget.LinearLayout

        :param exact_match: 是否精确查找

        :param duration: 滑动持续时间

        :param direct: 滑动方向

        :param swipe_percent: 滑动的比例
        """
        e = self.scroll_get_element(element=element, locator=locator, text=text, exact_match=exact_match,
                                    duration=duration, direct=direct, swipe_time=swipe_time,
                                    swipe_percent=swipe_percent, timeout=timeout)
        self.__client.click(e)

    def scroll_up_get_element(self, element: Union[Dict[str, str], WebElement, UiObject], locator: Dict[str, str],
                              text: str, exact_match: bool = False, duration: float = None, swipe_time: int = None,
                              swipe_percent: float = 0.8,
                              timeout: float = _DEFAULT_TIME_OUT) -> Union[WebElement, UiObject]:
        """
         在可滑动的空间中，向上滑动并查找文字所在的控件

        :param element: 可滑动的控件

        :param locator: 滑动控件中行/列控件，一般来说是一般来说是classname: android.widget.LinearLayout

        :param text: 行/列控件中要查找的文字

        :param exact_match: 是否精确查找

        :param duration: 滑动持续时间

        :param swipe_time: 滑动次数，默认为None，即滑动到头

        :param swipe_percent: 滑动的比例

        :param timeout: 超时时间

        :return: 查询到的对象
        """
        return self.__client.scroll_get_element(element, locator, text, exact_match, duration, SwipeDirectorEnum.UP,
                                                swipe_time, swipe_percent, timeout)

    def scroll_up_get_element_and_click(self, element: Union[Dict[str, str], WebElement, UiObject],
                                        locator: Dict[str, str], text: str, exact_match: bool = False,
                                        duration: float = None, swipe_time: int = None,
                                        swipe_percent: float = 0.8, timeout: float = _DEFAULT_TIME_OUT):
        """
         在可滑动的空间中，向上滑动并查找文字所在的控件, 并点击

        :param element: 可滑动的控件

        :param locator: 滑动控件中行/列控件，一般来说是一般来说是classname: android.widget.LinearLayout

        :param text: 行/列控件中要查找的文字

        :param exact_match: 是否精确查找

        :param duration: 滑动持续时间

        :param swipe_time: 滑动次数，默认为None，即滑动到头

        :param swipe_percent: 滑动的比例

        :param timeout: 超时时间
        """
        e = self.scroll_up_get_element(element, locator, text, exact_match, duration, swipe_time, swipe_percent,
                                       timeout)
        self.__client.click(e)

    def scroll_down_get_element(self, element: Union[Dict[str, str], WebElement, UiObject], locator: Dict[str, str],
                                text: str, exact_match: bool = False, duration: float = None, swipe_time: int = None,
                                swipe_percent: float = 0.8,
                                timeout: float = _DEFAULT_TIME_OUT) -> Union[WebElement, UiObject]:
        """
         在可滑动的空间中，向下滑动并查找文字所在的控件

        :param element: 可滑动的控件

        :param locator: 滑动控件中行/列控件，一般来说是一般来说是classname: android.widget.LinearLayout

        :param text: 行/列控件中要查找的文字

        :param exact_match: 是否精确查找

        :param duration: 滑动持续时间

        :param swipe_time: 滑动次数，默认为None，即滑动到头

        :param swipe_percent: 滑动的比例

        :param timeout: 超时时间

        :return: 查询到的对象
        """
        return self.__client.scroll_get_element(element, locator, text, exact_match, duration, SwipeDirectorEnum.DOWN,
                                                swipe_time, swipe_percent, timeout)

    def scroll_down_get_element_and_click(self, element: Union[Dict[str, str], WebElement, UiObject],
                                          locator: Dict[str, str], text: str, exact_match: bool = False,
                                          duration: float = None, swipe_time: int = None,
                                          swipe_percent: float = 0.8, timeout: float = _DEFAULT_TIME_OUT):
        """
         在可滑动的空间中，向下滑动并查找文字所在的控件，并点击

        :param element: 可滑动的控件

        :param locator: 滑动控件中行/列控件，一般来说是一般来说是classname: android.widget.LinearLayout

        :param text: 行/列控件中要查找的文字

        :param exact_match: 是否精确查找

        :param duration: 滑动持续时间

        :param swipe_time: 滑动次数，默认为None，即滑动到头

        :param swipe_percent: 滑动的比例

        :param timeout: 超时时间
        """
        e = self.scroll_down_get_element(element, locator, text, exact_match, duration, swipe_time, swipe_percent,
                                         timeout)
        self.__client.click(e)

    def scroll_left_get_element(self, element: Union[Dict[str, str], WebElement, UiObject], locator: Dict[str, str],
                                text: str, exact_match: bool = False, duration: float = None, swipe_time: int = None,
                                swipe_percent: float = 0.8,
                                timeout: float = _DEFAULT_TIME_OUT) -> Union[WebElement, UiObject]:
        """
         在可滑动的空间中，向左滑动并查找文字所在的控件

        :param element: 可滑动的控件

        :param locator: 滑动控件中行/列控件，一般来说是一般来说是classname: android.widget.LinearLayout

        :param text: 行/列控件中要查找的文字

        :param exact_match: 是否精确查找

        :param duration: 滑动持续时间

        :param swipe_time: 滑动次数，默认为None，即滑动到头

        :param swipe_percent: 滑动的比例

        :param timeout: 超时时间

        :return: 查询到的对象
        """
        return self.__client.scroll_get_element(element, locator, text, exact_match, duration, SwipeDirectorEnum.UP,
                                                swipe_time, swipe_percent, timeout)

    def scroll_left_get_element_and_click(self, element: Union[Dict[str, str], WebElement, UiObject],
                                          locator: Dict[str, str], text: str,
                                          exact_match: bool = False, duration: float = None, swipe_time: int = None,
                                          swipe_percent: float = 0.8, timeout: float = _DEFAULT_TIME_OUT):
        """
         在可滑动的空间中，向左滑动并查找文字所在的控件, 并点击

        :param element: 可滑动的控件

        :param locator: 滑动控件中行/列控件，一般来说是一般来说是classname: android.widget.LinearLayout

        :param text: 行/列控件中要查找的文字

        :param exact_match: 是否精确查找

        :param duration: 滑动持续时间

        :param swipe_time: 滑动次数，默认为None，即滑动到头

        :param swipe_percent: 滑动的比例

        :param timeout: 超时时间

        :return: 查询到的对象
        """
        e = self.scroll_left_get_element(element, locator, text, exact_match, duration, swipe_time, swipe_percent,
                                         timeout)
        self.__client.click(e)

    def scroll_right_get_element(self, element: Union[Dict[str, str], WebElement, UiObject], locator: Dict[str, str],
                                 text: str, exact_match: bool = False, duration: float = None, swipe_time: int = None,
                                 swipe_percent: float = 0.8,
                                 timeout: float = _DEFAULT_TIME_OUT) -> Union[WebElement, UiObject]:
        """
         在可滑动的空间中，向右滑动并查找文字所在的控件

        :param element: 可滑动的控件

        :param locator: 滑动控件中行/列控件，一般来说是一般来说是classname: android.widget.LinearLayout

        :param text: 行/列控件中要查找的文字

        :param exact_match: 是否精确查找

        :param duration: 滑动持续时间

        :param swipe_time: 滑动次数，默认为None，即滑动到头

        :param swipe_percent: 滑动的比例

        :param timeout: 超时时间

        :return: 查询到的对象
        """
        return self.__client.scroll_get_element(element, locator, text, exact_match, duration, SwipeDirectorEnum.UP,
                                                swipe_time, swipe_percent, timeout)

    def scroll_right_get_element_and_click(self, element: Union[Dict[str, str], WebElement, UiObject],
                                           locator: Dict[str, str], text: str, exact_match: bool = False,
                                           duration: float = None, swipe_time: int = None,
                                           swipe_percent: float = 0.8, timeout: float = _DEFAULT_TIME_OUT):
        """
         在可滑动的空间中，向右滑动并查找文字所在的控件

        :param element: 可滑动的控件

        :param locator: 滑动控件中行/列控件，一般来说是一般来说是classname: android.widget.LinearLayout

        :param text: 行/列控件中要查找的文字

        :param exact_match: 是否精确查找

        :param duration: 滑动持续时间

        :param swipe_time: 滑动次数，默认为None，即滑动到头

        :param swipe_percent: 滑动的比例

        :param timeout: 超时时间

        :return: 查询到的对象
        """
        e = self.scroll_right_get_element(element, locator, text, exact_match, duration, swipe_time, swipe_percent,
                                          timeout)
        self.__client.click(e)

    def get_location(self, locator: Union[Dict[str, str], WebElement, UiObject],
                     timeout: float = _DEFAULT_TIME_OUT) -> Tuple[int, int, int, int]:
        """
        获取元素的位置

        :param timeout: 超时时间

        :param locator: 定位符（只支持字典类型)

        :return:

            元素在屏幕中的位置, x, y, width, height
        """
        return self.__client.get_location(locator, timeout)

    def get_device_id(self) -> str:
        """
        获取device id

        :return: device_id
        """
        return self.__client.get_device_id()

    def click(self, locator: Union[Tuple[int, int], str, Dict[str, str], WebElement, UiObject],
              timeout: float = _DEFAULT_TIME_OUT):
        """
        点击元素的某个位置

        :param locator: 定位符

            tuple: 点击x, y坐标(TIPS: 如果直接传入的是X,Y)则后续的偏移不可用

            str: 查找文字并点击，即dict中只指定text元素

            dict: 查找元素并进行点击操作

            WebElement, UiObject: 直接对元素进行点击操作（前者仅适用于appium，后者适用于u2)

        :param timeout: 超时时间， 默认3秒
        """
        logger.debug(f"locator is {locator}")
        self.__client.click(locator, timeout)

    def double_click(self, locator: Union[Tuple[int, int], str, Dict[str, str], WebElement, UiObject],
                     timeout: float = _DEFAULT_TIME_OUT, duration: float = 0.1):
        """
        点击元素的某个位置
        :param duration: 两次点击的间隔时间，默认0.1秒

        :param locator: 定位符

            tuple: 点击x, y坐标(TIPS: 如果直接传入的是X,Y)则后续的偏移不可用

            str: 查找文字并点击，即dict中只指定text元素

            dict: 查找元素并进行点击操作

            WebElement, UiObject: 直接对元素进行点击操作（前者仅适用于appium，后者适用于u2)

        :param timeout: 超时时间， 默认3秒
        """
        self.__client.double_click(locator, timeout, duration)

    def press(self, locator: Union[Tuple[int, int], str, Dict[str, str], WebElement, UiObject], duration: float,
              timeout: float = _DEFAULT_TIME_OUT):
        """
        点击元素的某个位置
        :param duration: 两次点击的间隔时间


        :param locator: 定位符

            tuple: 点击x, y坐标(TIPS: 如果直接传入的是X,Y)则后续的偏移不可用

            str: 查找文字并点击，即dict中只指定text元素

            dict: 查找元素并进行点击操作

            WebElement, UiObject: 直接对元素进行点击操作（前者仅适用于appium，后者适用于u2)

        :param timeout: 超时时间， 默认3秒
        """
        self.press(locator, duration, timeout)

    def drag(self, start_x: int, start_y: int, end_x: int, end_y: int):
        """
        从某点拖动到某点

        :param start_x: 拖动的起始点x坐标

        :param start_y: 拖动的起始点y坐标

        :param end_x: 拖动的结束点x坐标

        :param end_y: 拖动的结束点y坐标
        """
        self.__client.drag(start_x, start_y, end_x, end_y)

    def drag_element_to(self, locator1: Union[Tuple[int, int], str, Dict[str, str], WebElement, UiObject],
                        locator2: Union[Tuple[int, int], str, Dict[str, str], WebElement, UiObject],
                        timeout: float = _DEFAULT_TIME_OUT):
        """
        从某点拖动到某点

        :param timeout: 超时时间

        :param locator1: 定位符1

        :param locator2: 定位符2

        """
        self.__client.drag_element_to(locator1, locator2, timeout)

    def drag_to(self, locator1: Union[Tuple[int, int], str, Dict[str, str], WebElement, UiObject],
                x: int, y: int, timeout: float = _DEFAULT_TIME_OUT):
        """
        从某点拖动到某点

        :param timeout: 超时时间

        :param locator1: 定位符1

        :param x: 拖动目的地的x

        :param y: 拖动目的地的y
        """
        self.__client.drag_to(locator1, x, y, timeout)

    def swipe_element(self, from_element: Union[Tuple[int, int], str, Dict[str, str], WebElement, UiObject],
                      to_element: Union[Tuple[int, int], str, Dict[str, str], WebElement, UiObject],
                      duration: float = None, timeout: float = _DEFAULT_TIME_OUT):
        """
        滑动元素从from到to

        :param timeout: 超时时间， 默认3秒

        :param from_element: 起始滑动的元素

        :param to_element: 滑动截止的元素

        :param duration: 持续时间
        """
        self.__client.swipe_element(from_element, to_element, duration, timeout)

    def swipe(self, swipe_element: Union[str, Dict[str, str], WebElement, UiObject],
              locator: Union[str, Dict[str, str], WebElement, UiObject],
              duration: float = None, direction: SwipeDirectorEnum = SwipeDirectorEnum.UP, swipe_time: int = None,
              wait_time: float = None, timeout: float = _DEFAULT_TIME_OUT, swipe_percent: float = 0.8):
        """
        滑动元素

        首先获取locator定位的元素， 并判断该元素是否可滑动，若不可滑动则发出警告信息

        其次，获取x, y, width, height， 根据方向确定start_x, start_y, end_x, end_y

        若swipe_time为None，表示滑动到顶

        :param wait_time: 滑动等待时间

        :param swipe_percent: 滑动比例

        :param swipe_element: 可滑动的元素, 一般情况是android.widget.ListView

        :param timeout: 超时时间， 默认3秒

        :param swipe_time: 滑动次数，默认为None表示滑动到头

        :param locator: 用于定位是否滑动到最后的元素，一般是android.widget.LinearLayout

        :param duration: 持续时间

        :param direction: 方向，只支持UP/DOWN/LEFT/RIGHT四个方向

        """
        self.__client.swipe(swipe_element, locator, duration, direction, swipe_time, wait_time, timeout, swipe_percent)

    def swipe_up(self, swipe_element: Union[str, Dict[str, str], WebElement, UiObject],
                 locator: Union[str, Dict[str, str], WebElement, UiObject],
                 duration: float = None, swipe_time: int = None, wait_time: float = None,
                 timeout: float = _DEFAULT_TIME_OUT, swipe_percent: float = 0.8):
        """
        向上滑动元素

        首先获取locator定位的元素， 并判断该元素是否可滑动，若不可滑动则发出警告信息

        其次，获取x, y, width, height， 根据方向确定start_x, start_y, end_x, end_y

        若swipe_time为None，表示滑动到顶

        :param wait_time: 滑动等待时间

        :param swipe_percent: 滑动比例

        :param swipe_element: 可滑动的元素, 一般情况是android.widget.ListView

        :param timeout: 超时时间， 默认3秒

        :param swipe_time: 滑动次数，默认为None表示滑动到头

        :param locator: 用于定位是否滑动到最后的元素，一般是android.widget.LinearLayout

        :param duration: 持续时间

        """
        self.__client.swipe(swipe_element, locator, duration, SwipeDirectorEnum.UP, swipe_time, wait_time, timeout,
                            swipe_percent)

    def swipe_down(self, swipe_element: Union[str, Dict[str, str], WebElement, UiObject],
                   locator: Union[str, Dict[str, str], WebElement, UiObject],
                   duration: float = None, swipe_time: int = None, wait_time: float = None,
                   timeout: float = _DEFAULT_TIME_OUT, swipe_percent: float = 0.8):
        """
        向下滑动元素

        首先获取locator定位的元素， 并判断该元素是否可滑动，若不可滑动则发出警告信息

        其次，获取x, y, width, height， 根据方向确定start_x, start_y, end_x, end_y

        若swipe_time为None，表示滑动到顶

        :param wait_time: 滑动等待时间

        :param swipe_percent: 滑动比例

        :param swipe_element: 可滑动的元素, 一般情况是android.widget.ListView

        :param timeout: 超时时间， 默认3秒

        :param swipe_time: 滑动次数，默认为None表示滑动到头

        :param locator: 用于定位是否滑动到最后的元素，一般是android.widget.LinearLayout

        :param duration: 持续时间

        """
        self.__client.swipe(swipe_element, locator, duration, SwipeDirectorEnum.DOWN, swipe_time, wait_time, timeout,
                            swipe_percent)

    def swipe_left(self, swipe_element: Union[str, Dict[str, str], WebElement, UiObject],
                   locator: Union[str, Dict[str, str], WebElement, UiObject],
                   duration: float = None, swipe_time: int = None, wait_time: float = None,
                   timeout: float = _DEFAULT_TIME_OUT, swipe_percent: float = 0.8):
        """
        向左滑动元素

        首先获取locator定位的元素， 并判断该元素是否可滑动，若不可滑动则发出警告信息

        其次，获取x, y, width, height， 根据方向确定start_x, start_y, end_x, end_y

        若swipe_time为None，表示滑动到顶

        :param wait_time: 滑动等待时间

        :param swipe_percent: 滑动比例

        :param swipe_element: 可滑动的元素, 一般情况是android.widget.ListView

        :param timeout: 超时时间， 默认3秒

        :param swipe_time: 滑动次数，默认为None表示滑动到头

        :param locator: 用于定位是否滑动到最后的元素，一般是android.widget.LinearLayout

        :param duration: 持续时间

        """
        self.__client.swipe(swipe_element, locator, duration, SwipeDirectorEnum.LEFT, swipe_time, wait_time, timeout,
                            swipe_percent)

    def swipe_right(self, swipe_element: Union[str, Dict[str, str], WebElement, UiObject],
                    locator: Union[str, Dict[str, str], WebElement, UiObject],
                    duration: float = None, swipe_time: int = None, wait_time: float = None,
                    timeout: float = _DEFAULT_TIME_OUT, swipe_percent: float = 0.8):
        """
        向右滑动元素

        首先获取locator定位的元素， 并判断该元素是否可滑动，若不可滑动则发出警告信息

        其次，获取x, y, width, height， 根据方向确定start_x, start_y, end_x, end_y

        若swipe_time为None，表示滑动到顶

        :param wait_time: 滑动等待时间

        :param swipe_percent: 滑动比例

        :param swipe_element: 可滑动的元素, 一般情况是android.widget.ListView

        :param timeout: 超时时间， 默认3秒

        :param swipe_time: 滑动次数，默认为None表示滑动到头

        :param locator: 用于定位是否滑动到最后的元素，一般是android.widget.LinearLayout

        :param duration: 持续时间

        """
        self.__client.swipe(swipe_element, locator, duration, SwipeDirectorEnum.RIGHT, swipe_time, wait_time, timeout,
                            swipe_percent)

    def get_text(self, locator: Union[Dict[str, str], WebElement, UiObject], timeout: float = _DEFAULT_TIME_OUT) -> str:
        """
        获取元素的文本

        :param locator: 定位符

        :param timeout:  超时时间，默认3秒

        :return: element的文本
        """
        return self.__client.get_text(locator, timeout)

    def input_text(self, locator: Union[str, Dict[str, str], WebElement, UiObject], text: str,
                   timeout: float = _DEFAULT_TIME_OUT):
        """
        对指定控件输入文本信息

        :param timeout: 超时时间， 默认3秒

        :param locator:  定位符（只支持字典类型)

        :param text: 要输入的文字
        """
        self.__client.input_text(locator, text, timeout)

    def clear_text(self, locator: Union[str, Dict[str, str], WebElement, UiObject], timeout: float = _DEFAULT_TIME_OUT):
        """
        清空编辑框中的文字

        :param timeout: 超时时间， 默认3秒

        :param locator: 定位符（只支持字典类型)

        """
        self.__client.clear_text(locator, timeout)

    def screen_shot(self, file: str):
        """
        截图到本地文件

        :param file: 要存储的文件
        """
        self.__client.screen_shot(file)

    def get_xml_struct(self) -> str:
        """
        获取xml结构

        :return: xml结构字符串
        """
        return self.__client.get_xml_struct()

    def exist(self, locator: Union[str, Dict[str, str], WebElement, UiObject],
              timeout: float = _DEFAULT_TIME_OUT) -> bool:
        """
        元素是否存在
        :return: 存在/不存在
        """
        try:
            self.__client.get_element(locator, timeout)
            return True
        except NoSuchElementException:
            return False
