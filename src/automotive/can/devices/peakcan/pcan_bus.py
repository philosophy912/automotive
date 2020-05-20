# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, China TSP, All rights reserved
# --------------------------------------------------------                 
# @Name:        pcan_bus.py
# @Purpose:     PCanBus
# @Author:      lizhe
# @Created:     2019/11/30 22:35  
# --------------------------------------------------------
from time import sleep
from loguru import logger
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
from .pcan import PCan
from automotive.can.interfaces import Message, CanBus


class PCanBus(CanBus):
    """
        实现CANBus接口，能够多线程发送和接收can信号
    """

    def __init__(self):
        super().__init__()
        # 线程池句柄
        self.__thread_pool = None
        # PCAN实例化
        self.__pcan = PCan()
        # 是否需要接收，用于线程关闭
        self.__need_receive = True
        # 是否需要一直发送
        self.__need_transmit = True
        # 发送线程
        self.__transmit_thread = []
        # 接收线程
        self.__receive_thread = []

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
        while self.__pcan.is_open and self.__need_receive:
            try:
                receive_msg, timestamp = self.__pcan.receive()
                msg_id = receive_msg.id
                logger.trace(f"msg id = {hex(msg_id)}")
                receive_message = self.__get_message(receive_msg, timestamp)
                self._receive_messages[msg_id] = receive_message
                if len(self._stack) == self._max_stack:
                    self._stack.pop()
                else:
                    logger.trace(f"stack size is {len(self._stack)}")
                    self._stack.append(receive_message)
            except RuntimeError:
                continue

    def __transmit(self, message: Message, cycle_time: float):
        """
        CAN发送帧函数，在线程中执行。

        :param message: message
        """
        logger.trace(f"peak can status is {self.__pcan.is_open}")
        logger.trace(f"cycle_time = {cycle_time}")
        msg_id = message.msg_id
        while self.__pcan.is_open and not message.stop_flag and self.__need_transmit:
            logger.trace(f"send msg {hex(msg_id)} and cycle time is {message.cycle_time}")
            try:
                self.__pcan.transmit(message)
            except RuntimeError as e:
                logger.trace(f"some issue found, error is {e}")
            # 循环发送的等待周期
            sleep(cycle_time)

    def __cycle_msg(self, message: Message):
        """
        发送周期性型号

        :param message: message的集合对象
        """
        msg_id = message.msg_id
        if msg_id not in self._send_messages:
            # 周期信号
            self._send_messages[msg_id] = message
            data = message.data
            hex_msg_id = hex(msg_id)
            cycle_time = message.cycle_time / 1000.0
            # 周期性发送
            logger.info(f"****** Transmit msg id {hex_msg_id} data is {list(map(lambda x: hex(x), data))} "
                        f"Circle time is {message.cycle_time}ms ******")
            self.__transmit_thread.append(self.__thread_pool.submit(self.__transmit, message, cycle_time))
        else:
            # 已经在里面了，所以修改data值而已
            self._send_messages[msg_id].data = message.data
            # 反向update一下保证signal是对的
            self._send_messages[msg_id].update(False)

    def __event(self, message: Message):
        """
        发送事件信号

        :param message: message的集合对象
        """
        msg_id = message.msg_id
        hex_msg_id = hex(msg_id)
        data = message.data
        cycle_time = message.cycle_time_fast / 1000.0
        # 事件信号
        for i in range(message.cycle_time_fast_times):
            logger.debug(f"****** The {i} times send msg[{hex_msg_id}] and data [{list(map(lambda x: hex(x), data))}] "
                         f"and cycle time [{message.cycle_time_fast}]")
            self.__pcan.transmit(message)
            sleep(cycle_time)

    def open_can(self):
        """
        对CAN设备进行打开、初始化等操作，并同时开启设备的帧接收线程。
        """
        # 设置线程池，最大线程数为100
        self.__thread_pool = ThreadPoolExecutor(max_workers=self._max_workers)
        # 打开设备，并初始化设备
        self.__pcan.open_device()
        # 开启设备的接收线程
        self.__need_receive = True
        # 开启设备的发送线程
        self.__need_transmit = True
        # 把接收函数submit到线程池中
        self.__receive_thread.append(self.__thread_pool.submit(self.__receive))

    def close_can(self):
        """
        关闭USB CAN设备。
        """
        self.__need_transmit = False
        wait(self.__transmit_thread, return_when=ALL_COMPLETED)
        self.__need_receive = False
        wait(self.__receive_thread, return_when=ALL_COMPLETED)
        self.__thread_pool.shutdown()
        self._send_messages.clear()
        self.__pcan.close_device()

    @check_status
    def transmit(self, message: Message):
        """
        发送CAN帧函数。

        TODO: 延时没有实现

        :param message: message对象
        """
        msg_id = message.msg_id
        cycle_time = message.cycle_time
        if message.msg_send_type == self._cycle or cycle_time > 0:
            logger.trace("cycle send message")
            # 周期信号
            self.__cycle_msg(message)
        elif message.msg_send_type == self._event:
            logger.trace("event send message")
            # 事件信号
            self.__event(message)
        else:
            logger.trace("cycle&event send message")
            # 周期事件信号
            if msg_id not in self._send_messages:
                self.__cycle_msg(message)
            # 暂停已发送的消息
            self._send_messages[msg_id].stop_flag = True
            self.__event(message)
            # 发送完成了周期性事件信号，恢复信号发送
            self._send_messages[msg_id].stop_flag = False
            self.__cycle_msg(message)

    @check_status
    def stop_transmit(self, msg_id: int = None):
        """
        停止某一帧CAN数据的发送。(当message_id为None时候停止所有发送的CAN数据)

        :param msg_id: 停止发送的Message的ID
        """
        logger.trace(f"send message list size is {len(self._send_messages)}")
        if msg_id:
            logger.trace(f"try to stop message {hex(msg_id)}")
            if msg_id in self._send_messages:
                logger.info(f"Message <{hex(msg_id)}> is stop to send.")
                self._send_messages[msg_id].stop_flag = True
            else:
                logger.error(f"Please check message id, Message <{hex(msg_id)}> is not contain.")
        else:
            logger.trace(f"try to stop all messages")
            for key, item in self._send_messages.items():
                logger.info(f"Message <{hex(key)}> is stop to send.")
                item.stop_flag = True

    @check_status
    def resume_transmit(self, msg_id: int = None):
        """
        恢复某一帧数据的发送函数。

        :param msg_id:停止发送的Message的ID
        """
        if msg_id:
            logger.trace(f"try to resume message {hex(msg_id)}")
            if msg_id in self._send_messages:
                logger.info(f"Message <{hex(msg_id)}> is resume to send.")
                message = self._send_messages[msg_id]
                message.stop_flag = False
                self.transmit(message)
            else:
                logger.error(f"Please check message id, Message <{hex(msg_id)}> is not contain.")
        else:
            logger.trace(f"try to resume all messages")
            for key, item in self._send_messages.items():
                logger.info(f"Message <{hex(key)}> is resume to send.")
                # 当发现这个msg是停止的时候就恢复发送
                if item.stop_flag:
                    item.stop_flag = False
                    self.transmit(item)

    @check_status
    def receive(self, msg_id: int) -> Message:
        """
        接收函数。此函数从指定的设备CAN通道的接收缓冲区中读取数据。

        :param msg_id: 接收所需Message的ID

        :return: Message对象
        """
        if msg_id in self._receive_messages:
            return self._receive_messages[msg_id]
        else:
            raise RuntimeError(f"message_id {msg_id} not receive")

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
        return self._stack

    @check_status
    def clear_stack_data(self):
        """
        清除栈数据
        """
        self._stack.clear()

    def set_stack_size(self, size: int):
        """
        设置栈大小

        :param size: 用于定义最大的保存数据数量
        """
        self._max_stack = size
