# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        vspy_ase_reader.py
# @Author:      lizhe
# @Created:     2021/5/1 - 23:45
# --------------------------------------------------------
import re
from typing import Sequence, Tuple

from automotive.core.can.message import Message
from .trace_reader import TraceReader
from automotive.logger.logger import logger


class VspyAseReader(TraceReader):

    def read(self, file: str) -> Sequence[Tuple[float, Message]]:
        contents = self.__filter_content(file)
        logger.debug(f"trace size = {len(contents)}")
        return self.__convert(contents)

    @staticmethod
    def __filter_content(file: str):
        with open(file, "r") as f:
            lines = f.readlines()
            return list(filter(lambda x: len(x.split(" ")) >= 28, lines))

    @staticmethod
    def __convert(contents: Sequence) -> Sequence[Tuple[float, Message]]:
        """
        解析content，并生成message对象
        0.000000 0 25C             Tx   d 8 00 00 00 00 00 00 00 00
        :param contents:
        :return: List<Message>
        """
        traces = []
        for content in contents:
            logger.trace(f"content = {content}")
            time = re.search(r"\d+.\d{6}", content).group(0)
            msg_id = re.search(r"\s\w{3}", content).group(0).strip()
            data = re.search(r"(\s\w{2}){8}", content).group(0).strip().split(" ")
            logger.debug(f"{time}, {msg_id}")
            message = Message()
            message.msg_id = int(msg_id, 16)
            message.data = list(map(lambda x: int(x, 16), data))
            traces.append((float(time), message))
        return traces
