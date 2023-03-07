# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        android_service.py
# @Author:      lizhe
# @Created:     2021/5/1 - 23:48
# --------------------------------------------------------
from typing import Optional, Sequence, Union

from appium.webdriver.common.touch_action import TouchAction
from selenium.common.exceptions import NoSuchElementException

from .common.enums import SwipeDirectorEnum, ElementAttributeEnum, ToolTypeEnum
from .common.typehints import Capability, Driver, LocatorElement, Locator, Element, Attributes, ClickPosition
from .uiautomator2_client import UiAutomator2Client
from .appium_client import AppiumClient
from .adb import ADB
from automotive.common.typehints import Position
from automotive.common.singleton import Singleton
from automotive.logger.logger import logger


class AndroidService(metaclass=Singleton):
    """
    Android 测试服务，实现主要的测试方式，同时兼容APPIUM和Uiautomator2两种框架，

    前者当前最流行的开源框架https://github.com/appium/appium，

    后者则为python的自动化测试框架https://github.com/openatx/uiautomator2

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

    android_service 也提供了原生的能力，可以直接调用driver实现, 如:
    android_service = AndroidService(ToolTypeEnum.APPIUM)
    android_service.driver.xxx
    """
    _DEFAULT_TIME_OUT = 3

    def __init__(self, tool_type: Union[ToolTypeEnum, str] = ToolTypeEnum.UIAUTOMATOR2, temp_folder: str = None):
        self.adb = ADB()
        if isinstance(tool_type, str):
            self.__type = ToolTypeEnum.from_value(tool_type)
        else:
            self.__type = tool_type
        if self.__type == ToolTypeEnum.APPIUM:
            self.__client = AppiumClient(temp_folder)
        elif self.__type == ToolTypeEnum.UIAUTOMATOR2:
            self.__client = UiAutomator2Client(temp_folder)
        else:
            raise TypeError(f"{tool_type} not support, only support APPIUM and UIAUTOMATOR2")

    @property
    def actions(self) -> TouchAction:
        if self.__type == ToolTypeEnum.UIAUTOMATOR2:
            raise TypeError(f"uiautomator2 is not support touch action")
        return self.__client.actions

    @property
    def driver(self) -> Driver:
        return self.__client.driver

    def connect(self, device_id: str, capability: Optional[Capability] = None,
                url: str = "http://localhost:4723/wd/hub"):
        """
        连接Android设备

        appium: 连接Android设备并打开app

        u2: 连接Android设备，如果传入了package和activity，则需要打开app，否则不打开app

        :param url: appium的URL

        :param capability: appium相关的配置参数

        :param device_id 设备编号
        """
        self.__client.connect(device_id=device_id, capability=capability, url=url)

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
        self.__client.open_app(package=package, activity=activity)

    def close_app(self, package: str = None):
        """
        关闭应用

        appium: 只能关闭所有应用

        u2: 可以单独关闭某个应用，如果没有填则表示调用app_stop_all方法

        :param package: 应用的package
        """
        self.__client.close_app(package=package)

    def get_element(self, locator: LocatorElement, timeout: float = _DEFAULT_TIME_OUT) -> Element:
        """
        根据定位符获取元素

        :param timeout:  超时时间, 默认3秒

        :param locator:  定位符（只支持字典类型)

        :return:

            appium: 获取的是WebElement对象

            u2: 获取的是UiObject对象
        """
        return self.__client.get_element(locator=locator, timeout=timeout)

    def get_elements(self, locator: Locator, timeout: float = _DEFAULT_TIME_OUT) -> Sequence[Element]:
        """
        根据定位符获取元素列表

        :param locator:  定位符（只支持字典类型)

        :param timeout:  超时时间, 默认3秒

        :return: 元素列表集合

            appium: 获取的是WebElement对象列表

            u2: 获取的是UiObject对象列表
        """
        return self.__client.get_elements(locator=locator, timeout=timeout)

    def get_child_element(self, parent: LocatorElement, locator: Locator,
                          timeout: float = _DEFAULT_TIME_OUT) -> Element:
        """
        在父元素中查找子元素

        :param parent: 父元素

        :param locator: 子元素定位符

        :param timeout: 超时时间，默认3秒

        :return:

            appium: 获取的是WebElement对象列表

            u2: 获取的是UiObject对象列表
        """
        return self.__client.get_child_element(parent=parent, locator=locator, timeout=timeout)

    def get_child_elements(self, parent: LocatorElement, locator: Locator,
                           timeout: float = _DEFAULT_TIME_OUT) -> Sequence[Element]:
        """
        在父元素中查找子元素列表

        :param parent: 父元素

        :param locator: 子元素定位符

        :param timeout: 超时时间，默认3秒

        :return: 元素列表集合

            appium: 获取的是WebElement对象列表

            u2: 获取的是UiObject对象列表
        """
        return self.__client.get_child_elements(parent=parent, locator=locator, timeout=timeout)

    def get_element_attribute(self, locator: LocatorElement,
                              timeout: float = _DEFAULT_TIME_OUT) -> Attributes:
        """
        获取元素的属性，以列表方式返回

        :param locator: 子元素定位符

        :param timeout: 超时时间，默认3秒

        :return: 属性字典，键值对

            key: ElementAttribute

            value: bool类型，True or False
        """
        return self.__client.get_element_attribute(locator=locator, timeout=timeout)

    def is_checkable(self, locator: LocatorElement, timeout: float = _DEFAULT_TIME_OUT) -> bool:
        """
        元素是否可选择

        :param locator: 定位符

        :param timeout: 超时时间

        :return: 是/否
        """
        return self.__client.get_element_attribute(locator=locator, timeout=timeout)[ElementAttributeEnum.CHECKABLE]

    def is_checked(self, locator: LocatorElement, timeout: float = _DEFAULT_TIME_OUT) -> bool:
        """
        元素是否可选中

        :param locator: 定位符

        :param timeout: 超时时间

        :return: 是/否
        """
        return self.__client.get_element_attribute(locator=locator, timeout=timeout)[ElementAttributeEnum.CHECKED]

    def is_clickable(self, locator: LocatorElement, timeout: float = _DEFAULT_TIME_OUT) -> bool:
        """
        元素是否可点击

        :param locator: 定位符

        :param timeout: 超时时间

        :return: 是/否
        """
        return self.__client.get_element_attribute(locator=locator, timeout=timeout)[ElementAttributeEnum.CLICKABLE]

    def is_enable(self, locator: LocatorElement, timeout: float = _DEFAULT_TIME_OUT) -> bool:
        """
        元素是否可用

        :param locator: 定位符

        :param timeout: 超时时间

        :return: 是/否
        """
        return self.__client.get_element_attribute(locator=locator, timeout=timeout)[ElementAttributeEnum.ENABLED]

    def is_focusable(self, locator: LocatorElement, timeout: float = _DEFAULT_TIME_OUT) -> bool:
        """
        元素是否可以存在焦点

        :param locator: 定位符

        :param timeout: 超时时间

        :return: 是/否
        """
        return self.__client.get_element_attribute(locator=locator, timeout=timeout)[ElementAttributeEnum.FOCUSABLE]

    def is_focused(self, locator: LocatorElement, timeout: float = _DEFAULT_TIME_OUT) -> bool:
        """
        元素是否焦点中

        :param locator: 定位符

        :param timeout: 超时时间

        :return: 是/否
        """
        return self.__client.get_element_attribute(locator=locator, timeout=timeout)[ElementAttributeEnum.FOCUSED]

    def is_scrollable(self, locator: LocatorElement, timeout: float = _DEFAULT_TIME_OUT) -> bool:
        """
        元素是否可滑动

        :param locator: 定位符

        :param timeout: 超时时间

        :return: 是/否
        """
        return self.__client.get_element_attribute(locator=locator, timeout=timeout)[ElementAttributeEnum.SCROLLABLE]

    def is_long_clickable(self, locator: LocatorElement, timeout: float = _DEFAULT_TIME_OUT) -> bool:
        """
        元素是否可长按

        :param locator: 定位符

        :param timeout: 超时时间

        :return: 是/否
        """
        return self.__client.get_element_attribute(locator=locator, timeout=timeout)[
            ElementAttributeEnum.LONG_CLICKABLE]

    def is_display(self, locator: LocatorElement, timeout: float = _DEFAULT_TIME_OUT) -> bool:
        """
        元素是否可显示，对于uiautomator2来说，默认可显示，即不准

        :param locator: 定位符

        :param timeout: 超时时间

        :return: 是/否
        """
        return self.__client.get_element_attribute(locator=locator, timeout=timeout)[ElementAttributeEnum.CHECKABLE]

    def is_selected(self, locator: LocatorElement, timeout: float = _DEFAULT_TIME_OUT) -> bool:
        """
        元素是否可选择

        :param locator: 定位符

        :param timeout: 超时时间

        :return: 是/否
        """
        return self.__client.get_element_attribute(locator=locator, timeout=timeout)[ElementAttributeEnum.SELECTED]

    def scroll_get_element(self,
                           element: LocatorElement,
                           locator: Locator,
                           text: str,
                           exact_match: bool = False,
                           duration: Optional[float] = None,
                           direct: Union[SwipeDirectorEnum, str] = SwipeDirectorEnum.UP,
                           swipe_time: Optional[int] = None,
                           swipe_percent: float = 0.8,
                           timeout: float = _DEFAULT_TIME_OUT,
                           wait_time: float = 1) -> Element:
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
        if isinstance(direct, str):
            direct = SwipeDirectorEnum.from_value(direct)
        return self.__client.scroll_get_element(element=element, locator=locator, text=text, exact_match=exact_match,
                                                duration=duration, direct=direct, swipe_time=swipe_time,
                                                swipe_percent=swipe_percent, timeout=timeout, wait_time=wait_time)

    def scroll_get_element_and_click(self,
                                     element: LocatorElement,
                                     locator: Locator,
                                     text: str,
                                     exact_match: bool = False,
                                     duration: Optional[float] = None,
                                     direct: Union[SwipeDirectorEnum, str] = SwipeDirectorEnum.UP,
                                     swipe_time: Optional[int] = None,
                                     swipe_percent: float = 0.8,
                                     timeout: float = _DEFAULT_TIME_OUT,
                                     wait_time: float = 1):
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

        :param wait_time: 滑动等待时间
        """

        self.scroll_get_element(element=element, locator=locator, text=text, exact_match=exact_match,
                                duration=duration, direct=direct, swipe_time=swipe_time,
                                swipe_percent=swipe_percent, timeout=timeout, wait_time=wait_time).click()

    def scroll_up_get_element(self,
                              element: LocatorElement,
                              locator: Locator,
                              text: str,
                              exact_match: bool = False,
                              duration: Optional[float] = None,
                              swipe_time: Optional[int] = None,
                              swipe_percent: float = 0.8,
                              timeout: float = _DEFAULT_TIME_OUT,
                              wait_time: float = 1) -> Element:
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

        :param wait_time: 滑动等待时间

        :return: 查询到的对象
        """
        return self.__client.scroll_get_element(element=element, locator=locator, text=text, exact_match=exact_match,
                                                duration=duration, direct=SwipeDirectorEnum.UP,
                                                swipe_time=swipe_time, swipe_percent=swipe_percent, timeout=timeout,
                                                wait_time=wait_time)

    def scroll_up_get_element_and_click(self,
                                        element: LocatorElement,
                                        locator: Locator,
                                        text: str,
                                        exact_match: bool = False,
                                        duration: Optional[float] = None,
                                        swipe_time: Optional[int] = None,
                                        swipe_percent: float = 0.8,
                                        timeout: float = _DEFAULT_TIME_OUT,
                                        wait_time: float = 1):
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

        :param wait_time: 滑动等待时间
        """
        self.__client.scroll_get_element(element=element, locator=locator, text=text, exact_match=exact_match,
                                         duration=duration, direct=SwipeDirectorEnum.UP,
                                         swipe_time=swipe_time, swipe_percent=swipe_percent, timeout=timeout,
                                         wait_time=wait_time).click()

    def scroll_down_get_element(self,
                                element: LocatorElement,
                                locator: Locator,
                                text: str,
                                exact_match: bool = False,
                                duration: Optional[float] = None,
                                swipe_time: Optional[int] = None,
                                swipe_percent: float = 0.8,
                                timeout: float = _DEFAULT_TIME_OUT,
                                wait_time: float = 1) -> Element:
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

        :param wait_time: 滑动等待时间

        :return: 查询到的对象
        """
        return self.__client.scroll_get_element(element=element, locator=locator, text=text, exact_match=exact_match,
                                                duration=duration, direct=SwipeDirectorEnum.DOWN,
                                                swipe_time=swipe_time, swipe_percent=swipe_percent, timeout=timeout,
                                                wait_time=wait_time)

    def scroll_down_get_element_and_click(self,
                                          element: LocatorElement,
                                          locator: Locator,
                                          text: str,
                                          exact_match: bool = False,
                                          duration: Optional[float] = None,
                                          swipe_time: Optional[int] = None,
                                          swipe_percent: float = 0.8,
                                          timeout: float = _DEFAULT_TIME_OUT,
                                          wait_time: float = 1):
        """
         在可滑动的空间中，向下滑动并查找文字所在的控件，并点击

        :param element: 可滑动的控件

        :param locator: 滑动控件中行/列控件，一般来说是一般来说是classname: android.widget.LinearLayout

        :param text: 行/列控件中要查找的文字

        :param exact_match: 是否精确查找

        :param duration: 滑动持续时间

        :param swipe_time: 滑动次数，默认为None，即滑动到头

        :param swipe_percent: 滑动的比例

        :param wait_time: 滑动等待时间

        :param timeout: 超时时间
        """
        self.__client.scroll_get_element(element=element, locator=locator, text=text, exact_match=exact_match,
                                         duration=duration, direct=SwipeDirectorEnum.DOWN,
                                         swipe_time=swipe_time, swipe_percent=swipe_percent, timeout=timeout,
                                         wait_time=wait_time).click()

    def scroll_left_get_element(self,
                                element: LocatorElement,
                                locator: Locator,
                                text: str,
                                exact_match: bool = False,
                                duration: Optional[float] = None,
                                swipe_time: Optional[int] = None,
                                swipe_percent: float = 0.8,
                                timeout: float = _DEFAULT_TIME_OUT,
                                wait_time: float = 1) -> Element:
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

        :param wait_time: 滑动等待时间

        :return: 查询到的对象
        """
        return self.__client.scroll_get_element(element=element, locator=locator, text=text, exact_match=exact_match,
                                                duration=duration, direct=SwipeDirectorEnum.LEFT,
                                                swipe_time=swipe_time, swipe_percent=swipe_percent, timeout=timeout,
                                                wait_time=wait_time)

    def scroll_left_get_element_and_click(self,
                                          element: LocatorElement,
                                          locator: Locator,
                                          text: str,
                                          exact_match: bool = False,
                                          duration: Optional[float] = None,
                                          swipe_time: Optional[int] = None,
                                          swipe_percent: float = 0.8,
                                          timeout: float = _DEFAULT_TIME_OUT,
                                          wait_time: float = 1):
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

        :param wait_time: 滑动等待时间

        :return: 查询到的对象
        """
        self.__client.scroll_get_element(element=element, locator=locator, text=text, exact_match=exact_match,
                                         duration=duration, direct=SwipeDirectorEnum.LEFT,
                                         swipe_time=swipe_time, swipe_percent=swipe_percent, timeout=timeout,
                                         wait_time=wait_time).click()

    def scroll_right_get_element(self,
                                 element: LocatorElement,
                                 locator: Locator,
                                 text: str,
                                 exact_match: bool = False,
                                 duration: Optional[float] = None,
                                 swipe_time: Optional[int] = None,
                                 swipe_percent: float = 0.8,
                                 timeout: float = _DEFAULT_TIME_OUT,
                                 wait_time: float = 1) -> Element:
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

        :param wait_time: 滑动等待时间

        :return: 查询到的对象
        """
        return self.__client.scroll_get_element(element=element, locator=locator, text=text, exact_match=exact_match,
                                                duration=duration, direct=SwipeDirectorEnum.RIGHT,
                                                swipe_time=swipe_time, swipe_percent=swipe_percent, timeout=timeout,
                                                wait_time=wait_time)

    def scroll_right_get_element_and_click(self,
                                           element: LocatorElement,
                                           locator: Locator,
                                           text: str,
                                           exact_match: bool = False,
                                           duration: Optional[float] = None,
                                           swipe_time: Optional[int] = None,
                                           swipe_percent: float = 0.8,
                                           timeout: float = _DEFAULT_TIME_OUT,
                                           wait_time: float = 1):
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

        :param wait_time: 滑动等待时间

        :return: 查询到的对象
        """
        self.__client.scroll_get_element(element=element, locator=locator, text=text, exact_match=exact_match,
                                         duration=duration, direct=SwipeDirectorEnum.RIGHT,
                                         swipe_time=swipe_time, swipe_percent=swipe_percent, timeout=timeout,
                                         wait_time=wait_time).click()

    def get_location(self, locator: LocatorElement, timeout: float = _DEFAULT_TIME_OUT) -> Position:
        """
        获取元素的位置

        :param timeout: 超时时间

        :param locator: 定位符（只支持字典类型)

        :return:

            元素在屏幕中的位置, x, y, width, height
        """
        return self.__client.get_location(locator=locator, timeout=timeout)

    def get_device_id(self) -> str:
        """
        获取device id

        :return: device_id
        """
        return self.__client.get_device_id()

    def click_if_attributes(self,
                            locator: Union[ClickPosition, LocatorElement],
                            attributes: Attributes,
                            timeout: float = _DEFAULT_TIME_OUT):
        """
        根据多个属性值判断

        :param locator: 定位符

        :param attributes: 属性值字典

        :param timeout: 超时时间
        """
        current_attributes = self.__client.get_element_attribute(locator, timeout)
        flag = True
        for element_attribute, status in attributes.items():
            if current_attributes[element_attribute] != status:
                flag = False
        if flag:
            self.__client.click(locator, timeout)

    def click_if_attribute(self,
                           locator: Union[ClickPosition, LocatorElement],
                           element_attribute: ElementAttributeEnum,
                           status: bool,
                           timeout: float = _DEFAULT_TIME_OUT):
        """
        首先过滤ElementAttributeEnum中的DISPLAYED和TEXT属性
        首先找到这个元素，然后判断属性值是否为Ture和False，当满足属性值等于status， 则点击
        """
        self.__client.click_if_attribute(locator=locator, element_attribute=element_attribute, status=status,
                                         timeout=timeout)

    def click_if_checkable(self,
                           locator: Union[ClickPosition, LocatorElement],
                           status: bool,
                           timeout: float = _DEFAULT_TIME_OUT):
        """
        当定位到的元素状态和status一致的时候，进行点击

        :param locator:  定位符

        :param status: 元素CHECKABLE属性状态

        :param timeout: 超时时间
        """
        self.__client.click_if_attribute(locator, ElementAttributeEnum.CHECKABLE, status, timeout)

    def click_if_checked(self,
                         locator: Union[ClickPosition, LocatorElement],
                         status: bool,
                         timeout: float = _DEFAULT_TIME_OUT):
        """
        当定位到的元素状态和status一致的时候，进行点击

        :param locator:  定位符

        :param status: 元素CHECKABLE属性状态

        :param timeout: 超时时间
        """
        self.__client.click_if_attribute(locator, ElementAttributeEnum.CHECKED, status, timeout)

    def click_if_clickable(self,
                           locator: Union[ClickPosition, LocatorElement],
                           status: bool,
                           timeout: float = _DEFAULT_TIME_OUT):
        """
        当定位到的元素状态和status一致的时候，进行点击

        :param locator:  定位符

        :param status: 元素CHECKABLE属性状态

        :param timeout: 超时时间
        """
        self.__client.click_if_attribute(locator, ElementAttributeEnum.CLICKABLE, status, timeout)

    def click_if_enabled(self,
                         locator: Union[ClickPosition, LocatorElement],
                         status: bool,
                         timeout: float = _DEFAULT_TIME_OUT):
        """
        当定位到的元素状态和status一致的时候，进行点击

        :param locator:  定位符

        :param status: 元素CHECKABLE属性状态

        :param timeout: 超时时间
        """
        self.__client.click_if_attribute(locator, ElementAttributeEnum.ENABLED, status, timeout)

    def click_if_focusable(self,
                           locator: Union[ClickPosition, LocatorElement],
                           status: bool,
                           timeout: float = _DEFAULT_TIME_OUT):
        """
        当定位到的元素状态和status一致的时候，进行点击

        :param locator:  定位符

        :param status: 元素CHECKABLE属性状态

        :param timeout: 超时时间
        """
        self.__client.click_if_attribute(locator, ElementAttributeEnum.FOCUSABLE, status, timeout)

    def click_if_focused(self,
                         locator: Union[ClickPosition, LocatorElement],
                         status: bool,
                         timeout: float = _DEFAULT_TIME_OUT):
        """
        当定位到的元素状态和status一致的时候，进行点击

        :param locator:  定位符

        :param status: 元素CHECKABLE属性状态

        :param timeout: 超时时间
        """
        self.__client.click_if_attribute(locator, ElementAttributeEnum.FOCUSED, status, timeout)

    def click_if_scrollable(self,
                            locator: Union[ClickPosition, LocatorElement],
                            status: bool,
                            timeout: float = _DEFAULT_TIME_OUT):
        """
        当定位到的元素状态和status一致的时候，进行点击

        :param locator:  定位符

        :param status: 元素CHECKABLE属性状态

        :param timeout: 超时时间
        """
        self.__client.click_if_attribute(locator, ElementAttributeEnum.SCROLLABLE, status, timeout)

    def click_if_long_clickable(self,
                                locator: Union[ClickPosition, LocatorElement],
                                status: bool,
                                timeout: float = _DEFAULT_TIME_OUT):
        """
        当定位到的元素状态和status一致的时候，进行点击

        :param locator:  定位符

        :param status: 元素CHECKABLE属性状态

        :param timeout: 超时时间
        """
        self.__client.click_if_attribute(locator, ElementAttributeEnum.LONG_CLICKABLE, status, timeout)

    def click_if_selected(self,
                          locator: Union[ClickPosition, LocatorElement],
                          status: bool,
                          timeout: float = _DEFAULT_TIME_OUT):
        """
        当定位到的元素状态和status一致的时候，进行点击

        :param locator:  定位符

        :param status: 元素CHECKABLE属性状态

        :param timeout: 超时时间
        """
        self.__client.click_if_attribute(locator, ElementAttributeEnum.SELECTED, status, timeout)

    def click(self, locator: Union[ClickPosition, LocatorElement], timeout: float = _DEFAULT_TIME_OUT):
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
        self.__client.click(locator=locator, timeout=timeout)

    def double_click(self,
                     locator: Union[ClickPosition, LocatorElement],
                     timeout: float = _DEFAULT_TIME_OUT,
                     duration: float = 0.1):
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
        self.__client.double_click(locator=locator, timeout=timeout, duration=duration)

    def press(self, locator: Union[ClickPosition, LocatorElement], duration: float, timeout: float = _DEFAULT_TIME_OUT):
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
        self.__client.press(locator=locator, timeout=timeout, duration=duration)

    def drag(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: int = 1):
        """
        从某点拖动到某点

        :param start_x: 拖动的起始点x坐标

        :param start_y: 拖动的起始点y坐标

        :param end_x: 拖动的结束点x坐标

        :param end_y: 拖动的结束点y坐标

        :param duration: 拖动持续时间
        """
        self.__client.drag(start_x=start_x, start_y=start_y, end_x=end_x, end_y=end_y, duration=duration)

    def drag_element_to(self,
                        locator1: LocatorElement,
                        locator2: LocatorElement,
                        duration: int = 1,
                        timeout: float = _DEFAULT_TIME_OUT):
        """
        从某点拖动到某点

        :param timeout: 超时时间

        :param locator1: 定位符1

        :param locator2: 定位符2

        :param duration: 拖动持续时间

        """
        self.__client.drag_element_to(locator1=locator1, locator2=locator2, duration=duration, timeout=timeout)

    def drag_to(self,
                locator: LocatorElement,
                x: int,
                y: int,
                duration: int = 1,
                timeout: float = _DEFAULT_TIME_OUT):
        """
        从某点拖动到某点

        :param timeout: 超时时间

        :param locator: 定位符1

        :param x: 拖动目的地的x

        :param y: 拖动目的地的y

        :param duration: 拖动持续时间
        """
        self.__client.drag_to(locator=locator, x=x, y=y, duration=duration, timeout=timeout)

    def swipe_element(self,
                      from_element: LocatorElement,
                      to_element: LocatorElement,
                      duration: Optional[float] = None,
                      timeout: float = _DEFAULT_TIME_OUT):
        """
        滑动元素从from到to

        :param timeout: 超时时间， 默认3秒

        :param from_element: 起始滑动的元素

        :param to_element: 滑动截止的元素

        :param duration: 持续时间
        """
        self.__client.swipe_element(from_element=from_element, to_element=to_element, duration=duration,
                                    timeout=timeout)

    def swipe(self,
              swipe_element: LocatorElement,
              locator: Locator,
              duration: Optional[float] = None,
              direction: Union[SwipeDirectorEnum, str] = SwipeDirectorEnum.UP,
              swipe_time: Optional[int] = None,
              wait_time: Optional[float] = None,
              timeout: float = _DEFAULT_TIME_OUT,
              swipe_percent: float = 0.8):
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
        if isinstance(direction, str):
            direction = SwipeDirectorEnum.from_name(direction)
        self.__client.swipe(swipe_element=swipe_element, locator=locator, duration=duration, direction=direction,
                            swipe_time=swipe_time, wait_time=wait_time, timeout=timeout, swipe_percent=swipe_percent)

    def swipe_up(self,
                 swipe_element: LocatorElement,
                 locator: Locator,
                 duration: Optional[float] = None,
                 swipe_time: Optional[int] = None,
                 wait_time: Optional[float] = None,
                 timeout: float = _DEFAULT_TIME_OUT,
                 swipe_percent: float = 0.8):
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
        self.__client.swipe(swipe_element=swipe_element, locator=locator, duration=duration,
                            direction=SwipeDirectorEnum.UP, swipe_time=swipe_time, wait_time=wait_time, timeout=timeout,
                            swipe_percent=swipe_percent)

    def swipe_down(self,
                   swipe_element: LocatorElement,
                   locator: Locator,
                   duration: Optional[float] = None,
                   swipe_time: Optional[int] = None,
                   wait_time: Optional[float] = None,
                   timeout: float = _DEFAULT_TIME_OUT,
                   swipe_percent: float = 0.8):
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
        self.__client.swipe(swipe_element=swipe_element, locator=locator, duration=duration,
                            direction=SwipeDirectorEnum.DOWN, swipe_time=swipe_time, wait_time=wait_time,
                            timeout=timeout, swipe_percent=swipe_percent)

    def swipe_left(self,
                   swipe_element: LocatorElement,
                   locator: Locator,
                   duration: Optional[float] = None,
                   swipe_time: Optional[int] = None,
                   wait_time: Optional[float] = None,
                   timeout: float = _DEFAULT_TIME_OUT,
                   swipe_percent: float = 0.8):
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
        self.__client.swipe(swipe_element=swipe_element, locator=locator, duration=duration,
                            direction=SwipeDirectorEnum.LEFT, swipe_time=swipe_time, wait_time=wait_time,
                            timeout=timeout, swipe_percent=swipe_percent)

    def swipe_right(self,
                    swipe_element: LocatorElement,
                    locator: Locator,
                    duration: Optional[float] = None,
                    swipe_time: Optional[int] = None,
                    wait_time: Optional[float] = None,
                    timeout: float = _DEFAULT_TIME_OUT,
                    swipe_percent: float = 0.8):
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
        self.__client.swipe(swipe_element=swipe_element, locator=locator, duration=duration,
                            direction=SwipeDirectorEnum.RIGHT, swipe_time=swipe_time, wait_time=wait_time,
                            timeout=timeout, swipe_percent=swipe_percent)

    def swipe_point(self, start: ClickPosition, end: ClickPosition, swipe_time: int, duration: float):
        """
        滑动点
        :param start: 起点
        :param end: 终点
        :param swipe_time: 滑动次数
        :param duration: 每次滑动持续时间
        """
        self.__client.swipe_point(start_point=start, end_point=end, swipe_time=swipe_time, duration=duration)

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
        self.__client.swipe_in_element(element=element, swipe_time=swipe_time, duration=duration, percent=percent,
                                       director=director)

    def swipe_up_in_element(self, element: LocatorElement, swipe_time: int, duration: float, percent: float = 0.8,
                            director: SwipeDirectorEnum = SwipeDirectorEnum.DOWN):
        """
        滑动可滑动元素
        :param element: 可滑动的元素
        :param percent: 滑动幅度
        :param swipe_time: 滑动次数
        :param duration: 每次滑动持续时间
        :param director:滑动方向
        """
        self.__client.swipe_in_element(element=element, swipe_time=swipe_time, duration=duration, percent=percent,
                                       director=director)

    def swipe_down_in_element(self, element: LocatorElement, swipe_time: int, duration: float, percent: float = 0.8,
                              director: SwipeDirectorEnum = SwipeDirectorEnum.DOWN):
        """
        滑动可滑动元素
        :param element: 可滑动的元素
        :param percent: 滑动幅度
        :param swipe_time: 滑动次数
        :param duration: 每次滑动持续时间
        :param director:滑动方向
        """
        self.__client.swipe_in_element(element=element, swipe_time=swipe_time, duration=duration, percent=percent,
                                       director=director)

    def swipe_left_in_element(self, element: LocatorElement, swipe_time: int, duration: float, percent: float = 0.8,
                              director: SwipeDirectorEnum = SwipeDirectorEnum.LEFT):
        """
        滑动可滑动元素
        :param element: 可滑动的元素
        :param percent: 滑动幅度
        :param swipe_time: 滑动次数
        :param duration: 每次滑动持续时间
        :param director:滑动方向
        """
        self.__client.swipe_in_element(element=element, swipe_time=swipe_time, duration=duration, percent=percent,
                                       director=director)

    def swipe_right_in_element(self, element: LocatorElement, swipe_time: int, duration: float, percent: float = 0.8,
                               director: SwipeDirectorEnum = SwipeDirectorEnum.RIGHT):
        """
        滑动可滑动元素
        :param element: 可滑动的元素
        :param percent: 滑动幅度
        :param swipe_time: 滑动次数
        :param duration: 每次滑动持续时间
        :param director:滑动方向
        """
        self.__client.swipe_in_element(element=element, swipe_time=swipe_time, duration=duration, percent=percent,
                                       director=director)

    def get_text(self, locator: LocatorElement, timeout: float = _DEFAULT_TIME_OUT) -> str:
        """
        获取元素的文本

        :param locator: 定位符

        :param timeout:  超时时间，默认3秒

        :return: element的文本
        """
        return self.__client.get_text(locator=locator, timeout=timeout)

    def input_text(self, locator: LocatorElement, text: str, timeout: float = _DEFAULT_TIME_OUT):
        """
        对指定控件输入文本信息

        :param timeout: 超时时间， 默认3秒

        :param locator:  定位符（只支持字典类型)

        :param text: 要输入的文字
        """
        self.__client.input_text(locator=locator, text=text, timeout=timeout)

    def clear_text(self, locator: LocatorElement, timeout: float = _DEFAULT_TIME_OUT):
        """
        清空编辑框中的文字

        :param timeout: 超时时间， 默认3秒

        :param locator: 定位符（只支持字典类型)

        """
        self.__client.clear_text(locator=locator, timeout=timeout)

    def screen_shot(self, file: str):
        """
        截图到本地文件

        :param file: 要存储的文件
        """
        self.__client.screen_shot(file=file)

    def get_xml_struct(self) -> str:
        """
        获取xml结构

        :return: xml结构字符串
        """
        return self.__client.get_xml_struct()

    def exist(self, locator: LocatorElement, timeout: float = _DEFAULT_TIME_OUT) -> bool:
        """
        元素是否存在
        :return: 存在/不存在
        """
        try:
            self.__client.get_element(locator=locator, timeout=timeout)
            return True
        except NoSuchElementException:
            return False

    def slide_to_top(self, swipe_element: LocatorElement,
                     locator: Locator,
                     duration: Optional[float] = None,
                     wait_time: Optional[float] = None,
                     timeout: float = _DEFAULT_TIME_OUT,
                     swipe_percent: float = 0.8
                     ):
        """
        滑动到顶
        :return:
        """
        self.__client.slide_to_top(swipe_element=swipe_element,
                                   locator=locator,
                                   duration=duration,
                                   wait_time=wait_time,
                                   timeout=timeout,
                                   swipe_percent=swipe_percent)

    def slide_to_bottom(self, swipe_element: LocatorElement,
                        locator: Locator,
                        duration: Optional[float] = None,
                        wait_time: Optional[float] = None,
                        timeout: float = _DEFAULT_TIME_OUT,
                        swipe_percent: float = 0.8
                        ):
        """
        滑动到底
        :return:
        """
        self.__client.slide_to_bottom(swipe_element=swipe_element,
                                      locator=locator,
                                      duration=duration,
                                      wait_time=wait_time,
                                      timeout=timeout,
                                      swipe_percent=swipe_percent)

    def slide_to_left(self, swipe_element: LocatorElement,
                      locator: Locator,
                      duration: Optional[float] = None,
                      wait_time: Optional[float] = None,
                      timeout: float = _DEFAULT_TIME_OUT,
                      swipe_percent: float = 0.8):
        """
        滑动到左
        :return:
        """
        self.__client.slide_to_leftmost(swipe_element=swipe_element,
                                        locator=locator,
                                        duration=duration,
                                        wait_time=wait_time,
                                        timeout=timeout,
                                        swipe_percent=swipe_percent)

    def slide_to_right(self, swipe_element: LocatorElement,
                       locator: Locator,
                       duration: Optional[float] = None,
                       wait_time: Optional[float] = None,
                       timeout: float = _DEFAULT_TIME_OUT,
                       swipe_percent: float = 0.8):
        """
        滑动到右
        :return:
        """
        self.__client.slide_to_rightmost(swipe_element=swipe_element,
                                         locator=locator,
                                         duration=duration,
                                         wait_time=wait_time,
                                         timeout=timeout,
                                         swipe_percent=swipe_percent)

    def slide_up_times(self, swipe_element: LocatorElement,
                       swipe_time: int,
                       duration: Optional[float] = None,
                       wait_time: Optional[float] = None,
                       timeout: float = _DEFAULT_TIME_OUT,
                       swipe_percent: float = 0.8):
        """
        向上滑动x次
        :return:
        """
        self.__client.slide_up_times(swipe_element=swipe_element,
                                     swipe_time=swipe_time,
                                     duration=duration,
                                     wait_time=wait_time,
                                     timeout=timeout,
                                     swipe_percent=swipe_percent)

    def slide_down_times(self, swipe_element: LocatorElement,
                         swipe_time: int,
                         duration: Optional[float] = None,
                         wait_time: Optional[float] = None,
                         timeout: float = _DEFAULT_TIME_OUT,
                         swipe_percent: float = 0.8):
        """
        向上滑动x次
        :return:
        """
        self.__client.slide_down_times(swipe_element=swipe_element,
                                       swipe_time=swipe_time,
                                       duration=duration,
                                       wait_time=wait_time,
                                       timeout=timeout,
                                       swipe_percent=swipe_percent)

    def slide_left_times(self, swipe_element: LocatorElement,
                         swipe_time: int,
                         duration: Optional[float] = None,
                         wait_time: Optional[float] = None,
                         timeout: float = _DEFAULT_TIME_OUT,
                         swipe_percent: float = 0.8):
        """
        向上滑动x次
        :return:
        """
        self.__client.slide_left_times(swipe_element=swipe_element,
                                       swipe_time=swipe_time,
                                       duration=duration,
                                       wait_time=wait_time,
                                       timeout=timeout,
                                       swipe_percent=swipe_percent)

    def slide_right_times(self, swipe_element: LocatorElement,
                          swipe_time: int,
                          duration: Optional[float] = None,
                          wait_time: Optional[float] = None,
                          timeout: float = _DEFAULT_TIME_OUT,
                          swipe_percent: float = 0.8):
        """
        向上滑动x次
        :return:
        """
        self.__client.slide_right_times(swipe_element=swipe_element,
                                        swipe_time=swipe_time,
                                        duration=duration,
                                        wait_time=wait_time,
                                        timeout=timeout,
                                        swipe_percent=swipe_percent)

    def click_by_image(self, small_img: str, big_img: str):
        """
        通过图像单击坐标点
        :return:
        """
        self.__client.click_by_images(small_image=small_img, big_image=big_img)

    def double_click_by_image(self, small_image: str, big_image: str):
        """
        通过图像双击坐标点
        :return:
        """
        self.__client.double_click_by_image(small_image=small_image, big_image=big_image)

    def press_by_image(self, small_image: str, big_image: str, duration: float = 0.5):
        """
        通过图像长按坐标点
        :return:
        """
        self.__client.press_by_image(small_image=small_image, big_image=big_image, duration=duration)

    def exist_by_locator(self, locator: LocatorElement, timeout: float = _DEFAULT_TIME_OUT):
        """
        元素是否存在
        :return: 存在/不存在
        """
        try:
            self.__client.get_element(locator=locator, timeout=timeout)
            return True
        except NoSuchElementException:
            return False

    def exist_by_image(self, small_image: str, big_image: str):
        """
        根据截图判定是否存在
        :return:
        """
        result = self.__client.exist_by_image(small_image=small_image, big_image=big_image)
        return result
