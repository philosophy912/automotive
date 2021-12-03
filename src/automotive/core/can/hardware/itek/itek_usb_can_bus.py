# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2021, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        itek_usb_can_bus.py
# @Author:      lizhe
# @Created:     2021/11/1 - 21:58
# --------------------------------------------------------
from automotive.core.can.message import Message
from automotive.core.can.common.interfaces import BaseCanBus
from automotive.core.can.common.enums import BaudRateEnum
from automotive.logger.logger import logger

from .itek_usb_can import ItekUsbCanDevice


class ItekUsbCanBus(BaseCanBus):

    def __init__(self, baud_rate: BaudRateEnum = BaudRateEnum.HIGH, can_fd: bool = False):
        super().__init__(baud_rate=baud_rate, can_fd=can_fd)
        # 实例化艾泰
        self._can = ItekUsbCanDevice(can_fd)

    @staticmethod
    def __get_time_stamp(timestamp) -> int:
        """
        peak CAN获取时间方法

        :param timestamp:  peak can读取的时间

        :return: 转换后的时间 (毫秒)
        """
        time_stamp = timestamp.micros + 1000 * timestamp.millis + 0x100000000 * 1000 * timestamp.millis_overflow
        return int(time_stamp / 1000)

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

    def __get_message(self, p_receive) -> Message:
        """
        获取message对象

        :param p_receive: message信息

        :return: Message对象
        """
        msg = Message()
        frame = p_receive.frame
        msg.msg_id = frame.can_id
        # 转换成毫秒
        msg.time_stamp = int(p_receive.time_stamp / 10)
        msg.data_length = self._get_dlc_length(p_receive.len)
        msg.data = self.__get_data(p_receive.data, msg.data_length)
        return msg

    def __receive(self):
        """
        CAN接收帧函数，在接收线程中执行
        """
        while self._can.is_open and self._need_receive:
            try:
                count, p_receive = self._can.receive()
                logger.trace(f"return size is {count}")
                for i in range(count):
                    receive_message = self.__get_message(p_receive[i])
                    logger.trace(f"msg id = {hex(receive_message.msg_id)}")
                    self._receive_messages[receive_message.msg_id] = receive_message
                    self._stack.append(receive_message)
            except RuntimeError:
                continue

    def open_can(self):
        """
        对CAN设备进行打开、初始化等操作，并同时开启设备的帧接收线程。
        """
        super()._open_can()
        # 把接收函数submit到线程池中
        self._receive_thread.append(self._thread_pool.submit(self.__receive))
