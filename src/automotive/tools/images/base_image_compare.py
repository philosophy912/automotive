# -*- coding:utf-8 -*-
# --------------------------------------------------------  
# Copyright (C), 2016-2020, China TSP, All rights reserved
# --------------------------------------------------------                 
# @Name:        base_image_compare
# @Purpose:     接口类
# @Author:      lizhe  
# @Created:     2020/2/19 11:28  
# --------------------------------------------------------
import importlib
import inspect
import os
from abc import ABCMeta, abstractmethod
from loguru import logger
from automotive import Utils
from .images import Images
from .base_screen_shot import BaseScreenShot


class ImageProperty(object):
    """
        self.name = None # 名字

        self.comment = None # 备注

        self.x = None # x坐标点，列表模式

        self.y = None # y坐标点，列表模式

        self.gary = None # 是否灰度对比

        self.gary_threshold = None # 灰度阈值参数，主要设置明亮度，非对比的阈值

        self.height = None # 高度， 列表模式

        self.width = None # 宽度， 列表模式

        self.pic_template_dark = None # 亮图的名字

        self.pic_template_light = None  # 暗图的名字

        self.shot_count = None # 截图张数

        self.threshold = None # 阈值

        self.wait_time = None # 等待时间，主要用于图片闪烁

        self.is_area = False # 是否区域截图，默认不是区域截图
    """

    def __init__(self):
        self.name = None
        self.comment = None
        self.x = None
        self.y = None
        self.gary = None
        self.gary_threshold = None
        self.height = None
        self.width = None
        self.pic_template_dark = None
        self.pic_template_light = None
        self.shot_count = None
        self.threshold = None
        self.wait_time = None
        # 是否区域截图，默认不是区域截图
        self.is_area = False

    def set_value(self, name: str, config: dict):
        """
        设置相关的值, 如果设置不一样，可以直接手动设置类中的属性

        TAG: 如果要增加或者变更内容，修改这里

        :param name: 函数名

        :param config: 配置字典
        """
        self.name = name
        self.comment = config["comment"]
        self.x = config["x"]
        self.y = config["y"]
        self.height = config["height"]
        self.width = config["width"]
        self.gary = config["gray"]
        self.gary_threshold = config["gray_threshold"]
        self.pic_template_dark = config["template_dark"]
        self.pic_template_light = config["template_light"]
        self.shot_count = config["shot_count"]
        self.threshold = config["threshold"]
        self.wait_time = config["wait_time"]


class BaseImageCompare(metaclass=ABCMeta):
    """
    基础的图片对比类，如果需要可以直接调用本包下面的ImageCompare类。

    self._screen_shot: screenshot类的实例

    self._color: 画框的颜色 ，默认蓝色（用于区域）

    self._images: 实例化Image工具对象

    self._template_path: 标准图片存放的路径

    self._screen_shot_path: 截图文件存放的路径

    self._report_path: 报告文件存放的路径

    self._properties: 配置文件读取出来的对象

    self._default_image: 默认截图图片

    """

    def __init__(self, screen_shot: (str, BaseScreenShot), template_path: str, screen_shot_path: str,
                 report_path: str, config: (str, dict), color: tuple = (255, 0, 0), default_image_name: str = "1.bmp"):
        """
        :param screen_shot:
            1。可以直接传入实例化对象
            2. 可以传入实现了BaseScreenShot类的包名
            通用screenshot模块的完成包名，该模块中必须包含继承（实现)了BaseScreenShot的类。

        :param template_path: 标准图片存放的路径

        :param screen_shot_path: 截图文件存放的路径

        :param report_path: 报告文件存放的路径。

        :param config: 测试生成的json/py文件
        """
        # 标准图片存放的路径
        self._template_path = self.__check_path(template_path)
        # 截图文件存放的路径
        self._screen_shot_path = self.__check_path(screen_shot_path)
        # 报告文件存放的路径
        self._report_path = self.__check_path(report_path, True)
        # 获取screenshot类的实例
        if isinstance(screen_shot, str):
            self._screen_shot = self.__get_screen_instance(screen_shot)
        elif isinstance(screen_shot, BaseScreenShot):
            self._screen_shot = screen_shot
        # 画框的颜色 ，默认蓝色（用于区域）
        self._color = color
        # 实例化Image工具对象
        self._images = Images()
        # 配置文件读取出来的对象
        self._properties = self.__get_property_from_json(config)
        # 默认截图图片
        self._default_image = default_image_name

    @staticmethod
    def __check_path(path: str, create: bool = False) -> str:
        """
        检查路径是否存在并返回路径

        :param path: 传入的路径字符串

        :param create: 是否创建文件夹
        """
        if not os.path.exists(path):
            # 跳过表示不创建文件夹，抛出异常
            if create:
                logger.debug(f"create path[{path}]")
                os.makedirs(path)
                return path
            else:
                raise ValueError(f"path[{path}] is not exist, please check it")
        else:
            return path

    @staticmethod
    def __get_property_from_json(config: (str, dict)) -> dict:
        """
        Json文件中读取的内容转换成property对象
        :param config: json文件或者内容
        :return: property字典
        """
        properties = dict()
        if isinstance(config, str):
            config = Utils().get_json_obj(config)
        for name, content in config.items():
            image_property = ImageProperty()
            image_property.set_value(name, content)
            properties[name] = image_property
        return properties

    @staticmethod
    def __get_screen_instance(self, module_name: str) -> BaseScreenShot:
        """
        实例化screen对象

        通过传入的包名来导入模块，同时判断该模块下有没有继承与BaseScreenShot的类，如果有，则返回类的实例

        :param module_name: 模块的名字

        :return 返回BaseScreenShot子类的实例
        """
        module = importlib.import_module(module_name)
        for clazz in dir(module):
            # 由于有参数，需要传入参数，否则实例化会失败
            instance = getattr(module, clazz)
            if inspect.isclass(instance) and instance.__base__.__name__ == "BaseScreenShot":
                return instance(self._screen_shot_path)
        raise RuntimeError(f"module[{module_name}] cannot include subclass of BaseScreenShot")

    @abstractmethod
    def compare_image_light(self, name: str) -> tuple:
        """
        对比亮图

        :param name: 函数名字

        :return: 图片对比结果和拷贝到结果文件夹的路径（用于结果展示)
        """
        pass

    @abstractmethod
    def compare_image_dark(self, name: str) -> tuple:
        """
        对比暗图

        :param name: 函数名字

        :return: 图片对比结果和拷贝到结果文件夹的路径（用于结果展示)
        """
        pass

    @abstractmethod
    def compare_image_blink(self, name: str) -> tuple:
        """
        对比闪烁图片

        :param name: 函数名字

        :return: 图片对比结果和拷贝到结果文件夹的路径（用于结果展示)
        """
        pass

    @abstractmethod
    def get_origin_images(self, name: str) -> tuple:
        """
        获取原始图片

        :param name: 函数名字

        :return: 亮图和暗图的绝对路径
        """
        pass
