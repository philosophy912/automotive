# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        api.py
# @Author:      lizhe
# @Created:     2021/5/1 - 23:48
# --------------------------------------------------------
import time
from abc import ABCMeta, abstractmethod
from enum import Enum, unique
from typing import Union, Dict, List, Tuple

from appium.webdriver import WebElement
from appium.webdriver.common.touch_action import TouchAction
from appium.webdriver.webdriver import WebDriver
from selenium.common.exceptions import NoSuchElementException
from uiautomator2 import UiObject, Device
from automotive.logger import logger


@unique
class SwipeDirectorEnum(Enum):
    """
    滑动方向

    支持四个方向
    """
    LEFT = 1
    RIGHT = 2
    UP = 3
    DOWN = 4


@unique
class DirectorEnum(Enum):
    """
    点击方式

    支持9个点的点击
    """
    CENTER = 0
    LEFT = 1
    RIGHT = 2
    TOP = 3
    BOTTOM = 4
    LEFT_TOP = 5
    LEFT_BOTTOM = 6
    RIGHT_TOP = 7
    RIGHT_BOTTOM = 8


@unique
class ElementAttributeEnum(Enum):
    """
    元素属性

    CHECKABLE、CHECKED、CLICKABLE、ENABLED、FOCUSABLE、FOCUSED、SCROLLABLE、LONG_CLICKABLE、DISPLAYED、SELECTED
    """
    CHECKABLE = "checkable"
    CHECKED = "checked"
    CLICKABLE = "clickable"
    ENABLED = "enabled"
    FOCUSABLE = "focusable"
    FOCUSED = "focused"
    SCROLLABLE = "scrollable"
    LONG_CLICKABLE = "longClickable"
    DISPLAYED = "displayed"
    SELECTED = "selected"
    TEXT = "text"

    @staticmethod
    def from_value(value: str):
        """
        从枚举的值获取枚举对象

        :param value: 枚举对象对应的值

        :return: 枚举对象本身
        """
        for key, item in ElementAttributeEnum.__members__.items():
            if value.lower() == item.value.lower():
                return item
        raise ValueError(f"{value} can not be found in ElementAttributeEnum")


class BaseAndroid(metaclass=ABCMeta):
    """
    AndroidService类用于构建一个uiautomator2(简称u2)和appium都能够用到的统一接口

    对于操作来说，一定需要等待元素存在。

    对于元素获取来说，也可以设置超时
    """
    _DEFAULT_TIME_OUT = 3

    _LOCATORS = "resourceId", "className", "xpath", "text", "description"

    _UISELECTORS = "text", "textContains", "textMatches", "textStartsWith", \
                   "className", "classNameMatches", \
                   "description", "descriptionContains", "descriptionMatches", "descriptionStartsWith", \
                   "checkable", "checked", "clickable", "longClickable", \
                   "scrollable", "enabled", "focusable", "focused", "selected", \
                   "packageName", "packageNameMatches", \
                   "resourceId", "resourceIdMatches", \
                   "index", "instance"

    _LOWER_LOCATORS = list(map(lambda x: x.lower(), _LOCATORS))

    _LOWER_UISELECTORS = list(map(lambda x: x.lower(), _UISELECTORS))

    def __init__(self):
        self._driver = None
        self._actions = None

    @property
    def actions(self) -> TouchAction:
        return self._actions

    @property
    def driver(self) -> (WebDriver, Device):
        return self._driver

    @abstractmethod
    def connect(self, device_id: str, capability: dict = None, url: str = "http://localhost:4723/wd/hub"):
        """
        连接Android设备

        appium: 连接Android设备并打开app

        u2: 连接Android设备，如果传入了package和activity，则需要打开app，否则不打开app

        eg:
            capability参考url: https://appium.io/docs/en/writing-running-appium/caps/

            capability = {

                "deviceName": "6e29c407d82",  # device name

                "platformVersion": "6.0.1",  # 安卓版本号

                "platformName": "Android",  # 平台，支持ios和android

                "automationName": "UiAutomator2",  # 安卓使用的类型，uiautomator或者uiautomator2

                "appPackage": "com.android.settings",  # 打开的应用包名

                "appActivity": "com.android.settings.MainSettings",  # 打开的应用包名

                "newCommandTimeout": 1800,  # 执行命令超时时间

                "noReset": True,

                "autoLaunch": True

            }

            appium:  connect("6e29c407d82", capability=capability, str="http://localhost:4723/wd/hub")

            u2: connect("6e29c407d82")

        :param url: appium的URL

        :param capability: appium相关的配置参数

        :param device_id 设备编号
        """
        pass

    def disconnect(self):
        """
        断开连接，目前仅把driver置空
        """
        if self._driver:
            self._driver = None
        if self._actions:
            self._actions = None

    @abstractmethod
    def open_app(self, package: str, activity: str):
        """
        打开应用。 由于u2连接的时候不会主动打开application，则需要调用该接口

        u2/appium: 打开某个应用

        eg: open_app(package="com.android.settings", activity="com.android.settings.MainSettings")

        :param package 应用的package

        :param activity 应用的activity
        """
        pass

    @abstractmethod
    def close_app(self, package: str = None):
        """
        关闭应用

        appium: 只能关闭所有应用

        u2: 可以单独关闭某个应用，如果没有填则表示调用app_stop_all方法

        eg:

            close_app(package="com.android.settings") 表示关闭setting这个应用, 仅appium支持

            close_app(package="com.android.settings") 表示关闭所有应用

        :param package: 应用的package
        """
        pass

    @abstractmethod
    def get_element(self, locator: Union[str, Dict[str, str], WebElement, UiObject],
                    timeout: float = _DEFAULT_TIME_OUT) -> Union[WebElement, UiObject]:
        """
        根据定位符获取元素，如果查询到了多个元素，返回查询到的第一个元素

        eg:
            目前支持查找方式为_LOCATORS以及_UISELECTORS定义的方式

            get_element({"resourceId", "com.android.settings:id/title"}) 单一方式定位

            get_element("相机") 同方法 get_element({"text": "相机"}) 文本方式定位

            get_element({"className", "android.widget.ListView"}) 单一方式定位

            get_element({"className", "android.widget.TextView", "text" : "相机"}) 多重方式定位

        :param timeout:  超时时间, 默认3秒

        :param locator:  定位符

        :return:

            appium: 获取的是WebElement对象

            u2: 获取的是UiObject对象
        """
        pass

    @abstractmethod
    def get_elements(self, locator: Union[str, Dict[str, str]],
                     timeout: float = _DEFAULT_TIME_OUT) -> List[Union[WebElement, UiObject]]:
        """
        根据定位符获取元素列表

        eg:
            目前支持查找方式为_LOCATORS以及_UISELECTORS定义的方式

            get_elements({"resourceId", "com.android.settings:id/title"}) 单一方式定位

            get_elements("相机") 同方法 get_element({"text": "相机"}) 文本方式定位

            get_elements({"className", "android.widget.ListView"}) 单一方式定位

            get_elements({"className", "android.widget.TextView", "text" : "相机"}) 多重方式定位

        :param locator:  定位符

        :param timeout:  超时时间, 默认3秒

        :return: 元素列表集合

            appium: 获取的是WebElement对象列表

            u2: 获取的是UiObject对象列表
        """
        pass

    @abstractmethod
    def get_child_element(self, parent: Union[Dict[str, str], WebElement, UiObject],
                          locator: Union[str, Dict[str, str]],
                          timeout: float = _DEFAULT_TIME_OUT) -> Union[WebElement, UiObject]:
        """
        在父元素中查找子元素, 如果查询到了多个元素，返回查询到的第一个元素

        eg:
            get_child_element({"resourceId", "com.android.settings:id/title"}， {"className", "android.widget.ListView"})

        :param parent: 父元素(支持单一或者多重方式定位)

        :param locator: 子元素定位符(支持单一或者多重方式定位)

        :param timeout: 超时时间，默认3秒

        :return:

            appium: 获取的是WebElement对象列表

            u2: 获取的是UiObject对象列表
        """
        pass

    @abstractmethod
    def get_child_elements(self, parent: Union[Dict[str, str], WebElement, UiObject],
                           locator: Union[str, Dict[str, str]],
                           timeout: float = _DEFAULT_TIME_OUT) -> List[Union[WebElement, UiObject]]:
        """
        在父元素中查找子元素列表

        eg:
            get_child_element({"resourceId", "com.android.settings:id/title"}， {"className", "android.widget.ListView"})

        :param parent: 父元素(支持单一或者多重方式定位)

        :param locator: 子元素定位符(支持单一或者多重方式定位)

        :param timeout: 超时时间，默认3秒

        :return: 元素列表集合

            appium: 获取的是WebElement对象列表

            u2: 获取的是UiObject对象列表
        """
        pass

    @abstractmethod
    def get_element_attribute(self, locator: Union[str, Dict[str, str], WebElement, UiObject],
                              timeout: float = _DEFAULT_TIME_OUT) -> Dict[ElementAttributeEnum, bool]:
        """
        获取元素的属性，以列表方式返回

        eg:
            attr = get_element_attribute({"resourceId", "com.android.settings:id/title"}, \

                {"className", "android.widget.ListView"})

            attr = get_element_attribute({"resourceId", "com.android.settings:id/title"})

            attr = get_element_attribute("相机")

            查询元素某一个属性，具体属性请参考ElementAttribute枚举

            scrollable = attr[ElementAttribute.SCROLLABLE]

        :param locator: 子元素定位符

        :param timeout: 超时时间，默认3秒

        :return: 属性字典，键值对

            key: ElementAttribute

            value: bool类型，True or False
        """
        pass

    @abstractmethod
    def scroll_get_element(self, element: Union[Dict[str, str], WebElement, UiObject], locator: dict, text: str,
                           exact_match: bool = True, duration: float = None,
                           direct: SwipeDirectorEnum = SwipeDirectorEnum.UP, swipe_time: int = None,
                           swipe_percent: float = 0.8,
                           timeout: float = _DEFAULT_TIME_OUT, wait_time: int = 1) -> Union[WebElement, UiObject]:
        """
        在可滑动的空间中，查找文字所在的控件

        eg:
            表示向上滑动查找相册, 滑动类型（滑动到底）

            scroll_get_element({"classname": "android.widget.ListView"}, {"classname": "android.widget.TextView"}, \

                "相册")

            表示向上滑动查找相册, 滑动类型（滑动到底）， 滑动方向请参考SwipeDirectorEnum枚举

            scroll_get_element({"classname": "android.widget.ListView"}, {"classname": "android.widget.TextView"}, \

                "相册", direct=SwipeDirectorEnum.DOWN)

            表示向上滑动查找相册，表示只要存在相册这个词就返回控件, 滑动类型（滑动到底）

            scroll_get_element({"classname": "android.widget.ListView"}, {"classname": "android.widget.TextView"}, \

                "相册", exact_match=False)

            表示向上滑动查找相册，表示只要存在相册这个词就返回控件, 滑动类型（滑动到底）

            scroll_get_element({"classname": "android.widget.ListView"}, {"classname": "android.widget.TextView"}, \

                "相册", exact_match=False)

            表示向上滑动查找相册，表示只要存在相册这个词就返回控件, 滑动类型(滑动20次)

            scroll_get_element({"classname": "android.widget.ListView"}, {"classname": "android.widget.TextView"}, \

                "相册", swipe_time=20)

            表示向上滑动查找相册，表示只要存在相册这个词就返回控件, 滑动类型(滑动20次), 表示滑动比例是在element控件范围内的50%

            scroll_get_element({"classname": "android.widget.ListView"}, {"classname": "android.widget.TextView"}, \

                "相册", swipe_time=20, swipe_percent=0.5)

        :param swipe_time: 滑动次数，默认为None，即滑动到头

        :param timeout: 超时时间

        :param text: 行/列控件中要查找的文字

        :param element: 可滑动的控件， 一般来说是classname=android.widget.ListView,即ListView控件

        :param locator: 滑动控件中行/列控件，该子控件一定是存在于element下面且能够查询到多个的控件定位符

            一般来说是一般来说是classname: android.widget.LinearLayout或者是classname: android.widget.TextView

            由于u2的get_elements方法可能获取到重复的元素，更推荐使用TextView定位符

        :param exact_match: 是否精确查找

        :param duration: 滑动持续时间

        :param direct: 滑动方向（默认是向上滑动)

        :param swipe_percent: 滑动的比例

        :param wait_time: 每次滑动等等时间

        :return:

            appium: 获取的是WebElement对象列表

            u2: 获取的是UiObject对象列表
        """
        pass

    @abstractmethod
    def get_location(self, locator: Union[str, Dict[str, str], WebElement, UiObject],
                     timeout: float = _DEFAULT_TIME_OUT) -> Tuple[int, int, int, int]:
        """
        获取元素的位置， 返回了该控件的左上角的坐标点(x, y), 以及控件的宽度和高度

        eg:
            get_location({"classname": "android.widget.ListView"})

            get_location({"resourceId", "com.android.settings:id/title"}, {"classname": "android.widget.ListView"})

        :param timeout: 超时时间

        :param locator: 定位符, 参考get_element中的locator

        :return:

            元素在屏幕中的位置, x, y, width, height
        """
        pass

    @abstractmethod
    def get_device_id(self) -> str:
        """
        获取device id

        :return: device_id
        """
        pass

    @abstractmethod
    def click_if_attribute(self, locator: Union[Tuple[int, int], str, Dict[str, str], WebElement, UiObject],
                           element_attribute: ElementAttributeEnum, status: bool,
                           timeout: float = _DEFAULT_TIME_OUT):
        """
        当被点击的元素状态满足需求的时候则进行点击动作

        :param locator:  元素定位符

        :param element_attribute:  元素属性

        :param status:  要满足的元素属性状态

        :param timeout:  超时时间
        """
        pass

    @abstractmethod
    def click(self, locator: Union[Tuple[int, int], str, Dict[str, str], WebElement, UiObject],
              timeout: float = _DEFAULT_TIME_OUT):
        """
        点击元素的某个位置

        eg:

            click({"resourceId", "com.android.settings:id/title"})

            click({"resourceId", "com.android.settings:id/title"}, {"classname": "android.widget.ListView"})

            click((12, 15))

        :param locator: 定位符

            tuple: 点击x, y坐标(TIPS: 如果直接传入的是X,Y)则后续的偏移不可用

            str: 查找文字并点击，即dict中只指定text元素

            dict: 查找元素并进行点击操作

            WebElement, UiObject: 直接对元素进行点击操作（前者仅适用于appium，后者适用于u2)

        :param timeout: 超时时间， 默认3秒
        """
        pass

    @abstractmethod
    def double_click(self, locator: Union[Tuple[int, int], str, Dict[str, str], WebElement, UiObject],
                     timeout: float = _DEFAULT_TIME_OUT, duration: float = 0.1):
        """
        点击元素的某个位置

         eg:

            double_click({"resourceId", "com.android.settings:id/title"})

            double_click({"resourceId", "com.android.settings:id/title"}, {"classname": "android.widget.ListView"})

            double_click((12, 15))

        :param duration: 两次点击的间隔时间，默认0.1秒

        :param locator: 定位符

            tuple: 点击x, y坐标(TIPS: 如果直接传入的是X,Y)则后续的偏移不可用

            str: 查找文字并点击，即dict中只指定text元素

            dict: 查找元素并进行点击操作

            WebElement, UiObject: 直接对元素进行点击操作（前者仅适用于appium，后者适用于u2)

        :param timeout: 超时时间， 默认3秒
        """
        pass

    @abstractmethod
    def press(self, locator: Union[Tuple[int, int], str, Dict[str, str], WebElement, UiObject], duration: float,
              timeout: float = _DEFAULT_TIME_OUT):
        """
        点击元素的某个位置

        eg:

            press({"resourceId", "com.android.settings:id/title"})

            press({"resourceId", "com.android.settings:id/title"}, {"classname": "android.widget.ListView"})

            press((12, 15))

        :param duration: 两次点击的间隔时间

        :param locator: 定位符

            tuple: 点击x, y坐标(TIPS: 如果直接传入的是X,Y)则后续的偏移不可用

            str: 查找文字并点击，即dict中只指定text元素

            dict: 查找元素并进行点击操作

            WebElement, UiObject: 直接对元素进行点击操作（前者仅适用于appium，后者适用于u2)

        :param timeout: 超时时间， 默认3秒
        """
        pass

    @abstractmethod
    def drag(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: int = 1):
        """
        从某点拖动到某点

        tips:  u2不支持该方法

        eg:

            drag(15, 15, 125, 125)

        :param start_x: 拖动的起始点x坐标

        :param start_y: 拖动的起始点y坐标

        :param end_x: 拖动的结束点x坐标

        :param end_y: 拖动的结束点y坐标

        :param duration: 拖动持续时间
        """
        pass

    @abstractmethod
    def drag_element_to(self, locator1: Union[str, Dict[str, str], WebElement, UiObject],
                        locator2: Union[str, Dict[str, str], WebElement, UiObject],
                        duration: int = 1, timeout: float = _DEFAULT_TIME_OUT):
        """
        从某点拖动到某点

        eg:
            drag_element_to({"resourceId", "com.android.settings:id/title"}, {"classname": "android.widget.ListView"})

            drag_element_to({"resourceId", "com.android.settings:id/title", "classname": "android.widget.ListView"}, \

                {"classname": "android.widget.ListView"})

        :param timeout: 超时时间

        :param locator1: 定位符1

        :param locator2: 定位符2

        :param duration: 拖动持续时间
        """
        pass

    @abstractmethod
    def drag_to(self, locator: Union[str, Dict[str, str], WebElement, UiObject],
                x: int, y: int, duration: int = 1, timeout: float = _DEFAULT_TIME_OUT):
        """
        从某个元素拖动到某点

        eg:
            drag_element_to({"resourceId", "com.android.settings:id/title"}, 125, 125)

            drag_element_to({"resourceId", "com.android.settings:id/title", "classname": "android.widget.ListView"}, \

                125, 125)

        :param timeout: 超时时间

        :param locator: 定位符1

        :param x: 拖动目的地的x

        :param y: 拖动目的地的y

        :param duration: 拖动持续时间

        """
        pass

    @abstractmethod
    def swipe_element(self, from_element: Union[str, Dict[str, str], WebElement, UiObject],
                      to_element: Union[str, Dict[str, str], WebElement, UiObject], duration: float = None,
                      timeout: float = _DEFAULT_TIME_OUT):
        """
        滑动元素从from到to

        eg:
            swipe_element({"resourceId", "com.android.settings:id/title"}, {"classname": "android.widget.ListView"})

            swipe_element({"resourceId", "com.android.settings:id/title", "classname": "android.widget.ListView"}, \

                {"classname": "android.widget.TextView"})

        :param timeout: 超时时间， 默认3秒

        :param from_element: 起始滑动的元素

        :param to_element: 滑动截止的元素

        :param duration: 持续时间
        """
        pass

    @abstractmethod
    def swipe(self, swipe_element: Union[Dict[str, str], WebElement, UiObject], locator: dict, duration: float = None,
              direction: SwipeDirectorEnum = SwipeDirectorEnum.UP, swipe_time: int = None,
              wait_time: float = None, timeout: float = _DEFAULT_TIME_OUT, swipe_percent: float = 0.8):
        """
        滑动元素, 若swipe_time存在的时候，不去检查locator的text属性，即不判断是否到头

        eg:
            在swipe_element控件范围内上滑动到顶

            swipe({"classname": "android.widget.ListView"}, {"classname": "android.widget.TextView"})

            上滑动到顶, 每次滑动后等待2秒

            swipe({"classname": "android.widget.ListView"}, {"classname": "android.widget.TextView"}, wait_time=2)

            上滑动20次（不判定是否滑动到头）

            swipe({"classname": "android.widget.ListView"}, {"classname": "android.widget.TextView"}, swipe_time=20)

            上滑动20次（不判定是否滑动到头）, 滑动比例0.7

            swipe({"classname": "android.widget.ListView"}, {"classname": "android.widget.TextView"}, swipe_percent=0.7)

        :param wait_time: 滑动等待时间

        :param swipe_percent: 滑动比例

        :param swipe_element: 可滑动的元素, 一般情况是android.widget.ListView

        :param timeout: 超时时间， 默认3秒

        :param swipe_time: 滑动次数，默认为None表示滑动到头

        :param locator: 用于定位是否滑动到最后的元素，一般是android.widget.LinearLayout

        :param duration: 持续时间

        :param direction: 方向，只支持UP/DOWN/LEFT/RIGHT四个方向

        """
        pass

    @abstractmethod
    def get_text(self, locator: Union[str, Dict[str, str], WebElement, UiObject],
                 timeout: float = _DEFAULT_TIME_OUT) -> str:
        """
        获取元素的文本

        eg:

            get_text({"classname": "android.widget.ListView"})

            get_text({"text": "相册"})

            get_text("相册")

        :param locator: 定位符

        :param timeout:  超时时间，默认3秒

        :return: element的文本
        """
        pass

    @abstractmethod
    def input_text(self, locator: Union[str, Dict[str, str], WebElement, UiObject], text: str,
                   timeout: float = _DEFAULT_TIME_OUT):
        """
        对指定控件输入文本信息

        eg:

            input_text({"classname": "android.widget.ListView"}, "测试")

            input_text({"text": "相册"}, "测试")

            input_text("相册", "测试")

        :param timeout: 超时时间， 默认3秒

        :param locator:  定位符（只支持字典类型)

        :param text: 要输入的文字
        """
        pass

    @abstractmethod
    def clear_text(self, locator: Union[str, Dict[str, str], WebElement, UiObject], timeout: float = _DEFAULT_TIME_OUT):
        """
        清空编辑框中的文字

        eg:

            clear_text({"classname": "android.widget.ListView"})

            clear_text({"text": "相册"})

            clear_text("相册")

        :param timeout: 超时时间， 默认3秒

        :param locator: 定位符（只支持字典类型)

        """
        pass

    @abstractmethod
    def screen_shot(self, file: str):
        """
        截图到本地文件

        eg:
            screen_shot(r"d:\temp\a.jpg")

        :param file: 要存储的文件
        """
        pass

    @abstractmethod
    def get_xml_struct(self) -> str:
        """
        获取xml结构

        :return: xml结构字符串
        """
        pass

    @staticmethod
    def get_point(start_x: int, start_y: int, width: int, height: int, position: DirectorEnum) -> tuple:
        """
        根据position确定需要点击的范围

        :param start_x 开始的坐标点x

        :param start_y 开始的坐标点y

        :param width 宽度

        :param height 高度

        :param position: 要点击的位置

        :return: 坐标点x, y
        """
        offset = 5
        if position == DirectorEnum.RIGHT:
            x = start_x + width - offset
            y = start_y + height // 2
        elif position == DirectorEnum.LEFT:
            x = start_x + offset
            y = start_y + height // 2
        elif position == DirectorEnum.TOP:
            x = start_x + width // 2
            y = start_y + offset
        elif position == DirectorEnum.BOTTOM:
            x = start_x + width // 2
            y = start_y + height - offset
        elif position == DirectorEnum.LEFT_TOP:
            x = start_x + offset
            y = start_y + offset
        elif position == DirectorEnum.LEFT_BOTTOM:
            x = start_x + offset
            y = start_y + height - offset
        elif position == DirectorEnum.RIGHT_TOP:
            x = start_x + width - offset
            y = start_y + offset
        elif position == DirectorEnum.RIGHT_BOTTOM:
            x = start_x + width - offset
            y = start_y + height - offset
        else:
            x = start_x + width // 2
            y = start_y + height // 2
        return int(x), int(y)

    def __get_last_element_text(self, elements: List[Union[UiObject, WebElement]], direct: SwipeDirectorEnum,
                                timeout: float) -> str:
        """
        获取当前页面中的text

        :param elements: 当前页面中存在的所有element

        :param direct 滑动方向，用于判断element在前还是在后
        """
        edge_element = self._get_edge_element(elements, direct)
        last_text = self._get_element_text(edge_element, timeout)
        if last_text == "":
            edge_element = self._get_edge_element(elements, direct, True)
            return self._get_element_text(edge_element, timeout)
        else:
            return last_text

    @staticmethod
    def _get_edge_element(elements: List[Union[UiObject, WebElement]], direct: SwipeDirectorEnum,
                          second: bool = False) -> Union[UiObject, WebElement]:
        """
        根据方向获取边缘的element

        :param elements: 查找到的边缘的element

        :param direct: 方向

        :return: 边缘的element元素
        """
        if second:
            return elements[-2] if direct in (SwipeDirectorEnum.UP, SwipeDirectorEnum.LEFT) else elements[1]
        else:
            return elements[-1] if direct in (SwipeDirectorEnum.UP, SwipeDirectorEnum.LEFT) else elements[0]

    @staticmethod
    def _get_swipe_point(x: int, y: int, width: int, height: int, direct: SwipeDirectorEnum,
                         swipe_percent: float) -> tuple:
        """
        获取要滑动的位置

        :param x:  支持滚动属性的控件x

        :param y:  支持滚动属性的控件y

        :param width:  支持滚动属性的控件width

        :param height:  支持滚动属性的控件height

        :param direct: 滑动的方向，默认为向上滑动['up', 'down', 'left', 'right']

        :param swipe_percent: 滑动的距离占控件的高度比例[0, 1], default =0.8

        :return: start_x, end_x, start_y, end_y
        """
        if swipe_percent < 0:
            swipe_percent = 0.1
        elif swipe_percent > 1:
            swipe_percent = 0.9
        if direct == SwipeDirectorEnum.UP:
            x1 = x + width / 2
            x2 = x1
            space = height * (1 - swipe_percent) / 2
            y1 = y + height - space
            y2 = y + space
        elif direct == SwipeDirectorEnum.DOWN:
            x2 = x + width / 2
            x1 = x2
            space = height * (1 - swipe_percent) / 2
            y2 = y + height - space
            y1 = y + space
        elif direct == SwipeDirectorEnum.LEFT:
            y1 = y + height / 2
            y2 = y1
            space = width * (1 - swipe_percent) / 2
            x1 = x + width - space
            x2 = x + space
        else:
            y2 = y + height / 2
            y1 = y2
            space = width * (1 - swipe_percent) / 2
            x2 = x + width - space
            x1 = x + space
        logger.debug(f"x1 = {x1}, x2 = {x2}, y1 = {y1}, y2 = {y2}")
        return int(x1), int(y1), int(x2), int(y2)

    def _get_click_point(self, element: WebElement, position: DirectorEnum = DirectorEnum.CENTER) -> tuple:
        """
        根据position确定需要点击的范围

        :param element: 要点击元素对象

        :param position: 要点击的位置

        :return: 坐标点x, y
        """
        start_x, start_y, width, height = self.get_location(element)
        return self.get_point(start_x, start_y, width, height, position)

    def _get_element_location(self, locator: Union[Tuple[str, str], str, Dict[str, str], UiObject, WebElement],
                              director: DirectorEnum, timeout: float):
        """
        获取控件的location的值

        :param locator: 定位符

        :param director: 点击位置

        :param timeout: 超时时间

        :return: x, y
        """
        if not isinstance(locator, (tuple, str, dict, UiObject, WebElement)):
            raise TypeError(f"locator must be type(tuple, str, dict, UiObject)")
        if isinstance(locator, tuple) and len(locator) == 2:
            x, y = locator
        elif isinstance(locator, str):
            element = self.get_element({"text": locator}, timeout)
            x, y = self._get_click_point(element, director)
        else:
            element = self.get_element(locator, timeout)
            x, y = self._get_click_point(element, director)
        return x, y

    def _get_element_text(self, element: Union[WebElement, UiObject], timeout: float) -> str:
        """
        获取当前element元素下面的文本内容

        直接获取element下面的text，当text为空白（"")的时候，则获取TextView中的text值
        {"classname": "android.widget.TextView"}

        :param element: 要查找的element

        :param timeout: 超时时间

        :return: 文本内容
        """
        locator = {"classNameMatches": ".*Text.*"}
        if not isinstance(element, (WebElement, UiObject)):
            raise TypeError(f"element{type(element)} is not support, only support WebElement, UiObject")
        if isinstance(element, WebElement):
            element_text = element.text
        else:
            element_text = element.get_text()
        if element_text == "":
            try:
                if isinstance(element, WebElement):
                    return self.get_child_element(element, locator, timeout).text
                else:
                    return self.get_child_element(element, locator, timeout).get_text()
            except NoSuchElementException:
                return ""
        else:
            return element_text

    def _find_text_in_elements(self, elements: List[Union[WebElement, UiObject]], text: str, exact_match: bool,
                               timeout: float) -> WebElement:
        """
        用于滑动查找文字（若有多个匹配，则返回第一个)

        :param elements: 当前页面中存在的所有element

        :param text: 要查找的文字

        :param exact_match: 是否精确查找

        :return: 查找到的element
        """
        for element in elements:
            element_text = self._get_element_text(element, timeout)
            if exact_match:
                if text == element_text:
                    return element
            else:
                if text in element_text:
                    return element
        raise NoSuchElementException(f"can not found [{text}] when swipe scroll element")

    def _scroll_element(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: float,
                        direct: SwipeDirectorEnum, swipe_element: Union[WebElement, UiObject], locator: dict,
                        text: str = None, exact_match: bool = False, timeout: float = None, swipe_time: int = None,
                        wait_time: float = None) -> Union[WebElement, UiObject]:
        """
        滑动查找控件: 主要用于文本内容的查找


        1、先在swipe_element中查找locator定位的elements

        2、当不存在滑动次数的时候，根据direct的方向来查找边缘的元素所在的text的值

        2.1、 根据方向查询倒数第一个元素或者其元素下面的text值

        2.2、 若倒数第一个元素查不到text元素，即抛出NoSuchElement异常的时候，则查找倒数第二个元素下面的text值

        3、当存在滑动次数的时候，则不做任何查找动作

        4、根据方向进行滑动查找

        5、当超过5分钟的时候还没有找到最后一个元素，则停止查找

        6、当swipe_time存在次数的时候，且有text的时候，表示滑动swipe_time去查找text，当查找到的时候则返回查找到的元素

        7、当text不存在的时候则表示只滑动，不查找，若有swipe_time的时候表示只滑动x次

        8、当text和swipe_time都为空的时候，表示滑动到头。

        9、判定滑动到头标准是根据locator定位的元素中的最后一个元素的text值和每次滑动的text值相同就表示滑动到底了（不考虑网络加载缓慢的问题)

        :param start_x: 开始滑动的点x

        :param start_y: 开始滑动的点y

        :param end_x: 结束滑动的点x

        :param end_y: 结束滑动的点y

        :param duration: 滑动持续的时间s

        :param direct: 滑动的方向

        :param locator: 定位符(ListView中的每一行/列的元素定位符， 一般来说是classname: android.widget.LinearLayout)

        :param text: 要查找的文本对象(即在每一列中查找到的文本对象)

        :param exact_match: 是否精确匹配

        :param swipe_time: 滑动的次数，默认None

        :param wait_time: 滑动后等待的时间

        :return: WebElement
        """
        # 转换时间为毫秒
        duration = duration * 1000 if duration else duration
        # 设置超时时间5分钟，即滑动失效，5分钟没有找到也会退出
        start_time = time.time()
        swipe_time_out = 5 * 60
        if not swipe_time:
            elements = self.get_child_elements(swipe_element, locator, timeout)
            # 获取当前页面最后一个元素的文本内容（可能是子元素的文本)
            last_element_text = self.__get_last_element_text(elements, direct, timeout)
            logger.debug(f"current edge text = {last_element_text}")
            if text:
                try:
                    return self._find_text_in_elements(elements, text, exact_match, timeout)
                except NoSuchElementException:
                    logger.debug(f"swipe and continue find element")
        else:
            last_element_text = None
        # 计数器
        count = 1
        # 滑动标识符
        swipe_flag = True
        while swipe_flag:
            # 超时退出机制
            if time.time() - start_time > swipe_time_out:
                swipe_flag = False
            # 设置了swipe_time的时候生效
            if swipe_time and swipe_time > count:
                swipe_flag = False
            logger.debug(f"swipe from {start_x}, {start_y} to {end_x}, {end_y}")
            self._driver.swipe(start_x, start_y, end_x, end_y, duration)
            if wait_time:
                time.sleep(wait_time)
                logger.trace(f"{self.get_xml_struct()}")
            # 表示没有指定次数
            if not swipe_time:
                # 表示没有找到相关元素
                elements = self.get_child_elements(swipe_element, locator, timeout)
                logger.debug(f"swipe {count} and find elements size is {len(elements)}")
                if text:
                    try:
                        return self._find_text_in_elements(elements, text, exact_match, timeout)
                    except NoSuchElementException:
                        logger.debug(f"swipe and continue find element")
                # 获取当前页面最边缘的元素
                current_last_element_text = self.__get_last_element_text(elements, direct, timeout)
                logger.debug(f"last_text = {last_element_text} and current_text = {current_last_element_text}")
                # 由于存在last_element_text为None的情况，需要判断， 另外也存在last_element_text=""的情况
                if last_element_text and last_element_text != "" and last_element_text == current_last_element_text:
                    swipe_flag = False
                else:
                    # 把当的最后一个元素设置为最后一个元素
                    if current_last_element_text != "":
                        last_element_text = current_last_element_text
            count += 1
        # 当只有查找text的时候才会抛出找不到的异常
        if text:
            raise NoSuchElementException(f"can not found [{text}] when swipe scroll element")

    def _get_swipe_param(self, element: Union[str, Dict[str, str], UiObject, WebElement], direct: SwipeDirectorEnum,
                         duration: float = None,
                         swipe_percent: float = 0.8, check_scrollable: bool = False) -> tuple:
        """
        获取swipe的相关参数

        :param element: 支持滚动属性的控件

        :param duration:  滑动持续的时间s

        :param direct: 滑动的方向，默认为向上滑动["up", "down", "left", "right"]

        :param swipe_percent: 滑动的距离占控件的高度比例[0, 1], default =0.8

        :param check_scrollable: 是否检查空间是scrollable的

        :return: start_x, end_x, start_y, end_y, duration
        """
        element = self.get_element(element)
        if check_scrollable:
            attribute = self.get_element_attribute(element)
            logger.debug(f"attribute is {str(attribute)}")
            if attribute[ElementAttributeEnum.SCROLLABLE] is not True:
                raise ValueError(f"element is not scrollable")
        # 转换时间为毫秒
        duration = duration * 1000 if duration else duration
        x, y, width, height = self.get_location(element)
        start_x, end_x, start_y, end_y = self._get_swipe_point(x, y, width, height, direct, swipe_percent)
        return start_x, end_x, start_y, end_y, duration

    @staticmethod
    def _check_instance(variable, types):
        """
        检查variable是否属于支持的类型中，若不支持，则抛出异常

        :param variable: 变量

        :param types: 类型列表
        """
        if not isinstance(variable, types):
            raise TypeError(f"only support {types} but now is {type(variable)}")

    def _convert_locator(self, locator: Union[str, Dict[str, str]]) -> dict:
        """
        将字符串转换成字典类型，并且将字典的key转换成支持的格式

        :param locator: 定位符

        :return: 定位字典
        """
        if isinstance(locator, str):
            return {"text": locator}
        elif isinstance(locator, dict):
            new_locator = dict()
            for key, item in locator.items():
                lower_key = key.lower().replace("-", "")
                if lower_key in self._LOWER_LOCATORS:
                    key = self._LOCATORS[self._LOWER_LOCATORS.index(lower_key)]
                elif lower_key in self._LOWER_UISELECTORS:
                    key = self._UISELECTORS[self._LOWER_UISELECTORS.index(lower_key)]
                new_locator[key] = item
            return new_locator
        else:
            raise TypeError(f"locator type is not str or dict but [{type(locator)}]")
