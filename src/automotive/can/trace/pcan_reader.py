# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, China TSP, All rights reserved
# --------------------------------------------------------
# @Name:        pcan_reader.py
# @Purpose:     todo
# @Author:      lizhe
# @Created:     2020/6/29 - 9:51
# --------------------------------------------------------
import re
from ..interfaces.message import Message
from .trace_reader import TraceReader
from loguru import logger


class PCanReader(TraceReader):

    def read(self, file: str) -> list:
        contents = self.__filter_content(file)
        logger.debug(f"trace size = {len(contents)}")
        return self.__convert(contents)

    @staticmethod
    def __filter_content(file: str):
        with open(file, "r") as f:
            lines = f.readlines()
            return list(filter(lambda x: "Rx" in x, lines))

    @staticmethod
    def __convert(contents: list) -> list:
        """
        解析content，并生成message对象
             3)    216628.2  Rx         0406  8  06 01 00 00 00 00 00 00
        :param contents:
        :return: List<Message>
        """
        trace = []
        for content in contents:
            time = re.search(r"\s\d+\.\d+\s", content).group(0)
            data = re.search(r"(\s\w{2}){8}", content).group(0).strip().split(" ")
            msg_id = re.search(r"\s\w{4}\s", content).group(0)
            logger.debug(f"{time}, {data}, {msg_id}")
            message = Message()
            message.msg_id = int(msg_id, 16)
            message.data = list(map(lambda x: int(x, 16), data))
            trace.append((float(time)/1000, message))
        return trace
