# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, China TSP, All rights reserved
# --------------------------------------------------------
# @Name:        base_config.py
# @Purpose:     配置类的基类
# @Author:      lizhe
# @Created:     2020/02/05 21:19
# --------------------------------------------------------
from abc import abstractmethod, ABCMeta


class BaseConfig(metaclass=ABCMeta):
    """
    配置类的基类，子类需要实现抽象方法update，即把配置更新到类中
    """

    def _update(self, origin: dict, target: dict, special: str, skip: str = None):
        """
        更新数据，用于读取配置文件之后更新到对象中

        :param origin:  原始字典，实际用途中用到了类的self.__dict__对象

        :param target:  要更新的内容，yml文件中配置的内容

        :param special: 要特殊处理的部分，即字典嵌套字典的部分

        :param skip: 需要跳过的部分
        """
        for key in origin.keys():
            if key in target:
                # special 特殊处理
                if key != special:
                    self.__set_value(key, origin, target, skip)
                else:
                    self.__update_special(origin[special], target[key], skip)

    def __update_special(self, origin: dict, target: dict, skip: str = None):
        """
        特殊处理的部分

        :param origin self.__dict__中对应key的字典

        :param target yml文件中读取到的字典的部分

        :param skip: 需要跳过的部分
        """
        for key in origin.keys():
            if key in target:
                self.__set_value(key, origin, target, skip)

    @staticmethod
    def __set_value(key: str, origin: dict, target: dict, skip: str = None):
        """
        设置值，主要处理None类型（需要区分None和NONE)

        :param key: 键

        :param origin: 原始的字典

        :param target: 目标的字典

        :param skip: 需要跳过的部分
        """

        if "None" == target[key]:
            if skip and key != skip:
                origin[key] = None
        else:
            origin[key] = target[key]

    @abstractmethod
    def update(self, data: dict):
        """
        更新数据，即从yml文件中读取的数据更新到类中

        :param data: 从yml文件中读取到的内容
        """
        pass
