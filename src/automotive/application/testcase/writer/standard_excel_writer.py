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

from automotive.application.common.constants import PRIORITY_CONFIG, COLUMN_CONFIG, RESULTS
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


class StandardExcelWriter(BaseWriter):

    def __init__(self):
        self.__start_row = 3

    def write_to_file(self, file: str, testcases: Dict[str, TestCases], need_format: bool = True):
        """
        把测试用例写入到excel文件中去
        :param file:  输出的excel文件
        :param testcases:  测试用例集合，字典类型
        :param need_format: 是否格式化单元格
        """
        self._check_testcases(testcases)
        logger.debug(f"testcases is {testcases}")
        template = self.__get_template_file()
        app = xw.App(visible=False, add_book=False)
        app.display_alerts = False
        app.screen_updating = False
        workbook = app.books.open(template)
        # 读取summary的sheet
        summary_sheet = workbook.sheets["Summary"]
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
            if need_format:
                # 格式化数据 [特别影响效率，会非常慢]
                self.__format_excel(new_sheet)
                # 写公式
                self.__write_formula(summary_sheet, module, index, "A")
            index += 1
        self.__write_summary(summary_sheet, index)
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
    def __get_template_file(template: str = None):
        if not template:
            logger.debug(__file__)
            # 只考虑windows的情况, 找寻当前文件的文件夹所在路径
            directory, file = os.path.split(__file__)
            template = fr"{directory}\template.xlsx"
        return template

    def __convert_testcases(self, testcases: TestCases) -> Sequence[Tuple]:
        """
        根据模板文件生成相关的内容
        :param testcases: 测试用例列表
        :return: 多维数组  (序号	所属模块  用例名称	子模块名	前置条件	执行步骤	预期结果	需求ID  优先级)
        """
        # 序号 所属模块 用例名称	子模块名	前置条件	执行步骤	预期结果  需求ID	优先级
        result = []
        for i, testcase in enumerate(testcases):
            index = i + 1
            logger.debug(f"The {index} test case is {testcase.name}")
            test_case_name = testcase.name
            sub_module = testcase.module
            module_id = testcase.module_id
            pre_condition = self.__convert_pre_condition(testcase.pre_condition)
            steps, exception = self.__convert_steps_condition(testcase.steps)
            # 增加异常处理exception是None时，导致的startswith报错
            if exception is None:
                exception = ''
            # 考虑exception有异常符号，做替换处理
            if exception.startswith('-') or exception.startswith('_') or exception.startswith(
                    '.') or exception.startswith(' '):
                exception = exception.replace(exception[0], '', 1)
            priority = PRIORITY_CONFIG[int(testcase.priority)] if testcase.priority else ""
            requirement_id = testcase.requirement_id
            # *********************** 如果excel变化，需要修改这里 ***********************
            line = (index, module_id, test_case_name, sub_module, pre_condition,
                    steps, exception, requirement_id, priority)
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

    def __format_excel(self, sheet: Sheet):
        """
        格式化内容
        :return:
        """
        column_range = COLUMN_CONFIG.keys()
        max_row = sheet.used_range.last_cell.row
        # 处理边框
        for i in range(max_row - 1):
            for column in column_range:
                cell_range = sheet.range(f"{column}{i + self.__start_row - 1}")
                # 前置条件 执行步骤 预期结果
                if COLUMN_CONFIG[column] in ("前置条件", "执行步骤", "预期结果"):
                    self.__set_border(cell_range, False)
                else:
                    self.__set_border(cell_range, True)
                # 测试结果
                if COLUMN_CONFIG[column] == "测试结果":
                    self.__set_valid_value(cell_range, RESULTS)

    @staticmethod
    def __set_valid_value(cell_range: Range, values: list):
        """
        设置下拉框
        :param values: 下拉框的值
        """
        formula = ",".join(values)
        cell_range.api.Validation.Add(Type=DVType.xlValidateList, Formula1=formula)

    def __write_formula(self, summary_sheet: Sheet, module: str, index: int, summary_column: str = "H"):
        """
        写模块的公式
        :param summary_sheet:  summary_sheet对象
        :param module: 模块名
        """
        actual_index = index + 2
        cells = {
            "A": (True, False, index),
            "B": (True, False, module),
            "C": (False, False, f'=COUNTIF(INDIRECT($B{actual_index}&"!$L:L"),C$2)'),
            "D": (False, True, f'=$C{actual_index}/$L{actual_index}'),
            "E": (False, False, f'=COUNTIF(INDIRECT($B{actual_index}&"!$L:L"),E$2)'),
            "F": (False, True, f'=$E{actual_index}/$L{actual_index}'),
            "G": (False, False, f'=COUNTIF(INDIRECT($B{actual_index}&"!$L:L"),G$2)'),
            "H": (False, True, f'=$G{actual_index}/$L{actual_index}'),
            "I": (False, False, f'=COUNTIF(INDIRECT($B{actual_index}&"!$L:L"),I$2)'),
            "J": (False, True, f'=$I{actual_index}/$L{actual_index}'),
            "K": (False, False, f'=$C{actual_index}+$E{actual_index}+$G{actual_index}'),
            "L": (False, False, f'=COUNTA(INDIRECT($B{actual_index}&"!${summary_column}:{summary_column}"))-1'),
            "M": (
                False, True,
                f'=($C{actual_index}+$E{actual_index}+$G{actual_index}+$I{actual_index})/$L{actual_index}'),
            "N": (True, False, ""),
            "O": (True, False, "")
        }
        for key, value in cells.items():
            cell_range = summary_sheet.range(f"{key}{actual_index}")
            is_formula, is_percent, cell_value = value
            if is_formula:
                cell_range.value = cell_value
            else:
                cell_range.formula = cell_value
            if is_percent:
                cell_range.api.NumberFormat = "0.00%"
            self.__set_border(cell_range, border_width=3)

    def __write_summary(self, summary_sheet: Sheet, index: int):
        """
        写入统计sheet的模式

        :param summary_sheet: summary_sheet对象
        :param index 序号
        """
        actual_index = index + 2
        # (True, False, "统计"), 第一个True代表是否是数值类，否则是公式，第二个是是否为百分比
        cells = {
            "A": (True, False, "统计"),
            "B": (True, False, ""),
            "C": (False, False, f'=SUM(C3:C{index - 1})'),
            "D": (False, True, f'=$C{actual_index}/$L{actual_index}'),
            "E": (False, False, f'=SUM(E3:E{index - 1})'),
            "F": (False, True, f'=$E{actual_index}/$L{actual_index}'),
            "G": (False, False, f'=SUM(G3:G{index - 1})'),
            "H": (False, True, f'=$G{actual_index}/$L{actual_index}'),
            "I": (False, False, f'=SUM(I3:I{index - 1})'),
            "J": (False, True, f'=$I{actual_index}/$L{actual_index}'),
            "K": (False, False, f'=SUM(K3:K{index - 1})'),
            "L": (False, False, f'=SUM(L3:L{index - 1})'),
            "M": (
                False, True,
                f'=($C{actual_index}+$E{actual_index}+$G{actual_index}+$I{actual_index})/$L{actual_index}'),
            "N": (True, False, ""),
            "O": (True, False, "")
        }
        for key, value in cells.items():
            cell_range = summary_sheet.range(f"{key}{actual_index}")
            is_formula, is_percent, value = value
            if is_formula:
                cell_range.value = value
            else:
                cell_range.formula = value
            if is_percent:
                cell_range.api.NumberFormat = "0.00%"
            self.__set_border(cell_range, border_width=3)

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
                contents.append(f"{i + 1} {pre_condition}")
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
                steps_contents.append(f"{index} {key}")
                value_size = len(value)
                # 用于定义子编号
                if value_size > 0:
                    if value_size == 1:
                        for sub_index, exception in enumerate(value):
                            exception_contents.append(f"{index} {exception}")
                    else:
                        for sub_index, exception in enumerate(value):
                            exception_contents.append(f"{index}.{sub_index + 1} {exception}")
                index += 1
        steps_str = "\n".join(steps_contents)
        exception_str = "\n".join(exception_contents)
        logger.debug(f"exception_str = {exception_str}")
        return steps_str, exception_str

    @staticmethod
    def __set_border(cell_range: Range, is_center: bool = True, border_width: int = None):
        """
        设置边框
        :param cell_range:
        """
        borders = 7, 8, 9, 10
        # 底部边框 9 左边框 7 顶部框 8 右边框 10
        for border in borders:
            cell_range.api.Borders(border).LineStyle = 1
            if border_width:
                cell_range.api.Borders(border).Weight = border_width

        if is_center:
            # 居中显示
            cell_range.api.HorizontalAlignment = -4108
        # 自动换行
        cell_range.api.WrapText = True
