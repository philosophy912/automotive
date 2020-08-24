# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, China TSP, All rights reserved
# --------------------------------------------------------
# @Name:        appium_library
# @Purpose:     基于Appium官方的PythonClient开发的库
# @Author:      lizhe
# @Created:     2019/8/21 9:47
# --------------------------------------------------------
import subprocess as sp
import time
from appium import webdriver
from time import sleep
from appium.webdriver.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from appium.webdriver.common.touch_action import TouchAction
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.remote.webelement import WebElement
from loguru import logger
from automotive.utils import Utils
from .adb import ADB
from automotive.core.deprecated import deprecated


@deprecated(class_name="AndroidService")
class AppiumPythonClient(object):
    """
       AppiumPythonClient: 基于Appium的PythonClient进行的封装代码，由于提供了pull/push/install/uninstall的操作，
       所以需要依赖adb utils库

       按照了RobotFramework的appiumLibrary进行了API的定义。

       提供了get_actions提供了appium的action操作，可以利用该对象进行链式操作

    """

    def __init__(self):
        self.__driver = None
        self.__actions = None
        # 开关，用于是否需要打印当前的resource
        self.__debug = False
        self.__utils = Utils()
        self.__adb_utils = ADB()
        self.__attribute = "checkable", "checked", "clickable", "enabled", "focusable", \
                           "focused", "scrollable", "longClickable", "password", "selected"
        self.__locator_list = "resourceid", "classname", "xpath", "text", "description"
        self.__common_list = self.__attribute + self.__locator_list
        self.__position = "left_top", "left_bottom", "right_top", "right_bottom", \
                          "center", "left", "right", "bottom", "top", None
        self.__direct = "up", "down", "left", "right"

    def __get_xpath_text(self, text: str) -> str:
        """
        设置获取的text的xpath地址

        :param text: 要获取的text名字

        :return: xpath的text地址
        """
        self.__utils.is_type_correct(text, str)
        return "//*[@text=\"" + text + "\"]"

    def __get_attribute(self, element: WebElement) -> dict:
        """
        获取控件的属性值

        :param element: 控件

        :return:  字典对象，如{"checkable": True}
        """
        self.__utils.is_type_correct(element, WebElement)
        attr_dict = dict()
        for attr in self.__attribute:
            flag = element.get_attribute(attr)
            logger.debug(f"The {attr} attribute is {flag}")
            if flag == "false":
                attr_dict[attr] = False
            elif flag == "true":
                attr_dict[attr] = True
        return attr_dict

    def __get_scroll_point(self, from_: dict, to_: dict) -> tuple:
        """
        获取起始空间的xy值

        :param from_: 开始的控件

        :param to_: 结束的空间

        :return: 开始滑动的x,y点以及结束的x, y点
        """
        from_ = self.get_webelement(from_)
        to_ = self.get_webelement(to_)
        start_position = from_.location
        from_size = from_.size
        start_x = start_position["x"] + from_size["width"] / 2
        start_y = start_position["y"] + from_size["height"] / 2
        end_position = to_.location
        to_size = to_.size
        end_x = end_position["x"] + to_size["width"] / 2
        end_y = end_position["y"] + to_size["height"] / 2
        return start_x, start_y, end_x, end_y

    def __get_start_end_point(self, element: WebElement, direct: str, swipe_percent: float) -> tuple:
        """
        获取要滑动的位置

        :param element:  支持滚动属性的控件

        :param direct: 滑动的方向，默认为向上滑动['up', 'down', 'left', 'right']

        :param swipe_percent: 滑动的距离占控件的高度比例[0, 1], default =0.8

        :return: start_x, end_x, start_y, end_y
        """
        self.__utils.is_type_correct(element, WebElement)
        if direct not in self.__direct:
            raise ValueError(f"direct{direct} is only support {self.__direct}")
        swipe_percent = self.__get_default_percent(swipe_percent)
        location = element.location
        size = element.size
        logger.debug(f"location {location} : size {size}")
        # 初始化该值
        start_x, end_x, start_y, end_y = 0, 0, 0, 0
        if direct in ("up", "down"):
            start_x = location["x"] + size["width"] / 2
            end_x = start_x
            if direct == "up":
                start_y = location["y"] + size["height"] * swipe_percent - 1
                end_y = location["y"]
            else:
                end_y = location["y"] + size["height"] * swipe_percent - 1
                start_y = location["y"] + 5
        elif direct in ("left", "right"):
            start_y = location["y"] + size["height"] / 2
            end_y = start_y
            if direct == "left":
                start_x = location["x"] + size["width"] * swipe_percent - 1
                end_x = location["x"]
            else:
                end_x = location["x"] + size["width"] * swipe_percent - 1
                start_x = location["x"] + 5
        return start_x, end_x, start_y, end_y

    def __get_element_click_point(self, element: (dict, WebElement), position: str, offset: tuple) -> tuple:
        """
        获取元素点击位置

        :param element: 元素对象

        :param position:  位置

        :param offset: 偏移量

        :return: 点击的绝对位置
        """
        element = self.get_webelement(element)
        if position not in self.__position:
            raise ValueError(f"position{position} is only support {self.__position}")
        location = element.location
        size = element.size
        x, y = 0, 0
        if position == 'left_top':
            x = location['x'] + 5
            y = location['y'] + 5
        elif position == 'left_bottom':
            x = location['x'] + 5
            y = location['y'] + size["height"] - 5
        elif position == "right_top":
            x = location['x'] + size['width'] - 5
            y = location['y'] + 5
        elif position == "right_bottom":
            x = location['x'] + size['width'] - 5
            y = location['y'] + size['height'] - 5
        elif position == "center":
            x = location['x'] + size['width'] // 2
            y = location['y'] + size['height'] // 2
        elif position == "left":
            x = location["x"] + 5
            y = location['y'] + size['height'] // 2
        elif position == "right":
            x = location['x'] + size['width'] - 5
            y = location['y'] + size['height'] // 2
        elif position == "top":
            x = location['x'] + size['width'] // 2
            y = location['y'] + 5
        elif position == "bottom":
            x = location['x'] + size['width'] // 2
            y = location['y'] + size['height'] - 5
        elif position is None:
            x = location["x"] + offset[0]
            y = location["y"] + offset[1]
        return x, y

    def __get_type(self, type_: str) -> (str, By):
        """
        根据类型转换成appium支持的类型

        :param type_:  目前只支持"resourceId", "className", "xpath", "text"

        :return: appium中的By ID、CLASS_NAME、XPATH、NAME四种方式，其中NAME采取的是XPATH的方式解析
        """
        type_ = type_.lower()
        if type_ not in self.__locator_list:
            raise TypeError(f"key [{type_}] is not in {self.__locator_list}")
        if type_ == "resourceid":
            return By.ID
        elif type_ == "classname":
            return By.CLASS_NAME
        elif type_ == "xpath":
            return By.XPATH
        elif type_ == "text":
            return By.NAME
        elif type_ == "description":
            return "description"

    def __get_window_size(self) -> dict:
        """
        获取窗体的高度和宽度

        :return: 窗体的高度和宽度
        """
        return self.__driver.get_window_size()

    @staticmethod
    def __get_default_percent(percent: float) -> float:
        """
        获取滑动的比例，当小与0的时候为0.1，大于1的时候为0.9

        :param percent: 比例

        :return: 比例值
        """
        if percent < 0:
            percent = 0.1
        elif percent > 1:
            percent = 0.9
        return percent

    @staticmethod
    def __get_duration(duration: (int, float)) -> (int, float):
        """
        设置滑动持续时间

        :param duration: 持续时间，转换成ms

        :return: None或者时间
        """
        if duration is not None:
            duration = duration * 1000
        return duration

    def __get_type_value(self, locator: (tuple, dict)) -> tuple:
        """
        将元组或者转换成By的方式，字典或者元组只支持特定格式

        :param locator:
            元组或者字典{"resourceId":"android:id/title"} 或者("resourceId","android:id/title")

        :return: appium中的By ID、CLASS_NAME、XPATH、NAME四种方式，其中NAME采取的是XPATH的方式解析
        """
        self.__utils.is_type_correct(locator, (tuple, dict))
        if isinstance(locator, tuple) and len(locator) == 2:
            logger.info(f"locator{locator} is dict")
            type_ = locator[0]
            value = locator[1]
            return self.__get_type(type_), value
        elif isinstance(locator, dict) and len(locator) == 1:
            type_ = None
            for key in locator.keys():
                type_ = key
            value = locator[type_]
            return self.__get_type(type_), value
        else:
            raise TypeError(locator)

    def __get_swipe_param(self, element: (dict, WebElement), duration: (int, float) = None, direct: str = None,
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
        element = self.get_webelement(element)
        direct = direct.lower()
        if check_scrollable:
            attribute = self.__get_attribute(element)
            logger.debug(f"attribute is {str(attribute)}")
            if attribute["scrollable"] is not True:
                raise ValueError(f"element is not scrollable")
        # 转换时间为毫秒
        duration = self.__get_duration(duration)
        start_x, end_x, start_y, end_y = self.__get_start_end_point(element, direct, swipe_percent)
        return start_x, end_x, start_y, end_y, duration

    def __get_element(self, element: (WebDriver, WebElement), locator: dict) -> WebElement:
        """
        获取指定element下面的locator，用于查找子控件

        :param element: 指定的element

        :param locator: 查找该控件下面的子控件的定位

        :return: 查找到的子控件
        """
        self.__utils.is_type_correct(element, (WebDriver, WebElement))
        if isinstance(locator, dict):
            logger.debug(f"locator{locator} is dict")
            type_, value = self.__get_type_value(locator)
            if type_ == By.NAME:
                logger.debug(f"find element by name={value}")
                xpath = self.__get_xpath_text(value)
                return element.find_element_by_xpath(xpath)
            # 根据Accessibility ID来查找，即uiautomatorviewer中的content-desc
            elif type_ == "description":
                logger.debug(f"find element by description={value}")
                return element.find_element_by_accessibility_id(value)
            else:
                logger.debug(f"find element by {type_} and value is {value}")
                return element.find_element(type_, value)
        else:
            raise TypeError(locator)

    def __get_elements(self, element: (WebDriver, WebElement), locator: dict) -> list:
        """
        获取指定element下面的locator，用于查找子控件

        :param element: 指定的element

        :param locator: 查找该控件下面的子控件的定位

        :param locator: 查找该控件下面的子控件的定位

        :return:查找到的子控件列表
        """
        self.__utils.is_type_correct(element, (WebDriver, WebElement))
        if isinstance(locator, dict):
            logger.info(f"locator{locator} is dict")
            type_, value = self.__get_type_value(locator)
            if type_ == By.NAME:
                xpath = self.__get_xpath_text(value)
                return element.find_elements_by_xpath(xpath)
            # 根据Accessibility ID来查找，即uiautomatorviewer中的content-desc
            elif type_ == "description":
                logger.debug(f"find elements by description={value}")
                return element.find_elements_by_accessibility_id(value)
            else:
                return element.find_elements(type_, value)
        else:
            raise TypeError(locator)

    def __get_ui_selector(self, locator: dict) -> str:
        """
        根据locator来获取selector

        :param locator: 上层传递下来的dict对象

        :return:  Uiautomator方式的字符串
        """
        self.__utils.is_type_correct(locator, dict)
        selector = ""
        for key, value in locator.items():
            if key.lower() not in self.__common_list:
                raise TypeError(f"locator key{key} only support {self.__common_list}")
            elif key == "xpath":
                raise TypeError(f"locator must not include xpath")
            elif key not in self.__attribute:
                selector = selector + "." + key + "(\"" + value + "\")"
            # 如果是属性则表示True|False
            else:
                if not isinstance(value, bool):
                    raise TypeError(f"attribute value must be bool")
                if value:
                    selector = selector + "." + key + "(True)"
                else:
                    selector = selector + "." + key + "(False)"
        # 需要去掉第一个的点[.]
        return selector[1:]

    def __find_element_by_ui_selector(self, locator: dict) -> WebElement:
        """
        根据ui_selector查找对象

        :param locator: 上层传递下来的dict对象

        :return:  查找到的控件
        """
        ui_selector = self.__get_ui_selector(locator)
        logger.debug(f"ui_selector is {ui_selector}")
        return self.__driver.find_element_by_android_uiautomator(ui_selector)

    def __find_elements_by_ui_selector(self, locator: dict) -> list:
        """
        根据ui_selector查找对象

        :param locator: 上层传递下来的dict对象

        :return:  查找到的控件
        """
        ui_selector = self.__get_ui_selector(locator)
        logger.debug(f"ui_selector is {ui_selector}")
        return self.__driver.find_elements_by_android_uiautomator(ui_selector)

    def __find_element_by_locator(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: (float, int),
                                  swipe_time: int, direct: str, locator: dict, text: str = None,
                                  last_element: WebElement = None, exact_match: bool = False) -> (WebElement, None):
        """
        滑动查找控件，当text为None的时候只滑动

        :param start_x: 开始的x

        :param start_y: 开始的y

        :param end_x: 结束的x

        :param end_y: 结束的y

        :param duration: 滑动持续的时间s

        :param swipe_time: 连续滑动的次数

        :param direct: 滑动的方向，默认为向上滑动["up", "down", "left", "right"]

        :param locator: 查找目标的locator

        :param text: 要查找的文本对象

        :param last_element: 滚动空间中最后一个元素

        :param exact_match: 是否精确匹配

        :return: WebElement
        """
        logger.debug(f"text is {text}")
        # 设置滑动次数1000次
        if swipe_time is None:
            swipe_time = 1000
        for time_ in range(swipe_time):
            if time_ > 0:
                logger.debug(f"swipe from {start_x},{start_y} to {end_x}, {end_y}")
                self.__driver.swipe(start_x, start_y, end_x, end_y, duration)
            logger.debug(f"find element by locator{locator}")
            elements = self.get_webelements(locator)
            logger.debug(f"elements size is {len(elements)}")
            if direct in ("up", "right"):
                logger.debug("type is up or right")
                swiped_element = elements[-1].text
            else:
                logger.debug("type is down or left")
                swiped_element = elements[0].text
            logger.debug(f"{time_} 's swiped_element is {swiped_element} and last_element = {last_element}")
            element_list = elements
            # 最后一个没有变化表示已经滑动到头了
            if last_element == swiped_element:
                return None
            else:
                last_element = swiped_element
            # text为None表示只滚动不查找
            if text is not None:
                for e in element_list:
                    if exact_match:
                        if text == e.text:
                            return e
                    else:
                        if text in e.text:
                            return e

    def __swipe_scrollable_element(self, element: (dict, WebElement), duration: (int, float) = None,
                                   direct: str = "up", swipe_time: int = 1, swipe_percent: float = 0.8):
        """
        滑动支持滚动属性的控件，即scrollable属性为True

        :param element: 支持滚动属性的控件

        :param duration: 滑动持续的时间s

        :param direct: 滑动的方向，默认为向上滑动["up", "down", "left", "right"]

        :param swipe_time: 连续滑动的次数

        :param swipe_percent: 滑动的距离占控件的高度比例[0, 1], default =0.8
        """
        self.__utils.is_type_correct(element, (dict, WebElement))
        element = self.get_webelement(element)
        if direct not in self.__direct:
            raise TypeError(f"direct ({direct}) is incorrect")
        start_x, end_x, start_y, end_y, duration = self.__get_swipe_param(element, duration, direct, swipe_percent)
        for t in range(swipe_time):
            self.__driver.swipe(start_x, start_y, end_x, end_y, duration)

    def __swipe_scroll(self, element: (dict, WebElement), locator: dict, direct: str = "up", swipe_time: int = 1000,
                       swipe_percent: float = 0.8, duration: (int, float) = None):
        """
        滑动查找locator所在的位置

        :param element:  支持滚动属性的控件

        :param locator: 查找目标的locator

        :param direct: 滑动的方向，默认为向下滑动['up', 'down', 'left', 'right']

        :param swipe_time: 连续滑动的次数

        :param swipe_percent: 滑动的距离占控件的高度比例[0, 1], default =0.8

        :param duration: 滑动持续的时间s
        """
        if direct not in self.__direct:
            raise TypeError(f"direct ({direct}) is incorrect")
        if swipe_time is None:
            swipe_time = 1000
        start_x, end_x, start_y, end_y, duration = self.__get_swipe_param(element, duration, direct, swipe_percent)
        self.__find_element_by_locator(start_x, start_y, end_x, end_y, duration, swipe_time, direct, locator)

    def __swipe_scroll_find_text(self, element: (dict, WebElement), locator: dict, text: str,
                                 exact_match: bool = False, duration: (int, float) = None, direct: str = "up",
                                 swipe_time: int = None, swipe_percent: float = 0.6) -> WebElement:
        """
        滑动查找text

        :param element:  持滚动属性的控件

        :param locator: 查找目标的locator

        :param text: 文字

        :param exact_match: 精确匹配

        :param duration: 滑动持续的时间s

        :param direct: 滑动的方向，默认为向下滑动['up', 'down', 'left', 'right']

        :param swipe_time: 连续滑动的次数

        :param swipe_percent: 滑动的距离占控件的高度比例[0, 1], default =0.8

        :return: WebElement
        """
        if direct not in ("up", "down", "left", "right"):
            raise TypeError(f"direct ({direct}) is incorrect")
        start_x, end_x, start_y, end_y, duration = self.__get_swipe_param(element, duration, direct, swipe_percent)
        return self.__find_element_by_locator(start_x, start_y, end_x, end_y, duration, swipe_time, direct,
                                              locator, text, exact_match=exact_match)

    def __wait_until_page_contain_element_by_ui_selector(self, locator: dict, timeout: int) -> WebElement:
        """
        等待元素出现，用uiselector方式

        :param locator: 查找目标的locator

        :param timeout: 超时时间

        :return: WebElement
        """
        end_time = time.time() + timeout
        while True:
            value = self.__find_element_by_ui_selector(locator)
            logger.debug(f"value is {value}")
            if value:
                return value
            time.sleep(0.5)
            if time.time() > end_time:
                break
        raise Exception(f"no found locator[{locator}]")

    def __wait_until_page_contain_elements_by_ui_selector(self, locator: dict, timeout: int) -> list:
        """
        等待元素出现，用uiselector方式

        :param locator: 查找目标的locator

        :param timeout: 超时时间

        :return: WebElements
        """
        end_time = time.time() + timeout
        while True:
            value = self.__find_elements_by_ui_selector(locator)
            if value:
                return value
            time.sleep(0.5)
            if time.time() > end_time:
                break
        raise Exception(f"no found locator[{locator}]")

    def __wait_until_page_not_contain_element_by_ui_selector(self, locator: dict, timeout: int):
        """
        等待元素出现，用uiselector方式

        :param locator: 查找目标的locator

        :param timeout: 超时时间
        """
        end_time = time.time() + timeout
        while True:
            value = self.__find_element_by_ui_selector(locator)
            if value:
                raise Exception(f"found locator[{locator}]")
            time.sleep(0.5)
            if time.time() > end_time:
                break

    def __wait_until_page_not_contain_elements_by_ui_selector(self, locator: dict, timeout: int):
        """
        等待元素出现，用uiselector方式

        :param locator: 查找目标的locator

        :param timeout: 超时时间
        """
        end_time = time.time() + timeout
        while True:
            value = self.__find_elements_by_ui_selector(locator)
            if value:
                raise Exception(f"found locator[{locator}]")
            time.sleep(0.5)
            if time.time() > end_time:
                break

    def open_application(self, url: str, **capability):
        """
        设置连接appium，并打开application

        url = "http://localhost:4723/wd/hub"

        settings = {

            "deviceName": "1234567", # device name

            "platformVersion": "8.1.0", # 安卓版本号

            "platformName": "Android", # 平台，支持ios和anorid

            "automationName": "UiAutomator2",  # 安卓使用的类型，uiautomator或者uiautomator2

            "appPackage": "com.chinatsp.settings", # 打开的应用包名

            "appActivity": ".SettingsActivity" # 打开的应用包名

        }

        :param url: appium的URL

        :param capability: 相关配置参数{}，参考appium官网的配置
        """
        self.__driver = webdriver.Remote(url, capability)
        self.__actions = TouchAction(self.__driver)

    def start_application(self, package_name: str, package_activity: str):
        """
        已连接状况下打开application

        :param package_name: app的package

        :param package_activity:  app的activity
        """
        self.__driver.start_activity(package_name, package_activity)

    def close_all_applications(self):
        """
        结束测试（并非关闭所有打开的application)
        """
        self.__driver.quit()

    def get_capability(self):
        """
        获取当前设置设置的capabilities

        :return:  当前的capability，dict对象, 参考open_application中的settings
        """
        return self.__driver.capabilities

    def get_webelement(self, locator: (dict, WebElement)) -> WebElement:
        """
        获取Webelement对象，可以通过resourceId、className、xpath、text四种方式获取。

        如果传入的WebElement对象则直接返回传入的对象

        locator = {"resourceId": "xx.xxx.xxx.xx"}

        :param locator: 定位，目前只支持resourceId、className、xpath、text

        :return: Webelement
        """
        if self.__debug:
            logger.debug(self.get_source())
        if isinstance(locator, dict):
            if len(locator) == 1:
                logger.debug(f"locator{locator} is dict")
                return self.__get_element(self.__driver, locator)
            else:
                return self.__find_element_by_ui_selector(locator)
        elif isinstance(locator, WebElement):
            return locator
        else:
            raise TypeError(locator)

    def get_webelements(self, locator: dict) -> list:
        """
        获取Webelement对象列表，即Webelements，可以通过resourceId、className、xpath、text四种方式获取。

        locator = {"resourceId": "xx.xxx.xxx.xx"}

        :param locator: 定位，目前只支持resourceId、className、xpath、text

        :return: Webelement的列表
        """
        if self.__debug:
            logger.debug(self.get_source())
        if isinstance(locator, dict):
            if len(locator) == 1:
                logger.debug(f"locator{locator} is dict")
                return self.__get_elements(self.__driver, locator)
            else:
                return self.__find_elements_by_ui_selector(locator)
        else:
            raise TypeError(locator)

    def get_driver(self) -> WebDriver:
        """
        获取当前driver对象，方便使用原生的driver方式查找对象，具体使用方法请参考Appium官网

        :return: WebDriver对象
        """
        return self.__driver

    def get_actions(self) -> TouchAction:
        """
        获取当前的action对象，可以使用action方法来做操作，具体使用方法请参考Appium官网

        :return: TouchAction对象
        """
        return self.__actions

    def get_device_id(self):
        """
        获取当前的device id, 如123456

        :return: 当前的device_id
        """
        capability = self.get_capability()
        return capability["deviceName"]

    def wait_until_page_contains_element(self, locator: (dict, tuple), timeout: int = 3):
        """
        在timeout的时间之内等待locator描述的对象被找到


        :param locator: 定位方式

            支持方式： {"resourceId": "com.android.settings:id/title"}

                ("resourceId", "com.android.settings:id/title")

        :param timeout: 超时时间，默认3秒
        """
        if timeout is None:
            timeout = 3
        try:
            # 字典类型，即第一种，长度必须为1
            condition1 = isinstance(locator, dict) and len(locator) == 1
            # 元组类型，即第二种，长度必须为2
            condition2 = isinstance(locator, tuple) and len(locator) == 2
            if condition1 or condition2:
                type_, value = self.__get_type_value(locator)
                logger.debug(f"locator be convert to {type_}, {value}")
                if type_ == By.NAME:
                    xpath = self.__get_xpath_text(value)
                    WebDriverWait(self.__driver, timeout).until(ec.presence_of_element_located((By.XPATH, xpath)))
                else:
                    WebDriverWait(self.__driver, timeout).until(ec.presence_of_element_located((type_, value)))
            else:
                logger.debug(f"using ui selector method to locator {locator}")
                self.__wait_until_page_contain_element_by_ui_selector(locator, timeout)
        except Exception:
            raise ValueError(f"locator {locator} not found")

    def wait_until_page_does_not_contain_element(self, locator: (dict, tuple), timeout: int = 3):
        """
        在timeout的时间之内等待locator描述的对象没有被找到

        :param locator: 定位方式

            支持方式： {"resourceId": "com.android.settings:id/title"}

                ("resourceId", "com.android.settings:id/title")

        :param timeout: 超时时间，默认3秒
        """
        if timeout is None:
            timeout = 3
        try:
            # 字典类型，即第一种，长度必须为1
            condition1 = isinstance(locator, dict) and len(locator) == 1
            # 元组类型，即第二种，长度必须为2
            condition2 = isinstance(locator, tuple) and len(locator) == 2
            if condition1 or condition2:
                type_, value = self.__get_type_value(locator)
                logger.debug(f"locator be convert to {type_}, {value}")
                if type_ == By.NAME:
                    xpath = self.__get_xpath_text(value)
                    WebDriverWait(self.__driver, timeout).until_not(ec.presence_of_element_located((By.XPATH, xpath)))
                else:
                    WebDriverWait(self.__driver, timeout).until_not(ec.presence_of_element_located((type_, value)))
            else:
                logger.debug(f"using ui selector method to locator {locator}")
                self.__wait_until_page_not_contain_element_by_ui_selector(locator, timeout)
        except Exception:
            raise ValueError(f"locator {locator} not found")

    def wait_and_click_element(self, locator: dict, timeout: int):
        """
        在timeout的时间之内出现locator描述的对象被找到就点击

        :param locator: 定位方式

            支持方式： {"resourceId": "com.android.settings:id/title"}

                ("resourceId", "com.android.settings:id/title")

        :param timeout: 等待超时,默认时间3秒
        """
        self.wait_until_page_contains_element(locator, timeout)
        self.get_webelement(locator).click()

    def wait_until_page_contains(self, text: str, timeout: int = 3):
        """
        在timeout的时间之内出现text描述的内容

        :param text: text文字内容

        :param timeout: 超时时间，默认3秒
        """
        self.__utils.is_type_correct(text, str)
        self.wait_until_page_contains_element({"text": text}, timeout)

    def wait_until_page_does_not_contain(self, text: str, timeout: int):
        """
        在timeout的时间之内没有出现text描述的内容

        :param text: text文字内容

        :param timeout: 超时时间，默认3秒
        """
        self.__utils.is_type_correct(text, str)
        self.wait_until_page_does_not_contain_element({"text": text}, timeout)

    def click_element(self, locator: (dict, WebElement)):
        """
        单击Webelement对象, 支持定位方式或者直接传入webelement对象

        :param locator: 定位，目前只支持resourceId、className、xpath、text
        """
        element = self.get_webelement(locator)
        element.click()

    def double_click_element(self, locator: (dict, WebElement), duration: (int, float) = 0.1):
        """
        双击Webelement对象, 支持定位方式或者直接传入webelement对象

        :param locator: 定位，目前只支持resourceId、className、xpath、text

        :param duration:  双击间隔时间，默认0.1秒
        """
        element = self.get_webelement(locator)
        self.click_element(element)
        sleep(duration)
        self.click_element(element)

    def click_text(self, text: str, exact_match: bool = True):
        """
        根据文字找到的Webelement并进行单击。

        :param text:  文字内容

        :param exact_match: 是否精确匹配
        """
        self.__utils.is_type_correct(text, str)
        if exact_match:
            self.click_element({"text": text})
        else:
            logger.error("function is not implements")
            raise AssertionError("function is not implements, do not use this function")

    def click_a_point(self, location: dict, duration: (int, float) = 0.1):
        """
        根据传入的坐标点进行单击（非adb事件点击，而使用appium方式点击)

        :param location: 字典类型

            如：{"x":33,"y":55}

        :param duration: 持续时长，默认100毫秒
        """
        self.__utils.is_type_correct(location, dict)
        x = location["x"]
        y = location["y"]
        logger.debug(f"the point[{x}:{y}] will be click")
        self.__actions.press(x=x, y=y).wait(duration).release().perform()

    def double_click_point(self, location: dict, duration: (int, float) = 0.1):
        """
        根据传入的坐标点进行双击（非adb事件点击，而使用appium方式点击)

        :param location: 字典类型，

            如：{"x":33,"y":55}

        :param duration: 双击间隔时间，默认100毫秒
        """
        self.__utils.is_type_correct(location, dict)
        x = location["x"]
        y = location["y"]
        logger.debug(f"the point[{x}:{y}] will be click")
        self.click_a_point(x, y)
        sleep(duration)
        self.click_a_point(x, y)

    def click_element_at_coordinates(self, element: dict, position: str = None, offset: tuple = (0, 0)):
        """
        点击控件的特定位置，如左上角、右下角或者控件的偏移坐标（相对控件左上角，值为像素个数）

        :param element: 被点击的控件对象

        :param position: 控件上的相对位置

            支持【left, right, bottom, top, leftTop, leftBottom, rightTop, rightBottom, center】

        :param offset: 偏移位置 -> 元组对象

            如：（0, 1)
        """
        position = position.lower()
        if position not in self.__position:
            raise TypeError(
                f"position{position} is must below types (leftTop, leftBottom, rightTop, rightBottom, center)")
        if len(offset) != 2:
            raise TypeError(f"offset{offset} must by only offset_x and offset_y")
        x, y = self.__get_element_click_point(element, position, offset)
        logger.debug(f"the click point is {x}:{y}")
        self.click_a_point(x, y)

    def touch_element(self, locator: (dict, WebElement)):
        """
        单击Webelement对象（采取actions的perform方法进行)

        :param locator: 定位，目前只支持resourceId、className、xpath、text
        """
        element = self.get_webelement(locator)
        self.__actions.tap(element).perform()

    def long_press(self, locator: (dict, WebElement), duration: (int, float) = 1):
        """
        长按某个元素

        :param locator: 定位，目前只支持resourceId、className、xpath、text

        :param duration:  长按持续时间，默认1秒
        """
        element = self.get_webelement(locator)
        duration = self.__get_duration(duration)
        self.__actions.press(element).wait(duration).release().perform()

    def swipe_scrollable_element(self, element: (dict, WebElement), swipe_time: int = 1, direct: str = "up",
                                 duration: (int, float) = None, swipe_percent: float = 0.8):
        """
        滑动可以滑动的列表

        :param element: 可以滑动的控件对象

        :param swipe_time: 需要滑动的次数

        :param direct: 滑动的方向，默认为向上滑动

            支持：['up', 'down', 'left', 'right']

        :param duration: 滑动持续的时间，即滑动的快慢，单位s

        :param swipe_percent: 滑动的距离占控件范围的比例，避免滑动范围过大无法识别，默认0.8
        """
        self.__swipe_scrollable_element(element, duration, direct, swipe_time, swipe_percent)

    def swipe_element(self, from_: dict, to_: dict, duration: (int, float) = None):
        """
        滑动空间（从某一个控件滑动到另外一个控件）

        :param from_:  开始滑动的控件

        :param to_:    结束滑动的空间

        :param duration: 滑动时间（秒）
        """
        duration = self.__get_duration(duration)
        start_x, start_y, end_x, end_y = self.__get_scroll_point(from_, to_)
        logger.info(f"start from {start_x} : {start_y} to scroll to {end_x}: {end_y}")
        self.__driver.swipe(start_x, start_y, end_x, end_y, duration)

    def swipe_up(self, element: (dict, WebElement), duration: (int, float) = None,
                 swipe_time: int = 1, swipe_percent: float = 0.8):
        """
        向上滑动可滑动的空间

        :param element: 可以滑动的控件对象

        :param duration: 滑动持续的时间(秒）

        :param swipe_time: 连续滑动的次数

        :param swipe_percent: 滑动的距离占控件的高度比例[0, 1], default =0.8
        """
        self.__swipe_scrollable_element(element, duration, "up", swipe_time, swipe_percent)

    def swipe_down(self, element: (dict, WebElement), duration: (int, float) = None,
                   swipe_time: int = 1, swipe_percent: float = 0.8):
        """
        向下滑动可滑动的空间

        :param element: 可以滑动的控件对象

        :param duration: 滑动持续的时间(秒）

        :param swipe_time: 连续滑动的次数

        :param swipe_percent: 滑动的距离占控件的高度比例[0, 1], default =0.8
        """
        self.__swipe_scrollable_element(element, duration, "down", swipe_time, swipe_percent)

    def swipe_left(self, element: (dict, WebElement), duration: (int, float) = None,
                   swipe_time: int = 1, swipe_percent: float = 0.8):
        """
        向左滑动可滑动的空间

        :param element: 可以滑动的控件对象

        :param duration: 滑动持续的时间(秒）

        :param swipe_time: 连续滑动的次数

        :param swipe_percent: 滑动的距离占控件的高度比例[0, 1], default =0.8
        """
        self.__swipe_scrollable_element(element, duration, "left", swipe_time, swipe_percent)

    def swipe_right(self, element: (dict, WebElement), duration: (int, float) = None,
                    swipe_time: int = 1, swipe_percent: float = 0.8):
        """
        向右滑动可滑动的空间

        :param element: 可以滑动的控件对象

        :param duration: 滑动持续的时间(秒）

        :param swipe_time: 连续滑动的次数

        :param swipe_percent: 滑动的距离占控件的高度比例[0, 1], default =0.8
        """
        self.__swipe_scrollable_element(element, duration, "right", swipe_time, swipe_percent)

    def swipe_to_top(self, element: (dict, WebElement), locator: dict, swipe_time: int = None,
                     swipe_percent: float = 0.8, duration: (int, float) = None):
        """
        滑动列表到顶部，滑动到开始位置(如果滑动控件本身有问题则会失效)

        :param element: 可以滑动的控件对象

        :param locator: 定位，目前只支持resourceId、className、xpath、text

        :param swipe_time: 连续滑动的次数

        :param swipe_percent: 滑动的距离占控件的高度比例[0, 1], default =0.8

        :param duration: 滑动持续的时间秒
        """
        self.__swipe_scroll(element, locator, "down", swipe_time, swipe_percent, duration)

    def swipe_to_bottom(self, element: (dict, WebElement), locator: dict, swipe_time: int = None,
                        swipe_percent: float = 0.8, duration: (int, float) = None):
        """
        滑动列表到底部，滑动到开始位置(如果滑动控件本身有问题则会失效)

        :param element: 可以滑动的控件对象

        :param locator: 定位，目前只支持resourceId、className、xpath、text

        :param swipe_time: 连续滑动的次数

        :param swipe_percent: 滑动的距离占控件的高度比例[0, 1], default =0.8

        :param duration: 滑动持续的时间秒
        """
        self.__swipe_scroll(element, locator, "up", swipe_time, swipe_percent, duration)

    def swipe_scrollable_element_and_find_text(self, element: (dict, WebElement), locator: dict, text: str,
                                               exact_match: bool = False, duration: (int, float) = None,
                                               direct: str = "up", swipe_time: int = None,
                                               swipe_percent: float = 0.6) -> WebElement:
        """
        滑动查找滚动空间中的text并返回该对象

        :param element: 支持滚动属性的控件

            也可以通过定位方式传入，目前只支持resourceId、className、xpath、text，建议以className方式传入

        :param locator: 定位，目前只支持resourceId、className、xpath、text，建议以className方式传入

        :param text: 要查找的text文字

        :param exact_match: 是否精确查找

        :param duration: 滑动持续的时间秒

        :param direct: 滑动的方向，默认为向下滑动

            支持['up', 'down', 'left', 'right']

        :param swipe_time: 连续滑动的次数

        :param swipe_percent: 滑动的距离占控件的高度比例[0, 1], default =0.6

        :return: text所在的对象
        """
        return self.__swipe_scroll_find_text(element, locator, text, exact_match, duration, direct,
                                             swipe_time, swipe_percent)

    def swipe_scrollable_element_and_click_text(self, element: (dict, WebElement), locator: dict, text: str,
                                                exact_match: bool = False, duration: (int, float) = None,
                                                direct: str = "up", swipe_time: int = None,
                                                swipe_percent: float = 0.6):
        """
        滑动查找滚动空间中的text并单击改对象

        :param element: 支持滚动属性的控件

            也可以通过定位方式传入，目前只支持resourceId、className、xpath、text，建议以className方式传入

        :param locator: 定位，目前只支持resourceId、className、xpath、text，建议以className方式传入

        :param text: 要查找的text文字

        :param exact_match: 是否精确查找

        :param duration: 滑动持续的时间秒

        :param direct: 滑动的方向，默认为向下滑动

            支持['up', 'down', 'left', 'right']

        :param swipe_time: 连续滑动的次数

        :param swipe_percent: 滑动的距离占控件的高度比例[0, 1], default =0.6
        """
        text_element = self.__swipe_scroll_find_text(element, locator, text, exact_match, duration, direct,
                                                     swipe_time, swipe_percent)
        self.click_element(text_element)

    def swipe_by_percent(self, start_percent_x: float, start_percent_y: float, end_percent_x: int, end_percent_y: int,
                         duration: float = 0.1):
        """
        通过百分比滑动（不需要找到滑动控件）

        :param start_percent_x: 开始滑动点在屏幕中x的百分比

        :param start_percent_y: 开始滑动点在屏幕中y的百分比

        :param end_percent_x: 结束滑动点在屏幕中x的百分比

        :param end_percent_y: 结束滑动点在屏幕中y的百分比

        :param duration: 滑动速度，默认为0.1s
        """
        start_percent_x = self.__get_default_percent(start_percent_x)
        start_percent_y = self.__get_default_percent(start_percent_y)
        end_percent_x = self.__get_default_percent(end_percent_x)
        end_percent_y = self.__get_default_percent(end_percent_y)
        duration = self.__get_duration(duration)
        width = self.get_window_width()
        height = self.get_window_height()
        start_x = start_percent_x * width
        end_x = end_percent_x * width
        start_y = start_percent_y * height
        end_y = end_percent_y * height
        offset_x = end_x - start_x
        offset_y = end_y - start_y
        self.swipe(int(start_x), int(start_y), int(offset_x), int(offset_y), duration)

    def swipe(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: (float, int) = None):
        """
        通过坐标点滑动（不需要找到滑动控件）

        :param start_x: 开始滑动位置x轴

        :param start_y: 开始滑动位置y轴

        :param end_x: 结束滑动位置x轴

        :param end_y: 结束滑动位置y轴

        :param duration: 持续时长s
        """
        duration = self.__get_duration(duration)
        self.__driver.swipe(start_x, start_y, end_x, end_y, duration)

    def page_should_contain_element(self, locator: (dict, WebElement)):
        """
        页面中是否包含某个元素，当找不到的时候抛出异常，用于结果判断

        :param locator:  定位，目前只支持resourceId、className、xpath、text
        """
        logger.debug(f"page should contain element in locator {locator}")
        try:
            self.get_webelement(locator)
        except NoSuchElementException:
            raise AssertionError("Page should have contained element '%s' "
                                 "but did not" % locator)
        logger.info(f"Current page contains element '{str(locator)}'.")

    def page_should_contain_element_by_resource(self, resource: dict, check_list: (list, tuple)):
        """
        页面是否包含resource中包含的多个元素
        
        如：resource = {"a": "xxx.xxx.xxx", "b"："xxx.xxx.xxx", "c"："xxx.xxx.xxx"}

        check_list = ["a","b"] 

        :param resource: 顶层的resource

        :param check_list: 判断元素的key列表
        """
        if not isinstance(resource, dict):
            raise TypeError("resource is not dict")
        if not isinstance(check_list, (list, tuple)):
            raise TypeError("checklist is must be list or tuple")
        for check_point in check_list:
            self.page_should_contain_element(resource[check_point])

    def page_should_not_contain_element(self, locator: (dict, WebElement)):
        """
        页面中不包含某个元素

        :param locator: 定位，目前只支持resourceId、className、xpath、text
        """
        try:
            self.get_webelement(locator)
            raise AssertionError("Page should not have contained element '%s'" % locator)
        except NoSuchElementException:
            logger.info(f"Current page not contains element '{str(locator)}'.")

    def page_should_contain_text(self, text: str):
        """
        页面中包含某个text的内容， 精准匹配

        :param text: text内容
        """
        self.__utils.is_type_correct(text, str)
        try:
            self.get_webelement({"text": text})
        except NoSuchElementException:
            raise AssertionError("Page should have contained text '%s' "
                                 "but did not" % text)
        logger.info(f"Current page contains element '{text}'.")

    def page_should_not_contain_text(self, text: str):
        """
        页面中不包含某个text， 精准匹配

        :param text: text内容
        """
        self.__utils.is_type_correct(text, str)
        try:
            self.get_webelement({"text": text})
            raise AssertionError("Page should not have contained text '%s'" % text)
        except NoSuchElementException:
            logger.info(f"Current page does not contains text '{text}'.")

    def get_children_element(self, parent_locator: (dict, WebElement), child_locator: dict) -> WebElement:
        """
        获取父控件中包含的子控件

        :param parent_locator: 父控件的定位， 定位，目前只支持resourceId、className、xpath、text

        :param child_locator:  子控件的定位， 定位，目前只支持resourceId、className、xpath、text

        :return: 查找到的子控件
        """
        parent_locator = self.get_webelement(parent_locator)
        return self.__get_element(parent_locator, child_locator)

    def get_children_elements(self, parent_locator: (dict, WebElement), child_locator: dict) -> list:
        """
        获取父控件中包含的子控件列表

        :param parent_locator: 父控件的定位， 定位，目前只支持resourceId、className、xpath、text

        :param child_locator:  子控件的定位， 定位，目前只支持resourceId、className、xpath、text

        :return: 查找到的子控件列表
        """
        parent = self.get_webelement(parent_locator)
        return self.__get_elements(parent, child_locator)

    def get_element_attribute(self, locator: (dict, WebElement)) -> dict:
        """
        获取locator的属性，以列表的形式返回

        :param locator: 定位，目前只支持resourceId、className、xpath、text

        :return: 支持查找的key为["checkable", "checked", "clickable", "enabled", "focusable",
            "focused", "scrollable", "long-clickable", "password", "selected"]
        """
        element = self.get_webelement(locator)
        return self.__get_attribute(element)

    def get_element_location(self, locator: (dict, WebElement)) -> dict:
        """
        获取对象在页面中的位置

        :param locator:  定位，目前只支持resourceId、className、xpath、text

        :return: 对象在页面中的位置，如{"x":375,"y":485}
        """
        element = self.get_webelement(locator)
        return element.location

    def get_element_size(self, locator: (dict, WebElement)) -> dict:
        """
        获取对象的高度和宽度

        :param locator:  定位，目前只支持resourceId、className、xpath、text

        :return: 对象的高度和宽度，如{"width":375,"height":485}
        """
        element = self.get_webelement(locator)
        return element.size

    def get_text(self, locator: (dict, WebElement)) -> str:
        """
        获取对象的文字内容

        :param locator: 定位，目前只支持resourceId、className、xpath、text

        :return: 该对象的文字内容
        """
        element = self.get_webelement(locator)
        return element.text

    def get_selected(self, locator: (dict, WebElement)) -> str:
        """
        指定的对象是否处于被选择的状态

        :param locator: 定位，目前只支持resourceId、className、xpath、text

        :return:
            True: 已选择
            False：未选择
        """
        attribute = self.get_element_attribute(locator)
        return attribute["selected"]

    def input_text(self, locator: (dict, WebElement), text: str):
        """
        针对指定控件输入文本信息

        :param locator: 定位，目前只支持resourceId、className、xpath、text

        :param text: 要输入的文本信息
        """
        element = self.get_webelement(locator)
        logger.debug(f"element text is {element.text}")
        element.send_keys(text)

    def clear_text(self, locator: (dict, WebElement, str)):
        """
        清空编辑框中的文字

        :param locator:
            定位，目前只支持resourceId、className、xpath、text

            同时也支持直接传入text对应的文本作为Webelement查找的方式
        """
        if isinstance(locator, str):
            element = self.get_webelement({"text": locator})
        else:
            element = self.get_webelement(locator)
        element.clear()

    def get_window_width(self) -> int:
        """
        获取屏幕宽度

        :return: 屏幕宽度
        """
        return self.__get_window_size()["width"]

    def get_window_height(self) -> int:
        """
        获取屏幕高度

        :return: 屏幕高度
        """
        return self.__get_window_size()["height"]

    def get_center_point(self, locator: (dict, WebElement)) -> tuple:
        """
        获取控件的中心点

        :param locator: 定位，目前只支持resourceId、className、xpath、text

        :return: 该控件的中心点(x, y)
        """
        location = self.get_element_location(locator)
        size = self.get_element_size(locator)
        x = location["x"] + size["width"] // 2
        y = location["y"] + size["height"] // 2
        return x, y

    def get_source(self) -> str:
        """
        获取当前页面的xml

        :return: 当前页面的xml(string)
        """
        return self.__driver.page_source

    def get_element_count(self, locator: dict) -> int:
        """
        获取当前页面相同定位条件的控件个数

        :param locator: 定位，目前只支持resourceId、className、xpath、text

        :return: 查找到的控件数量
        """
        elements = self.get_webelements(locator)
        return len(elements)

    def get_screen_status(self) -> bool:
        """
        获取屏幕状态：黑屏或亮屏

        :return:
            True: 亮屏

            False: 黑屏
        """
        device_id = self.get_device_id()
        cmd = f"adb -s {device_id} shell dumpsys widnow policy"
        result = sp.Popen(cmd, stdout=sp.PIPE)
        for line in iter(result.stdout.readline, b''):
            line = line.decode('utf-8')
            if "mScreenOnFully=true" in line:
                return True
            elif "mScreenOnFully=false" in line:
                return False
        result.stdout.close()
        result.wait()
        raise UserWarning("can not get screen on-off status")

    def pull_file(self, remote_address: str, local_address: str) -> bool:
        """
        从Android端拉取文件到本地

        :param remote_address: 手机端的文件地址 如: /sdcard/xxx.apk

        :param local_address:  本地端的路径 如：d:/

        :return:
            True: 成功

            False: 失败
        """
        device_id = self.get_device_id()
        return self.__adb_utils.pull(remote_address, local_address, device_id)

    def push_file(self, local_address: str, remote_address: str):
        """
        从本地把文件推送到服务端

        :param local_address: 本地端的路径 如：d:/a.txt

        :param remote_address: 手机端的文件地址 如: /sdcard/

        :return:
            True: 成功

            False: 失败
        """
        device_id = self.get_device_id()
        self.__adb_utils.push(local_address, remote_address, device_id)

    def install_app(self, local_apk: str):
        """
        把本地文件安装到安卓手机

        :param local_apk: 本地的apk所在的路径

        :return:
            True: 成功

            False: 失败
        """
        device_id = self.get_device_id()
        self.__adb_utils.install(local_apk, device_id)

    def uninstall_app(self, package_name: str, keep_data: bool = False):
        """
        卸载app

        :param package_name: 要卸载的app的包名，必须

        :param keep_data: 是否保存数据和缓存文件，默认不保存

        :return:
            True: 成功

            False: 失败
        """
        device_id = self.get_device_id()
        self.__adb_utils.uninstall(package_name, keep_data, device_id)
