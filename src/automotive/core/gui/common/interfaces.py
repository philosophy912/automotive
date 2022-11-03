# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        interfaces.py
# @Author:      lizhe
# @Created:     2022/11/1 - 13:12
# --------------------------------------------------------
from abc import ABCMeta, abstractmethod
from typing import Sequence
from queue import Queue

from automotive.logger.logger import logger
from automotive.utils.excel_utils import ExcelUtils
from automotive.utils.player import Player
from automotive.utils.images import Images

from automotive.utils.utils import Utils
from .constants import get_yml_config, CLASS_INSTANCE, FUNCTION_OPEN, FUNCTION_CLOSE


class BaseAction(metaclass=ABCMeta):

    def __init__(self, yml_file: str, open_methods: Sequence = None, close_methods: Sequence = None):
        """
        :param open_methods: yml配置文件中类支持的打开方法
        :param close_methods: yml配置文件中类支持的关闭方法
        :param yml_file: YML文件所在路径
        """
        self._utils = Utils()
        # 配置open和close用到的方法
        self.__open_methods = open_methods if open_methods else ("connect", "open", "open_can")
        self.__close_methods = close_methods if close_methods else ("close", "disconnect", "close_can")
        # 这一部分就是传参才能生成的对象实例
        self.__result_dict = get_yml_config(yml_file, self._utils, self.__open_methods, self.__close_methods)
        # 存入对象池，方便调用
        self._instances = dict()
        # 此时实例化对象, 后续就可以根据这个配置的内容来直接调用
        for name, value in self.__result_dict.items():
            self.__class, self.__params = value[CLASS_INSTANCE]
            self._instances[name] = self.__class(**self.__params)
        # 图像对比类实例化
        self._images = Images()
        # 播放器类实例化
        self._player = Player()
        # Excel类实例化, 默认xlwings
        self._excel_utils = ExcelUtils("xlwings")

    def open(self):
        """
        根据配置的内容决定打开的设备，如摄像头、串口等
        抽象类初始化的时候就会打开这些设备
        TIPS: ExcelUtils除外
        该方法在类初始化的时候自动调用
        """
        logger.debug("call open method")
        for name, instance in self._instances.items():
            # 'connect', {'port': 'COM12', 'baud_rate': 115200, 'log_folder': 'd:\\test'}
            function_name, function_param = self.__result_dict[name][FUNCTION_OPEN]
            # 调用方法
            getattr(instance, function_name)(**function_param)

    def close(self):
        """
        根据配置的内容决定关闭的设备，如摄像头、串口等
        在代码结束的时候关闭之前打开的设备
        TIPS: ExcelUtils除外
        该方法在子类Run方法结束的时候需要手动调用
        """
        logger.debug("call close method")
        for name, instance in self._instances.items():
            # 'disconnect', {}
            function_name, function_param = self.__result_dict[name][FUNCTION_CLOSE]
            # 调用方法
            getattr(instance, function_name)(**function_param)

    @abstractmethod
    def readme(self, queue: Queue):
        """
        抽象方法，该方法用于测试步骤的总体描述
        框架会自动调用该方法
        """
        pass

    @abstractmethod
    def run(self, queue: Queue):
        pass

    def run_stress(self, queue: Queue):
        self.readme(queue)
        self.open()
        self.run(queue)
        self.close()
