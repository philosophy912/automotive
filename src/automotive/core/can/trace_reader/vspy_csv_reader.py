# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, China TSP, All rights reserved
# --------------------------------------------------------
# @Name:        vspy_reader.py
# @Purpose:     todo
# @Author:      lizhe
# @Created:     2020/6/29 - 9:51
# --------------------------------------------------------
from ..message import Message
from .trace_reader import TraceReader
from automotive.logger.logger import logger


class VspyCsvReader(TraceReader):

    def read(self, file: str) -> list:
        contents = self.__filter_content(file)
        logger.debug(f"trace size = {len(contents)}")
        return self.__convert(contents)

    @staticmethod
    def __filter_content(file: str):
        with open(file, "r") as f:
            lines = f.readlines()
            return list(filter(lambda x: len(x.split(",")) >= 23, lines))

    @staticmethod
    def __convert(contents: list) -> list:
        """
        解析content，并生成message对象
        2,0.281,0,67108866,F,T,PDC_1,HS CAN,BCM1,25C,F,F,00,00,00,00,00,00,00,00,,,SysSt_PDC,Off,
        :param contents:
        :return: List<Message>
        """
        traces = []
        for content in contents:
            values = content.split(",")
            try:
                index = int(values[0])
                time = float(values[1])
                msg_id = int(values[9], 16)
                logger.debug(f"{index}, {time}, {msg_id}")
                message = Message()
                message.msg_id = int(msg_id)
                message.data = []
                for i in range(8):
                    message.data.append(int(values[i + 12], 16))
                traces.append((time, message))
            except ValueError:
                logger.debug("skip handle, because index is no integer")
        dates = []
        # 隔一行取一个数据(去掉重复的部分)
        for index, trace in enumerate(traces):
            if index % 2 == 0:
                dates.append(trace)
        return dates
