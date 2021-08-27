# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        utils.py
# @Author:      lizhe
# @Created:     2021/5/1 - 23:34
# --------------------------------------------------------
import json
import time
import os
import platform
import subprocess as sp
import random
import inspect
import zipfile
from typing import Union, List, Any, Dict, Tuple

import yaml
from enum import Enum

from automotive.logger import logger
from automotive.core.singleton import Singleton


class SystemTypeEnum(Enum):
    """
    系统类型
    """
    QNX = "qnx"
    LINUX = "linux"

    @staticmethod
    def from_value(value: str):
        for key, item in SystemTypeEnum.__members__.items():
            if value.upper() == item.value.upper():
                return item
        raise ValueError(f"{value} can not be found in {SystemTypeEnum.__name__}")


class PinyinEnum(Enum):
    """
    枚举类，仅仅列出了拼音的类型

    DIACRITICAL: 输出的拼音含有声调

    NUMERICAL: 输出拼音音调以数字形式紧随拼音

    STRIP: 不包含声调
    """
    # 输出的拼音含有声调
    DIACRITICAL = "diacritical"
    # 输出拼音音调以数字形式紧随拼音
    NUMERICAL = "numerical"
    # 不包含声调
    STRIP = "strip"

    @staticmethod
    def from_value(value: str):
        for key, item in PinyinEnum.__members__.items():
            if value.upper() == item.value.upper():
                return item
        raise ValueError(f"{value} can not be found in {PinyinEnum.__name__}")


class Utils(metaclass=Singleton):
    """
    工具类（单例模式), 提供常用的一些方法.

    1、 get_time_as_string： 返回格式化之后的系统时间，默认时间为年-月-日_小时-分钟-秒

    2、random_decimal/random_int： 返回随机小数和整数

    3、get_pin_yin: 返回中文的拼音，可以结合speaker下面的player在Windows10上进行TTS的测试

    4、get_current_function_name：用于获取当前函数名的名字

    5、sleep：改进型的sleep，当sleep超过1分钟的时候，可能会导致程序死锁，

    6、read_yml_full/read_yml_safe/read_yml_un_safe: YML相关的读取函数
    """

    @staticmethod
    def get_time_as_string(fmt: str = '%Y-%m-%d_%H-%M-%S') -> str:
        """
        返回当前系统时间，类型为string

        :param fmt: 格式化类型 如'%Y-%m-%d_%H-%M-%S'

        :return: 当前系统时间，如：2018-07-27_14-18-59
        """
        return time.strftime(fmt, time.localtime(time.time()))

    @staticmethod
    def random_decimal(min_: Union[float, int], max_: Union[float, int]) -> Union[float, int]:
        """
        随机返回一个最小数和最大数之间的小数

        :param min_: 最小数

        :param max_: 最大数

        :return:  介于最小数和最大数之间的小数
        """
        return random.uniform(min_, max_)

    @staticmethod
    def random_int(min_: Union[float, int], max_: Union[float, int]) -> Union[float, int]:
        """
        随机返回一个最小数和最大数之间的整数

        :param min_: 最小数

        :param max_: 最大数

        :return: 返回随机生成的介于最小数和最大数之间的整数
        """
        return random.randint(min_, max_)

    @staticmethod
    def get_pin_yin(text: Union[str, bytes], delimiter: str = '', is_first: bool = False,
                    format_: PinyinEnum = PinyinEnum.STRIP) -> str:
        """
        获取中文的拼音写法，其中text必须是unicode编码格式

        :param text: 需要进行转换的中文

        :param delimiter: 输出拼音的分隔符

        :param is_first:
            True: 只截取首字母

            False: 全拼拼音输出

        :param format_:  默认为strip方式

            diacritical:输出的拼音含有声调

            numerical:输出拼音音调以数字形式紧随拼音

            strip:不包含声调

        :return: 返回拼音的字符串
        """
        try:
            from pinyin import pinyin
        except ModuleNotFoundError:
            os.system("pip install pinyin")
        from pinyin import pinyin
        if isinstance(text, bytes):
            text = text.decode("utf-8")
        return pinyin.get_initial(text, delimiter) if is_first else pinyin.get(text, delimiter, format_.value)

    @staticmethod
    def is_type_correct(actual_: object, except_: Union[object, tuple]) -> bool:
        """
        判断类型是否属于期望类型

        :param actual_: 原始对象

        :param except_: 期望对象

        :return:
            True: 表示类型和期望类型一致

            False: 表示类型和期望类型不一致
        """
        return isinstance(actual_, except_)

    @staticmethod
    def get_current_function_name() -> str:
        """
        获取当前函数的名字

        :return: 当前函数的名字
        """
        return inspect.stack()[1][3]

    @staticmethod
    def is_sub_list(list1: List[Any], list2: List[Any]) -> bool:
        """
        列表list1中所有的是否包含在list2中

        :param list1: 列表1

        :param list2: 列表2

        :return:
            True 包含在其中

            False 不包含在其中
        """
        list1 = set(list1)
        list2 = set(list2)
        return list1.issubset(list2)

    @staticmethod
    def sleep(sleep_time: float, text: str = None):
        """
        带文字版的sleep，其中logger为loguru输出，级别为info

        :param sleep_time: 休息时间

        :param text:  文字内容
        """
        logger.debug(f"it will sleep {sleep_time} seconds")
        if text is None:
            logger.info(f"--------------------休息{sleep_time}秒--------------------")
        else:
            logger.info(f"--------------------休息{text},休息{sleep_time}秒--------------------")
        integer = int(sleep_time // 1)
        decimal = sleep_time - integer
        # 超过1分钟的休眠会分段休息
        if sleep_time > 60:
            for i in range(integer):
                time.sleep(1)
        else:
            time.sleep(sleep_time)
        time.sleep(decimal)

    def random_sleep(self, start: Union[int, float], end: Union[int, float]):
        """
        随机sleep

        :param start: 开始时间

        :param end: 结束时间
        """
        if end < start:
            raise ValueError(f"开始{start}必须大于结束{end}")
        sleep_time = int(self.random_decimal(start, end))
        logger.info(f"随机休眠时间{sleep_time}")
        # 超过1分钟的休眠会分段休息
        if sleep_time > 60:
            for i in range(sleep_time):
                time.sleep(1)
        else:
            time.sleep(sleep_time)

    @staticmethod
    def text(content: str, level: str = None):
        """
        输出文字，方便调用

        :param content: 文字内容

        :param level:  只支持info和debug，默认info
        """
        if level == "debug":
            logger.debug(content)
        else:
            logger.info(content)

    @staticmethod
    def get_folder_path(folder_name: str, top_folder_name: str, current_path: str) -> str:
        """
        在top_folder_name目录下找folder_name文件夹存在的位置

        Tips: 当该文件夹下面有两个相同的folder_name的时候，以第一个为准

        :param folder_name: 要查找的文件名字，要查找的在top_folder_name下面的文件夹的名字

        :param top_folder_name: 要查找的顶层目录文件夹名字， 通常设置为automatedtest

        :param current_path: 要查找的文件夹路径，一般传入当前运行文件所在的文件夹

        :return: top_folder_name目录下folder_name文件夹的路径
        """
        if top_folder_name not in current_path:
            raise ValueError(f"top_folder_name[{top_folder_name}] must in current_path[{current_path}]")
        head_path = current_path.split(top_folder_name)[0]
        top_folder_path = os.path.join(head_path, top_folder_name)
        logger.debug(f"top_folder_path = {top_folder_path}")
        for root, dirs, files in os.walk(top_folder_path):
            if folder_name in dirs:
                dir_path = os.path.join(root, folder_name)
                return dir_path
        raise RuntimeError(f"can not found {top_folder_name} in {current_path} ")

    @staticmethod
    def zip_file(zip_folder: str, zip_file_name: str):
        """
        压缩文件夹到文件中

        :param zip_folder: 被压缩的文件夹

        :param zip_file_name: 压缩后的文件名字
        """
        zip_file = zipfile.ZipFile(zip_file_name, "w", zipfile.ZIP_DEFLATED)
        if os.path.exists(zip_folder):
            for item in os.listdir(zip_folder):
                zip_file.write("\\".join([zip_folder, item]))
            zip_file.close()

    @staticmethod
    def get_json_obj(file: str, encoding: str = "utf-8") -> Dict[Any, Any]:
        """
        获取json文件中object对象

        :param encoding: 编码方式

        :param file: json文件的路径

        :return: json文件中的object对象
        """
        logger.debug(f"file is {file}")
        with open(file, "r", encoding=encoding) as fp:
            content = json.load(fp)
            logger.trace(f"content is {content}")
            return content

    @staticmethod
    def read_yml_full(file: str, encoding: str = "UTF-8") -> Dict[str, str]:
        """
        读取yml文件中的内容(full_load方法)

        :param file: yml文件的绝对路径

        :param encoding: 编码格式，默认UTF-8

        :return: yml对象对应的字典对象
        """
        logger.debug(f"file is {file}")
        with open(file, "r", encoding=encoding) as fp:
            content = yaml.full_load(fp)
            logger.debug(f"content is {content}")
            return content

    @staticmethod
    def read_yml_safe(file: str, encoding: str = "UTF-8") -> Dict[str, str]:
        """
        读取yml文件中的内容（safe_load方法)

        :param file: yml文件的绝对路径

        :param encoding: 编码格式，默认UTF-8

        :return: yml对象对应的字典对象
        """
        logger.debug(f"file is {file}")
        with open(file, "r", encoding=encoding) as fp:
            content = yaml.safe_load(fp)
            logger.debug(f"content is {content}")
            return content

    @staticmethod
    def read_yml_un_safe(file: str, encoding: str = "UTF-8") -> Dict[str, str]:
        """
        读取yml文件中的内容(unsafe_load方法)

        :param file: yml文件的绝对路径

        :param encoding: 编码格式，默认UTF-8

        :return: yml对象对应的字典对象
        """
        logger.debug(f"file is {file}")
        with open(file, "r", encoding=encoding) as fp:
            content = yaml.unsafe_load(fp)
            logger.debug(f"content is {content}")
            return content

    @staticmethod
    def filter_images(folder: str, image_name: str) -> List[str]:
        """
        遍历文件夹取出名字是测试用例名字的图片

        :param folder: 要查找的文件夹路径

        :param image_name: 截图保存的文件名

        :return: 筛选出来的图片集合
        """
        # 在screen_shot_path路径中查找
        folder_files = os.listdir(folder)
        if "__init__.py" in folder_files:
            folder_files.remove("__init__.py")
        images = list(filter(lambda x: x.split("__")[0] == image_name, folder_files))
        filter_images = list(map(lambda x: "\\".join([folder, x]), images))
        logger.debug(f"{folder} contain {len(filter_images)} {image_name} files")
        return filter_images

    @staticmethod
    def exec_command_with_output(command: str, workspace: str = None, encoding: str = "utf-8") -> Tuple:
        """
        有输出的执行

        :param command:  命令

        :param workspace: 工作目录

        :param encoding: 编码格式

        :return: 输出的值
        """
        is_shell = False if platform.system() == "Windows" else True
        if workspace:
            logger.debug(f"cwd is [{workspace}]")
            p = sp.Popen(command, shell=is_shell, cwd=workspace, stdout=sp.PIPE, stderr=sp.PIPE)
        else:
            p = sp.Popen(command, shell=is_shell, stdout=sp.PIPE, stderr=sp.PIPE)
        stdout, stderr = p.communicate()
        return stdout.decode(encoding), stderr.decode(encoding)
