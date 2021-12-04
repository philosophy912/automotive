# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        pcan_bus.py
# @Author:      lizhe
# @Created:     2021/5/1 - 23:39
# --------------------------------------------------------
from automotive.logger.logger import logger
from .pcan import PCanDevice
from automotive.core.can.common.interfaces import BaseCanBus
from automotive.core.can.common.enums import BaudRateEnum
from automotive.core.can.message import Message


class PCanBus(BaseCanBus):
    """
        实现CANBus接口，能够多线程发送和接收can信号
    """

    def __init__(self, baud_rate: BaudRateEnum = BaudRateEnum.HIGH, can_fd: bool = False):
        super().__init__(baud_rate=baud_rate, can_fd=can_fd)
        # PCAN实例化
        self._can = PCanDevice(can_fd)

    @staticmethod
    def __get_data(data, length: int) -> list:
        """
        转换pcan收的data为list

        :param data: 收到的data数据

        :param length:  长度

        :return: 8byte的list对象
        """
        msg_data = []
        for i in range(length):
            msg_data.append(data[i])
        return msg_data

    @staticmethod
    def __get_time_stamp(timestamp) -> int:
        """
        peak CAN获取时间方法

        :param timestamp:  peak can读取的时间

        :return: 转换后的时间 (毫秒)
        """
        time_stamp = timestamp.micros + 1000 * timestamp.millis + 0x100000000 * 1000 * timestamp.millis_overflow
        return int(time_stamp / 1000)

    def __get_message(self, message, timestamp) -> Message:
        """
        获取message对象

        :param message: message信息

        :return: PeakCanMessage对象
        """
        msg = Message()
        msg.msg_id = message.id
        msg.time_stamp = self.__get_time_stamp(timestamp)
        msg.send_type = message.msg_type
        msg.data_length = 8 if message.len > 8 else message.len
        msg.data = self.__get_data(message.data, msg.data_length)
        return msg

    def __receive(self):
        """
        CAN接收帧函数，在接收线程中执行
        """
        while self._can.is_open and self._need_receive:
            try:
                receive_msg, timestamp = self._can.receive()
                msg_id = receive_msg.id
                logger.trace(f"msg id = {hex(msg_id)}")
                receive_message = self.__get_message(receive_msg, timestamp)
                self._receive_messages[msg_id] = receive_message
                self._stack.append(receive_message)
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
