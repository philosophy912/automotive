# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, China TSP, All rights reserved
# --------------------------------------------------------
# @Name:        actions.py
# @Purpose:     onoff测试中相关的所有操作
# @Author:      lizhe
# @Created:     2020/02/05 20:34
# --------------------------------------------------------
from abc import ABCMeta, abstractmethod

from automotive.tools.utils import Utils


class BaseActions(metaclass=ABCMeta):
    """
    操作类的基类，用于统一操作方法
    """

    def __init__(self):
        # 工具类
        self._utils = Utils()

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
