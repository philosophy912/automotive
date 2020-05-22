# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, China TSP, All rights reserved
# --------------------------------------------------------
# @Name:        can_actions.py
# @Purpose:     CAN设备操作
# @Author:      lizhe
# @Created:     2020/02/05 21:33
# --------------------------------------------------------
from time import sleep
from loguru import logger
from automotive.can import CANService
from .base_actions import BaseActions


class CanActions(BaseActions):
    """
    CAN盒操作类
    """

    def __init__(self, messages: dict):
        super().__init__()
        self.__can = None
        self.__messages = messages

    def open(self):
        """
        打开can
        """
        logger.info("初始化CAN模块")
        self.__can = CANService(self.__messages)
        self.__can.open_can()
        logger.info(f"*************CAN模块初始化成功*************")

    def close(self):
        """
        关闭can
        """
        logger.info("关闭CAN盒子")
        self.__can.close_can()

    def reverse_on(self, signal: list):
        """
        发送倒档信号

        :param signal: signal配置 如 [0x150, "signal_name", 0x1]
        """
        logger.info(f"发送倒档信号")
        msg = signal[0]
        signal_name = signal[1]
        signal_value = signal[2]
        logger.info(f"发送msg为[{msg}],signal名字为[{signal_name}]，值为[{signal_value}]到CAN总线")
        self.__can.send_can_signal_message(msg, {signal_name, signal_value})

    def reverse_off(self, signal: list):
        """
        发送空挡信号

        :param signal: signal配置 如 [0x150, "signal_name", 0x1]
        """
        logger.info(f"发送空档信号")
        msg = signal[0]
        signal_name = signal[1]
        signal_value = signal[2]
        logger.info(f"发送msg为[{msg}],signal名字为[{signal_name}]，值为[{signal_value}]到CAN总线")
        self.__can.send_can_signal_message(msg, {signal_name, signal_value})

    def check_can_available(self, continue_time: int = 5) -> bool:
        """
        判断can消息是否存活

        :param continue_time: 持续监测时间，默认5秒

        :return:
            True: CAN总线正常

            False: CAN总线异常
        """
        return self.__can.is_can_bus_lost(continue_time)

    def bus_sleep(self, event: list):
        """
        整车休眠

        :param event: event配置 如 [0x150, "signal_name", 0x1, 5], 其中5代表持续时间
        """
        if event is None:
            raise RuntimeError(f"请输入正确的进入休眠的事件信息")
        logger.debug("开始发送CAN信号")
        self.__can.send(event[0], {event[1]: event[2]})
        sleep(event[3])
        logger.debug("避免出现倒档信号发送了没有停止，这个地方停止所有信号发送")
        self.__can.stop_all_messages()
