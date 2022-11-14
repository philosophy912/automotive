# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        constants.py
# @Author:      lizhe
# @Created:     2022/11/1 - 13:13
# --------------------------------------------------------
from typing import Sequence, Dict

from automotive.logger.logger import logger
from automotive.utils.utils import Utils

CLASS_INSTANCE = "instance"
FUNCTION_OPEN = "open"
FUNCTION_CLOSE = "close"
FUNCTION_INIT = "__init__"


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
                instance_methods.update(utils.get_param_from_class_name(class_name))
            else:
                # 获取类下面的方法
                instance_methods = utils.get_param_from_class_name(class_name)
            class_instance = utils.get_class_from_name(class_name)
            # 去掉type，方便后续做查找
            instance_param.pop("type")
            logger.debug(f"instance_methods size is {len(instance_methods)}")
            logger.debug(f"instance_methods is {instance_methods}")
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
