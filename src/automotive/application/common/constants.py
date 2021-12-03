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


class Testcase(object):

    def __init__(self):
        # 唯一标识符
        self.identify = ""
        # 分类
        self.category = ""
        # 模块名 禅道的模块名只会去解析(#93)，前面的内容可以随便填写
        self.module = ""
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
        # 是否自动化
        self.automation = False

    def __str__(self):
        values = []
        exclude = "category", "module", "module_id", "requirement_id", "keywords", "test_case_type", "phase", "status"
        for key, value in self.__dict__.items():
            if key not in exclude:
                values.append(f"{key}={value}")
        return ",".join(values)

    def update(self, index: int, category: str):
        # print(self)
        sub_module = []
        # 把模块名变成前置条件
        if not self.pre_condition:
            for i, module in enumerate(self.module.split(split_char)):
                if module.startswith(module_prefix):
                    sub_module.append(module.replace(module_prefix, ""))
                else:
                    self.pre_condition.append(f"{module}")

        # 处理步骤
        if self.steps:
            new_steps = {}
            values = []
            for key, value in self.steps.items():
                # print(f"key = {key}")
                for ex in value:
                    if requirement_prefix in ex:
                        self.requirement = ex.replace(requirement_prefix, "")
                    else:
                        values.append(ex)
                if key.startswith(automation_prefix):
                    self.automation = True
                    new_key = key.replace(automation_prefix, "")
                else:
                    new_key = key
                new_steps[new_key] = values
            self.steps = new_steps
        else:
            if self.name.startswith(automation_prefix):
                self.automation = True
                self.name = self.name.replace(automation_prefix, "")
            self.steps[self.name] = []
        self.category = category.split(split_char)[0]
        self.module = ""
        category = category.replace(split_char, replace_char)
        if sub_module:
            sub_module = replace_char.join(sub_module)
            self.name = f"{category}_{sub_module}_{index + 1}"
        else:
            self.name = f"{category}_{index + 1}"
        # print("after")
        # print(self)

    def convert(self, category: str):
        category = category.replace(split_char, replace_char)
        sub_module_str = self.name.replace(category, "")[1:]
        sub_module = []
        if replace_char in sub_module_str:
            sub_module = sub_module_str.split(replace_char)[:-1]
        if sub_module:
            for module in sub_module:
                self.pre_condition.insert(0, f"{module_prefix}{module}")
        # 把前置条件变成模块名
        self.module = split_char.join(self.pre_condition)
        for key, value in self.steps.items():
            # 把key变成name
            self.name = key
            if self.requirement:
                value.append(f"{requirement_prefix}{self.requirement}")
        self.pre_condition = []

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
            total.append(self.requirement)
        if self.requirement_id:
            total.append(self.requirement_id)
        logger.debug(f"total is {total}")
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
        logger.debug(f"total is {total}")
        total_str = "".join(total)
        self.identify = hashlib.md5(total_str.encode(encoding='UTF-8')).hexdigest()