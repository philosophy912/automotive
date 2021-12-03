# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        trace_playback.py
# @Author:      lizhe
# @Created:     2021/5/1 - 23:42
# --------------------------------------------------------
import importlib
from typing import List, Any, Tuple, Optional
from time import sleep

from automotive.logger.logger import logger
from ..can_service import Can
from ..message import Message
from ..common.enums import CanBoxDeviceEnum, BaudRateEnum, TraceTypeEnum


class TracePlayback(object):
    """
    用于回放CAN设备抓取的trace

    目前支持PCAN、USB_CAN、SPY3（CSV、ASC)和CANoe（ASC)
    """

    def __init__(self, can_box_device: Optional[CanBoxDeviceEnum] = None, baud_rate: BaudRateEnum = BaudRateEnum.HIGH,
                 can_fd: bool = False):
        self.__can = Can(can_box_device=can_box_device, baud_rate=baud_rate, can_fd=can_fd)

    @staticmethod
    def __handle_traces(traces: List[Tuple[float, Message]]) -> List[Tuple[float, Any]]:
        """
        把需要间隔的时间提前计算出来
        :param traces:
        """
        handle_traces = []
        for i, trace in enumerate(traces):
            message = traces[i][1]
            if i == 0:
                handle_traces.append((0, message))
            else:
                # 计算间隔时间
                last_time = traces[i - 1][0]
                current_time = traces[i][0]
                handle_traces.append((current_time - last_time, message))
        return handle_traces

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

    def read_trace(self, file: str, trace_type: TraceTypeEnum) -> List[Tuple[float, Message]]:
        """
        从文件中读取并生成可以发送的trace列表

        :param file: trace文件

        :param trace_type:  存trace的类型，支持vspy3和cantools以及pcan， canoe存的log

        :return: trace 列表
        """
        module_name, class_name = trace_type.value
        # 动态导入模块
        module = importlib.import_module(f"automotive.core.can.trace_reader.{module_name}")
        # 实例化模块的类名
        reader = getattr(module, class_name)()
        logger.info(f"read all messages in trace file[{file}]")
        # 由于统一了接口，调用统一的方法就可以实现读取的功能
        traces = reader.read(file)
        logger.info(f"done read work, it will send {len(traces)} messages")
        return self.__handle_traces(traces)

    def send_trace(self, traces: List[Tuple[float, Message]]):
        """
        回放trace

        :param traces: trace列表
        """
        # 初始的时间
        logger.info("start to send message")
        for index, trace in enumerate(traces):
            sleep_time, msg = trace
            if index != 0:
                sleep(sleep_time)
            try:
                self.__can.transmit_one(msg)
            except RuntimeError:
                logger.error(f"the {index + 1} message transmit failed")
        logger.info("message send done")
