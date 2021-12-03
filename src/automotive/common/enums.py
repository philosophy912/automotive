# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2021, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        enums.py
# @Author:      lizhe
# @Created:     2021/11/18 - 22:02
# --------------------------------------------------------
from enum import Enum, unique


@unique
class CompareTypeEnum(Enum):
    """
    图片对比

    亮图、暗图、闪烁
    """
    LIGHT = "light", "亮图"
    DARK = "dark", "暗图"
    BLINK = "blink", "闪烁图"

    @staticmethod
    def from_value(value: str):
        for key, item in CompareTypeEnum.__members__.items():
            if value in item.value:
                return item
        raise ValueError(f"can not cast value{value} to CompareTypeEnum")
