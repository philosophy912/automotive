# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2021, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        testcase.py
# @Author:      lizhe
# @Created:     2021/7/3 - 23:07
# --------------------------------------------------------
import importlib
from typing import Dict, List

from automotive.application.common.constants import Testcase
from automotive.application.common.enums import FileTypeEnum
from automotive.application.common.interfaces import BaseReader, BaseWriter, TestCases
from automotive.logger.logger import logger
from .writer.testcase_writer import write_to_template_file


class TestCaseGenerator(object):

    @staticmethod
    def __get_reader(file: str, is_sample: bool) -> BaseReader:
        file_type = FileTypeEnum.from_extends(file)
        module_name, class_name, extends_names = file_type.value
        if is_sample:
            reader = f"automotive.application.testcase.reader.{module_name}_reader_sample"
        else:
            reader = f"automotive.application.testcase.reader.{module_name}_reader"
        module = importlib.import_module(reader)
        if is_sample:
            return getattr(module, f"{class_name}SampleReader")()
        else:
            return getattr(module, f"{class_name}Reader")()

    @staticmethod
    def __get_writer(file: str, is_sample: bool) -> BaseWriter:
        file_type = FileTypeEnum.from_extends(file)
        module_name, class_name, extends_names = file_type.value
        if is_sample:
            writer = f"automotive.application.testcase.writer.{module_name}_writer_sample"
        else:
            writer = f"automotive.application.testcase.writer.{module_name}_writer"
        module = importlib.import_module(writer)
        if is_sample:
            return getattr(module, f"{class_name}SampleWriter")()
        else:
            return getattr(module, f"{class_name}Writer")()

    @staticmethod
    def __check_sample_file(file1: str, file2: str):
        file_type1 = FileTypeEnum.from_extends(file1)
        file_type2 = FileTypeEnum.from_extends(file2)
        condition1 = file_type1 == FileTypeEnum.XMIND8 and file_type2 == FileTypeEnum.STANDARD_EXCEL
        condition2 = file_type1 == FileTypeEnum.STANDARD_EXCEL and file_type2 == FileTypeEnum.XMIND8
        if not (condition1 or condition2):
            raise RuntimeError("简版输入只支持Excel和xmind互转")

    def __compare(self, file1: str, file2: str):
        """
        找出两个文件之间的差别，仅支持xmind和excel两种格式
        """
        testcase1 = self.__get_testcases(file1)
        testcase2 = self.__get_testcases(file2)
        key = list(testcase1.keys())[0]
        testcases1 = testcase1.get(key)
        testcases2 = testcase2.get(key)
        self.__get_different(testcases1, testcases2)

    @staticmethod
    def __print_testcases(testcases: Dict[str, List[Testcase]]):
        for key, value in testcases.items():
            for tc in value:
                print(tc)

    def __get_testcases(self, file: str) -> Dict[str, List[Testcase]]:
        file_type = FileTypeEnum.from_extends(file)
        available_types = FileTypeEnum.XMIND8, FileTypeEnum.STANDARD_EXCEL
        if file_type not in available_types:
            raise RuntimeError("简版比较只支持Excel和xmind")
        reader = self.__get_reader(file, is_sample=True)
        testcase = reader.read_from_file(file)
        if len(testcase.keys()) != 1:
            raise RuntimeError(f"{file}有多个模块，目前仅支持一个模块")
        else:
            return testcase

    @staticmethod
    def __get_different(testcases1: List[Testcase], testcases2: List[Testcase]) -> List[Testcase]:
        result = []
        different = []
        for testcase1 in testcases1:
            flag = False
            for testcase2 in testcases2:
                # 表示testcase没有修改
                if testcase1.identify == testcase2.identify:
                    flag = True
            if not flag:
                # 表示testcase有修改，找不到
                different.append(testcase1)
        # 去掉名字重算
        for testcase in testcases2:
            testcase.calc_hash_value()
        for diff in different:
            diff.calc_hash_value()
            flag = False
            for testcase in testcases2:
                if testcase.identify == diff.identify:
                    flag = True
            if not flag:
                result.append(diff)
        return result

    def get_testcases(self, file: str, is_sample: bool = True) -> Dict[str, TestCases]:
        """
        获取测试用例
        :param file: 输入文件
        :param is_sample: 简版输入，读取的时候会重新组织内容
        :return:
        """
        reader = self.__get_reader(file, is_sample)
        return reader.read_from_file(file)

    def generator(self, in_file: str, out_file: str, is_sample: bool = True):
        """

        :param in_file: 输入的文件

        :param out_file: 输出的文件

        :param is_sample: 简版输入，读取的时候会重新组织内容
        """

        if is_sample:
            self.__check_sample_file(in_file, out_file)
        reader = self.__get_reader(in_file, is_sample)
        writer = self.__get_writer(out_file, is_sample)
        testcases = reader.read_from_file(in_file)
        logger.debug(f"testcases is {testcases}")
        writer.write_to_file(out_file, testcases)
        logger.info(f"read testcase from [{in_file}] and write to file [{out_file}]")

    def write_template(self, in_file: str, output_file: str = None, is_sample: bool = True):
        """
        测试用例直接写入到java版本测试用例生成器中

        :param in_file: xmind文件或者excel文件

        :param output_file: 生成的template文件

        :param is_sample: 简版输入，读取的时候会重新组织内容
        """
        testcases = self.get_testcases(in_file, is_sample=is_sample)
        write_to_template_file(testcases, output_file)
