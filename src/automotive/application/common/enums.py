# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2021, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        enums.py
# @Author:      lizhe
# @Created:     2021/11/18 - 20:50
# --------------------------------------------------------
from enum import Enum, unique


@unique
class FileTypeEnum(Enum):
    """
    读文件的类型

    """
    XMIND8 = "xmind8", "Xmind8", ("xmind",)

    STANDARD_EXCEL = "standard_excel", "StandardExcel", ("xlsx", "xls")

    ZENTAO_CSV = "zentao_csv", "ZentaoCsv", ("csv",)

    @staticmethod
    def from_extends(file: str):
        for key, item in FileTypeEnum.__members__.items():
            module_name, class_name, extends_names = item.value
            for extends in extends_names:
                if file.endswith(extends):
                    return item
        raise ValueError(f"{file} can not be found in FileTypeEnum")


@unique
class GuiButtonTypeEnum(Enum):
    CHECK_BUTTON = "单选按钮"
    COMBOX_BUTTON = "下拉框"
    INPUT_BUTTON = "输入框"
    EVENT_CHECK_BUTTON = "事件单选框"

    @staticmethod
    def from_name(type_: str):
        for key, item in GuiButtonTypeEnum.__members__.items():
            if type_.strip() == item.value:
                return item
        raise ValueError(f"{type_} can not be found in GuiButtonTypeEnum")
