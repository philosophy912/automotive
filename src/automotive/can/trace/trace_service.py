# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, China TSP, All rights reserved
# --------------------------------------------------------
# @Name:        trace_service.py
# @Purpose:     todo
# @Author:      lizhe
# @Created:     2020/6/29 - 11:19
# --------------------------------------------------------

from ..interfaces.can_device import CanBoxDevice
from ..devices.peakcan import PCanBus
from ..devices.usbcan import UsbCanBus
from ..interfaces.can_bus import CanBus
from time import sleep
from loguru import logger
from enum import Enum
from .pcan_reader import PCanReader
from .canoe_reader import CanoeAscReader
from .usb_can_reader import UsbCanReader
from .vspy_reader import VspyReader
from .trace_reader import TraceReader


class TraceType(Enum):
    PCAN = "Pcan"
    USB_CAN = "usbcan"
    SPY3 = "spy3"
    CANOE = "canoe"


class TraceService(object):

    def __init__(self, can_box_device: CanBoxDevice = None):
        self.__can = self.__get_can_bus(can_box_device)

    def __get_can_bus(self, can_box_device: CanBoxDevice) -> CanBus:
        if not can_box_device:
            can_box_device = self.__get_can_box_device()
        if can_box_device == CanBoxDevice.PEAKCAN:
            logger.info("use pcan")
            return PCanBus()
        else:
            logger.info("use can box")
            return UsbCanBus(can_box_device)

    @staticmethod
    def __get_can_box_device() -> CanBoxDevice:
        can = PCanBus()
        can.open_can()
        if can.is_open():
            can.close_can()
            return CanBoxDevice.PEAKCAN
        can = UsbCanBus(can_box_device=CanBoxDevice.CANALYST)
        can.open_can()
        if can.is_open():
            can.close_can()
            return CanBoxDevice.CANALYST
        can = UsbCanBus(can_box_device=CanBoxDevice.USBCAN)
        can.open_can()
        if can.is_open():
            can.close_can()
            return CanBoxDevice.USBCAN
        raise RuntimeError("no device found")

    @staticmethod
    def __get_reader(trace_type: TraceType) -> TraceReader:
        if trace_type == TraceType.PCAN:
            return PCanReader()
        elif trace_type == TraceType.CANOE:
            return CanoeAscReader()
        elif trace_type == TraceType.USB_CAN:
            return UsbCanReader()
        elif trace_type == TraceType.SPY3:
            return VspyReader()

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

    def send_trace(self, file: str, trace_type: TraceType):
        reader = self.__get_reader(trace_type)
        logger.info(f"read all messages in trace file[{file}]")
        traces = reader.read(file)
        logger.info(f"done read work, it will send {len(traces)} messages")
        # 初始的时间
        current_time = None
        logger.info("start to send message")
        count = 1
        while len(traces) > 0:
            trace_time, message = traces[0]
            logger.debug(f"{trace_time}, {current_time}")
            # 是否是第一个
            if current_time:
                interval = trace_time - current_time
                logger.debug(f"sleep {interval} seconds")
                sleep(interval)
            current_time = trace_time
            logger.info(f"transmit the {count} message")
            try:
                self.__can.transmit_one(message)
            except RuntimeError:
                logger.error(f"the {count} message transmit failed")
            traces.pop(0)
            count += 1
        logger.info("message send done")
