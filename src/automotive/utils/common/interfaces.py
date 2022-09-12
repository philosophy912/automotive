# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2021, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        interfaces.py
# @Author:      lizhe
# @Created:     2021/12/25 - 22:19
# --------------------------------------------------------
import os
from abc import ABCMeta, abstractmethod
from typing import Sequence, Union, Dict

try:
    import xlwings as xw
except ModuleNotFoundError:
    os.system("pip install xlwings")
finally:
    import xlwings as xw
    from xlwings import Sheet, Book, Range

try:
    import openpyxl
except ModuleNotFoundError:
    os.system("pip install openpyxl")
finally:
    import openpyxl
    from openpyxl.worksheet.worksheet import Worksheet
    from openpyxl.cell import Cell
    from openpyxl import Workbook

wb = Union[Workbook, Book]
sht = Union[Worksheet, Sheet]
cell_range = Union[Range, Cell]


class BaseExcelUtils(metaclass=ABCMeta):

    @abstractmethod
    def create_workbook(self) -> wb:
        """
        创建workbook
        :return: Workbook对象
        """
        pass

    @abstractmethod
    def create_sheet(self, workbook: wb, sheet_name: str) -> sht:
        """
        创建sheet
        :param workbook Workbook对象
        :param sheet_name: sheet名称
        :return: sheet
        """
        pass

    @abstractmethod
    def open_workbook(self, file: str) -> wb:
        """
        从文件中读取workbook
        :param file: excel文件
        :return: Workbook对象
        """
        pass

    @abstractmethod
    def get_sheets(self, workbook: wb) -> Sequence[sht]:
        """
        获取所有的sheet
        :param workbook workbook
        :return: sheet对象集合
        """
        pass

    @abstractmethod
    def get_sheet_dict(self, workbook: wb) -> Dict[str, sht]:
        """
        字典类型获取sheet
        :param workbook: workbook
        :return: sheet对象字典对象， [sheet的名字， sheet本身]
        """
        pass

    @abstractmethod
    def get_sheet(self, workbook: wb, sheet_name: str) -> sht:
        """
        根据sheet的序号获取sheet对象
        :param workbook workbook
        :param sheet_name: sheet的名字或者序号
        :return: sheet对象
        """
        pass

    @abstractmethod
    def get_sheet_name(self, sheet: sht) -> str:
        """
        根据sheet获取sheet的名字
        :param sheet:
        :return: sheet名字
        """
        pass

    @abstractmethod
    def copy_sheet(self, workbook: wb, origin_sheet: str, target_sheet: str) -> sht:
        """
        复制sheet
        :param workbook: workbook
        :param origin_sheet: 原始的sheet的名字
        :param target_sheet: 目标sheet名字
        :return: sheet对象
        """
        pass

    @abstractmethod
    def delete_sheet(self, workbook: wb, sheet: str):
        """
        删除sheet
        :param workbook: workbook对象
        :param sheet: sheet名字
        """
        pass

    @abstractmethod
    def get_max_rows(self, sheet: sht) -> int:
        """
        获取sheet的最大行数
        :param sheet:sheet
        :return: 行数
        """
        pass

    @abstractmethod
    def get_max_columns(self, sheet: sht) -> int:
        """
        获取sheet的最大列数
        :param sheet:sheet
        :return: 列数
        """
        pass

    @abstractmethod
    def get_sheet_contents(self, sheet: sht, start_row: int = 1) -> Sequence:
        """
        读取sheet中的所有contents
        :param sheet: sheet
        :param start_row: 从那列开始读
        :return: 内容
        """
        pass

    @abstractmethod
    def set_sheet_contents(self, sheet: sht, contents: Sequence, start_row: int = 1, border: bool = False):
        """
        把contents内容写入到sheet中
        :param sheet:
        :param contents: 内容
        :param start_row: 从那列开始写
        :param border 是否写入边框
        """
        pass

    @abstractmethod
    def get_cell_value(self, sheet: sht, row_index: int, column_index: Union[str, int]) -> str:
        """
        根据行列获取单元格的值
        :param sheet sheet
        :param row_index: 行序号 （从1开始)
        :param column_index: 列序号 (从1开始) 或者列名
        :return: 值
        """
        pass

    @abstractmethod
    def set_cell_value(self, sheet: sht, row_index: int, column_index: Union[str, int], value: str,
                       border: bool = False):
        """
        设置单元格的值
        :param sheet: sheet
        :param row_index: 行序号 （从1开始)
        :param column_index: 列序号 (从1开始)或者列名
        :param value: 值
        :param border 是否写入边框
        """
        pass

    @abstractmethod
    def save_workbook(self, file: str, workbook: wb):
        """
        写入workbook到文件
        :param file:  文件
        :param workbook workbook
        """
        pass

    @abstractmethod
    def close_workbook(self, workbook: wb):
        """
        关闭workbook
        :param workbook: workbook
        """
        pass

    @abstractmethod
    def set_border(self, cell: cell_range):
        """
        设置边框
        :param cell: 单元格
        """
        pass

    @staticmethod
    def _get_column_name(column_index: int) -> str:
        # 根据ascii码来计算列名
        start_value = 64
        max_char = 26
        mods = []
        div, mod = column_index // max_char, column_index % max_char
        # print(div, mod)
        if mod == 0:
            mods.insert(0, chr(max_char + start_value))
            div = div - 1
        else:
            mods.insert(0, chr(mod + start_value))
        while div != 0:
            div, mod = div // max_char, div % max_char
            if mod == 0:
                mods.insert(0, chr(max_char + start_value))
                div = div - 1
            else:
                mods.insert(0, chr(mod + start_value))
        return "".join(mods)

    @staticmethod
    def _get_column_index(column_name: str) -> int:
        start_value = 64
        max_char = 26
        size = len(column_name)
        count = 0
        for i, char_name in enumerate(column_name):
            index = size - i - 1
            char_index = ord(char_name) - start_value
            count += (max_char ** index) * char_index
        return count
