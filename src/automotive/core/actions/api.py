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
from automotive.utils.utils import Utils


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


class PowerActions(BaseActions):
    """
    电源相关的操作类，用于统一接口
    """

    def __init__(self):
        super().__init__()

    @abstractmethod
    def on(self):
        """
        打开设备
        """
        pass

    @abstractmethod
    def off(self):
        """
        关闭设备
        """
        pass

    @abstractmethod
    def set_voltage_current(self, voltage: float, current: float = 10):
        """
        设置电源电压电流

        :param voltage: 电压

        :param current: 电流
        """
        pass

    @abstractmethod
    def change_voltage(self, start: float, end: float, step: float, interval: float = 0.5, current: float = 10):
        """
        调节电压

        :param start: 开始电压

        :param end: 结束电压

        :param step: 调整的步长

        :param interval: 间隔时间，默认0.5秒

        :param current: 电流值， 默认10A

        :return: 只针对konstanter实际有效，对IT6831电源则永远返回True
        """
        pass
