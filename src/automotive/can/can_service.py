# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, China TSP, All rights reserved
# --------------------------------------------------------
# @Name:        CANService
# @Purpose:     调用CAN Box进行can信号的收发（单例模式）
#               无需关心底层的CAN硬件设备。
# @Author:      lizhe
# @Created:     2019/8/21 9:47
# --------------------------------------------------------
import time
from loguru import logger
from automotive.tools import Singleton
from .interfaces.parser import Parser
from .interfaces.tools import Tools
from .devices.device_can_bus import DeviceCanBus
from .interfaces.message import PeakCanMessage, UsbCanMessage


class CANService(metaclass=Singleton):
    """
        CAN的服务类，主要用于CAN信号的发送，接收等操作。

    """

    def __init__(self, message: (str, list), encoding: str = "utf-8"):
        self.__can = DeviceCanBus()
        self.__tools = Tools()
        self.__parser = Parser()
        logger.debug(f"read message from file {message}")
        self.__messages, self.__name_messages = self.__parser.get_message(message, encoding=encoding)
        # 用于记录当前栈中msg的最后一个数据的时间点
        self.__last_msg_time_in_stack = dict()

    @property
    def name_messages(self):
        return self.__name_messages

    @name_messages.setter
    def name_messages(self, name_messages):
        self.__name_messages = name_messages

    @property
    def messages(self):
        return self.__messages

    @messages.setter
    def messages(self, messages):
        self.__messages = messages

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

    def stop_transmit(self, message_id: int = None):
        """
        发送CAN帧函数。

        :param message_id: message对象
        """
        self.__can.stop_transmit(message_id)

    def resume_transmit(self, message_id: int):
        """
        恢复某一帧数据的发送函数。

        :param message_id:停止发送的Message的ID
        """
        self.__can.resume_transmit(message_id)

    def is_open(self) -> bool:
        """
        CAN设备是否被打开

        :return:
            True 打开

            False 关闭
        """
        return self.__can.is_open()

    def send_can_message_by_id_or_name(self, msg: (int, str)):
        """
        据矩阵表中定义的Messages，通过msg ID或者name来发送message到网络中

        该方法仅发送Message消息，但不会改变Message的值，如需改变值，请使用send_can_signal_message方法

        :param msg： msg的名字或者id
        """
        if isinstance(msg, int):
            send_msg = self.messages[msg]
        elif isinstance(msg, str):
            send_msg = self.name_messages[msg]
        else:
            raise RuntimeError(f"msg only support str or int, but now is {msg}")
        self.send_can_message(send_msg, False)

    def send_can_signal_message(self, msg: (int, str), signal: dict):
        """
        根据矩阵表中定义的Messages，来设置并发送message。

        tips：不支持8byte数据发送，如果是8Byte数据请使用send_can_message来发送

        :param msg: msg的名字或者id

        :param signal: 需要修改的信号，其中key是信号名字，value是物理值（如车速50)

            如： {"signal_name1": 0x1, "signal_name2": 0x2}
        """
        if isinstance(msg, str):
            msg_id = self.name_messages[msg]
        elif isinstance(msg, int):
            msg_id = msg
        else:
            raise RuntimeError(f"msg only support msg id or msg name but current value is {msg}")
        set_message = self.messages[msg_id]
        for name, value in signal.items():
            set_signal = set_message.signals[name]
            set_signal.physical_value = value
        set_message.check_message()
        self.send_can_message_by_id_or_name(msg_id)

    def send_can_message(self, send_msg: (PeakCanMessage, UsbCanMessage), type_: bool = False):
        """
        直接发送的Message对象数据，可以选择8byte数据发送和signals数据发送两种方式，默认使用signals方式构建数据

        :param send_msg: Message对象

        :param type_: 发送类型（默认使用Signals方式)

            True： 8byte数据发送

            False: signals方式发送
        """
        send_msg.check_message(type_)
        send_msg.update(True)
        self.__can.transmit(send_msg)

    def receive_can_message(self, message_id: int) -> (PeakCanMessage, UsbCanMessage):
        """
        接收在CAN上收到的Message消息，当能够在内置的messages对象中查询到则能够查询到具体的signals的值，否则只能查询到8byte数据

        :param message_id: message id值

        :return: Message对象
        """
        receive_msg = self.__can.receive(message_id)
        try:
            # 如果能在messages对象中查询到相关内容，更新一下value值
            json_msg = self.messages[receive_msg.msg_id]
            json_msg.data = receive_msg.data
            json_msg.update(False)
            return json_msg
        except KeyError:
            return receive_msg

    def receive_can_message_signal_value(self, message_id: int, signal_name: str) -> float:
        """
        接收CAN上收到的消息并返回指定的signal的值， 如果Message不是在messages中已定义的，则回抛出异常

        :param message_id: message id值

        :param signal_name: 信号的名称

        :return: 查到的指定信号的物理值
        """
        return self.receive_can_message(message_id).signals[signal_name].physical_value

    def is_lost_message(self, msg_id: int, cycle_time: int, continue_time: int = 5, lost_period: int = None,
                        bus_time: int = None) -> bool:
        """
        判断message是否丢失

        判断规则：

        1、总线是否丢失

        2、最后两帧收到的消息间隔时间大于信号周期间隔时间且收到的消息小于应该收到的消息去掉信号丢失周期应该收到的消息数量

        :param msg_id: message id值

        :param lost_period: 信号丢失周期（默认为10个周期)

        :param continue_time: 检测时间（当不为空的时候，会清空数据并等待time ms，然后再检测数据)

        :param cycle_time: 信号周期 单位ms

        :param bus_time: 总线丢失检测时间,默认不检测
        """
        # 先判断是否总线丢失，如果总线丢失则表示信号丢失
        if bus_time:
            logger.info(f"judge bus status")
            if self.is_can_bus_lost(bus_time):
                return True
        logger.debug(f"sleep {continue_time}")
        # 清空栈数据，继续接收数据
        self.clear_stack_data()
        time.sleep(continue_time)
        stack = self.__can.get_stack()
        logger.debug(f"stack size is {len(stack)}")
        # 过滤掉没有用的数据
        msg_stack_list = list(filter(lambda x: x.msg_id == msg_id, stack))
        msg_stack_size = len(msg_stack_list)
        logger.debug(f"msg_stack_size is {msg_stack_size}")
        # 计算continue_time时间内应该受到的帧数量
        receive_msg_size = (continue_time * 1000) / cycle_time
        logger.debug(f"receive_msg_size is {receive_msg_size}")
        if lost_period:
            logger.debug(f"lost_period exist")
            # 确保至少收到两个以上的信号
            if msg_stack_size < 2:
                return True
            else:
                pass_time = (int(msg_stack_list[-1].time_stamp, 16) - int(msg_stack_list[-2].time_stamp, 16)) / 1000
                judge_time = cycle_time * lost_period
                logger.info(f"pass time is {pass_time} and judge time is {judge_time}")
                # 最后两帧的间隔时间大于信号周期间隔时间且收到的消息小于应该收到的消息去掉信号丢失周期应该收到的消息
                max_lost_receive_msg_size = receive_msg_size - (lost_period * 1000) / cycle_time
                logger.info(f"msg_stack_size is {msg_stack_size} and max_size is {max_lost_receive_msg_size}")
                return pass_time > judge_time and msg_stack_size < max_lost_receive_msg_size
        else:
            logger.info(f"need receive msg size [{receive_msg_size}] and actual receive size is [{msg_stack_size}]")
            return msg_stack_size < receive_msg_size

    def is_can_bus_lost(self, continue_time: int = 5) -> bool:
        """
        can总线是否数据丢失，如果检测周期内有一帧can信号表示can网络没有中断

        :param continue_time: 清空数据，10s内收不到任何的CAN消息表示CAN总线丢失
        """
        # 清空栈数据
        self.clear_stack_data()
        time.sleep(continue_time)
        return len(self.__can.get_stack()) == 0

    def clear_stack_data(self):
        """
        清除栈数据
        """
        # 清除message记录的时间
        self.__last_msg_time_in_stack.clear()
        self.__can.clear_stack_data()

    def is_msg_value_changed(self, msg_id: int, continue_time: int = 5) -> bool:
        """
        检测某个msg是否有变化，只能检测到整个8byte数据是否有变化

        :param continue_time: 检测持续时间

        :param msg_id: 信号ID

        :return:
            True: 有变化

            False: 没有变化
        """
        # 清空栈数据
        self.clear_stack_data()
        logger.info(f"start detect msg data, if you have any operation, please finished it in {continue_time}")
        time.sleep(continue_time)
        stack = self.__can.get_stack()
        # 过滤掉没有用的数据
        data_list = list(filter(lambda x: x.msg_id == msg_id, stack))
        duplicate = set()
        for message in data_list:
            data = message.data
            duplicate.add(data)
        return len(duplicate) > 1

    def is_signal_value_changed(self, msg_id: int, signal_name: str, continue_time: int = 10, ) -> bool:
        """
        检测某个msg中某个signal是否有变化

        :param msg_id: 信号ID

        :param signal_name: 信号名称

        :param continue_time: 检测持续时间， 默认10秒

        :return:
            True: 有变化

            False: 没有变化
        """
        # 清空栈数据
        self.clear_stack_data()
        logger.info(f"start detect msg data, if you have any operation, please finished it in {continue_time}")
        time.sleep(continue_time)
        stack = self.__can.get_stack()
        # 过滤掉没有用的数据
        data_list = list(filter(lambda x: x.msg_id == msg_id, stack))
        duplicate = set()
        for message in data_list:
            signal = message.signals[signal_name]
            duplicate.add(signal.value)
        return len(duplicate) > 1
