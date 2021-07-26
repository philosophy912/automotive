# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        __init__.py
# @Author:      lizhe
# @Created:     2021/6/14 - 23:51
# --------------------------------------------------------
import hashlib
from abc import ABCMeta, abstractmethod
from enum import unique, Enum
from typing import Tuple, List, Dict


class Testcase(object):

    def __init__(self):
        # 唯一标识符
        self.identify = ""
        # 模块名 禅道的模块名只会去解析(#93)，前面的内容可以随便填写
        self.module = ""
        # 禅道的模块编号
        self.module_id = ""
        # 禅道的需求编号
        self.requirement_id = ""
        # 测试用例名字
        self.name = ""
        # 前置条件
        self.pre_condition = []
        # 执行步骤
        self.steps = dict()
        # 优先级
        self.priority = 3
        # 关键词
        self.keywords = ""
        # 用例类型
        self.test_case_type = "功能测试"
        # 适用阶段
        self.phase = "系统测试阶段"
        # 用例状态
        self.status = "正常"


@unique
class FileType(Enum):
    """
    读文件的类型

    """
    XMIND8 = "xmind8", "Xmind8", ("xmind",)

    STANDARD_EXCEL = "standard_excel", "StandardExcel", ("xlsx", "xls")

    ZENTAO_CSV = "zentao_csv", "ZentaoCsv", ("csv",)


class Reader(metaclass=ABCMeta):
    @abstractmethod
    def read_from_file(self, file: str) -> Dict[str, List[Testcase]]:
        """
        从文件中读取testCase类
        :param file:  文件
        :return: 读取到的测试用例集合
        """
        pass


class Writer(metaclass=ABCMeta):
    @abstractmethod
    def write_to_file(self, file: str, testcases: Dict[str, List[Testcase]]):
        """
        把测试用例集合写入到文件中
        :param file:  文件
        :param testcases: 测试用例集合
        """
        pass

    @staticmethod
    def _check_testcases(testcases: Dict[str, List[Testcase]]):
        if testcases is None:
            raise RuntimeError("testcases is None")
        if len(testcases) == 0:
            raise RuntimeError("no testcase found")


column_config = {"A": "序号",
                 "B": "用例名称",
                 "C": "子模块名",
                 "D": "前置条件",
                 "E": "执行步骤",
                 "F": "预期结果",
                 "G": "优先级",
                 "H": "功能分期",
                 "I": "测试时间",
                 "J": "测试人员",
                 "K": "测试版本",
                 "L": "测试结果",
                 "M": "备注"}

standard_header = {'所属模块': 0,
                   '用例标题': 1,
                   '步骤': 2,
                   '预期': 3,
                   '关键词': 4,
                   '用例类型': 5,
                   '优先级': 6,
                   '用例状态': 7,
                   '适用阶段': 8,
                   '前置条件': 9,
                   '相关需求': 10}

priority_config = {1: "A", 2: "B", 3: "C", 4: "D", "A": 1, "B": 2, "C": 3, "D": 4}

split_char = "-"
replace_char = "_"
point = "."


def calc_hash_value(testcase: Testcase) -> str:
    """
    根据测试用例计算哈希值以便确定该模块是否有更新
    :return: 哈希值
    """
    if testcase.priority:
        total = f"{testcase.name}{testcase.module}{testcase.priority}"
    else:
        total = f"{testcase.name}{testcase.module}"
    # 前置条件
    precondition = "".join(testcase.pre_condition)
    steps = ""
    for key, value in testcase.steps.items():
        steps += f"{key}{value}"
    total = f"{total}{precondition}{steps}"
    return hashlib.md5(total.encode(encoding='UTF-8')).hexdigest()


def parse_id(content: str, split_character: Tuple[str, str] = ("[", "]")) -> Tuple[str, str]:
    """
    用于解析数据如 在线音乐[#93] 用以适配禅道的需求导入
    :param split_character: 左右分隔符
    :param content: 模块名
    :return: 在线音乐[#93] -> 在线音乐#93
    """
    content = content.strip()
    left, right = split_character
    if left in content:
        index = content.index(left)
        module = content[:index]
        if content.endswith(right):
            module_id = content[index + 1:-1]
        else:
            module_id = content[index + 1:]
        return module, module_id
    else:
        return content, ""


def get_module(module: str) -> Tuple[str, str]:
    """
    用于解析module
    :param module:
    :return: module和module_id
    """
    if replace_char in module:
        module_list = module.split(replace_char)
        return module_list[0], module_list[1]
    else:
        return module, ""
