# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        api.py
# @Author:      lizhe
# @Created:     2021/5/1 - 23:42
# --------------------------------------------------------
import time
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
from automotive.logger.logger import logger
from time import sleep
from abc import ABCMeta, abstractmethod
from enum import Enum, unique

from .message import Message


@unique
class BaudRate(Enum):
    """
    CAN传输速率

    目前支持HIGH、LOW
    """
    # 高速CAN
    HIGH = "500Kbps"
    # 低速CAN
    LOW = "125kBPS"


@unique
class CanBoxDevice(Enum):
    """
    CAN盒子的类型，目前支持

    PEAKCAN、USBCAN、CANALYST
    """
    # PCAN
    PEAKCAN = "PEAKCAN"
    # USB CAN
    USBCAN = "USBCAN"
    # CAN分析仪
    CANALYST = "CANALYST"
    # CAN LIN Analyser
    # ANALYSER = "ANALYSER"


class BaseCanDevice(metaclass=ABCMeta):

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


class BaseCanBus(metaclass=ABCMeta):
    def __init__(self):
        # 最大线程数
        self._max_workers = 300
        # 保存接受数据帧的字典，用于接收
        self._receive_messages = dict()
        # 保存发送数据帧的字典，用于发送
        self._send_messages = dict()
        # 保存发送的事件信号的字典，用于发送
        self._event_send_messages = dict()
        # 用于存放接收到的数据
        self._stack = []
        # 周期性信号
        self._cycle = "Cycle"
        # 事件性信号
        self._event = "Event"
        # 周期事件性信号
        self._cycle_event = "Cycle and Event"
        # 线程池句柄
        self._thread_pool = ThreadPoolExecutor(max_workers=self._max_workers)
        # 是否需要接收，用于线程关闭
        self._need_receive = True
        # 是否需要一直发送
        self._need_transmit = True
        # 发送线程
        self._transmit_thread = []
        # 接收线程
        self._receive_thread = []
        # 事件信号线程
        self._event_thread = dict()

    def __transmit(self, can: BaseCanDevice, message: Message, cycle_time: float):
        """
        CAN发送帧函数，在线程中执行。
        :param can can设备实例化
        :param message: message
        """
        logger.trace(f"cycle_time = {cycle_time}")
        msg_id = message.msg_id
        while can.get_status() and not message.stop_flag and self._need_transmit:
            logger.trace(f"send msg {hex(msg_id)} and cycle time is {message.cycle_time}")
            try:
                can.transmit(message)
            except RuntimeError as e:
                logger.trace(f"some issue found, error is {e}")
            # 循环发送的等待周期
            sleep(cycle_time)

    def __cycle_msg(self, can: BaseCanDevice, message: Message):
        """
        发送周期性型号
        :param can can设备实例化
        :param message: message的集合对象
        """
        msg_id = message.msg_id
        # msg_id不在发送队列中
        condition1 = msg_id not in self._send_messages
        # msg_id在发送队列中，且stop_flag为真，即停止发送了得
        condition2 = msg_id in self._send_messages and self._send_messages[msg_id].stop_flag
        logger.debug(f"condition1[{condition1}] and condition2 = [{condition2}]")
        if condition1 or condition2:
            # 周期信号
            self._send_messages[msg_id] = message
            data = message.data
            hex_msg_id = hex(msg_id)
            cycle_time = message.cycle_time / 1000.0
            message.stop_flag = False
            # 周期性发送
            logger.info(f"****** Transmit msg id {hex_msg_id} data is {list(map(lambda x: hex(x), data))} "
                        f"Circle time is {message.cycle_time}ms ******")
            task = self._thread_pool.submit(self.__transmit, can, message, cycle_time)
            self._transmit_thread.append(task)
        else:
            # 周期事件信号，当周期信号发送的时候，只在变化data的时候会进行快速发送消息
            if message.msg_send_type == self._cycle_event:
                # 暂停已发送的消息
                self.stop_transmit(msg_id)
                self._send_messages[msg_id].data = message.data
                self.__event(can, message)
                # 发送完成了周期性事件信号，恢复信号发送
                self._resume_transmit(can, msg_id)
            else:
                # 已经在里面了，所以修改data值而已
                self._send_messages[msg_id].data = message.data

    def __event_transmit(self, can: BaseCanDevice, msg_id: int, cycle_time: float):
        """
        事件信号发送线程
        :return:
        """
        # 需要发送数据以及当前还有数据可以发送
        while self._need_transmit and msg_id in self._event_send_messages and len(
                self._event_send_messages[msg_id]) > 0:
            message = self._event_send_messages[msg_id].pop(0)
            logger.debug(f"****** Send msg[{hex(msg_id)}] and data [{list(map(lambda x: hex(x), message.data))}] "
                         f"and cycle time [{message.cycle_time_fast}]")
            can.transmit(message)
            sleep(cycle_time)

    def __event(self, can: BaseCanDevice, message: Message):
        """
        发送事件信号
        :param can can设备实例化
        :param message: message的集合对象
        """
        msg_id = message.msg_id
        cycle_time = message.cycle_time_fast / 1000.0
        # 事件信号
        event_times = message.cycle_time_fast_times if message.cycle_time_fast_times > 0 else 1
        # 构建消息列表
        messages = []
        for i in range(event_times):
            messages.append(message)
        # 第一次发送
        if msg_id not in self._event_send_messages:
            self._event_send_messages[msg_id] = messages
            # 第一次发送，所以需要新开线程
            self._event_thread[msg_id] = self._thread_pool.submit(self.__event_transmit, can, msg_id, cycle_time)
        else:
            self._event_send_messages[msg_id] += messages
            # 判断消息是否发送完成，若发送完成则需要新开线程，否则继续使用老的线程发送
            if self._event_thread[msg_id].done():
                self._event_thread[msg_id] = self._thread_pool.submit(self.__event_transmit, can, msg_id, cycle_time)

    def _open_can(self):
        """
        对CAN设备进行打开、初始化等操作，并同时开启设备的帧接收线程。
        """
        # 线程池句柄
        if self._thread_pool is None:
            self._thread_pool = ThreadPoolExecutor(max_workers=self._max_workers)
        # 开启设备的接收线程
        self._need_receive = True
        # 开启设备的发送线程
        self._need_transmit = True

    def _close_can(self):
        """
        关闭USB CAN设备。
        """
        self._need_transmit = False
        wait(self._transmit_thread, return_when=ALL_COMPLETED)
        self._need_receive = False
        wait(self._receive_thread, return_when=ALL_COMPLETED)
        wait(self._event_thread.values(), return_when=ALL_COMPLETED)
        if self._thread_pool:
            logger.info("shutdown thread pool")
            self._thread_pool.shutdown()
        self._send_messages.clear()
        self._thread_pool = None

    @staticmethod
    def _transmit_one(can: BaseCanDevice, message: Message):
        """
        发送一帧数据

        :param can: can设备实例化

        :param message: message对象
        """
        can.transmit(message)

    def _transmit(self, can: BaseCanDevice, message: Message):
        """
        发送CAN帧函数。

        TODO: 延时没有实现

        :param can: can设备实例化

        :param message: message对象
        """
        cycle_time = message.cycle_time
        logger.debug(f"message send type is {message.msg_send_type}")
        if message.msg_send_type == self._cycle or cycle_time > 0:
            logger.debug("cycle send message")
            # 周期信号
            self.__cycle_msg(can, message)
        elif message.msg_send_type == self._event:
            logger.debug("event send message")
            # 事件信号
            self.__event(can, message)
        elif message.msg_send_type == self._cycle_event:
            logger.debug("cycle&event send message")
            # 周期事件信号
            self.__cycle_msg(can, message)

    def _stop_transmit(self, message_id: int):
        """
        停止某一帧CAN数据的发送。(当message_id为None时候停止所有发送的CAN数据)

        :param message_id: 停止发送的Message的ID
        """
        """
        停止某一帧CAN数据的发送。(当message_id为None时候停止所有发送的CAN数据)

        :param msg_id: 停止发送的Message的ID
        """
        logger.trace(f"send message list size is {len(self._send_messages)}")
        if message_id:
            logger.trace(f"try to stop message {hex(message_id)}")
            if message_id in self._send_messages:
                logger.info(f"Message <{hex(message_id)}> is stop to send.")
                self._send_messages[message_id].stop_flag = True
                # self._send_messages[message_id].pause_flag = True
            else:
                logger.error(f"Please check message id, Message <{hex(message_id)}> is not contain.")
        else:
            logger.trace(f"try to stop all messages")
            for key, item in self._send_messages.items():
                logger.info(f"Message <{hex(key)}> is stop to send.")
                item.stop_flag = True
                # item.pause_flag = True

    def _resume_transmit(self, can: BaseCanDevice, message_id: int):
        """
        恢复某一帧数据的发送函数。

        :param can: canDevice实例化

        :param message_id:停止发送的Message的ID
        """
        if message_id:
            logger.trace(f"try to resume message {hex(message_id)}")
            if message_id in self._send_messages:
                logger.info(f"Message <{hex(message_id)}> is resume to send.")
                message = self._send_messages[message_id]
                # message.stop_flag = False
                self._transmit(can, message)
            else:
                logger.error(f"Please check message id, Message <{hex(message_id)}> is not contain.")
        else:
            logger.trace(f"try to resume all messages")
            for key, item in self._send_messages.items():
                logger.info(f"Message <{hex(key)}> is resume to send.")
                # 当发现这个msg是停止的时候就恢复发送
                if item.stop_flag:
                    # item.stop_flag = False
                    self._transmit(can, item)

    def _receive(self, message_id: int) -> Message:
        """
        接收函数。此函数从指定的设备CAN通道的接收缓冲区中读取数据。

        :param message_id: 接收所需Message的ID

        :return: Message对象
        """
        if message_id in self._receive_messages:
            return self._receive_messages[message_id]
        else:
            raise RuntimeError(f"message_id {message_id} not receive")

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
    def transmit_one(self, message: Message):
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

    def get_stack(self) -> list:
        """
        获取CAN的stack
        """
        return self._stack

    def clear_stack_data(self):
        """
        清除栈数据
        """
        self._stack.clear()
