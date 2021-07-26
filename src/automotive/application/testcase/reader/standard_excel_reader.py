# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2021, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        standard_excel_reader.py
# @Author:      lizhe
# @Created:     2021/7/3 - 22:14
# --------------------------------------------------------
import os
from typing import Dict, List

from ..api import Reader, Testcase, calc_hash_value, point, priority_config
from automotive.logger.logger import logger

try:
    import xlwings as xw
except ModuleNotFoundError:
    os.system("pip install xlwings")
finally:
    import xlwings as xw
    from xlwings import Sheet, Book


class StandardExcelReader(Reader):

    def __init__(self, ignore_sheet_name: List[str] = "Summary"):
        # 从哪一行开始读取
        self.__start_row = 3
        self.__ignore_sheet_name = ignore_sheet_name

    def read_from_file(self, file: str) -> Dict[str, List[Testcase]]:
        result = dict()
        app = xw.App(visible=False, add_book=False)
        app.display_alerts = False
        app.screen_updating = False
        wb = app.books.open(file)
        sheet_count = wb.sheets.count
        for i in range(sheet_count):
            sheet_name = wb.sheets[i].name
            # 可以过滤SummarySheet页面
            if sheet_name not in self.__ignore_sheet_name:
                self.__handle_sheet(wb, sheet_name, result)
        wb.close()
        app.quit()
        try:
            app.kill()
        except AttributeError:
            logger.debug("app kill fail")
        logger.info("read excel done")
        return result

    def __handle_sheet(self, wb: Book, sheet_name: str, result: Dict[str, List[Testcase]]):
        """
        解析sheet
        :param wb: workbook
        :param sheet_name: sheet name
        :param result: 结果集
        """
        logger.info(f"handle sheet {sheet_name}")
        sheet = wb.sheets[sheet_name]
        testcases = self.__parse_test_case(sheet)
        result[sheet_name] = testcases

    def __parse_test_case(self, sheet: Sheet) -> List[Testcase]:
        """
        逐个解析测试用例
        :param sheet:
        :return: 测试用例
        """
        testcases = []
        max_row = sheet.used_range.last_cell.row
        for i in range(max_row + 1):
            if i > (self.__start_row - 1):
                testcase = Testcase()
                testcase.name = sheet.range(f"B{i}").value
                testcase.module = sheet.range(f"C{i}").value
                testcase.pre_condition = self.__parse_pre_condition(sheet.range(f"D{i}").value)
                testcase.steps = self.__parse_steps(sheet.range(f"E{i}").value, sheet.range(f"F{i}").value)
                testcase.priority = priority_config[sheet.range(f"G{i}").value]
                testcase.identify = calc_hash_value(testcase)
                # 避免空行的存在
                # if testcase.name and testcase.module and len(testcase.pre_condition) > 0 \
                #         and testcase.pre_condition and len(testcase.steps) > 0:
                testcases.append(testcase)
        return testcases

    @staticmethod
    def __filter_automotive(content: str) -> bool:
        return not (content.startswith("0x") or content.startswith("0X"))

    def __parse_pre_condition(self, pre_condition: str) -> List[str]:
        """
        解析前置条件
        :param pre_condition: 前置条件的字符串
        :return:
        """
        logger.debug(f"pre_condition = {pre_condition}")
        contents = []
        if pre_condition:
            pre_conditions = list(filter(lambda x: self.__filter_automotive(x) and x != "", pre_condition.split("\n")))
            pre_conditions = list(map(lambda x: x.replace("、", "."), pre_conditions))
            for pre in pre_conditions:
                if point in pre:
                    pre = pre.replace(point, " ").strip()
                pre = pre[2:].strip()
                logger.debug(f"pre  = {pre}")
                contents.append(pre)
        return contents

    def __parse_steps(self, steps: str, exception: str) -> Dict[str, List[str]]:
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
                    if content[0] == point:
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
                        if e_content[0] == point:
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
