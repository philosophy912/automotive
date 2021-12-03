# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        singleton.py
# @Author:      lizhe
# @Created:     2021/5/1 - 23:57
# --------------------------------------------------------
from typing import Any, Optional


class Singleton(type):
    """
    单例方法，所有的类要使用则需要继承该类

    目前CANService使用到了单例方法
    """

    def __init__(cls, what, bases: Optional[Any] = None, dict_: Optional[Any] = None):
        """
        初始化Type类
        :param what: 类名
        :param bases: 类所继承的基类
        :param dict_: 类的属性
        """
        super().__init__(what, bases, dict_)
        cls._instance = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance
