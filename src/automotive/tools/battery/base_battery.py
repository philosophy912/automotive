# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, China TSP, All rights reserved
# --------------------------------------------------------
# @Name:        base_battery.py
# @Purpose:     todo
# @Author:      lizhe
# @Created:     2020/05/04 20:20
# --------------------------------------------------------
from abc import abstractmethod, ABCMeta


class BaseBattery(metaclass=ABCMeta):

    @abstractmethod
    def open(self):
        """
        打开设备
        """
        pass

    @abstractmethod
    def close(self):
        """
        关闭设备
        """
        pass
