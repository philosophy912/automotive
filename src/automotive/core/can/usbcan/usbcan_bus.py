# -*- coding:utf-8 -*-
# --------------------------------------------------------  
# Copyright (C), 2016-2020, China TSP, All rights reserved
# --------------------------------------------------------                 
# @Name:        usbcan_bus  
# @Purpose:     UsbCanBus
# @Author:      lizhe  
# @Created:     2019/12/2 12:57  
# --------------------------------------------------------
from automotive.logger.logger import logger
from .usb_can import UsbCan
from ..api import CanBoxDevice, BaseCanBus
from ..message import Message


class UsbCanBus(BaseCanBus):
    """
    实现CANBus接口，能够多线程发送和接收can信号
    """

    def __init__(self, can_box_device: CanBoxDevice):
        super().__init__()
        # USB CAN BOX实例化
        self.__usbcan = UsbCan(can_box_device)
        # Default TimeStamp有效
        self.__time_flag = 1

    def check_status(func):
        """
        检查设备是否已经连接
        :param func: 装饰器函数
        """

        def wrapper(self, *args, **kwargs):
            if not self.__usbcan.is_open:
                raise RuntimeError("please open usb can device first")
            return func(self, *args, **kwargs)

        return wrapper

    @staticmethod
    def __get_data(data, length: int) -> list:
        """
        转换CAN BOX收的data为list

        :param data: 收到的data数据

        :param length:  长度

        :return: 8byte的列表
        """
        msg_data = []
        for i in range(length):
            msg_data.append(data[i])
        return msg_data

    @staticmethod
    def __get_reserved(reserved_value) -> list:
        """
        获取reversed参数

        :param reserved_value:  reversed的内容(can上收到的)

        :return: 解析后的列表
        """
        reserved_list = []
        for i in range(3):
            reserved_list.append(reserved_value[i])
        return reserved_list

    def __get_message(self, p_receive) -> Message:
        """
        获取message对象

        :param p_receive: message信息

        :return: PeakCanMessage对象
        """
        msg = Message()
        msg.msg_id = p_receive.id
        msg.time_stamp = hex(p_receive.time_stamp)
        msg.time_flag = p_receive.time_flag
        msg.send_type = p_receive.send_type
        msg.remote_flag = p_receive.remote_flag
        msg.external_flag = p_receive.extern_flag
        msg.reserved = self.__get_reserved(p_receive.reserved)
        msg.data_length = 8 if p_receive.data_len > 8 else p_receive.data_len
        msg.data = self.__get_data(p_receive.data, msg.data_length)
        return msg

    def __receive(self):
        """
        CAN接收帧函数，在接收线程中执行
        """
        while self.__usbcan.is_open and self._need_receive:
            try:
                ret, p_receive = self.__usbcan.receive()
                for i in range(ret):
                    receive_message = self.__get_message(p_receive[i])
                    logger.trace(f"msg id = {receive_message.msg_id}")
                    # 单帧数据
                    if receive_message.external_flag == 0:
                        # 获取数据并保存到self._receive_msg字典中
                        self._receive_messages[receive_message.msg_id] = receive_message
                        self._stack.append(receive_message)
                    # 扩展帧
                    else:
                        logger.debug("type is external frame, not implement")
            except RuntimeError:
                continue

    def open_can(self):
        """
        对CAN设备进行打开、初始化等操作，并同时开启设备的帧接收线程。
        """
        super()._open_can()
        # 打开设备，并初始化设备
        self.__usbcan.open_device()
        # 把接收函数submit到线程池中
        self._receive_thread.append(self._thread_pool.submit(self.__receive))

    def close_can(self):
        """
        关闭USB CAN设备。
        """
        super()._close_can()
        self.__usbcan.close_device()

    @check_status
    def transmit(self, message: Message):
        """
        发送CAN帧函数。

        TODO: 延时没有实现

        :param message: message对象
        """
        super()._transmit(self.__usbcan, message)

    @check_status
    def transmit_one(self, message: Message):
        """
        发送CAN帧函数。

        TODO: 延时没有实现

        :param message: message对象
        """
        super()._transmit_one(self.__usbcan, message)

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
        super()._resume_transmit(self.__usbcan, msg_id)

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
        return self.__usbcan.is_open

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
