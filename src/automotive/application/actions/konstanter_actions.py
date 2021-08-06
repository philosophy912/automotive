# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        konstanter_actions.py
# @Author:      lizhe
# @Created:     2021/5/2 - 0:02
# --------------------------------------------------------
from typing import List, Tuple

from automotive.logger.logger import logger
from automotive.core.battery.konstanter_control import KonstanterControl
from automotive.common.api import BasePowerAdjustActions


class KonstanterActions(BasePowerAdjustActions):
    """
    konstanter电源操作类
    """

    def __init__(self, port: str, baud_rate: int = 19200):
        super().__init__()
        self.__konstanter = None
        self.__port = port.upper()
        self.__baud_rate = baud_rate

    @property
    def konstanter(self):
        return self.__konstanter

    def open(self):
        """
        打开串口konstanter
        """
        logger.info("初始化konstanter电源模块")
        logger.info(f"打开串口{self.__port}")
        self.__konstanter = KonstanterControl(port=self.__port, baud_rate=self.__baud_rate)
        self.__konstanter.open()
        logger.info("获取电源状态")
        idn = self.__konstanter.get("IDN")
        logger.debug(f"电源状态{idn}")
        if not idn:
            self.__konstanter.close()
            raise RuntimeError(f"获取不到电源状态， 即将关闭串口，释放资源")

    def close(self):
        """
        关闭konstanter
        """
        if self.__konstanter:
            logger.info("关闭konstanter")
            self.__konstanter.close()

    def on(self):
        """
        设置konstanter输出有效
        """
        logger.info(f"设置konstanter电源模式为ON")
        self.__konstanter.output_enable(True)

    def off(self):
        """
        设置konstanter输出无效
        """
        logger.info(f"设置konstanter电源模式为OFF")
        self.__konstanter.output_enable(False)

    def set_voltage(self, voltage: float):
        """
        设置电源电压电流

        :param voltage: 电压
        """
        if not 0 <= voltage <= 20:
            raise RuntimeError(f"电源只支持0-20V电压，当前要设置的电压为{voltage}")
        logger.info(f"设置电压为{voltage}")
        self.__konstanter.set_voltage_current(voltage=voltage)

    def set_current(self, current: float):
        """
        设置电源电压电流

        :param current: 电流
        """
        logger.info(f"设置电流为{current}")
        self.__konstanter.set_voltage_current(current=current)

    def set_voltage_current(self, voltage: float, current: float = 10):
        """
        设置电源电压电流

        :param voltage: 电压

        :param current: 电流，默认电流10A
        """
        if not 0 <= voltage <= 20:
            raise RuntimeError(f"电源只支持0-20V电压，当前要设置的电压为{voltage}")
        logger.info(f"设置电压为{voltage}, 电流为{current}")
        self.__konstanter.set_voltage_current(voltage, current=current)

    def change_voltage(self, start: float, end: float, step: float, interval: float = 0.5, current: float = 10):
        """
        调节电压

        :param start: 开始电压

        :param end: 结束电压

        :param step: 调整的步长

        :param interval: 间隔时间，默认0.5秒

        :param current: 电流值， 默认10A

        :return: 只针对konstanter实际有效
        """
        if not (0 <= start <= 20 or 0 <= end <= 20):
            raise RuntimeError(f"电源只支持0-20V电压，当前要设置的起[{start}]始[{end}]电压为超过了范围")
        if start == end:
            raise RuntimeError(f"开始值{start}不能和结束值{end}相同")
        # 计算总共耗时
        total_time = (int(abs((end - start)) // step) + 1) * interval
        logger.debug(f"total_time = {total_time}")
        logger.debug(f"设置电压初始值为{start}")
        self.__konstanter.set_voltage_current(start, current=current)
        logger.info("正在设置电压到可编程电源")
        start, middle, end = self.__konstanter.set_raise_down(start, end, step, interval, current=current)
        logger.debug(f"from {start} and middle {middle} and end{end}")
        logger.info("开始执行电压变动")
        self.__konstanter.start(start, middle, total_time=total_time)

    def get_current_voltage(self) -> Tuple[float, float]:
        """
        获取当前电流电压值

        :return 当前电压和电流值
        """
        current = self.__konstanter.get("IOUT").split(" ")[-1].replace("+","")
        voltage = self.__konstanter.get("UOUT").split(" ")[-1].replace("+","")
        return float(voltage), float(current)

    def adjust_voltage_by_curve(self, curve: List[float], current: int = 5, interval: float = 0.01):
        """
        按照电压曲线来设置电压

        :param curve: 电压曲线列表（从csv文件中读取的)

        :param current: 最大电流值 (默认5A)

        :param interval 默认间隔时间(10ms)

        :return: 设置是否有效
        """
        logger.debug("设置电压能用")
        self.__konstanter.output_enable()
        logger.debug(f"设置当前电压为起始电压[{curve[0]}]")
        self.__konstanter.set_voltage_current(curve[0])
        start, end = self.__konstanter.set_user_voltages(curve, interval, current)
        self.__konstanter.start(start, end)
