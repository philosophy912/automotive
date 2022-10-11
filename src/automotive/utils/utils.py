# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        utils.py
# @Author:      lizhe
# @Created:     2021/5/1 - 23:34
# --------------------------------------------------------
import importlib
import importlib.util
import json
import shutil
import sys
import time
import os
import platform
import subprocess as sp
import random
import inspect
import zipfile
import yaml
from datetime import datetime
from typing import Union, Dict, Tuple, Optional, Sequence, NoReturn, Any

from ..common.typehints import Number
from ..logger.logger import logger
from ..common.singleton import Singleton
from .common.enums import PinyinEnum


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
    def codec(content: str, encoding: str, is_ignore: bool):
        """
        字符串的codec
        :param content: 字符串内容
        :param encoding:  编码方式
        :param is_ignore:  是否忽略错误
        :return:
        """
        if is_ignore:
            return content.encode(encoding, "ignore")
        else:
            return content.encode(encoding)

    @staticmethod
    def decode(content: bytes, encoding: str, is_ignore: bool):
        """
        字符串的decode
        :param content: 字节码
        :param encoding: 编码凡是
        :param is_ignore:  是否忽略错误
        :return:
        """
        if is_ignore:
            return content.decode(encoding, "ignore")
        else:
            return content.decode(encoding)

    @staticmethod
    def get_time_as_string(fmt: str = '%Y-%m-%d_%H-%M-%S') -> str:
        """
        返回当前系统时间，类型为string

        :param fmt: 格式化类型 如'%Y-%m-%d_%H-%M-%S'

        :return: 当前系统时间，如：2018-07-27_14-18-59
        """
        return time.strftime(fmt, time.localtime(time.time()))

    def get_week(self, date_time: str, fmt: str = '%Y%m%d') -> int:
        """
        获取指定时间是第几周

        :param date_time: 指定时间的字符串

        :param fmt: 指定时间的时间格式化类型

        :return: 第几周
        """
        year, week, week_of_day = self.convert_string_datetime(date_time, fmt).date().isocalendar()
        return week

    @staticmethod
    def convert_datetime_string(date_time: datetime, fmt: str = '%Y%m%d_%H%M%S') -> str:
        """
        转换时间为字符串

        :param date_time: 时间

        :param fmt: 转换格式

        :return 时间字符串
        """
        return date_time.strftime(fmt)

    @staticmethod
    def convert_string_datetime(date_time: str, fmt: str = '%Y%m%d_%H%M%S') -> datetime:
        """
        转换字符串为时间

        :param date_time: 时间字符串

        :param fmt: 转换格式

        :return: 时间
        """
        return datetime.strptime(date_time, fmt)

    @staticmethod
    def random_decimal(min_: float, max_: float) -> float:
        """
        随机返回一个最小数和最大数之间的小数

        :param min_: 最小数

        :param max_: 最大数

        :return:  介于最小数和最大数之间的小数
        """
        return random.uniform(min_, max_)

    @staticmethod
    def random_int(min_: int, max_: int) -> int:
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
    def is_type_correct(actual_, except_) -> bool:
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
    def sleep(sleep_time: float, text: Optional[str] = None) -> NoReturn:
        """
        带文字版的sleep，其中logger为loguru输出，级别为info

        :param sleep_time: 休息时间

        :param text:  文字内容
        """
        logger.debug(f"it will sleep {sleep_time} seconds")
        if text is None:
            logger.info(f"--------------------休息{sleep_time}秒--------------------")
        else:
            logger.info(f"--------------------{text},休息{sleep_time}秒--------------------")
        integer = int(sleep_time // 1)
        decimal = sleep_time - integer
        # 超过1分钟的休眠会分段休息
        if sleep_time > 60:
            for i in range(integer):
                time.sleep(1)
        else:
            time.sleep(sleep_time)
        time.sleep(decimal)

    def random_sleep(self, start: Number, end: Number) -> NoReturn:
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
    def text(content: str, level: Optional[str] = None) -> NoReturn:
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
    def zip_file(zip_folder: str, zip_file_name: str) -> NoReturn:
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
    def get_json_obj(file: str, encoding: str = "utf-8") -> Dict:
        """
        获取json文件中object对象

        :param encoding: 编码方式

        :param file: json文件的路径

        :return: json文件中的object对象
        """
        logger.debug(f"file is {file}")
        with open(file, "r", encoding=encoding, errors="ignore") as fp:
            content = json.load(fp)
            logger.trace(f"content is {content}")
            return content

    @staticmethod
    def read_yml_full(file: str, encoding: str = "UTF-8") -> Dict:
        """
        读取yml文件中的内容(full_load方法)

        :param file: yml文件的绝对路径

        :param encoding: 编码格式，默认UTF-8

        :return: yml对象对应的字典对象
        """
        logger.debug(f"file is {file}")
        with open(file, "r", encoding=encoding, errors="ignore") as fp:
            content = yaml.full_load(fp)
            logger.debug(f"content is {content}")
            return content

    @staticmethod
    def read_yml_safe(file: str, encoding: str = "UTF-8") -> Dict:
        """
        读取yml文件中的内容（safe_load方法)

        :param file: yml文件的绝对路径

        :param encoding: 编码格式，默认UTF-8

        :return: yml对象对应的字典对象
        """
        logger.debug(f"file is {file}")
        with open(file, "r", encoding=encoding, errors="ignore") as fp:
            content = yaml.safe_load(fp)
            logger.debug(f"content is {content}")
            return content

    @staticmethod
    def read_yml_un_safe(file: str, encoding: str = "UTF-8") -> Dict:
        """
        读取yml文件中的内容(unsafe_load方法)

        :param file: yml文件的绝对路径

        :param encoding: 编码格式，默认UTF-8

        :return: yml对象对应的字典对象
        """
        logger.debug(f"file is {file}")
        with open(file, "r", encoding=encoding, errors="ignore") as fp:
            content = yaml.unsafe_load(fp)
            logger.debug(f"content is {content}")
            return content

    @staticmethod
    def filter_images(folder: str, image_name: str) -> Sequence[str]:
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
    def exec_command_with_output(command: str, workspace: Optional[str] = None, encoding: str = "utf-8",
                                 is_shell: Optional[bool] = None) -> Tuple:
        """
        有输出的执行

        :param command:  命令

        :param workspace: 工作目录

        :param encoding: 编码格式

        :param is_shell: 是否以shell方式执行

        :return: 输出的值
        """
        logger.debug(f"command is {command}")
        if is_shell is None:
            is_shell = False if platform.system() == "Windows" else True
        if workspace:
            logger.debug(f"cwd is [{workspace}]")
            p = sp.Popen(command, shell=is_shell, cwd=workspace, stdout=sp.PIPE, stderr=sp.PIPE)
        else:
            p = sp.Popen(command, shell=is_shell, stdout=sp.PIPE, stderr=sp.PIPE)
        stdout, stderr = p.communicate()
        return stdout.decode(encoding), stderr.decode(encoding)

    def exec_command_must_success(self, command: str, workspace: Optional[str] = None,
                                  sub_process: bool = True) -> NoReturn:
        """
        有输出的执行必须成功

        :param command:  命令

        :param workspace: 工作目录

        :param sub_process: 是否以子进程方式执行

        :return: 输出的值
        """
        if self.exec_command(command, workspace, sub_process) != 0:
            logger.error(f"execute command [{command}] failed, please check it again")
            sys.exit(1)

    def exec_commands_must_success(self, commands: Sequence, workspace: Optional[str] = None) -> NoReturn:
        """
        有输出的执行必须成功

        :param commands:  命令集合

        :param workspace: 工作目录

        :return: 输出的值
        """
        for command in commands:
            self.exec_command_must_success(command, workspace)

    def exec_commands(self, commands: Sequence, workspace: Optional[str] = None, sub_process: bool = True) -> NoReturn:
        """
        执行命令集

        :param commands:  命令集合

        :param workspace: 工作目录

        :param sub_process: 是否以子进程方式运行

        :return: 输出的值
        """
        for command in commands:
            self.exec_command(command, workspace, sub_process)

    @staticmethod
    def exec_command(command: str, workspace: Optional[str] = None, sub_process: bool = True) -> int:
        """
        执行命令, 涉及到bat命令的时候，都需要使用os.system的方式执行，否则会出问题

        :param command: 命令

        :param workspace: 工作目录

        :param sub_process: 是否以子进程方式运行

        :return: 执行成功的结果，由于os.system没有，则永远返回0
        """
        logger.debug(f"it will execute command[{command}]")
        is_shell = False if platform.system() == "Windows" else True
        if sub_process:
            logger.trace("it use subprocess type")
            if workspace:
                logger.debug(f"cwd is [{workspace}]")
                p = sp.Popen(command, shell=is_shell, cwd=workspace, universal_newlines=True)
            else:
                p = sp.Popen(command, shell=is_shell, universal_newlines=True)
            p.communicate()
            return p.returncode
        else:
            logger.trace("it use os.system type")
            if workspace:
                os.chdir(workspace)
            return os.system(command)

    @staticmethod
    def remove_tree(folder: str) -> NoReturn:
        """
        删除文件夹 可能存在权限问题导致无法删除

        :param folder: 文件夹
        """
        if os.path.exists(folder) and os.path.isdir(folder):
            logger.debug(f"it will remove folder 【{folder}】")
            shutil.rmtree(folder)
        else:
            logger.info(f"[{folder}] is not exist or not folder")

    @staticmethod
    def check_file_exist(file: str) -> NoReturn:
        """
        检查文件是否存在
        :param file: w文件
        """
        if not (os.path.exists(file) and os.path.isfile(file)):
            raise RuntimeError(f"file[{file}] is not exist or not a file")

    @staticmethod
    def check_folder_exist(folder: str) -> NoReturn:
        """
        检查路径是否存在

        :param folder: 文件夹名称
        """
        if not (os.path.exists(folder) and os.path.isdir(folder)):
            raise RuntimeError(f"folder[{folder}] is not exist or not a folder")

    def check_git_repository(self, folder: str) -> NoReturn:
        """
        检查路径是否为git仓库

        :param folder: 文件夹名称
        """
        self.check_folder_exist(folder)
        git_folder = os.path.join(folder, ".git")
        if not (os.path.exists(git_folder) and os.path.isdir(git_folder)):
            raise RuntimeError(f"folder[{folder}] is not a git repository, please check it.")

    def check_repo_repository(self, folder: str) -> NoReturn:
        """
        检查路径是否为git仓库

        :param folder: 文件夹名称
        """
        self.check_folder_exist(folder)
        git_folder = os.path.join(folder, ".repo")
        if not (os.path.exists(git_folder) and os.path.isdir(git_folder)):
            raise RuntimeError(f"folder[{folder}] is not a repo repository, please check it.")

    def delete_file(self, file_name: str) -> NoReturn:
        """
        删除文件
        :param file_name: 文件名称
        """
        self.check_file_exist(file_name)
        flag = True
        if platform.system() == "Windows":
            cmd = f"del \"{file_name}\""
            flag = False
        else:
            cmd = f"rm -rvf {file_name}"
        self.exec_command(cmd, sub_process=flag)

    def delete_folder(self, folder_name: str) -> NoReturn:
        """
        删除文件夹

        :param folder_name: 文件夹名称
        """
        self.check_folder_exist(folder_name)
        flag = True
        if platform.system() == "Windows":
            cmd = f"rd /Q /S \"{folder_name}\""
            flag = False
        else:
            cmd = f"rm -rvf {folder_name}"
        self.exec_command(cmd, sub_process=flag)

    @staticmethod
    def to_hex_list(number_list: Sequence[int]) -> Sequence[str]:
        """
        把int列表转换成十六进制字符串列表
        :param number_list: 数字列表， 当十六进制数字小于16的时候，即1位数的时候，自动补零
        :return:
        """
        commands = []
        for command_value in number_list:
            hex_value = hex(command_value)[2:]
            if len(hex_value) != 2:
                hex_value = f"0{hex_value}"
            commands.append(hex_value)
        return commands

    @staticmethod
    def get_class_from_name(class_name: str) -> type:
        automotive_module = __import__("automotive", fromlist=[])
        # 获取类对象
        return getattr(automotive_module, class_name)

    def get_param_from_class_name(self, class_name: Union[str, type],
                                  default_filter: Optional[Sequence] = None) -> Dict:
        """
        根据类名获取不包含wrapper的方法以及对应的参数, 仅支持automotive库
        :param class_name: 类名，大小写敏感
        :param default_filter: 默认过滤的方法，包含装饰器的方法名
        :return:
        """
        methods = dict()
        if default_filter is None:
            default_filter = ["wrapper"]
        # 获取类对象
        if isinstance(class_name, str):
            clazz = self.get_class_from_name(class_name)
        else:
            clazz = class_name
        # 获取类中没有装饰器的函数
        clazz_methods = inspect.getmembers(clazz, inspect.isfunction)
        clazz_methods = list(filter(lambda x: not x[0].startswith("_") or x[0] == "__init__", clazz_methods))
        for filter_name in default_filter:
            clazz_methods = list(filter(lambda x: filter_name not in str(x[1]).lower(), clazz_methods))
        for clazz_method in clazz_methods:
            method_name = clazz_method[0]
            logger.debug(f"method_name is {method_name}")
            # 获取类中的方法
            function = getattr(clazz, method_name)
            # 获取类中的参数个数
            params = function.__code__.co_varnames[0:function.__code__.co_argcount]
            # 过滤self
            params = list(filter(lambda x: x != "self", params))
            methods[method_name] = params
        return methods

    @staticmethod
    def get_module_from_script(script: str) -> Any:
        """
        根据脚本动态导入
        :param script: 脚本全路径
        :return:
        """
        if not os.path.exists(script):
            logger.error(f"{script} is not exist")
            return None
        module_name = script.split(".")[0]
        # 根据文件获取spec，然后根据spec加载module
        module_spec = importlib.util.spec_from_file_location(module_name, script)
        module = importlib.util.module_from_spec(module_spec)
        # 模块的Loader必须要执行一次， 否则模块有问题
        module_spec.loader.exec_module(module)
        return module
