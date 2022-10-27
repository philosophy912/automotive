# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2021, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        standard_excel_writer.py
# @Author:      lizhe
# @Created:     2021/7/3 - 22:37
# --------------------------------------------------------
import os
from typing import Dict, Sequence, Tuple

from automotive.application.common.constants import PRIORITY_CONFIG
from automotive.application.common.interfaces import BaseWriter, TestCases
from automotive.logger.logger import logger

try:
    import xlwings as xw
except ModuleNotFoundError:
    os.system("pip install xlwings")
finally:
    import xlwings as xw
    from xlwings import Sheet, Book, Range
    from xlwings.constants import DVType


class StandardExcelSampleWriter(BaseWriter):

    def __init__(self):
        self.__start_row = 3

    def write_to_file(self, file: str, testcases: Dict[str, TestCases], temp_file: str = None):
        """
        把测试用例写入到excel文件中去
        :param file:  输出的excel文件
        :param testcases:  测试用例集合，字典类型
        :param temp_file: 读取的excel模板文件
        """
        self._check_testcases(testcases)
        logger.debug(f"testcases is {testcases}")
        template = self.__get_template_file(template=temp_file)
        app = xw.App(visible=False, add_book=False)
        app.display_alerts = False
        app.screen_updating = False
        workbook = app.books.open(template)
        # 读取summary的sheet
        # summary_sheet = workbook.sheets["Summary"]
        module_sheet = workbook.sheets["模块名"]
        index = 1
        for module, testcase in testcases.items():
            logger.debug(f"module is {module}")
            module_name, module_id = self._get_module(module)
            logger.debug(f"module_name = {module_name} and module_id = {module_id}")
            contents = self.__convert_testcases(testcase)
            logger.info(f"write [{module_name}].........")
            # 从模块名复制出来并重命名为module
            module_sheet.api.Copy(Before=module_sheet.api)
            new_sheet = workbook.sheets['模块名 (2)']
            # 需要注意sheet名字如果有问题，此处不会报错的
            new_sheet.name = module_name
            logger.debug(f"写入sheet名字{new_sheet.name}")
            # 写入内容到excel中并格式化单元格
            self.__write_content_to_cell(new_sheet, contents)
            index += 1
        # 删除module_sheet
        module_sheet.delete()
        workbook.save(file)
        workbook.close()
        app.quit()
        try:
            app.kill()
        except AttributeError:
            logger.debug("app kill fail")
        logger.info(f"write to file [{file}] done")

    @staticmethod
    def __get_template_file(template: str):
        if not template:
            logger.debug(__file__)
            # 只考虑windows的情况, 找寻当前文件的文件夹所在路径
            directory, file = os.path.split(__file__)
            template = fr"{directory}\template_sample.xlsx"
        else:
            if os.path.exists(template):
                template = template
            else:
                raise RuntimeError("传入的excel模板文件：template不存在，请检查")
        return template

    def __convert_testcases(self, testcases: TestCases) -> Sequence[Tuple]:
        """
        根据模板文件生成相关的内容
        :param testcases: 测试用例列表
        :return: 多维数组  (序号 所属模块 用例名称  前置条件	执行步骤	预期结果  对应需求 是否自动化 优先级 修改记录 测试时间 测试人员 测试版本 测试结果 备注 )
        """
        # 序号 所属模块 用例名称  前置条件	执行步骤	预期结果  对应需求 是否自动化 优先级 修改记录 测试时间 测试人员 测试版本 测试结果 备注
        result = []
        for i, testcase in enumerate(testcases):
            index = i + 1
            logger.debug(f"The {index} test case is {testcase.name}")
            test_case_name = testcase.name
            pre_condition = self.__convert_pre_condition(testcase.pre_condition)
            actions = testcase.actions
            exceptions = testcase.exceptions
            fix = testcase.fix
            steps = []
            exception_list = []
            # 只支持两种情况， actions有多个，exceptions只有一个，则表示exceptions对应actions的最后一个步骤
            if exceptions:
                if len(actions) < 1:
                    raise RuntimeError(f"没有操作步骤{actions}")
                if len(actions) != len(exceptions):
                    if len(actions) > 1 and len(exceptions) != 1:
                        # 多操作步骤，多期望结果
                        for j, action in enumerate(actions):
                            steps.append(f"{j + 1}.{action}")
                        for m, exception in enumerate(exceptions):
                            exception_list.append(f"{len(actions)}.{m + 1} {exception}")
                    elif len(actions) == 1 and len(exceptions) > 1:
                        # 一个操作步骤对应多个期望结果
                        steps.append(f"1.{actions[0]}")
                        for j, action in enumerate(exceptions):
                            exception_list.append(f"1.{j + 1} {exceptions[j]}")
                    else:
                        # 多操作步骤，一个期望结果
                        for j, action in enumerate(actions):
                            steps.append(f"{j + 1}.{action}")
                        exception_list.append(f"{len(actions)}.{exceptions[0]}")
                if len(actions) == len(exceptions):
                    # 有可能是一对一，有可能是二对二、三对三
                    if len(actions) == 1 and len(exceptions) == 1:
                        steps.append(f"1.{actions[0]}")
                        exception_list.append(f"1.{exceptions[0]}")
                    else:
                        for j, action in enumerate(actions):
                            steps.append(f"{j + 1}.{action}")
                        for m, exception in enumerate(exceptions):
                            exception_list.append(f"{len(actions)}.{m + 1} {exception}")

            else:
                for j, action in enumerate(actions):
                    steps.append(f"{j + 1}.{action}")

            # 两种情况，一种是step有多个操作步骤，一种情况是step只有一个操作步骤
            steps_str = "\n".join(steps)
            exceptions_str = "\n".join(exception_list)
            priority = PRIORITY_CONFIG[int(testcase.priority)] if testcase.priority else ""
            requirement = "\n".join(testcase.requirement) if testcase.requirement else ""
            if testcase.automation is not None:
                automation = "是"
            else:
                automation = "否"
            test_result = testcase.test_result
            # *********************** 如果excel变化，需要修改这里 ***********************
            line = (index, testcase.category, test_case_name, pre_condition, steps_str, exceptions_str, requirement,
                    automation, priority, fix, "", "", "", test_result, "")
            logger.debug(f"{index} line value is {line}")
            result.append(line)
        return result

    def __write_content_to_cell(self, sheet: Sheet, contents: Sequence[Tuple]):
        """
        一行一行写入数据
        :param sheet: sheet
        :param contents: 数据集
        """

        for index, content in enumerate(contents):
            logger.debug(f"now write the {index} line")
            last_char = chr(ord("A") + len(content))
            row_index = self.__start_row + index
            sheet.range(f'A{row_index}:{last_char}{row_index}').value = content

    @staticmethod
    def __set_valid_value(cell_range: Range, values: list):
        """
        设置下拉框
        :param values: 下拉框的值
        """
        formula = ",".join(values)
        cell_range.api.Validation.Add(Type=DVType.xlValidateList, Formula1=formula)

    @staticmethod
    def __convert_pre_condition(pre_conditions: Sequence[str]) -> str:
        """
        先把列表加上序号来进行相关的处理
        :param pre_conditions:前置条件列表
        :return: 要写入excel的文字
        """
        if len(pre_conditions) > 0:
            contents = []
            for i, pre_condition in enumerate(pre_conditions):
                # 处理加了序号的前提条件，去掉序号
                if pre_condition[0].isdigit() and pre_condition[1] == ".":
                    pre_condition = pre_condition[2:]
                # 加序号
                contents.append(f"{i+1}.{pre_condition}")
            return "\n".join(contents)
        else:
            return ""

    @staticmethod
    def __convert_steps_condition(steps: Dict[str, Sequence[str]]) -> Tuple[str, str]:
        """

        :param steps:
        :return:
        """
        steps_contents = []
        exception_contents = []
        if len(steps) > 0:
            # 用于定义主编号
            index = 1
            for key, value in steps.items():
                if key.startswith("1"):
                    steps_contents.append(f"{key}")
                else:
                    steps_contents.append(f"{index} {key}")
                value_size = len(value)
                # 用于定义子编号
                if value_size > 0:
                    if value_size == 1:
                        for sub_index, exception in enumerate(value):
                            exception_contents.append(f"{index} {exception}")
                    else:
                        for sub_index, exception in enumerate(value):
                            exception_contents.append(f"{sub_index + 1} {exception}")
                index += 1
        steps_str = "\n".join(steps_contents)
        exception_str = "\n".join(exception_contents)
        logger.debug(f"exception_str = {exception_str}")
        return steps_str, exception_str
