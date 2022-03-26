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
class ProjectEnum(Enum):
    """
    项目名称
    """
    # 项目名称   是否执行同步(sync)动作
    GSE_3J2 = "3J2", True
    GSE_3J320 = "3J320", True
    CHANGAN_75A121 = "75A121", False

    @staticmethod
    def from_value(file: str):
        for key, item in ProjectEnum.__members__.items():
            if item.value[0].upper in key:
                return item
        raise ValueError(f"{file} can not be found in ProjectEnum")


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


@unique
class ModifyTypeEnum(Enum):
    """
    用于xmind转excel的判断fix类型
    """
    FIX = "修改", "arrow-refresh"
    ADD = "增加", "symbol-plus"
    DELETE = "删除", "symbol-wrong"

    @staticmethod
    def read_xmind_from_name(flag_: str):
        logger.debug(f"flag_ is {flag_}")
        for key, item in ModifyTypeEnum.__members__.items():
            if flag_.strip() == item.value[1]:
                return item.value[0]
        raise ValueError(f"{flag_} can not be found in ModifyTypeEnum")

    @staticmethod
    def read_excel_from_name(flag_: str):
        logger.debug(f"flag_ is {flag_}")
        for key, item in ModifyTypeEnum.__members__.items():
            if flag_.strip() == item.value[0]:
                return item.value[1]
        raise ValueError(f"{flag_} can not be found in ModifyTypeEnum")
