# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        usb_can_reader.py
# @Author:      lizhe
# @Created:     2021/5/1 - 23:45
# --------------------------------------------------------
import re
from typing import Sequence, Tuple

from automotive.core.can.message import Message
from .trace_reader import TraceReader
from automotive.logger.logger import logger


class UsbCanReader(TraceReader):

    def read(self, file: str) -> Sequence[Tuple[float, Message]]:
        contents = self.__filter_content(file)
        logger.debug(f"trace size = {len(contents)}")
        return self.__convert(contents)

    @staticmethod
    def __filter_content(file: str):
        with open(file, "r") as f:
            lines = f.readlines()
            lines.pop(0)
            return lines

    def __convert(self, contents: Sequence) -> Sequence[Tuple[float, Message]]:
        """
        解析content，并生成message对象
        00345,="09:35:34.992",0x376549,ch1,接收,0x0406,数据帧,标准帧,0x08,x| 06 01 00 00 00 00 00 00
        :param contents:
        :return: List<Message>
        """
        trace = []
        for content in contents:
            time = re.search(r"\d{2}:\d{2}:\d{2}\.\d{3}", content).group(0)
            data = re.search(r"(\s\w{2}){8}", content).group(0).strip().split(" ")
            msg_id = re.search(r"0x\w{4},", content).group(0)[:-1]
            logger.debug(f"{time}, {data}, {msg_id}")
            message = Message()
            message.msg_id = int(msg_id, 16)
            message.data = list(map(lambda x: int(x, 16), data))
            trace.append((self.__get_time(time), message))
        return trace

    @staticmethod
    def __get_time(hex_time):
        splits = hex_time.split(".")
        date_time = splits[0].split(":")
        hour = date_time[0]
        minutes = date_time[1]
        seconds = date_time[2]
        millisecond = splits[1]
        current_time = (int(hour) * 60 * 60 + int(minutes) * 60 + int(seconds)) * 1000 + int(millisecond)
        return current_time / 1000
