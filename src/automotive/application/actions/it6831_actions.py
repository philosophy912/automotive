# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        it6831_actions.py
# @Author:      lizhe
# @Created:     2021/5/2 - 0:02
# --------------------------------------------------------
from time import sleep
from automotive.logger.logger import logger
from automotive.core.battery.it6831 import IT6831
from automotive.common.api import PowerActions


class It6831Actions(PowerActions):
    """
    IT6831电源操作类
    """

    def __init__(self, port: str, baud_rate: int):
        super().__init__()
        self.__it6831 = None
        self.__port = port.upper()
        self.__baud_rate = baud_rate
        # 默认开启电压
        self.__default_voltage = 12

    def open(self):
        """
        打开it6831
        """
        logger.info("初始化IT6831电源模块")
        self.__it6831 = IT6831(port=self.__port, baud_rate=self.__baud_rate)
        self.__it6831.open()
        logger.info("获取电源状态")
        self.__it6831.get_all_status()
        logger.info(f"*************IT6831电源模块初始化成功*************")
        logger.info("设置电源为远程操控模式")
        self.__it6831.set_power_control_mode()
        sleep(1)
        logger.info("设置电源为状态为打开状态")
        self.__it6831.set_power_output_status()
        sleep(1)
        logger.info("设置电源电压为12V")
        self.__it6831.set_voltage_value(self.__default_voltage)
        sleep(1)

    def close(self):
        """
        关闭IT6831
        """
        logger.info("关闭IT6831连接的串口")
        self.__it6831.close()

    def on(self):
        """
        打开电源，不管之前电压设置的多少伏，默认如果没有调整过电压则为12V
        """
        logger.info(f"设置IT6831电源模式为ON")
        self.__it6831.set_power_output_status(True)

    def off(self):
        """
        关闭电源输出
        """
        logger.info(f"设置IT6831电源模式为OFF")
        self.__it6831.set_power_output_status(False)

    def set_voltage(self, voltage: float):
        """
        设置电源电压电流

        :param voltage: 电压

        :param current: 电流， 默认10A
        """
        if not 0 <= voltage <= 20:
            raise RuntimeError(f"电源只支持0-20V电压，当前要设置的电压为{voltage}")
        logger.info(f"设置电压为{voltage}")
        self.__it6831.set_voltage_value(voltage)

    def set_current(self, current: float):
        """
        设置电源电压电流

        :param current: 电流， 默认10A
        """
        logger.debug(f"设置电流值{current}")
        self.__it6831.set_current_value(current)

    def set_voltage_current(self, voltage: float, current: float = 10):
        """
        设置电源电压电流

        :param voltage: 电压

        :param current: 电流， 默认10A
        """
        if not 0 <= voltage <= 20:
            raise RuntimeError(f"电源只支持0-20V电压，当前要设置的电压为{voltage}")
        logger.debug(f"设置电流值{current}")
        self.__it6831.set_current_value(current)
        logger.info(f"设置电压为{voltage}")
        self.__it6831.set_voltage_value(voltage)

    def change_voltage(self, start: float, end: float, step: float, interval: float = 0.5, current: float = 10):
        """
        调节电压

        :param start: 开始电压

        :param end: 结束电压

        :param step: 调整的步长

        :param interval: 间隔时间，默认0.5秒

        :param current: 电流值， 默认10A

        :return: 永远返回True
        """
        if not (0 <= start <= 20 or 0 <= end <= 20):
            raise RuntimeError(f"电源只支持0-20V电压，当前要设置的起[{start}]始[{end}]电压为超过了范围")
        if start == end:
            raise RuntimeError(f"开始值{start}不能和结束值{end}相同")
        logger.debug("设置电流值")
        self.__it6831.set_current_value(current)
        # 升压过程 如7-9
        if start < end:
            # 开始值+步长对于结束值，直接设置开始和结束
            if start + step > end:
                self.__it6831.set_voltage_value(start)
                self._utils.sleep(interval)
                self.__it6831.set_voltage_value(end)
            else:
                current_voltage = start
                logger.info(f"设置电压为{current_voltage}伏")
                self.__it6831.set_voltage_value(current_voltage)
                while current_voltage < end:
                    logger.info(f"设置电压为{current_voltage}伏")
                    self.__it6831.set_voltage_value(current_voltage)
                    current_voltage += step
                    self._utils.sleep(interval)
                logger.info(f"设置电压为{end}伏")
                self.__it6831.set_voltage_value(end)
        # 降压过程 如9-7
        else:
            if start - step < end:
                self.__it6831.set_voltage_value(start)
                self._utils.sleep(interval)
                self.__it6831.set_voltage_value(end)
            else:
                current_voltage = start
                logger.info(f"设置电压为{current_voltage}伏")
                self.__it6831.set_voltage_value(current_voltage)
                while current_voltage > end:
                    logger.info(f"设置电压为{current_voltage}伏")
                    self.__it6831.set_voltage_value(current_voltage)
                    current_voltage -= step
                    self._utils.sleep(interval)
                logger.info(f"设置电压为{end}伏")
                self.__it6831.set_voltage_value(end)
