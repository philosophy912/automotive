# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        trace_reader.py
# @Author:      lizhe
# @Created:     2021/5/1 - 23:45
# --------------------------------------------------------
from abc import ABCMeta, abstractmethod


class TraceReader(metaclass=ABCMeta):

    @abstractmethod
    def read(self, file: str) -> list:
        """
        从文件中读取内容，并生成一个Message对象的列表，
        列表中包含元组， (时间，Message对象)
        :param file: trace文件
        :return: 有序列表
        """
        pass
