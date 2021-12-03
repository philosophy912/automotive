# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2021, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        zentao_csv_writer.py
# @Author:      lizhe
# @Created:     2021/7/3 - 22:51
# --------------------------------------------------------
import csv
from typing import Dict, List, Tuple

from automotive.application.common.interfaces import BaseWriter, TestCases
from automotive.logger.logger import logger


class ZentaoCsvWriter(BaseWriter):
    def write_to_file(self, file: str, testcases: Dict[str, TestCases]):
        """
        把测试用例写入到excel文件中去

        :param file:  输出的csv文件所在的路径

        :param testcases:  测试用例集合，字典类型
        """
        self._check_testcases(testcases)
        file_header = "所属模块", "用例标题", "步骤", "预期", "关键词", "用例类型", "优先级", "用例状态", \
                      "适用阶段", "前置条件", "相关需求"
        for module, testcase in testcases.items():
            logger.debug(f"module name = {module}")
            contents = self.__convert_csv_testcases(module, testcase)
            with open(file, "w", encoding="gbk", newline="") as f:
                f_csv = csv.writer(f)
                f_csv.writerow(file_header)
                f_csv.writerows(contents)

    def __convert_csv_testcases(self, module: str, testcases: TestCases) -> List[List[str]]:
        """
        根据模板文件生成相关的内容
        :param testcases: 测试用例列表
        :return: 多维数组  ("所属模块", "用例标题", "步骤", "预期", "关键词", "用例类型", "优先级", "用例状态",
        "适用阶段", "前置条件", "相关需求")
        """
        # "所属模块", "用例标题", "步骤", "预期", "关键词", "用例类型", "优先级", "用例状态", "适用阶段", "前置条件", "相关需求"
        result = []
        for i, testcase in enumerate(testcases):
            index = i + 1
            logger.debug(f"The {index} test case is {testcase.name}")
            sub_module = testcase.module
            pre_condition = self.__convert_pre_condition(testcase.pre_condition)
            steps, exception = self.__convert_steps_condition(testcase.steps)
            priority = testcase.priority
            test_case_type = testcase.test_case_type
            keyword = testcase.keywords
            phase = testcase.phase
            status = testcase.status
            n = testcase.name
            # 添加testcase-name异常处理
            if n.startswith('.') or n.startswith('_') or n.startswith('-') \
                    or n.startswith(' '):
                testcase.name = n.replace(n[0], "", 1)
            if sub_module == '':
                test_case_name = f"{testcase.name}"
            else:
                test_case_name = f"{sub_module}-{testcase.name}"
            requirement_id = f"({testcase.requirement_id})"
            # 统一成了字符串格式，方便处理
            # 需要特别处理module
            module_name, module_id = self._get_module(module)
            new_module = f"{module_name}({module_id})"
            line = [new_module, test_case_name, steps, exception, keyword, test_case_type,
                    str(priority), status, phase, pre_condition, requirement_id]
            logger.debug(f"{index} line value is {line}")
            result.append(line)
        return result

    @staticmethod
    def __convert_pre_condition(pre_conditions: List[str]) -> str:
        """
        先把列表加上序号来进行相关的处理
        :param pre_conditions:前置条件列表
        :return: 要写入excel的文字
        """
        if len(pre_conditions) > 0:
            contents = []
            for i, pre_condition in enumerate(pre_conditions):
                contents.append(f"{i + 1} {pre_condition}")
            return "\n".join(contents)
        else:
            return ""

    @staticmethod
    def __convert_steps_condition(steps: Dict[str, List[str]]) -> Tuple[str, str]:
        """
        转换执行步骤和期望结果
        :param steps:
        :return:
        """
        steps_contents = []
        exception_contents = []
        if len(steps) > 0:
            # 用于定义主编号
            index = 1
            for key, value in steps.items():
                steps_contents.append(f"{index} {key}")
                value_size = len(value)
                # 用于定义子编号
                if value_size > 0:
                    if value_size == 1:
                        for sub_index, exception in enumerate(value):
                            if exception.startswith('.') or exception.startswith('_') or exception.startswith('-') \
                                    or exception.startswith(' '):
                                exception = exception.replace(exception[0], "", 1)
                            exception_contents.append(f"{index} {exception}")
                    else:
                        for sub_index, exception in enumerate(value):
                            if exception.startswith('.') or exception.startswith('_') or exception.startswith('-') \
                                    or exception.startswith(' '):
                                exception = exception.replace(exception[0], "", 1)
                            exception_contents.append(f"{index}.{sub_index + 1} {exception}")
                index += 1
        steps_str = "\n".join(steps_contents)
        exception_str = "\n".join(exception_contents)
        return steps_str, exception_str
