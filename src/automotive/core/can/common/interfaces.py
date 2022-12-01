# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2021, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        interfaces.py
# @Author:      lizhe
# @Created:     2021/11/18 - 22:07
# --------------------------------------------------------
import copy
import time
from abc import ABCMeta, abstractmethod
from concurrent.futures import ThreadPoolExecutor, ALL_COMPLETED, wait
from typing import Tuple, Sequence, List
from time import sleep

from automotive.common.constant import check_connect, can_tips
from automotive.logger.logger import logger
from .constant import dlc
from .enums import BaudRateEnum
from ..message import Message


class BaseCanDevice(metaclass=ABCMeta):

    def __init__(self):
        self._dlc = dlc
        self._is_open = False
        self._p_diag_module_index = 0

    @property
    def is_open(self) -> bool:
        return self._is_open

    @abstractmethod
    def open_device(self, baud_rate: BaudRateEnum = BaudRateEnum.HIGH, data_rate: BaudRateEnum = BaudRateEnum.DATA,
                    channel: int = 1):
        """
        打开CAN设备
        :param channel: 通道，默认选择为1

        :param data_rate: 速率， 默认2M， 仅CANFD有用

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
    def receive(self) -> Tuple:
        """
        接收CAN消息
        :return: message CAN消息
        """
        pass


class BaseCanBus(metaclass=ABCMeta):
    def __init__(self, baud_rate: BaudRateEnum = BaudRateEnum.HIGH, data_rate: BaudRateEnum = BaudRateEnum.DATA,
                 channel_index: int = 1, can_fd: bool = False, max_workers: int = 300, need_receive: bool = True,
                 is_uds_can_fd: bool = False):
        # UDS是否使用CANFD模式
        self._is_uds_can_fd = is_uds_can_fd
        # 表示间隔时间10ms
        self._interval_time = 10
        # 流控帧最大超时时间
        self._flow_control_time_out = 5
        # 接收连续帧最大超时时间
        self._mutil_frame_time_out = 0.1
        # baud_rate波特率，
        self._baud_rate = baud_rate
        # data_rate波特率， 仅canfd有用
        self._data_rate = data_rate
        # 通道
        self._channel_index = channel_index
        # CAN FD
        self._can_fd = can_fd
        # 是否开启接收线程
        self._need_start_receive = need_receive
        # 最大允许接收的CAN消息数量
        self._max_message_size = 500000
        # 最大线程数
        self._max_workers = max_workers
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
        logger.trace(f"the thread pool id is {id(self._thread_pool)}")
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
        # dlc对应关系
        self._dlc = dlc
        # can实例化的对象
        self._can = None
        # 诊断的请求ID
        self._request_id = None
        # 诊断的相应ID
        self._response_id = None
        # 诊断的功能请求ID
        self._function_id = None

    @property
    def can_device(self) -> BaseCanDevice:
        return self._can

    @property
    def thread_pool(self) -> ThreadPoolExecutor:
        return self._thread_pool

    def _append(self, message: Message):
        if len(self._stack) == self._max_message_size:
            self._stack.pop(0)
        self._stack.append(message)

    def _get_dlc_length(self, dlc_length: int) -> int:
        for key, value in self._dlc.items():
            if dlc_length == value:
                return key
        raise RuntimeError(f"dlc {dlc} not support, only support {self._dlc.keys()}")

    def _handle_continue_frame(self, message: Message):
        """
        处理流控帧的部分
        :param message:
        :return:
        """

        # 当设置了才能返回
        if self._response_id:
            # 这里只处理诊断数据，即7xx的信号
            if message.msg_id >> 8 == 7:
                logger.trace(f"msg_id is {message.msg_id}")
                first_data = message.data[0]
                if first_data == 0x10:
                    # 收到7xx的信号，且第一帧是10，表示是连续帧的首帧，需要回一个流控帧
                    msg = Message()
                    msg.msg_id = self._request_id
                    size = 64 if self._is_uds_can_fd else 8
                    msg.data = [0x30, 0x0, self._interval_time]
                    while len(msg.data) != size:
                        msg.data.append(0x0)
                    logger.debug(f"it will send msg {msg.msg_id} and data = {[hex(x) for x in msg.data]}")
                    self.transmit_one(msg)

    def _open_can(self):
        """
        对CAN设备进行打开、初始化等操作，并同时开启设备的帧接收线程。
        """
        # 线程池句柄
        if self._thread_pool is None:
            self._thread_pool = ThreadPoolExecutor(max_workers=self._max_workers)
            logger.trace(f"new init thread pool and id is {id(self._thread_pool)}")
        # 开启设备的接收线程
        self._need_receive = True
        # 开启设备的发送线程
        self._need_transmit = True
        # 打开设备，并初始化设备
        self._can.open_device(baud_rate=self._baud_rate, data_rate=self._data_rate, channel=self._channel_index)

    def __transmit(self, can: BaseCanDevice, message: Message, cycle_time: float):
        """
        CAN发送帧函数，在线程中执行。

        :param can can设备实例化

        :param message: message
        """
        logger.trace(f"cycle_time = {cycle_time}")
        msg_id = message.msg_id
        while can.is_open and not message.stop_flag and self._need_transmit:
            logger.debug(f"send msg {hex(msg_id)} and cycle time is {message.cycle_time}")
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
            logger.debug(f"****** Transmit [Cycle] {hex_msg_id} : {list(map(lambda x: hex(x), data))}"
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
                self.resume_transmit(msg_id)
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
            can.transmit(message)
            logger.debug(f"****** Transmit [Event] {msg_id} : {list(map(lambda x: hex(x), message.data))}"
                         f"Event Cycle time [{message.cycle_time_fast}]")
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

    def __get_response_frame(self):
        """
        接收返回帧
        :return:
        """
        result = []
        receive_flag = True
        start_time = time.time()
        logger.trace(f"timeout is {self._mutil_frame_time_out}")
        real_timeout = self._mutil_frame_time_out
        while receive_flag:
            stack = self.get_stack()
            receive_messages = list(filter(lambda x: x.msg_id == self._response_id, stack))
            message_size = len(receive_messages)
            logger.trace(f"message size is {message_size}")
            if message_size > 0:
                message = receive_messages[0]
                data = message.data
                show_data = [hex(x) for x in data]
                logger.trace(f"data is {show_data}")
                if data[0] == 0x10:
                    logger.trace(f"continue frame")
                    length = data[1]
                    logger.trace(f"length is {length}")
                    # 获取连续帧还需要发多少帧
                    frame_count = self.__get_frame_length(length)
                    logger.trace(f"frame_count is {frame_count}")
                    if real_timeout == self._mutil_frame_time_out:
                        # 根据每帧之间的间隔时间计算出来需要多少, 单位是秒  10是buffer时间
                        timeout = ((frame_count + 10) * self._interval_time * 1.2) / 1000
                        real_timeout = timeout
                        logger.debug(f"change timeout to {real_timeout}s")
                    # 判断是否收集完成所有帧数据
                    if self.__is_message_receive_finished(length, message_size):
                        for index, message in enumerate(receive_messages):
                            if index == 0:
                                msg_data = message.data[2:]
                            else:
                                msg_data = message.data[1:]
                            show_result = [hex(x) for x in result]
                            logger.debug(f"result = {show_result}")
                            result += msg_data
                        result = result[: length]
                        receive_flag = False
                else:
                    logger.debug(f"one frame")
                    for message in receive_messages:
                        msg_data = message.data
                        logger.debug(f"msg_data is {msg_data}")
                        result += msg_data
                        logger.debug(f"result = {result}")
                        receive_flag = False
            current_time = time.time()
            pass_time = current_time - start_time
            logger.trace(f"pass_time is {pass_time}")
            if pass_time > real_timeout:
                logger.debug(f"timeout exit , the pass time is {pass_time}")
                receive_flag = False
        return result

    def __get_frame_length(self, length: int) -> int:
        """
        根据第一帧检查需要收的帧数
        :param length: 数据的长度
        :return:
        """
        message_length = 64 if self._is_uds_can_fd else 8
        # 先把第一帧数据去掉
        length = length - (message_length - 2)
        size = length // (message_length - 1)
        left = length % (message_length - 1)
        logger.trace(f"length = {length}")
        logger.trace(f"size = {size}")
        logger.trace(f"left = {left}")
        if left == 0:
            size = size
        else:
            size = size + 1
        logger.trace(f"size is {size}")
        return size

    def __is_message_receive_finished(self, length: int, message_size: int) -> bool:
        """
        根据第一帧检查是否已经接收完成
        :param length: 数据的长度
        :param message_size:  目前收到的帧数
        :return:
        """
        size = self.__get_frame_length(length) + 1
        logger.trace(f"size is {size} and message_size is {message_size}")
        return size == message_size

    def __send_multi_frame(self, send_messages: List[Message]):
        """
        发多帧
        :param send_messages:
        :return:
        """
        # 清空接收数据，并发送发送第一帧，等待流控帧
        self.clear_stack_data()
        messages = copy.deepcopy(send_messages)
        messages_length = len(messages)
        logger.debug(f"messages size is {messages_length}")
        message = messages.pop(0)
        logger.debug(f"first frame message is {message}")
        if messages_length == 1:
            self.transmit_one(message)
        else:
            self.transmit_one(message)
            send_time = -1
            wait_flag = True
            start_time = time.time()
            while wait_flag:
                stack = self.get_stack()
                receive_messages = list(filter(lambda x: x.msg_id == self._response_id, stack))
                if len(receive_messages) > 0:
                    for message in receive_messages:
                        # 14.054030 CANFD   1 Rx 70E  1  0  8 8 30 08 05 00 00 00 00 00    0  0   1000 0 0 0 0 0
                        data = message.data
                        if data[0] == 0x30:
                            send_time = data[2]
                            # 收到了流控帧，就需要处理,否则解析出来的数据可能有问题
                            self.clear_stack_data()
                            wait_flag = False
                current_time = time.time()
                pass_time = current_time - start_time
                if pass_time > self._flow_control_time_out:
                    wait_flag = False
            logger.debug(f"send_time is {send_time}")
            # 没有收到流控帧
            if send_time != -1:
                interval_time = send_time / 1000
                for message in messages:
                    data = [hex(x) for x in message.data]
                    logger.debug(f"send message [{hex(message.msg_id)}] and data is [{data}]")
                    self.transmit_one(message)
                    sleep(interval_time)
            else:
                raise RuntimeError("can not receive flow control frame, not send message")

    def __get_message_data(self, message_data: List[int]) -> List[Message]:
        """
        根据数据长度组包，方便后期发送
        :param message_data: 数据列表
        :return: 二维数组，数组中的每一个值表示一个message中的data
        """
        messages = []
        message_datus = []
        message = copy.deepcopy(message_data)
        length = len(message)
        size = 64 if self._is_uds_can_fd else 8
        if length < size:
            msg_data = copy.deepcopy(message)
            msg_data.insert(0, length)
            while len(msg_data) != size:
                msg_data.append(0x0)
            msg = Message()
            msg.msg_id = self._request_id
            msg.data = msg_data
            messages.append(msg)
        else:
            # 这一步处理当数据超过3位的时候
            length_value = hex(length)[2:]
            if len(length_value) > 3:
                value = f"1{length_value}"
                first_frame = list(int(value, 16).to_bytes(64, "big"))
            else:
                first_frame = [0x10, length]
            while len(first_frame) != size:
                data = message.pop(0)
                logger.trace(f"data = {data}")
                first_frame.append(data)
            message_datus.append(first_frame)
            continue_frame = [0x21]
            # CAN FD的方式组包
            while len(message) != 0:
                data = message.pop(0)
                logger.trace(f"data = {data}")
                if len(continue_frame) != size:
                    continue_frame.append(data)
                else:
                    # 列表复用，所以需要深拷贝
                    message_datus.append(copy.deepcopy(continue_frame))
                    frame = continue_frame[0] + 1
                    continue_frame.clear()
                    continue_frame.append(frame)
                    continue_frame.append(data)
            # 追加尾部数据
            if len(continue_frame) != 0:
                while len(continue_frame) != size:
                    continue_frame.append(0xAA)
                message_datus.append(copy.deepcopy(continue_frame))
            for msg in message_datus:
                message = Message()
                message.msg_id = self._request_id
                message.data = msg
                messages.append(message)
        logger.debug(f"message is [{messages}]")
        return messages

    @abstractmethod
    def open_can(self):
        """
        对CAN设备进行打开、初始化等操作，并同时开启设备的帧接收线程。
        """
        pass

    def close_can(self):
        """
            关闭USB CAN设备。
        """
        self._need_transmit = False
        logger.trace("wait _transmit_thread close")
        wait(self._transmit_thread, return_when=ALL_COMPLETED)
        self._need_receive = False
        logger.trace("wait _receive_thread close")
        wait(self._receive_thread, return_when=ALL_COMPLETED)
        logger.trace("wait _event_thread close")
        wait(self._event_thread.values(), return_when=ALL_COMPLETED)
        if self._thread_pool:
            logger.info("shutdown thread pool")
            self._thread_pool.shutdown()
        logger.trace("_send_messages clear")
        self._send_messages.clear()
        self._thread_pool = None
        logger.trace("close_device")
        logger.trace(f"The thread pool id is {id(self._thread_pool)}")
        self._can.close_device()

    @check_connect("_can", can_tips, is_bus=True)
    def transmit(self, message: Message):
        """
        发送CAN帧函数。

        :param message: message对象
        """
        cycle_time = message.cycle_time
        logger.debug(f"message send type is {message.msg_send_type}")
        if message.msg_send_type == self._cycle or cycle_time > 0:
            logger.debug("cycle send message")
            # 周期信号
            self.__cycle_msg(self._can, message)
        elif message.msg_send_type == self._event:
            logger.debug("event send message")
            # 事件信号
            self.__event(self._can, message)
        elif message.msg_send_type == self._cycle_event:
            logger.debug("cycle&event send message")
            # 周期事件信号
            self.__cycle_msg(self._can, message)

    @check_connect("_can", can_tips, is_bus=True)
    def transmit_one(self, message: Message):
        """
        发送CAN帧函数。

        :param message: message对象
        """
        self._can.transmit(message)

    @check_connect("_can", can_tips, is_bus=True)
    def stop_transmit(self, message_id: int):
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
                logger.debug(f"Message <{hex(message_id)}> is stop to send.")
                self._send_messages[message_id].stop_flag = True
                # self._send_messages[message_id].pause_flag = True
            else:
                logger.error(f"Please check message id, Message <{hex(message_id)}> is not contain.")
        else:
            logger.trace(f"try to stop all messages")
            for key, item in self._send_messages.items():
                logger.debug(f"Message <{hex(key)}> is stop to send.")
                item.stop_flag = True
                # item.pause_flag = True

    @check_connect("_can", can_tips, is_bus=True)
    def resume_transmit(self, message_id: int):
        """
       恢复某一帧数据的发送函数。

       :param message_id:停止发送的Message的ID
       """
        if message_id:
            logger.trace(f"try to resume message {hex(message_id)}")
            if message_id in self._send_messages:
                logger.debug(f"Message <{hex(message_id)}> is resume to send.")
                message = self._send_messages[message_id]
                # message.stop_flag = False
                self.transmit(message)
            else:
                logger.error(f"Please check message id, Message <{hex(message_id)}> is not contain.")
        else:
            logger.trace(f"try to resume all messages")
            for key, item in self._send_messages.items():
                logger.debug(f"Message <{hex(key)}> is resume to send.")
                # 当发现这个msg是停止的时候就恢复发送
                if item.stop_flag:
                    # item.stop_flag = False
                    self.transmit(item)

    @check_connect("_can", can_tips, is_bus=True)
    def receive(self, message_id: int) -> Message:
        """
        接收函数。此函数从指定的设备CAN通道的接收缓冲区中读取数据。

        :param message_id: 接收所需Message的ID

        :return: Message对象
        """
        if message_id in self._receive_messages:
            return self._receive_messages[message_id]
        else:
            raise RuntimeError(f"message_id {message_id} not receive")

    @check_connect("_can", can_tips, is_bus=True)
    def get_stack(self) -> Sequence[Message]:
        """
        获取CAN的stack
        """
        return self._stack

    @check_connect("_can", can_tips, is_bus=True)
    def clear_stack_data(self):
        """
        清除栈数据
        """
        self._stack.clear()

    def init_uds(self, request_id: int, response_id: int, function_id: int):
        """
        初始化USD（仅同星可用)
        :param request_id:  地址请求ID
        :param response_id:  响应ID
        :param function_id: 功能寻址ID
        """
        self._request_id = request_id
        self._response_id = response_id
        self._function_id = function_id

    def send_and_receive_uds_message(self, message: List[int]) -> List[int]:
        """
        发送UDS诊断消息, 两种情况，没有init的UDS的时候，返回空列表，还有就是本身不返回
        :param message:
        :return:
        """
        if self._request_id and self._response_id and self._function_id:
            receive_message = []
            message_data = self.__get_message_data(message)
            logger.debug(f"message_data length is {len(message_data)}")
            try:
                self.__send_multi_frame(message_data)
                logger.debug(f"now get response data")
                receive_message = self.__get_response_frame()
            except RuntimeError as e:
                logger.error(e)
            return receive_message
        else:
            raise RuntimeError("please use function init_uds to init uds")
