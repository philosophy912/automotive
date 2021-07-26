# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2021, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        testcase.py
# @Author:      lizhe
# @Created:     2021/7/3 - 23:07
# --------------------------------------------------------
import importlib
from typing import List

from automotive.logger.logger import logger

from .api import FileType


class TestCaseGenerator(object):

    def __init__(self):
        self.__input = None
        self.__output = None

    def init_generator(self, input_file_type: FileType, output_file_type: FileType):
        self.__input = input_file_type
        self.__output = output_file_type

    def generator(self, in_file: str, out_file: str):
        """
        :param in_file: 输入的文件
        :param out_file: 输出的文件
        :return:
        """
        if self.__input and self.__output:
            input_module_name, input_class_name, input_extends = self.__input.value
            output_module_name, output_class_name, output_extends = self.__output.value
            if not self.__check_extends(input_extends, in_file):
                raise RuntimeError(f"input file [{in_file}] not in [{input_extends}], please check it ")
            if not self.__check_extends(output_extends, out_file):
                raise RuntimeError(f"output file [{out_file}] not in [{output_extends}], please check it ")
            # 动态导入模块
            reader_module = importlib.import_module(f"automotive.application.testcase.reader.{input_module_name}_reader")
            writer_module = importlib.import_module(f"automotive.application.testcase.writer.{output_module_name}_writer")
            # 实例化模块的类名
            reader = getattr(reader_module, f"{input_class_name}Reader")()
            writer = getattr(writer_module, f"{output_class_name}Writer")()
            testcases = reader.read_from_file(in_file)
            logger.debug(f"testcases is {testcases}")
            writer.write_to_file(out_file, testcases)
            logger.info(f"read testcase from [{in_file}] and write to file [{out_file}]")
        else:
            raise RuntimeError("please run function [{init_generator}] first")

    @staticmethod
    def __check_extends(file_extends: List[str], file: str) -> bool:
        """
        判断扩展名是否符合
        :param file_extends: 扩展名列表
        :param file: 文件名
        """
        for extends in file_extends:
            if file.endswith(extends):
                return True
        return False
