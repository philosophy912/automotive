# -*- coding:utf-8 -*-
# --------------------------------------------------------  
# Copyright (C), 2016-2020, China TSP, All rights reserved
# --------------------------------------------------------                 
# @Name:        message.py  
# @Purpose:     Message
# @Author:      lizhe  
# @Created:     2019/12/1 10:34  
# --------------------------------------------------------
from loguru import logger
from .tools import Tools


class Message(object):
    """
        CAN上传输消息的基类。
    """

    def __init__(self):
        self.__tools = Tools()
        # 信号ID
        self.msg_id = None
        # 信号发送的周期
        self.cycle_time = 0
        # 信号数据长度
        self.data_length = 8
        # 信号数据
        self.data = None
        # 信号停止标志
        self.stop_flag = False
        # 信号的名字
        self.msg_name = None
        # 信号发送者
        self.sender = None
        # signal
        self.signals = dict()
        # 时间印记
        self.time_stamp = None
        # 发送帧的帧长度
        self.frame_length = 1
        # 信号发送类型
        self.send_type = 0
        # message在CAN网络上发送类型（支持CYCLE/EVENT/CE)
        self.msg_send_type = None
        # 报文快速发送的次数
        self.cycle_time_fast_times = 0
        # 报文发送的快速周期
        self.cycle_time_fast = 0
        # 报文延时时间
        self.delay_time = 0
        # 是否是网络管理帧
        self.nm_message = False
        # diag请求
        self.diag_request = False
        # diag反馈
        self.diag_response = False
        # diag state
        self.diag_state = False
        # can fd
        self.is_can_fd = False
        # 是否标准can
        self.is_standard_can = True
        #################################################################################
        # USB MESSAGE独特的部分
        self.usb_can_send_type = 1
        # USB CAN特有的属性
        self.time_flag = 1
        # USB CAN特有的属性
        self.remote_flag = 0
        # USB CAN特有的属性
        self.external_flag = 0
        # 信号保留字
        self.reserved = None

    def __check_msg_id(self):
        """
        检查msg id是否在0-07ff之间
        """
        if not self.__tools.check_value(self.msg_id, 0, 0x7FF):
            raise ValueError(f"msg id [{self.msg_id}] is incorrect, only support [0 - 0x7ff]")

    def __check_msg_data(self):
        """
        检查msg数据，8byte是否每个数据都在0-0xff之间
        """
        for value in self.data:
            if not self.__tools.check_value(value, 0, 0xff):
                raise ValueError(f"data[{self.data}] is incorrect, each value only support [0 - 0xff]")

    def __check_signals(self):
        """
        检查signals对象
        """
        bit_list = []
        for i in range(64):
            bit_list.append(False)
        for name, signal in self.signals.items():
            logger.trace(f"before bit_list [{bit_list}]")
            signal.check_value()
            signal.check_bit_length_value()
            signal.check_start_bit_value()
            logger.trace(f"raw start bit is {signal.start_bit}")
            start = self.__tools.get_position(signal.start_bit)
            length = signal.bit_length
            logger.trace(f"start = {start} and length = {length}")
            for i in range(start, length):
                if bit_list[i]:
                    raise ValueError(f"bit_list = [{bit_list}] and i = [{i}] and "
                                     f"start-bit area is overlapping start({start}) + "
                                     f"length({length}) and name [{name}]")
                bit_list[i] = True
                logger.trace(f"after bit_list [{bit_list}]")

    def check_message(self, need_check_data: bool = False):
        """
        检查message， 包含:

        1、检查msg id是否正确

        2、检查signal是否正确或者检查data是否正确

        :param need_check_data: 是否需要检查8byte的数据，默认不检查
        """
        self.__check_msg_id()
        if need_check_data:
            self.__check_msg_data()
        else:
            self.__check_signals()

    def update(self, type_: bool):
        """
        更新8byte数据。

        :param type_: 更新类型

            True: 发送数据

            False:  收到数据
        """
        # 发送数据
        if type_:
            logger.debug("send message")
            if not self.data:
                raw_data = 0
            else:
                raw_data = self.__tools.convert_to_data(self.data)
            for name, signal in self.signals.items():
                logger.trace(f"signal name = {signal.signal_name}")
                # 根据原来的数据message_data，替换某一部分的内容
                raw_data = self.__tools.set_data(raw_data, signal.start_bit, signal.bit_length, signal.value,
                                                 signal.is_float)
                logger.trace(f"raw_data[{bin(raw_data)}]")
            self.data = self.__tools.convert_to_msg(raw_data)
            logger.trace(f"data is {list(map(lambda x: hex(x), self.data))}")
        # 收到数据
        else:
            logger.debug("receive message")
            raw_data = self.__tools.convert_to_data(self.data)
            for name, signal in self.signals.items():
                value = self.__tools.get_data(raw_data, signal.start_bit, signal.bit_length, signal.is_float)
                logger.trace(f"signal name {name} value is {value}")
                signal.value = value

    def set_value(self, message: dict):
        """
        设置message对象

        TAG: 如果要增加或者变更内容，修改这里

        :param message: message字典
        """
        self.msg_id = message["id"]
        self.msg_name = message["name"]
        self.data_length = message["length"]
        self.sender = message["sender"]
        #  特殊处理，如果不是Cycle/Event就是CE
        send_type = message["msg_send_type"]
        if send_type.upper() == "CYCLE":
            self.msg_send_type = "Cycle"
        elif send_type.upper() == "EVENT":
            self.msg_send_type = "Event"
        else:
            self.msg_send_type = "Cycle and Event"
        self.nm_message = message["nm_message"]
        self.diag_request = message["diag_request"]
        self.diag_response = message["diag_response"]
        self.diag_state = message["diag_state"]
        self.is_can_fd = message["is_can_fd"]
        self.is_standard_can = message["is_standard_can"]
        try:
            self.cycle_time = message["msg_cycle_time"]
        except KeyError:
            self.cycle_time = 0
        try:
            self.delay_time = message["msg_delay_time"]
        except KeyError:
            self.delay_time = 0
        try:
            self.cycle_time_fast = message["msg_cycle_time_fast"]
        except KeyError:
            self.cycle_time_fast = 0
        try:
            self.cycle_time_fast_times = message["gen_msg_nr_of_repetition"]
        except KeyError:
            self.cycle_time_fast_times = 0

        for sig in message["signals"]:
            signal = Signal()
            signal.set_value(sig)
            self.signals[signal.signal_name] = signal


class Signal(object):
    def __init__(self):
        self.__tools = Tools()
        # 信号的名字
        self.signal_name = None
        # 信号的位长度
        self.bit_length = None
        # 信号的开始位
        self.start_bit = None
        # 值类型，是否是float类型
        self.is_float = None
        # 计算因子
        self.factor = None
        # 偏移量
        self.offset = None
        # 最大物理值
        self.maximum = None
        # 最小物理值
        self.minimum = None
        # 接收者
        self.receiver = None
        # 有无符号
        self.is_sign = None
        # 单位
        self.unit = None
        # 备注
        self.comment = None
        # 对应值
        self.values = 0
        # 设置的值
        self.__value = 0
        # 物理值
        self.__physical_value = None

    def set_value(self, signal: dict):
        """
        设置signal的值

        TAG: 如果要增加或者变更内容，修改这里

        :param signal: signal字典
        """
        self.signal_name = signal["name"]
        self.bit_length = signal['signal_size']
        self.start_bit = signal["start_bit"]
        self.is_sign = signal["is_sign"]
        self.is_float = signal["byte_type"]
        self.factor = signal["factor"]
        self.offset = signal["offset"]
        self.minimum = signal["minimum"]
        self.maximum = signal["maximum"]
        self.unit = signal["unit"]
        self.receiver = signal["receiver"]
        self.value = signal["start_value"]
        try:
            self.values = signal["values"]
        except KeyError:
            self.values = None
        try:
            self.comment = signal["comment"]
        except KeyError:
            self.comment = ""

    def check_value(self, need_check: bool = False):
        """
        检查信号的值

        :param need_check： 是否检查值是否处于物理值最大最小值之间
        """
        if need_check:
            if self.is_float:
                if not float(self.minimum) <= self.value <= float(self.maximum):
                    raise ValueError(f"value[{self.value}] must in [{self.minimum} , {self.maximum}]")
            else:
                if not int(self.minimum) <= self.value <= int(self.maximum):
                    raise ValueError(f"value[{self.value}] must in [{self.minimum} , {self.maximum}]")
        # 检查当前设置的最大值是否超过bit length所允许的最大值
        max_value = 2 ** self.bit_length - 1
        if not self.__tools.check_value(self.value, 0, max_value):
            raise ValueError(f"value[{self.value}] must in [0, {max_value}]")

    def check_start_bit_value(self):
        """
        检查start bit是否设置正确
        """
        if not self.__tools.check_value(self.start_bit, 0, 0x3f):
            raise ValueError(f"start bit[{self.start_bit}] must in [0, 0x3f]")

    def check_bit_length_value(self):
        """
        检查bit length是否设置正确
        """
        if not self.__tools.check_value(self.bit_length, 0, 0x3f):
            raise ValueError(f"start bit[{self.bit_length}] must in [0, 0x3f]")

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        """
        收到的消息，
        """
        self.__value = value
        self.__physical_value = int((float(value) * float(self.factor)) + float(self.offset))
        logger.trace(f"signal[{self.signal_name}]value is {self.__value} and physical value is {self.__physical_value}")

    @property
    def physical_value(self):
        return self.__physical_value

    @physical_value.setter
    def physical_value(self, physical_value):
        self.__physical_value = physical_value
        self.__value = int((float(physical_value) - float(self.offset)) / float(self.factor))
        logger.trace(f"physical value is {self.__physical_value} and value is {self.__value}")
