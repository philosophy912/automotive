# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2021, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        api1.py.py
# @Author:      lizhe
# @Created:     2021/8/3 - 22:02
# --------------------------------------------------------
from abc import ABCMeta, abstractmethod
from queue import Queue
from time import sleep

from .constants import Testcase, REPLACE_CHAR, get_yml_config, CLASS_INSTANCE, FUNCTION_OPEN, FUNCTION_CLOSE
from typing import Tuple, Sequence, Optional, Dict

from automotive.utils.excel_utils import ExcelUtils
from automotive.utils.player import Player
from automotive.utils.images import Images
from automotive.utils.utils import Utils
from automotive.logger.logger import logger

Position = Tuple[int, int, int, int]
Voltage_Current = Tuple[float, float]
TestCases = Sequence[Testcase]


class BaseDevice(metaclass=ABCMeta):

    @abstractmethod
    def open(self):
        """
        打开设备
        """
        pass

    @abstractmethod
    def close(self):
        """
        关闭设备
        :return:
        """
        pass


class BaseSocketDevice(metaclass=ABCMeta):

    @abstractmethod
    def connect(self,
                username: Optional[str] = None,
                password: Optional[str] = None,
                ipaddress: Optional[str] = None):
        """
        连接并登陆系统

        :param ipaddress: IP地址

        :param username: 用户名

        :param password: 密码

        """
        pass

    @abstractmethod
    def disconnect(self):
        """
        断开
        """
        pass


class BaseScreenShot(metaclass=ABCMeta):

    @abstractmethod
    def screen_shot(self,
                    image_name: str,
                    count: int,
                    interval_time: float,
                    display: Optional[int] = None) -> Sequence[str]:
        """
        截图操作, 当截图有多张的时候，以__下划线分割并加编号

        :param image_name: 截图保存图片名称

        :param count: 截图张数

        :param interval_time: 截图间隔时间

        :param display: 屏幕序号
        """
        pass

    @abstractmethod
    def screen_shot_area(self,
                         position: Position,
                         image_name: str,
                         count: int,
                         interval_time: float,
                         display: Optional[int] = None) -> Sequence[str]:
        """
        区域截图, 当截图有多张的时候，以__下划线分割并加编号

        :param position: 截图区域(x, y, width, height)

        :param image_name: 截图保存图片名称

        :param count: 截图张数

        :param interval_time: 截图间隔时间

        :param display: 屏幕序号
        """
        pass


class BaseActions(metaclass=ABCMeta):

    @abstractmethod
    def click(self,
              display: int,
              x: int,
              y: int,
              interval: float = 0.2):
        """
        屏幕点击

        :param display: 屏幕序号

        :param x: 坐标点x

        :param y: 坐标点y

        :param interval: 按下和弹起的间隔时间
        """
        pass

    @abstractmethod
    def double_click(self,
                     display: int,
                     x: int,
                     y: int,
                     interval: float):
        """
        屏幕双击

        :param display: 屏幕序号

        :param x: 坐标点x

        :param y: 坐标点y

        :param interval: 两次点击之间的间隔时间
        """
        pass

    @abstractmethod
    def press(self,
              display: int,
              x: int,
              y: int,
              continue_time: float):
        """
        长按某个坐标点

        :param display: 屏幕序号

        :param x: 坐标点x

        :param y: 坐标点y

        :param continue_time: 长按持续时间
        """
        pass

    @abstractmethod
    def swipe(self,
              display: int,
              start_x: int,
              start_y: int,
              end_x: int,
              end_y: int,
              continue_time: float):
        """
        滑动页面

        :param display: 屏幕序号

        :param start_x: 起始点x

        :param start_y: 起始点y

        :param end_x: 结束点x

        :param end_y: 结束点y

        :param continue_time: 滑动耗时
        """
        pass


class BasePowerActions(BaseDevice):
    """
    电源相关的操作类，用于统一接口
    """

    def __init__(self):
        super().__init__()

    @abstractmethod
    def on(self):
        """
        打开设备
        """
        pass

    @abstractmethod
    def off(self):
        """
        关闭设备
        """
        pass


class BasePowerAdjustActions(BasePowerActions):
    """
    电源相关的操作类，用于统一接口
    """

    @abstractmethod
    def set_voltage(self, voltage: float):
        """
        设置电源电压

        :param voltage: 电压
        """
        pass

    @abstractmethod
    def set_current(self, current):
        """
        设置电源电流

        :param current: 电流
        """
        pass

    @abstractmethod
    def set_voltage_current(self, voltage: float, current: float = 10):
        """
        设置电源电压电流

        :param voltage: 电压

        :param current: 电流
        """
        pass

    @abstractmethod
    def change_voltage(self,
                       start: float,
                       end: float,
                       step: float,
                       interval: float = 0.5,
                       current: float = 10):
        """
        调节电压

        :param start: 开始电压

        :param end: 结束电压

        :param step: 调整的步长

        :param interval: 间隔时间，默认0.5秒

        :param current: 电流值， 默认10A

        :return: 只针对konstanter实际有效，对IT6831电源则永远返回True
        """
        pass

    @abstractmethod
    def get_current_voltage(self) -> Voltage_Current:
        """
        获取当前电流电压值

        :return 当前电压和电流值
        """
        pass


class BaseTestCase(metaclass=ABCMeta):

    @staticmethod
    def _parse_id(content: str, split_character: Tuple[str, str] = ("[", "]")) -> Tuple[str, str]:
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

    @staticmethod
    def _get_module(module: str) -> Tuple[str, str]:
        """
        用于解析module
        :param module:
        :return: module和module_id
        """
        if REPLACE_CHAR in module:
            module_list = module.split(REPLACE_CHAR)
            return module_list[0], module_list[1]
        else:
            return module, ""


class BaseReader(BaseTestCase):
    @abstractmethod
    def read_from_file(self, file: str) -> Dict[str, TestCases]:
        """
        从文件中读取testCase类
        :param file:  文件
        :return: 读取到的测试用例集合
        """
        pass


class BaseWriter(BaseTestCase):
    @abstractmethod
    def write_to_file(self, file: str, testcases: Dict[str, TestCases], temp_file: str = None):
        """
        把测试用例集合写入到文件中
        :param file:  文件
        :param testcases: 测试用例集合
        :param temp_file:excel模板文件地址
        """
        pass

    @staticmethod
    def _check_testcases(testcases: Dict[str, TestCases]):
        if testcases is None:
            raise RuntimeError("testcases is None")
        if len(testcases) == 0:
            raise RuntimeError("no testcase found")


class BaseAction(metaclass=ABCMeta):

    def __init__(self, yml_file: str, open_methods: Sequence = None, close_methods: Sequence = None):
        """
        :param open_methods: yml配置文件中类支持的打开方法
        :param close_methods: yml配置文件中类支持的关闭方法
        :param yml_file: YML文件所在路径
        """
        self._utils = Utils()
        # 配置open和close用到的方法
        self.__open_methods = open_methods if open_methods else ("connect", "open")
        self.__close_methods = close_methods if close_methods else ("close", "disconnect")
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
