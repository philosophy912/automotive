# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, China TSP, All rights reserved
# --------------------------------------------------------
# @Name:        trace_service.py
# @Purpose:     Can trace的回访类，未经过严格测试。
# @Author:      lizhe
# @Created:     2020/6/29 - 11:19
# --------------------------------------------------------
import importlib

from automotive.logger.logger import logger
from time import sleep
from enum import Enum
from .api import CanBoxDevice
from .can_service import get_can_bus


class TraceType(Enum):
    """
    枚举类：

        PCAN: PCAN录制的CAN log

        USB_CAN: USB CAN录制的CAN log

        SPY3_CSV: SPY3录制的CAN log(CSV类型)

        SPY3_ASC: SPY3录制的CAN log(ASC类型)

        CANOE_ASC: CANoe录制的CAN log(ASC类型)
    """
    PCAN = "pcan_reader", "PCanReader"
    USB_CAN = "usb_can_reader", "UsbCanReader"
    SPY3_CSV = "vspy_csv_reader", "VspyCsvReader"
    SPY3_ASC = "vspy_ase_reader", "VspyAseReader"
    CANOE_ASC = "canoe_asc_reader", "CanoeAscReader"


class TracePlayback(object):
    """
    用于回放CAN设备抓取的trace

    目前支持PCAN、USB_CAN、SPY3（CSV、ASC)和CANoe（ASC)
    """

    def __init__(self, can_box_device: CanBoxDevice = None):
        self._can_box_device, self.__can = get_can_bus(can_box_device)

    @staticmethod
    def __handle_traces(traces: list) -> list:
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

    def read_trace(self, file: str, trace_type: TraceType) -> list:
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

    def send_trace(self, traces):
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
