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
                    logger.trace("Method <{}> call success, and init CAN{} success.".format(func.__name__, args[2]))
                elif func.__name__ == "start_device":
                    logger.trace("Method <{}> call success, and start CAN{} success.".format(func.__name__, args[2]))
                else:
                    logger.trace("Method <{}> call success, and return success.".format(func.__name__))
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

    @abstractmethod
    def get_status(self) -> bool:
        """
        获取设备打开状态
        :return:  开/关
        """
        pass
