# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2021, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        constants.py
# @Author:      lizhe
# @Created:     2021/11/18 - 20:51
# --------------------------------------------------------
import hashlib

from automotive.logger.logger import logger

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
module_prefix = "[M]"
requirement_prefix = "[R]"
automation_prefix = "[A]"
results = "PASS", "FAIL", "BLOCK", "NT"
index_list = list(map(lambda x: f"{x}", [x + 1 for x in range(9)]))

TEXT = "text"
ON = "on"
OFF = "off"
VALUES = "values"
ACTIONS = "actions"
CHECK_MSGS = "check_msgs"
OPEN_DEVICE = "open_device", "打开设备"
CLOSE_DEVICE = "close_device", "关闭设备"
CLEAR_STACK = "clear_stack", "清除数据"
DEFAULT_MESSAGE = "default_message", "发送默认消息"
BUS_LOST = "bus_lost", "总线丢失"
MESSAGE_LOST = "message_lost", "要丢失信号"
CHECK_MESSAGE = "check_message", "检查发送消息"
EXACT_SEARCH = "exact_search", "精确查找"
SEARCH_COUNT = "search_count", "出现次数"
SIGNAL_VALUE = "signal_value", "信号值"
SIGNAL_NAME = "signal_name", "信号名称"
MESSAGE_ID = "message_id", "帧ID"
COMMON = "公共"
YES_OR_NO = "是", "否"


class Testcase(object):

    def __init__(self):
        # 唯一标识符
        self.identify = ""
        # 分类
        self.category = ""
        # 模块名 禅道的模块名只会去解析(#93)，前面的内容可以随便填写
        self.module = None
        # 禅道的模块编号
        self.module_id = ""
        # 需求内容
        self.requirement = None
        # 禅道的需求编号
        self.requirement_id = ""
        # 测试用例名字
        self.name = ""
        # 前置条件
        self.pre_condition = []
        # 执行步骤
        self.steps = dict()
        # 执行步骤
        self.actions = None
        # 期望结果
        self.exceptions = None
        # 优先级
        self.priority = None
        # 关键词
        self.keywords = ""
        # 用例类型
        self.test_case_type = "功能测试"
        # 适用阶段
        self.phase = "系统测试阶段"
        # 用例状态
        self.status = "正常"
        # 是否自动化
        self.automation = None
        # 测试结果
        self.test_result = None

    def __str__(self):
        values = []
        # exclude = "category", "module", "module_id", "requirement_id", "keywords", "test_case_type", "phase", "status"
        exclude = []
        for key, value in self.__dict__.items():
            if key not in exclude:
                values.append(f"{key}={value}")
        return ",".join(values)

    def calc_hash(self):
        # total = [self.name]
        total = []
        if self.priority:
            total.append(f"{self.priority}")
        if self.pre_condition:
            total.extend(self.pre_condition)
        for key, value in self.steps.items():
            total.append(key)
            total.extend(value)
        if self.requirement:
            for requirement in self.requirement:
                total.append(requirement)
        if self.requirement_id:
            total.append(self.requirement_id)
        if self.module:
            total.append(self.module)
        if self.actions:
            for action in self.actions:
                total.append(action)
        if self.exceptions:
            for exception in self.exceptions:
                total.append(exception)
        logger.trace(f"total is {total}")
        total_str = "".join(total)
        self.identify = hashlib.md5(total_str.encode(encoding='UTF-8')).hexdigest()

    def calc_hash_value(self):
        total = []
        if self.requirement:
            total.append(self.requirement)
        if self.pre_condition:
            total.extend(self.pre_condition)
        if self.priority:
            total.append(f"{self.priority}")
        for key, value in self.steps.items():
            total.append(key)
            total.extend(value)
        logger.trace(f"total is {total}")
        total_str = "".join(total)
        self.identify = hashlib.md5(total_str.encode(encoding='UTF-8')).hexdigest()


class GuiConfig(object):

    def __init__(self):
        self.name = None
        self.text_name = None
        self.button_type = None
        self.selected = None
        self.unselected = None
        self.items = None
        self.actions = None
        self.tab_name = None
        self.check_msgs = None

    def __str__(self):
        values = []
        # exclude = "category", "module", "module_id", "requirement_id", "keywords", "test_case_type", "phase", "status"
        exclude = []
        for key, value in self.__dict__.items():
            if key not in exclude:
                values.append(f"{key}={value}")
        return ",".join(values)
