# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, China TSP, All rights reserved
# --------------------------------------------------------
# @Name:        test_case.py
# @Purpose:     todo
# @Author:      lizhe
# @Created:     2020/02/06 22:31
# --------------------------------------------------------
from .service import Service


class OnOffTestCase(object):
    """
    测试用例类，主要用于配置测试用例
    """

    def __init__(self):
        # 前置准备
        self.prepare = None
        # 前置条件
        self.precondition = None
        # 操作步骤
        self.step = None
        # 结果操作
        self.result = None

    def __check_result(self):
        """
        检查result
        """
        if not isinstance(self.result, list):
            raise ValueError("result需要是列表模式，且列表为字典或者字符串格式.")
        else:
            self.__check_actions(self.result)

    def __check_step(self):
        """
        检查step
        """
        if "loop_time" not in self.step:
            raise ValueError(f"loop_time not exist in step, please check it.")
        loop_time = self.step["loop_time"]
        if not isinstance(loop_time, int) and loop_time < 1:
            raise ValueError(f"loop_time should be int but now {loop_time}")
        if "loop" not in self.step:
            raise ValueError(f"loop not exist in step, please check it.")
        loop = self.step["loop"]
        if not isinstance(loop, list):
            raise ValueError("loop需要是列表模式，且列表为字典或者字符串格式.")
        else:
            self.__check_actions(loop)

    def __check_precondition(self):
        """
        检查precondition
        """
        if not isinstance(self.precondition, list):
            raise ValueError("precondition需要是列表模式，且列表为字典或者字符串格式.")
        else:
            self.__check_actions(self.precondition)

    def __check_prepare(self):
        """
        检查prepare
        """
        if not isinstance(self.prepare, list):
            raise ValueError("prepare需要是列表模式，且列表为字典或者字符串格式.")
        else:
            self.__check_actions(self.prepare)

    @staticmethod
    def __check_actions(parts: list):
        """
        检查函数名是否属于OnOffService中

        :param parts: 测试用例的步骤
        """
        functions = dir(Service)
        for part in parts:
            if isinstance(part, str):
                if part not in functions:
                    raise ValueError(f"method [{part}] no support.")
            elif isinstance(part, dict):
                for key in part.keys():
                    if key not in functions:
                        raise ValueError(f"method [{key}] no support.")

    def update(self, test_case: dict):
        """
        从yml文件读取的内容更新到test case类的属性中

        :param test_case: 从yml文件读取出来的内容
        """
        # 检查是否有prepare
        try:
            self.prepare = test_case["prepare"]
        except KeyError:
            raise ValueError(f"prepare not exist, please check it.")
        # 检查是否有precondition
        try:
            self.precondition = test_case["precondition"]
        except KeyError:
            raise ValueError(f"precondition not exist, please check it.")
        # 检查是否有step
        try:
            self.step = test_case["step"]
        except KeyError:
            raise ValueError(f"step not exist, please check it.")
        # 检查是否有result
        try:
            self.result = test_case["result"]
        except KeyError:
            raise ValueError(f"result not exist, please check it.")

    def check(self):
        """
        检查测试用例是否编写正确

        1、检查prepare部分

        2、检查precondition部分

        3、检查step部分

        4、检查result部分
        """
        self.__check_prepare()
        self.__check_precondition()
        self.__check_step()
        self.__check_result()
