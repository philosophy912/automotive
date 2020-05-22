# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, China TSP, All rights reserved
# --------------------------------------------------------
# @Name:        device_enum.py
# @Purpose:     所有设备的枚举类
# @Author:      lizhe
# @Created:     2020/02/05 21:09
# --------------------------------------------------------
from enum import Enum


class DeviceEnum(Enum):
    """
    所有设备的枚举类
    """
    CAMERA = "camera"
    IT6831 = "it6831"
    RELAY = "relay"
    CAN = "can"
    SERIAL = "serial"
    KONSTANTER = "konstanter"

    @staticmethod
    def from_value(value: str):
        """
        从枚举的值获取枚举对象

        :param value: 枚举对象对应的值

        :return: 枚举对象本身
        """
        for key, item in DeviceEnum.__members__.items():
            if value == item.value:
                return item
        raise ValueError(f"{value} can not be found in DeviceEnum")
