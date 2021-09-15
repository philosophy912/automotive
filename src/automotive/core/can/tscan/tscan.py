# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        tscan.py.py
# @Author:      lizhe
# @Created:     2021/9/8 - 17:01
# --------------------------------------------------------
from typing import Tuple, Any

from automotive.logger.logger import logger
from ..api import CanBoxDevice, BaseCanDevice, BaudRate
from ..message import Message, control_decorator


class TsCan(BaseCanDevice):

    def __init__(self):
        self.is_open = False

    def check_status(func):
        """
        检查设备是否已经连接
        :param func: 装饰器函数
        """

        def wrapper(self, *args, **kwargs):
            if not self.is_open:
                raise RuntimeError("please open pcan device first")
            return func(self, *args, **kwargs)

        return wrapper

    def open_device(self, baud_rate: BaudRate = BaudRate.HIGH):
        pass

    def close_device(self):
        pass

    def read_board_info(self):
        pass

    def reset_device(self):
        pass

    def transmit(self, message: Message):
        pass

    def receive(self) -> Tuple[int, Any]:
        pass

    def get_status(self) -> bool:
        pass
