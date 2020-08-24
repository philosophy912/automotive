# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, China TSP, All rights reserved
# --------------------------------------------------------                 
# @Name:        pcan_bus.py
# @Purpose:     PCanBus
# @Author:      lizhe
# @Created:     2019/11/30 22:35  
# --------------------------------------------------------
from automotive.logger.logger import logger
from .pcan import PCan
from ..api import BaseCanBus
from ..message import Message


class PCanBus(BaseCanBus):
    """
        实现CANBus接口，能够多线程发送和接收can信号
    """

    def __init__(self):
        super().__init__()
        # PCAN实例化
        self.__pcan = PCan()

    def check_status(func):
        """
        检查设备是否已经连接
        :param func: 装饰器函数
        """

        def wrapper(self, *args, **kwargs):
            if not self.__pcan.is_open:
                raise RuntimeError("please open pcan device first")
            return func(self, *args, **kwargs)

        return wrapper

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
    def __get_time_stamp(timestamp) -> str:
        """
        peak CAN获取时间方法

        :param timestamp:  peak can读取的时间

        :return: 转换后的时间
        """
        return hex(timestamp.micros + 1000 * timestamp.millis + 0x100000000 * 1000 * timestamp.millis_overflow)

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
        while self.__pcan.is_open and self._need_receive:
            try:
                receive_msg, timestamp = self.__pcan.receive()
                msg_id = receive_msg.id
                logger.trace(f"msg id = {hex(msg_id)}")
                receive_message = self.__get_message(receive_msg, timestamp)
                self._receive_messages[msg_id] = receive_message
                self._stack.append(receive_message)
            except RuntimeError:
                continue

    def open_can(self):
        """
        对CAN设备进行打开、初始化等操作，并同时开启设备的帧接收线程。
        """
        super()._open_can()
        # 打开设备，并初始化设备
        self.__pcan.open_device()
        # 把接收函数submit到线程池中
        self._receive_thread.append(self._thread_pool.submit(self.__receive))

    def close_can(self):
        """
        关闭USB CAN设备。
        """
        super()._close_can()
        self.__pcan.close_device()

    @check_status
    def transmit(self, message: Message):
        """
        发送CAN帧函数。
        :param message: message对象
        """
        super()._transmit(self.__pcan, message)

    @check_status
    def transmit_one(self, message: Message):
        """
        仅发一帧数据
        :param message:
        :return:
        """
        super()._transmit_one(self.__pcan, message)

    @check_status
    def stop_transmit(self, msg_id: int = None):
        """
        停止某一帧CAN数据的发送。(当message_id为None时候停止所有发送的CAN数据)

        :param msg_id: 停止发送的Message的ID
        """
        super()._stop_transmit(msg_id)

    @check_status
    def resume_transmit(self, msg_id: int = None):
        """
        恢复某一帧数据的发送函数。

        :param msg_id:停止发送的Message的ID
        """
        super()._resume_transmit(self.__pcan, msg_id)

    @check_status
    def receive(self, msg_id: int) -> Message:
        """
        接收函数。此函数从指定的设备CAN通道的接收缓冲区中读取数据。

        :param msg_id: 接收所需Message的ID

        :return: Message对象
        """
        return super()._receive(msg_id)

    def is_open(self) -> bool:
        """
        CAN设备是否被打开

        :return:
            True 打开

            False 关闭
        """
        return self.__pcan.is_open

    @check_status
    def get_stack(self) -> list:
        """
        获取CAN的stack
        """
        return super().get_stack()

    @check_status
    def clear_stack_data(self):
        """
        清除栈数据
        """
        super().clear_stack_data()
