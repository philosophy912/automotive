# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        canoe_asc_reader.py
# @Author:      lizhe
# @Created:     2021/5/1 - 23:44
# --------------------------------------------------------
import re
from ..message import Message
from .trace_reader import TraceReader
from automotive.logger.logger import logger


class CanoeAscReader(TraceReader):

    def read(self, file: str) -> list:
        contents = self.__filter_content(file)
        logger.debug(f"trace size = {len(contents)}")
        return self.__convert(contents)

    @staticmethod
    def __filter_content(file: str):
        with open(file, "r") as f:
            lines = f.readlines()
            return list(filter(lambda x: len(x.split(" ")) == 41, lines))

    @staticmethod
    def __convert(contents: list) -> list:
        """
        解析content，并生成message对象
          10.868138 1  406             Rx   d 8 06 01 00 00 00 00 00 00  Length = 237910 BitCount = 123 ID = 1030
        :param contents:
        :return: List<Message>
        """
        trace = []
        for content in contents:
            time = re.search(r"\d+\.\d{6}", content).group(0)
            data = re.search(r"(\s\w{2}){8}", content).group(0).strip().split(" ")
            msg_id = re.search(r"ID\s=\s\d+", content).group(0).split("=")[1]
            logger.debug(f"{time}, {data}, {msg_id}")
            message = Message()
            message.msg_id = int(msg_id)
            message.data = list(map(lambda x: int(x, 16), data))
            trace.append((float(time), message))
        return trace
