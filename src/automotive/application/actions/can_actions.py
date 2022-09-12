# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        can_actions.py
# @Author:      lizhe
# @Created:     2021/5/2 - 0:01
# --------------------------------------------------------
from typing import Any, Dict, Union, Sequence

from automotive.core.can.message import Message
from automotive.logger.logger import logger
from automotive.core.can.can_service import CANService
from ..common.interfaces import BaseDevice
from automotive.core.can.common.enums import CanBoxDeviceEnum


class CanActions(BaseDevice):
    """
    CAN盒操作类， 提供了以下的方法

    1、send_default_messages， 发送过滤CAN总线的默认值，建议过滤掉被测对象发出的消息， (默认过滤了网络管理报文和诊断报文)

    2、send_random_messages， 随机发送CAN信号

    3、send_message 发送CAN信号(根据帧ID和信号值发送消息)

    4、receive_message 接受信号(根据帧ID和信号值接收消息)

    5、check_message 检查信号 (需要手动的获取总线的消息， 建议在操作之前清除消息，并在操作后调用get_messages获取消息)

    6、get_messages 获取总线接收到的所有帧消息

    7、clear_messages 清除总线接收到的所有帧消息

    如果要使用CANService的原生方法，可以使用实例化后的对象.can_service调用， 如

    actions = CanActions(messages)

    action.can_service.send_can_message_by_id_or_name(0x152)
    """

    def __init__(self, messages: Union[str, Dict[str, Any]], can_fd: bool = False,
                 can_box_device: CanBoxDeviceEnum = None):
        """
        初始化类
        :param messages: DBC文件或者转换后的产物
        :param can_fd: 是否CAN FD
        """
        super().__init__()
        self.__can = None
        self.__can_fd = can_fd
        self.__can_box_device = can_box_device
        self.__messages = messages

    @property
    def can_service(self):
        return self.__can

    def open(self):
        """
        打开can
        """
        logger.info("初始化CAN模块")
        if self.__can_fd:
            logger.info(f"使用CAN FD模式")
        else:
            logger.info(f"使用Standard CAN模式")
        self.__can = CANService(self.__messages, can_box_device=self.__can_box_device, can_fd=self.__can_fd)
        self.__can.open_can()
        logger.info(f"*************CAN模块初始化成功*************")

    def close(self):
        """
        关闭can
        """
        logger.info("关闭CAN盒子")
        self.__can.close_can()

    def send_default_messages(self, node_name: Union[str, Sequence[str]] = None):
        """
        发送除了node_name之外的所有信号的默认数据，该方法用于发送出测试对象之外的所有信号

        :param node_name: 测试对象节点名称
        """
        logger.info(f"发送除了{node_name}之外的所有消息的默认值")
        self.__can.send_default_messages(node_name)

    def send_random_messages(self, filter_sender: Union[str, Sequence[str]] = None, cycle_time: int = None,
                             interval: float = 0.1, default_message: Dict[str, str] = None):
        """
        随机发送信号

        :param filter_sender: 过滤发送者，如HU。支持单个或者多个节点

        :param cycle_time: 循环次数

        :param interval: 每轮信号值改变的间隔时间，默认是0.1秒

        :param default_message: 固定要发送的信号 {0x152: {"aaa": 0x1, "bbb": 0xc}, 0x119: {"ccc": 0x1, "ddd": 0x2}}
        """
        text_cycle_time = cycle_time if cycle_time else "无限次"
        logger.info(f"随机发送除了{filter_sender}之外的所有消息的{text_cycle_time}，间隔时间{interval}")
        if default_message:
            logger.info(f"默认消息为{default_message}")
        self.__can.send_random(filter_sender, cycle_time, interval, default_message)

    def send_message(self, msg: Union[int, str], signal: Dict[str, int]):
        """
        根据矩阵表中定义的Messages，来设置并发送message。

        tips：不支持8byte数据发送，如果是8Byte数据请使用send_can_message来发送

        :param msg: msg的名字或者id

        :param signal: 需要修改的信号，其中key是信号名字，value是物理值（如车速50)

            如： {"signal_name1": 0x1, "signal_name2": 0x2}
        """
        msg_id = msg if isinstance(msg, int) else self.__can.name_messages[msg].msg_id
        logger.info(f"发送{hex(msg_id)}, 信号是{signal}")
        self.__can.send_can_signal_message(msg, signal)

    def receive_message(self, message_id: int, signal_name: str) -> float:
        """
        接收CAN上收到的消息并返回指定的signal的值， 如果Message不是在messages中已定义的，则回抛出异常

        :param message_id: message id值

        :param signal_name: 信号的名称

        :return: 查到的指定信号的物理值
        """
        logger.info(f"接收{hex(message_id)}中的信号{signal_name}的值")
        value = self.__can.receive_can_message_signal_value(message_id, signal_name)
        logger.info(f"Message[{hex(message_id)}]中的信号{signal_name}的值是{value}")
        return value

    def check_message(self, stack: Sequence[Message], message_id: int, signal_name: str,
                      expect_value: int, count: int = None, exact: bool = True) -> bool:
        """
        检查信号
        :param stack: 记录的message数据， 调用get_messages方法获取

        :param message_id:  帧ID

        :param signal_name: 信号名字

        :param expect_value: 期望值

        :param count: 应该接收到的数量

        :param exact: 是否

        :return: 正确/错误
        """
        logger.info(f"检查{hex(message_id)}中的信号{signal_name},期望值是{expect_value}")
        if count:
            logger.info(f"该值应该有{count}个")
        result = self.__can.check_signal_value(stack, message_id, signal_name, exact, count, exact)
        if result:
            logger.info("检查结果是通过的")
        else:
            logger.info("检查结果是不通过的")
        return result

    def get_messages(self) -> Sequence[Message]:
        """
        获取总线接收的消息
        :return:
        """
        return self.__can.get_stack()

    def clear_messages(self):
        """
        清除总线接收的消息
        :return:
        """
        self.__can.clear_stack_data()
