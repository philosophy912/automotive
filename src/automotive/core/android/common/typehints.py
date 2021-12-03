# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        typehints.py
# @Author:      lizhe
# @Created:     2021/11/19 - 9:35
# --------------------------------------------------------
from typing import Dict, Union, Tuple
from appium.webdriver.webdriver import WebDriver
from uiautomator2 import UiObject, Device
from appium.webdriver import WebElement

from automotive.core.android.common.enums import ElementAttributeEnum

Capability = Dict[str, Union[str, int, bool]]
Driver = Union[WebDriver, Device]
Element = Union[WebElement, UiObject]
Locator = Dict[str, str]
#  str 文本定位， LocatorBy 属性定位
LocatorElement = Union[str, Locator, WebElement, UiObject]
ClickPosition = Tuple[int, int]
Attributes = Dict[ElementAttributeEnum, bool]
SwipeParam = Tuple[int, int, int, int, float]
AppiumLocatorElement = Union[str, Locator, WebElement]
U2LocatorElement = Union[str, Locator, UiObject]
