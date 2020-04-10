# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, China TSP, All rights reserved
# --------------------------------------------------------
# @Name:        device_can_bus
# @Purpose:     DeviceCanBus
# @Author:      lizhe
# @Created:     2019/11/30 22:32
# --------------------------------------------------------
from loguru import logger
from .peakcan.pcan_bus import PCanBus
from .usbcan.usbcan_bus import UsbCanBus
from ..interfaces.message import Message
from ..interfaces.can_bus import CanBus, CanBoxDevice


class DeviceCanBus(CanBus):

    def __init__(self, can_box_device: CanBoxDevice = None):
        super().__init__()
        if not can_box_device:
            can_box_device = self.__get_can_type()
        self.__can = self.__get_can_bus(can_box_device)

    def set_stack_size(self, size: int):
        """
        设置栈大小

        :param size: 用于定义最大的保存数据数量
        """
        self.__can.set_stack_size(size)

    @staticmethod
    def __get_can_type() -> CanBoxDevice:
        """
        通过尝试打开Pcan、usbcan以及canalyst分析仪获取当前连接设备

        :return: CanBoxDevice枚举
        """
        can = PCanBus()
        can.open_can()
        if can.is_open():
            can.close_can()
            return CanBoxDevice.PEAKCAN
        can = UsbCanBus(CanBoxDevice.USBCAN)
        try:
            can.open_can()
            if can.is_open():
                can.close_can()
                return CanBoxDevice.USBCAN
        except RuntimeError:
            logger.warning("USBCAN not found")
        can = UsbCanBus(CanBoxDevice.CANALYST)
        try:
            can.open_can()
            if can.is_open():
                can.close_can()
                return CanBoxDevice.CANALYST
        except RuntimeError:
            logger.warning("CANALYST not found")
        raise ValueError(f"peak can or USB CAN or CANALYST can not opened, please check device ")

    @staticmethod
    def __get_can_bus(can_box_device: CanBoxDevice) -> (PCanBus, UsbCanBus):
        """
        根据类型实例化can bus

        :param can_box_device: can盒类型

        :return: CanBus实例化的对象
        """
        if can_box_device == CanBoxDevice.PEAKCAN:
            return PCanBus()
        else:
            return UsbCanBus(can_box_device)

    def open_can(self):
        """
        对CAN设备进行打开、初始化等操作，并同时开启设备的帧接收线程。
        """
        self.__can.open_can()

    def close_can(self):
        """
        关闭USB CAN设备。
        """
        self.__can.close_can()

    def transmit(self, message: Message):
        """
        发送CAN帧函数。

        :param message: message对象
        """
        self.__can.transmit(message)

    def stop_transmit(self, message_id: int = None):
        """
        停止某一帧CAN数据的发送。(当message_id为None时候停止所有发送的CAN数据)

        :param message_id: 停止发送的Message的ID
        """
        self.__can.stop_transmit(message_id)

    def resume_transmit(self, message_id: int):
        """
        恢复某一帧数据的发送函数。

        :param message_id:停止发送的Message的ID
        """
        self.__can.resume_transmit(message_id)

    def receive(self, message_id: int) -> Message:
        """
        接收函数。此函数从指定的设备CAN通道的接收缓冲区中读取数据。

        :param message_id: 接收所需Message的ID

        :return: Message对象
        """
        return self.__can.receive(message_id)

    def is_open(self) -> bool:
        """
        CAN设备是否被打开

        :return:
            True 打开

            False 关闭
        """
        return self.__can.is_open()

    def get_stack(self) -> list:
        """
        获取CAN的stack
        """
        return self.__can.get_stack()

    def clear_stack_data(self):
        """
        清除栈数据
        """
        self.__can.clear_stack_data()
