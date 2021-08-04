# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        can_actions.py
# @Author:      lizhe
# @Created:     2021/5/2 - 0:01
# --------------------------------------------------------
from typing import Any, Dict, Tuple, Union, List

from automotive.logger.logger import logger
from automotive.core.can.can_service import CANService
from automotive.common.api import BaseDevice


class CanActions(BaseDevice):
    """
    CAN盒操作类
    """

    def __init__(self, messages: Dict[str, Any]):
        super().__init__()
        self.__can = None
        self.__messages = messages

    @property
    def can_service(self):
        return self.__can

    def open(self):
        """
        打开can
        """
        logger.info("初始化CAN模块")
        self.__can = CANService(self.__messages)
        self.__can.open_can()
        logger.info(f"*************CAN模块初始化成功*************")

    def close(self):
        """
        关闭can
        """
        logger.info("关闭CAN盒子")
        self.__can.close_can()

    def reverse_on(self, signal: Tuple[int, str, int]):
        """
        发送倒档信号

        :param signal: signal配置 如 [0x150, "signal_name", 0x1]
        """
        logger.info(f"发送倒档信号")
        msg = signal[0]
        signal_name = signal[1]
        signal_value = signal[2]
        logger.info(f"发送msg为[{msg}],signal名字为[{signal_name}]，值为[{signal_value}]到CAN总线")
        self.__can.send_can_signal_message(msg, {signal_name, signal_value})

    def send_default_messages(self, node_name: Union[str, List[str]] = None):
        """
        发送除了node_name之外的所有信号的默认数据，该方法用于发送出测试对象之外的所有信号

        :param node_name: 测试对象节点名称
        """
        logger.info(f"发送除了{node_name}之外的所有消息的默认值")
        self.__can.send_default_messages(node_name)

    def send_random_messages(self, filter_sender: Union[str, List[str]] = None, cycle_time: int = None,
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

    def send_can_signal_message(self, msg: Union[int, str], signal: Dict[str, int]):
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

    def receive_can_message_signal_value(self, message_id: int, signal_name: str) -> float:
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
        logger.info(f"检查{hex(msg_id)}中的信号{signal_name}的值是否有变化")
        value = self.__can.is_signal_value_changed(msg_id, signal_name, continue_time)
        logger.info(f"Messages[{hex(msg_id)}]中的信号{signal_name}的值被更改过")
        return value

    def is_can_bus_lost(self, continue_time: int = 5) -> bool:
        """
        can总线是否数据丢失，如果检测周期内有一帧can信号表示can网络没有中断

        :param continue_time: 清空数据，10s内收不到任何的CAN消息表示CAN总线丢失
        """
        logger.info(f"检查CAN总线是否已丢失")
        result = self.__can.is_can_bus_lost(continue_time)
        if result:
            logger.warning(f"**************************检查CAN总线已丢失**************************")
        else:
            logger.info(f"检查CAN总线没有丢失")
        return result
