# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, China TSP, All rights reserved
# --------------------------------------------------------
# @Name:        can_bus
# @Purpose:     adb相关的命令
# @Author:      lizhe
# @Created:     2019/8/21 9:47
# --------------------------------------------------------
from abc import ABCMeta, abstractmethod
from enum import Enum
from .message import PeakCanMessage, UsbCanMessage


class CanBoxDevice(Enum):
    # PCAN
    PEAKCAN = "PEAKCAN"
    # USB CAN
    USBCAN = "USBCAN"
    # CAN分析仪
    CANALYST = "CANALYST"


class CanBus(metaclass=ABCMeta):
    def __init__(self):
        # 最大线程数
        self._max_workers = 100
        # 保存接受数据帧的字典，用于接收
        self._receive_messages = dict()
        # 保存发送数据帧的字典，用于发送
        self._send_messages = dict()
        # 用于存放接收到的数据
        self._stack = []
        # 用于定义最大的保存数据数量
        self._max_stack = 5000
        # 周期性信号
        self._cycle = "Cycle"
        # 事件性信号
        self._event = "Event"
        # 周期事件性信号
        self._cycle_event = "Cycle and Event"

    @abstractmethod
    def open_can(self):
        """
        对CAN设备进行打开、初始化等操作，并同时开启设备的帧接收线程。
        """
        pass

    @abstractmethod
    def close_can(self):
        """
        关闭USB CAN设备。
        """
        pass

    @abstractmethod
    def transmit(self, message: (PeakCanMessage, UsbCanMessage)):
        """
        发送CAN帧函数。

        :param message: message对象
        """
        pass

    @abstractmethod
    def stop_transmit(self, message_id: int):
        """
        停止某一帧CAN数据的发送。(当message_id为None时候停止所有发送的CAN数据)

        :param message_id: 停止发送的Message的ID
        """
        pass

    @abstractmethod
    def resume_transmit(self, message_id: int):
        """
        恢复某一帧数据的发送函数。

        :param message_id:停止发送的Message的ID
        """
        pass

    @abstractmethod
    def receive(self, message_id: int) -> (PeakCanMessage, UsbCanMessage):
        """
        接收函数。此函数从指定的设备CAN通道的接收缓冲区中读取数据。

        :param message_id: 接收所需Message的ID

        :return: Message对象
        """
        pass

    @abstractmethod
    def is_open(self) -> bool:
        """
        CAN设备是否被打开

        :return:
            True 打开

            False 关闭
        """
        pass

    @abstractmethod
    def get_stack(self) -> list:
        """
        获取CAN的stack
        """
        pass

    @abstractmethod
    def clear_stack_data(self):
        """
        清除栈数据
        """
        pass
