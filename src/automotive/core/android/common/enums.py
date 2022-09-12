# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2021, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        enums.py
# @Author:      lizhe
# @Created:     2021/11/18 - 22:56
# --------------------------------------------------------
from enum import Enum, unique


@unique
class SwipeDirectorEnum(Enum):
    """
    滑动方向

    支持四个方向
    """
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    UP = "UP"
    DOWN = "DOWN"

    @staticmethod
    def from_name(type_: str):
        for key, item in SwipeDirectorEnum.__members__.items():
            if type_.strip().upper() == item.value.upper():
                return item
        raise ValueError(f"{type_} can not be found in SwipeDirectorEnum")


@unique
class DirectorEnum(Enum):
    """
    点击方式

    支持9个点的点击
    """
    CENTER = "CENTER"
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    TOP = "TOP"
    BOTTOM = "BOTTOM"
    LEFT_TOP = "LEFT_TOP"
    LEFT_BOTTOM = "LEFT_BOTTOM"
    RIGHT_TOP = "RIGHT_TOP"
    RIGHT_BOTTOM = "RIGHT_BOTTOM"

    @staticmethod
    def from_name(type_: str):
        for key, item in DirectorEnum.__members__.items():
            if type_.strip().upper() == item.value.upper():
                return item
        raise ValueError(f"{type_} can not be found in DirectorEnum")


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
            if value.strip().upper() == item.value.upper():
                return item
        raise ValueError(f"{value} can not be found in ElementAttributeEnum")


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
            if value.strip().upper() == item.value.upper():
                return item
        raise ValueError(f"{value} can not be found in ToolTypeEnum")


@unique
class KeyCodeEnum(Enum):
    """
    键盘类型
    """

    KEYCODE_UNKNOWN = 0
    KEYCODE_DPAD_CENTER = 23
    KEYCODE_R = 46
    KEYCODE_MINUS = 69
    KEYCODE_SOFT_LEFT = 1
    KEYCODE_VOLUME_UP = 24
    KEYCODE_S = 47
    KEYCODE_EQUALS = 70
    KEYCODE_SOFT_RIGHT = 2
    KEYCODE_VOLUME_DOWN = 25
    KEYCODE_T = 48
    KEYCODE_LEFT_BRACKET = 71
    KEYCODE_HOME = 3
    KEYCODE_POWER = 26
    KEYCODE_U = 49
    KEYCODE_RIGHT_BRACKET = 72
    KEYCODE_BACK = 4
    KEYCODE_CAMERA = 27
    KEYCODE_V = 50
    KEYCODE_BACKSLASH = 73
    KEYCODE_CALL = 5
    KEYCODE_CLEAR = 28
    KEYCODE_W = 51
    KEYCODE_SEMICOLON = 74
    KEYCODE_ENDCALL = 6
    KEYCODE_A = 29
    KEYCODE_X = 52
    KEYCODE_APOSTROPHE = 75
    KEYCODE_0 = 7
    KEYCODE_B = 30
    KEYCODE_Y = 53
    KEYCODE_SLASH = 76
    KEYCODE_1 = 8
    KEYCODE_C = 31
    KEYCODE_Z = 54
    KEYCODE_AT = 77
    KEYCODE_2 = 9
    KEYCODE_D = 32
    KEYCODE_COMMA = 55
    KEYCODE_NUM = 78
    KEYCODE_3 = 10
    KEYCODE_E = 33
    KEYCODE_PERIOD = 56
    KEYCODE_HEADSETHOOK = 79
    KEYCODE_4 = 11
    KEYCODE_F = 34
    KEYCODE_ALT_LEFT = 57
    KEYCODE_FOCUS = 80
    KEYCODE_5 = 12
    KEYCODE_G = 35
    KEYCODE_ALT_RIGHT = 58
    KEYCODE_PLUS = 81
    KEYCODE_6 = 13
    KEYCODE_H = 36
    KEYCODE_SHIFT_LEFT = 59
    KEYCODE_MENU = 82
    KEYCODE_7 = 14
    KEYCODE_I = 37
    KEYCODE_SHIFT_RIGHT = 60
    KEYCODE_NOTIFICATION = 83
    KEYCODE_8 = 15
    KEYCODE_J = 38
    KEYCODE_TAB = 61
    KEYCODE_SEARCH = 84
    KEYCODE_9 = 16
    KEYCODE_K = 39
    KEYCODE_SPACE = 62
    KEYCODE_MEDIA_PLAY_PAUSE = 85
    KEYCODE_STAR = 17
    KEYCODE_L = 40
    KEYCODE_SYM = 63
    KEYCODE_MEDIA_STOP = 86
    KEYCODE_POUND = 18
    KEYCODE_M = 41
    KEYCODE_EXPLORER = 64
    KEYCODE_MEDIA_NEXT = 87
    KEYCODE_DPAD_UP = 19
    KEYCODE_N = 42
    KEYCODE_ENVELOPE = 65
    KEYCODE_MEDIA_PREVIOUS = 88
    KEYCODE_DPAD_DOWN = 20
    KEYCODE_O = 43
    KEYCODE_ENTER = 66
    KEYCODE_MEDIA_REWIND = 89
    KEYCODE_DPAD_LEFT = 21
    KEYCODE_P = 44
    KEYCODE_DEL = 67
    KEYCODE_MEDIA_FAST_FORWARD = 90
    KEYCODE_DPAD_RIGHT = 22
    KEYCODE_Q = 45
    KEYCODE_GRAVE = 68
    KEYCODE_MUTE = 91
