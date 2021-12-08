# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2021, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        tsmaster_bus.py
# @Author:      lizhe
# @Created:     2021/10/27 - 21:26
# --------------------------------------------------------
from typing import List

from automotive.logger.logger import logger
from automotive.core.can.message import Message
from automotive.core.can.common.interfaces import BaseCanBus
from automotive.core.can.common.enums import BaudRateEnum
from .tsmaster import TSMasterDevice


class TsMasterCanBus(BaseCanBus):

    def __init__(self, baud_rate: BaudRateEnum = BaudRateEnum.HIGH, can_fd: bool = False):
        super().__init__(baud_rate=baud_rate, can_fd=can_fd)
        # 实例化同星
        self._can = TSMasterDevice(can_fd)

    @staticmethod
    def __get_data(data, length: int) -> List:
        msg_data = []
        for i in range(length):
            msg_data.append(data[i])
        return msg_data

    def __get_message(self, p_receive) -> Message:
        """
        获取message对象

        :param p_receive: message信息

        :return: PeakCanMessage对象
        """
        msg = Message()
        msg.msg_id = p_receive.FIdentifier
        msg.time_stamp = p_receive.FTimeUS
        msg.data = self.__get_data(p_receive.FData, self._get_dlc_length(p_receive.FDLC))
        msg.data_length = len(msg.data)
        return msg

    def __receive(self):
        """
        CAN接收帧函数，在接收线程中执行
        """
        logger.debug(
            f"start receive and tsmaster status = {self._can.is_open} and need_receive = {self._need_receive}")
        while self._can.is_open and self._need_receive:
            try:
                count, p_receive = self._can.receive()
                logger.debug(f"receive count is {count}")
                for i in range(count):
                    message = self.__get_message(p_receive[i])
                    logger.trace(f"message_id = {hex(message.msg_id)}")
                    self._receive_messages[message.msg_id] = message
                    self._stack.append(message)
            except RuntimeError as e:
                logger.trace(e)
                continue

    def open_can(self):
        """
        对CAN设备进行打开、初始化等操作，并同时开启设备的帧接收线程。
                """
        super()._open_can()
        # 把接收函数submit到线程池中
        self._receive_thread.append(self._thread_pool.submit(self.__receive))