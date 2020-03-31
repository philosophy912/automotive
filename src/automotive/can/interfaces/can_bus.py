# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, China TSP, All rights reserved
# --------------------------------------------------------
# @Name:        can_bus
# @Purpose:     adb相关的命令
# @Author:      lizhe
# @Created:     2019/8/21 9:47
# --------------------------------------------------------
import sys
from abc import ABCMeta, abstractmethod
from enum import Enum
from functools import wraps
from loguru import logger
from .message import Message


def control_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            ret = func(*args, **kwargs)
            if ret == 1:
                if func.__name__ == "init_device":
                    logger.debug("Method <{}> call success, and init CAN{} success.".format(func.__name__, args[2]))
                elif func.__name__ == "start_device":
                    logger.debug("Method <{}> call success, and start CAN{} success.".format(func.__name__, args[2]))
                else:
                    logger.debug("Method <{}> call success, and return success.".format(func.__name__))
                return ret
            elif ret == 0:
                raise RuntimeError("Method <{}> is called, and return failed.".format(func.__name__))
            elif ret == -1:
                raise RuntimeError("Method <{}> is called, and CAN is not exist.".format(func.__name__))
            else:
                raise RuntimeError("Method <{}> : Unknown error.".format(func.__name__))
        except Exception:
            error = sys.exc_info()
            logger.error('ERROR: ' + str(error[0]) + ' : ' + str(error[1]))
            raise RuntimeError(error[1])

    return wrapper


class BaudRate(Enum):
    # 高速CAN
    HIGH = "500Kbps"
    # 低速CAN
    LOW = "125kBPS"


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
    def set_stack_size(self, size: int):
        """
        设置栈大小

        :param size: 用于定义最大的保存数据数量
        """
        pass

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
    def transmit(self, message: Message):
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
    def receive(self, message_id: int) -> Message:
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


class CANDevice(metaclass=ABCMeta):

    @abstractmethod
    def open_device(self, baud_rate: BaudRate = BaudRate.HIGH):
        """
        打开CAN设备
        :param baud_rate: 速率，目前只支持500Kbps的高速CAN和125Kbps的低速CAN
        """
        pass

    @abstractmethod
    def close_device(self):
        """
        关闭CAN设备
        """
        pass

    @abstractmethod
    def read_board_info(self):
        """
        读取设备信息
        """
        pass

    @abstractmethod
    def reset_device(self):
        """
        重置CAN设备
        """
        pass

    @abstractmethod
    def transmit(self, message: Message):
        """
        发送CAN消息
        :param message: CAN消息
        """
        pass

    @abstractmethod
    def receive(self) -> tuple:
        """
        接收CAN消息
        :return: message CAN消息
        """
        pass
