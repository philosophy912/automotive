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

from automotive.application.common.constants import Testcase, priority_config, point, index_list
from automotive.application.common.interfaces import BaseReader, TestCases
from automotive.logger.logger import logger
from automotive.application.common.enums import ModifyTypeEnum

try:
    import xlwings as xw
except ModuleNotFoundError:
    os.system("pip install xlwings")
finally:
    import xlwings as xw
    from xlwings import Sheet, Book


class StandardExcelSampleReader(BaseReader):

    def __init__(self, ignore_sheet_name: List[str] = None):
        # 从哪一行开始读取
        if ignore_sheet_name is None:
            ignore_sheet_name = ["Summary"]
        self.__start_row = 3
        self.__ignore_sheet_name = ignore_sheet_name

    def read_from_file(self, file: str) -> Dict[str, TestCases]:
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

    def __handle_sheet(self, wb: Book, sheet_name: str, result: Dict[str, TestCases]):
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

    def __parse_test_case(self, sheet: Sheet) -> TestCases:
        """
        逐个解析测试用例
        :param sheet:
        :return: 测试用例
        """
        testcases = []
        # 存放用例ID
        tem = []
        max_row = sheet.used_range.last_cell.row
        for i in range(max_row + 1):
            if i > (self.__start_row - 1):
                testcase = Testcase()
                testcase.name = sheet.range(f"C{i}").value
                index = testcase.name.split('_')[-1]
                if not index.isdigit():
                    raise RuntimeError(f"此条用例名称： {testcase.name} 缺少ID号，请添加")
                tem.append(index)
                testcase.module = sheet.range(f"B{i}").value
                testcase.pre_condition = self.__parse_pre_condition(sheet.range(f"D{i}").value)
                testcase.actions = self.__parse_actions(sheet.range(f"E{i}").value)
                testcase.exceptions = self.__parse_exceptions(sheet.range(f"F{i}").value)
                requirement = sheet.range(f"G{i}").value
                testcase.requirement = requirement.split("\n") if requirement else None
                fix_cell = sheet.range(f"J{i}").value
                if fix_cell is not None:
                    try:
                        testcase.fix = ModifyTypeEnum.read_excel_from_name(fix_cell)
                    except ValueError:
                        logger.debug(f"{fix_cell} is not ModifyTypeEnum")
                automation_cell = sheet.range(f"H{i}").value
                # automation_cell=空“”，automation=None； =是，automation=True；=other，automation=False,只有是，xmind才写入[A]
                testcase.automation = automation_cell == "是" if automation_cell else None
                priority_cell = sheet.range(f"I{i}").value
                testcase.priority = priority_config[priority_cell] if priority_cell else None
                test_result = sheet.range(f"M{i}").value
                testcase.test_result = test_result.strip().upper() if test_result else None
                testcase.calc_hash()
                testcases.append(testcase)
        for i in tem:
            if tem.count(i) > 1:
                raise RuntimeError(f"此ID： {i} 有重复，请检查")
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
            if "\r\n" in pre_condition:
                pre_condition = pre_condition.replace("\r\n", "$")
            # pre_conditions = list(filter(lambda x: self.__filter_automotive(x) and x != "", pre_condition.split("\n")))
            pre_conditions = list(filter(lambda x: x != "", pre_condition.split("\n")))
            pre_conditions = list(map(lambda x: x.replace("、", "."), pre_conditions))
            for pre in pre_conditions:
                # if point in pre:
                #     pre = pre.replace(point, " ").strip()
                # 为了不去掉不带序号的前两个字符
                if pre[0].isdecimal() and pre[:2] != '0x':
                    pre = pre[2:].strip()
                if pre[:2] == "0x":
                    pre = pre
                logger.debug(f"pre  = {pre}")
                if "$" in pre:
                    pre = pre.replace("$", "\r\n")
                contents.append(pre)
        return contents

    def __parse_actions(self, actions: str) -> List[str]:
        total = []
        lines = actions.split("\n")
        temp = []
        for i, line in enumerate(lines):
            if line == '':
                continue
            if line[0] in index_list:
                # temp里装的是，每行带序号的索引（比如有四行：第一行和第三行，带操作步骤序号，temp=[0,2]
                temp.append(i)
        # 没有序号的情况，即只有一个操作步骤
        if temp:
            # 列表切片操作 0 2
            temp.pop(0)
            start_index = 0
            for t in temp:
                content = "\n".join(lines[start_index:t])
                total.append(content)
                start_index = t
            # 把最后一个步骤序号所在行，到最后一行都用\n拼接
            content = "\n".join(lines[start_index:])
            total.append(content)
        else:
            total.append(actions)
        # 处理掉1.类似的数据
        new_total = []
        for t in total:
            content = self.__handle_prefix_str(t)
            new_total.append(content)
        return new_total

    @staticmethod
    def __handle_prefix_str(content: str) -> str:
        """
        处理1. 2.这种前缀，去掉他们
        :param content:
        :return:
        """
        if content[0] in index_list:
            content = content[1:]
            if content[0] in (".", "。", " "):
                content = content[1:]
        return content

    def __parse_exceptions(self, exceptions: str) -> List[str]:
        contents = []
        if exceptions:
            exception_lines = exceptions.split("\r\n")
            for line in exception_lines:
                content = self.__handle_prefix_str(line)
                contents.append(content)
        return contents
