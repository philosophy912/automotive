# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2021, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        zentao_csv_reader.py
# @Author:      lizhe
# @Created:     2021/7/3 - 22:31
# --------------------------------------------------------
import csv
from typing import Dict, Sequence

from automotive.application.common.constants import STANDARD_HEADER, Testcase, SPLIT_CHAR, POINT
from automotive.application.common.interfaces import BaseReader, TestCases
from automotive.logger.logger import logger


class ZentaoCsvReader(BaseReader):

    def __init__(self):
        self.__module = None

    def read_from_file(self, file: str) -> Dict[str, TestCases]:
        """
        从csv中读取成测试用例
        :param file: csv文件
        :return: 测试用例集合
        """
        testcases = []
        with open(file, "r", encoding="gbk", newline="") as f:
            f_csv = csv.reader(f)
            header = next(f_csv)
            self.__convert_headers(header)
            logger.debug(f"header = {header}")
            for row in f_csv:
                testcase = self.__parse_line(row)
                testcases.append(testcase)
        return {self.__module: testcases}

    @staticmethod
    def __convert_headers(headers: Sequence[str]):
        """
        转换header为标准headers方便灵活读取
        :param headers:  表头
        """
        for header_name, column_id in STANDARD_HEADER.items():
            for index, header in enumerate(headers):
                if header_name == header:
                    STANDARD_HEADER[header_name] = index

    def __parse_line(self, row: Sequence[str]) -> Testcase:
        """
        每一行解析
        :param row:
        :return:
        """
        module = row[STANDARD_HEADER["所属模块"]]
        # U盘音乐-USB音乐进入方式
        name = row[STANDARD_HEADER["用例标题"]]
        steps = row[STANDARD_HEADER["步骤"]]
        exception = row[STANDARD_HEADER["预期"]]
        keywords = row[STANDARD_HEADER["关键词"]]
        test_case_type = row[STANDARD_HEADER["用例类型"]]
        priority = row[STANDARD_HEADER["优先级"]]
        status = row[STANDARD_HEADER["用例状态"]]
        phase = row[STANDARD_HEADER["适用阶段"]]
        pre_condition = row[STANDARD_HEADER["前置条件"]]
        requirement_id = row[STANDARD_HEADER["相关需求"]]
        testcase = Testcase()
        module, module_id = self._parse_id(module, ("(", ")"))
        self.__module = module
        # 此处的模块是需要name去做拆分的
        name_list = name.split(SPLIT_CHAR)
        testcase.module = SPLIT_CHAR.join(name_list[:-1])
        testcase.module_id = module_id
        # U盘音乐-USB音乐进入方式
        testcase.name = name_list[-1]
        testcase.pre_condition = pre_condition.split("\n")
        testcase.pre_condition = list(map(lambda x: x[2:], testcase.pre_condition))
        testcase.priority = priority
        testcase.test_case_type = test_case_type
        testcase.status = status
        testcase.phase = phase
        testcase.requirement_id = requirement_id
        testcase.keywords = keywords
        testcase.steps = self.__parse_steps(steps, exception)
        return testcase

    def __parse_steps(self, steps: str, exception: str) -> Dict[str, Sequence[str]]:
        """
        解析执行步骤
        :param steps:
        :param exception:
        :return:
        """
        contents = dict()
        if steps and exception:
            steps_list = list(filter(lambda x: self.__filter_automotive(x) and x != "", steps.split("\n")))
            steps_list = list(map(lambda x: x.replace("、", "."), steps_list))
            exceptions = list(filter(lambda x: self.__filter_automotive(x) and x != "", exception.split("\n")))
            exceptions = list(map(lambda x: x.replace("、", "."), exceptions))
            for step in steps_list:
                # 去掉前后的空格
                step = step.strip()
                logger.debug(f"step = [{step}]")
                # 容错，去掉空行
                if step != "":
                    # 找寻序号 固定方式，即第一个字符就是序号， 如： 1.电源ON
                    step_index = step[0]
                    content = step[1:]
                    # 去掉点
                    if content[0] == POINT:
                        content = content[1:]
                    # 去掉空格，因为格式有可能是 1 电源ON
                    content = content.strip()
                    exception_list = []
                    for exc in exceptions:
                        logger.debug(f"exc = [{exc}]")
                        # 找寻序号，固定方式，即第一个字符就是序号
                        e_index = exc[0]
                        e_content = exc[1:]
                        # 去掉点
                        if e_content[0] == POINT:
                            e_content = e_content[1:]
                        # 表示一个步骤有多个期望结果 如 2.1 动态轨迹线不偏移，与静态轨迹线平行
                        # 解析后就变成了e_content = 1 动态轨迹线不偏移，与静态轨迹线平行
                        try:
                            sub_e_index = int(e_content[0])
                            logger.debug(f"sub exception index is {sub_e_index}")
                            e_content = e_content[1:]
                        except ValueError:
                            # 没有子节点
                            logger.debug(f" sub_exception not exist")
                        finally:
                            e_content = e_content.strip()
                        if step_index == e_index:
                            # 配成一堆
                            exception_list.append(e_content)
                    contents[content] = exception_list
        logger.debug(f"steps  = {contents}")
        return contents

    @staticmethod
    def __filter_automotive(content: str) -> bool:
        return not (content.startswith("0x") or content.startswith("0X"))
