# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        can_service.py
# @Author:      lizhe
# @Created:     2021/5/1 - 23:42
# --------------------------------------------------------
import time
import random
import copy
from time import sleep
from automotive.logger.logger import logger
from .peakcan import PCanBus
from .usbcan import UsbCanBus
from .api import CanBoxDevice, BaseCanBus
from ..singleton import Singleton
from .message import Message, get_message


def __get_can_bus(can_box_device: CanBoxDevice) -> BaseCanBus:
    if can_box_device == CanBoxDevice.PEAKCAN:
        logger.info("use pcan")
        return PCanBus()
    else:
        logger.info("use can box")
        return UsbCanBus(can_box_device)


def __get_can_box_device() -> CanBoxDevice:
    """
    获取can盒子的类型， 依次从PCan找到CANALYST然后到USBCAN
    :return: can盒类型
    """
    can = PCanBus()
    try:
        can.open_can()
        if can.is_open():
            can.close_can()
            return CanBoxDevice.PEAKCAN
    except RuntimeError:
        logger.debug("open PEAKCAN failed")
    can = UsbCanBus(can_box_device=CanBoxDevice.CANALYST)
    try:
        can.open_can()
        if can.is_open():
            can.close_can()
            return CanBoxDevice.CANALYST
    except RuntimeError:
        logger.debug("open CANALYST failed")
    can = UsbCanBus(can_box_device=CanBoxDevice.USBCAN)
    try:
        can.open_can()
        if can.is_open():
            can.close_can()
            return CanBoxDevice.USBCAN
    except RuntimeError:
        logger.debug("open USBCAN failed")
    raise RuntimeError("No device found, is can box connected")


def get_can_bus(can_box_device: CanBoxDevice) -> tuple:
    """
    获取Can bus实例，并返回CAN设备的类型

    :param can_box_device: can box的设备类型

    :return: CAN设备的类型， Can bus实例
    """
    if not can_box_device:
        can_box_device = __get_can_box_device()
    return can_box_device, __get_can_bus(can_box_device)


class BaseCan(metaclass=Singleton):
    """
    CAN设备操作的父类，实现CAN的最基本的操作， 如打开、关闭设备, 传输、接收CAN消息，停止传输CAN消息，查看CAN设备打开状态等
    """

    def __init__(self, can_box_device: CanBoxDevice = None):
        self._can_box_device, self._can = get_can_bus(can_box_device)

    @property
    def can_box_device(self) -> CanBoxDevice:
        return self._can_box_device

    def open_can(self):
        """
        对CAN设备进行打开、初始化等操作，并同时开启设备的帧接收线程。
        """
        self._can.open_can()

    def close_can(self):
        """
        关闭USB CAN设备。
        """
        self._can.close_can()

    def stop_transmit(self, message_id: int = None):
        """
        发送CAN帧函数。

        :param message_id: message对象
        """
        self._can.stop_transmit(message_id)

    def resume_transmit(self, message_id: int):
        """
        恢复某一帧数据的发送函数。

        :param message_id:停止发送的Message的ID
        """
        self._can.resume_transmit(message_id)

    def is_open(self) -> bool:
        """
        CAN设备是否被打开

        :return:

            True 打开

            False 关闭
        """
        return self._can.is_open()

    def transmit(self, message: Message):
        """
        发送CAN消息帧

        :param message CAN消息帧，Message对象
        """
        self._can.transmit(message)

    def receive(self, message_id: int) -> Message:
        """
        接收CAN消息

        :param message_id: message的ID

        :return: Message对象
        """
        return self._can.receive(message_id)


class CANService(BaseCan):
    """
    CAN的服务类，主要用于CAN信号的发送，接收等操作。

    参数can_box_device用于指定设备，默认为None，即会依次寻找PCan、Can分析仪以及UsbCan三个设备

    也可以指定某个设备。

    该类可以传入相关的Message消息后，实现自动解析相关的信息计算出一个Message的8 byte的数据值，无需人工计算相关的值。

    该类同时扩展了基础的CAN服务，实现了以下服务

    1、发送message(周期/事件/周期事件)

    2、发送设置好的8 byte数据， 或者根据设置的signal来发送数据

    3、接收message数据，或者接收message的signal数据

    4、判断message是否丢失、判断CAN总线是否丢失、判断signal是否有变化

    5、获取/清除CAN总线上收到的数据、分析CAN消息上的数据

    6、根据message(即矩阵表)随机发送can上消息

    PS: message矩阵表为解析DBC文件生成（该工具为另外一个工具)

    """

    def __init__(self, messages: (str, list), encoding: str = "utf-8",
                 can_box_device: CanBoxDevice = None):
        super().__init__(can_box_device)
        logger.debug(f"read message from file {messages}")
        self.__messages, self.__name_messages = get_message(messages, encoding=encoding)
        # 备份message, 可以作为初始值发送
        self.__backup_messages = copy.deepcopy(self.__messages)
        self.__backup_name_messages = copy.deepcopy(self.__name_messages)
        # 用于记录当前栈中msg的最后一个数据的时间点
        self.__last_msg_time_in_stack = dict()

    @property
    def name_messages(self) -> dict:
        return self.__name_messages

    @property
    def messages(self) -> dict:
        return self.__messages

    def __restore_default_message(self):
        """
        恢复初始的message值
        """
        self.__messages = copy.deepcopy(self.__backup_messages)
        self.__name_messages = copy.deepcopy(self.__backup_name_messages)

    def __set_message(self, msg_id: int, data: list) -> Message:
        """
        :param msg_id: 消息ID

        :param data: 数据

        :return: Message对象
        """
        msg = self.messages[msg_id]
        msg.data = data
        msg.update(False)
        return msg

    @staticmethod
    def __is_message_in_node(message: Message, filter_sender: (str, tuple)) -> bool:
        sender = message.sender.lower()
        if isinstance(filter_sender, str):
            return sender == filter_sender.lower()
        elif isinstance(filter_sender, tuple):
            for item in filter_sender:
                if sender == item.lower():
                    return True
            return False

    def __filter_messages(self, filter_sender: (str, tuple) = None, filter_nm: bool = True,
                          filter_diag: bool = True) -> list:
        """
        根据条件过滤相应的消息帧
        :param filter_sender: 根据节点名称过滤
        :param filter_nm: 是否过滤网络管理帧
        :param filter_diag: 是否过滤诊断帧
        :return: 过滤后的消息
        """
        messages = []
        for msg_id, message in self.messages.items():
            if filter_sender:
                is_filter_sender = self.__is_message_in_node(message, filter_sender)
            else:
                is_filter_sender = False
            is_diag_message = filter_nm and (message.diag_request or message.diag_response or message.diag_state)
            is_nm_message = filter_diag and message.nm_message
            if not (is_filter_sender or is_diag_message or is_nm_message):
                messages.append(message)
        return messages

    def __send_message(self, message: Message, default_message: dict = None, is_default_value: bool = False):
        """
        计算值并发送消息
        :param message: 消息
        :param default_message: 默认发送的消息
        """
        msg_id = message.msg_id
        # 默认值优先，所以需要当不发默认值的时候才启用该函数
        if not is_default_value and default_message and msg_id in default_message:
            for sig_name, sig in message.signals.items():
                if sig_name in default_message[msg_id]:
                    sig.value = default_message[msg_id][sig_name]
                else:
                    max_value = 2 ** sig.bit_length - 1
                    value = random.randint(0, max_value)
                    logger.trace(f"value is [{value}]")
                    sig.value = value
        else:
            # 当不需要发送默认值的时候，就发随机值
            if not is_default_value:
                for sig_name, sig in message.signals.items():
                    max_value = 2 ** sig.bit_length - 1
                    value = random.randint(0, max_value)
                    logger.trace(f"value is [{value}]")
                    sig.value = value
        # 避免错误发生后不再发送数据，容错处理
        try:
            logger.trace(f"sender is {message.sender}")
            self.send_can_message(message)
        except RuntimeError as e:
            logger.error(f"transmit message {hex(msg_id)} failed, error is {e}")

    def __send_messages(self, messages: list, interval: float = 0, default_message: dict = None):
        for message in messages:
            self.__send_message(message, default_message)
        if interval > 0:
            sleep(interval)

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

    def send_can_message(self, send_msg: Message, type_: bool = False):
        """
        直接发送的Message对象数据，可以选择8byte数据发送和signals数据发送两种方式，默认使用signals方式构建数据

        :param send_msg: Message对象

        :param type_: 发送类型（默认使用Signals方式)

            True： 8byte数据发送

            False: signals方式发送
        """
        send_msg.check_message(type_)
        if not type_:
            send_msg.update(True)
        logger.debug(f"msg Id {hex(send_msg.msg_id)}, msg data is {list(map(lambda x: hex(x), send_msg.data))}")
        self.transmit(send_msg)

    def receive_can_message(self, message_id: int) -> Message:
        """
        接收在CAN上收到的Message消息，当能够在内置的messages对象中查询到则能够查询到具体的signals的值，否则只能查询到8byte数据

        :param message_id: message id值

        :return: Message对象
        """
        receive_msg = self.receive(message_id)
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
        stack = self._can.get_stack()
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
        return len(self._can.get_stack()) == 0

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
        stack = self._can.get_stack()
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
        stack = self._can.get_stack()
        # 过滤掉没有用的数据
        data_list = list(filter(lambda x: x.msg_id == msg_id, stack))
        duplicate = set()
        for message in data_list:
            signal = message.signals[signal_name]
            duplicate.add(signal.value)
        return len(duplicate) > 1

    def clear_stack_data(self):
        """
        清除栈数据
        """
        # 清除message记录的时间
        self.__last_msg_time_in_stack.clear()
        self._can.clear_stack_data()

    def get_stack(self) -> list:
        """
        获取当前栈中所收到的消息

        :return:  栈中数据List<Message>
        """
        return self._can.get_stack()

    def check_signal_value(self, stack: list, msg_id: int, sig_name: str, expect_value: int, count: int = None,
                           exact: bool = True):
        """
        检查signal的值是否符合要求

        :param exact: 是否精确对比

        :param msg_id: msg id

        :param sig_name:  sig name

        :param expect_value: expect value

        :param count: 检查数量

        :param stack: 栈中消息
        """
        if count:
            # 过滤需要的msg
            filter_messages = list(filter(lambda x: x.msg_id == msg_id, stack))
            logger.debug(f"filter messages length is {len(filter_messages)}")
            msg_count = 0
            for msg in filter_messages:
                logger.debug(f"msg data = {msg.data}")
                # 此时的msg只有data，需要调用方法更新内容
                message = self.__set_message(msg.msg_id, msg.data)
                actual_value = message.signals[sig_name].physical_value
                logger.debug(f"actual_value = {actual_value}")
                if actual_value == expect_value:
                    msg_count += 1
            logger.info(f"except count is {count}, actual count = {msg_count}")
            if exact:
                return msg_count == count
            else:
                return msg_count >= count
        else:
            # 直接读取can上的最后的值
            actual_value = self.receive_can_message_signal_value(msg_id, sig_name)
            logger.info(f"current value is {actual_value}, expect value is {expect_value}")
            return expect_value == actual_value

    def send_random(self, filter_sender: (str, tuple) = None, cycle_time: int = None, interval: float = 0.1,
                    default_message: dict = None, filter_nm: bool = True, filter_diag: bool = True):
        """
        随机发送信号

        1、不发送诊断帧和网络管理帧

        2、信号的值随机设置

        3、需要过滤指定的发送者

        :param default_message: 固定要发送的信号 {0x152: {"aaa": 0x1, "bbb": 0xc}, 0x119: {"ccc": 0x1, "ddd": 0x2}}

        :param filter_sender: 过滤发送者，如HU。支持单个或者多个节点

        :param cycle_time: 循环次数，默认1000万次

        :param interval: 每轮信号值改变的间隔时间，默认是0.1秒

        :param filter_nm: 是否过滤网络管理报文

        :param filter_diag: 是否过滤诊断报文
        """
        messages = self.__filter_messages(filter_sender, filter_nm, filter_diag)
        if cycle_time:
            for i in range(cycle_time):
                logger.info(f"The {i + 1} time set random value")
                self.__send_messages(messages, interval, default_message)
        else:
            while True:
                self.__send_messages(messages, interval, default_message)

    def send_messages(self, filter_sender: (str, tuple) = None):
        """
        发送除了filter_sender之外的所有信号，该方法用于发送出测试对象之外的所有信号

        :param filter_sender: 过滤发送者，如HU。支持单个或者多个节点
        """
        messages = self.__filter_messages(filter_sender)
        self.__send_messages(messages)

    def send_default_messages(self, node_name: (str, tuple) = None):
        """
        发送除了node_name之外的所有信号的默认数据，该方法用于发送出测试对象之外的所有信号

        :param node_name: 测试对象节点名称
        """
        self.__restore_default_message()
        self.send_messages(node_name)
