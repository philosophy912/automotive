# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2021, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        constants.py
# @Author:      lizhe
# @Created:     2021/11/18 - 20:51
# --------------------------------------------------------
import hashlib
from typing import Sequence, Dict

from automotive.utils.utils import Utils

from automotive.logger.logger import logger

COLUMN_CONFIG = {"A": "序号",
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

STANDARD_HEADER = {'所属模块': 0,
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

PRIORITY_CONFIG = {1: "A", 2: "B", 3: "C", 4: "D", "A": 1, "B": 2, "C": 3, "D": 4}

FUNCTION_INIT = "__init__"
CLASS_INSTANCE = "instance"
FUNCTION_OPEN = "open"
FUNCTION_CLOSE = "close"
SPLIT_CHAR = "-"
REPLACE_CHAR = "_"
POINT = "."
MODULE_PREFIX = "[M]"
REQUIREMENT_PREFIX = "[R]"
AUTOMATION_PREFIX = "[A]"
RESULTS = "PASS", "FAIL", "BLOCK", "NT"
INDEX_LIST = list(map(lambda x: f"{x}", [x + 1 for x in range(9)]))

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
CHECK_SIGNAL = "check_signal", "检查信号发送值"
EXACT_SEARCH = "exact_search", "精确查找"
SEARCH_COUNT = "search_count", "出现次数"
SIGNAL_VALUE = "signal_value", "信号值"
SIGNAL_VALUES = "signal_values", "信号值"
SIGNAL_NAME = "signal_name", "信号名称"
CHECK_SIGNAL_NAME = "check_signal_name", "检查信号名称"
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
        # 修改记录
        self.fix = None

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


def __get_function_param(function_param: Sequence, config_params: Dict) -> Dict:
    used_params = dict()
    for name, value in config_params.items():
        if name in function_param:
            used_params[name] = value
    return used_params


def get_yml_config(yml_file: str, utils: Utils, open_methods: Sequence, close_methods: Sequence):
    """
    从对应的action.yml文件中读取到要配置的类对象
    从配置文件如
    soc:
      type: SerialPort
      port: COM12
      baud_rate: 115200
      log_folder: d:\test
    返回 soc需要实例化的对象，如SerialPort对象， 并返回open和close的函数名以及参数
    :param close_methods: 关闭的函数名称
    :param open_methods: 打开的函数名称
    :param utils: 实例化后的Utils()对象
    :param yml_file:
    :return:
    {
        "soc" : {
            "instance": (类对象， 初始化__init__需要的参数字典)
            "open": (方法名: 方法所需要的参数)
            "close": (方法名: 方法所需要的参数)
        }
    }
    """
    # 从里面读取内容
    yml_dict = utils.read_yml_full(yml_file)
    # 最终要返回的字典
    result_dict = dict()
    if yml_dict is None:
        return result_dict
    for instance_name, instance_param in yml_dict.items():
        # 每一个配置对应的内容， 如SOC的内容
        typed_dict = dict()
        # 锚定符， 如果没有type，则不会读取内容
        if "type" in instance_param:
            class_name = instance_param["type"]
            logger.debug(f"class_name = {class_name}")
            # 特殊处理，由于CANService的父类才拥有open close方法，所以做一个转换
            if class_name == "CANService":
                # 找到他的父类的方法
                instance_methods = utils.get_param_from_class_name("Can")
            else:
                # 获取类下面的方法
                instance_methods = utils.get_param_from_class_name(class_name)
            class_instance = utils.get_class_from_name(class_name)
            # 去掉type，方便后续做查找
            instance_param.pop("type")
            logger.debug(f"instance_methods size is {len(instance_methods)}")
            # __init__函数的参数
            used_params = dict()
            # 如果存在init函数，则可能存在相关的参数， 如果没有配置，后续可能会执行失败
            if FUNCTION_INIT in instance_methods:
                # 类实例化是需要有参数的，所以需要处理参数
                # 获取init用到的参数
                params = instance_methods[FUNCTION_INIT]
                # 获取到配置的方法中__init__方法用到的参数
                used_params = __get_function_param(params, instance_param)
                # 移出实例化的类进行后续操作
                instance_methods.pop(FUNCTION_INIT)
            # 完成类的实例化
            typed_dict[CLASS_INSTANCE] = class_instance, used_params
            # 只是在open方法列表中查找 后续会涉及到调用部分
            for open_method in open_methods:
                if open_method in instance_methods:
                    open_method_params = instance_methods[open_method]
                    # 获取到配置的方法中用到的参数
                    used_params = __get_function_param(open_method_params, instance_param)
                    typed_dict[FUNCTION_OPEN] = open_method, used_params
                    # 多个只算第一个
                    break
            # 只是在close方法列表中查找，后续会涉及到调用
            for close_method in close_methods:
                if close_method in instance_methods:
                    close_method_params = instance_methods[close_method]
                    # 获取到配置的方法中用到的参数
                    used_params = __get_function_param(close_method_params, instance_param)
                    typed_dict[FUNCTION_CLOSE] = close_method, used_params
                    # 多个只算第一个
                    break
        # 完成一个文件解析
        result_dict[instance_name] = typed_dict
    return result_dict
