# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2021, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        enums.py
# @Author:      lizhe
# @Created:     2021/11/18 - 20:50
# --------------------------------------------------------
from enum import Enum, unique
from automotive.logger.logger import logger


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
    CHECK_BUTTON = "单选按钮", "check_buttons"
    COMBOX_BUTTON = "下拉框", "thread_buttons"
    INPUT_BUTTON = "输入框", "comboxs"
    EVENT_CHECK_BUTTON = "事件单选框", "entries"
    EVENT_BUTTON = "按钮", "buttons"
    RECEIVE_BUTTON = "检查", "receive_buttons"

    @staticmethod
    def from_name(type_: str):
        logger.debug(f"type_ is {type_}")
        for key, item in GuiButtonTypeEnum.__members__.items():
            if type_.strip() == item.value[0]:
                return item
        raise ValueError(f"{type_} can not be found in GuiButtonTypeEnum")
