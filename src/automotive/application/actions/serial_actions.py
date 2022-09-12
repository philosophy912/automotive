# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        serial_actions.py
# @Author:      lizhe
# @Created:     2021/5/2 - 0:02
# --------------------------------------------------------
from typing import Sequence

from automotive.utils.serial_utils import SerialUtils
from automotive.logger.logger import logger
from automotive.utils.common.enums import SystemTypeEnum
from ..common.interfaces import BaseDevice


class SerialActions(BaseDevice):
    """
    串口操作类
    """

    def __init__(self, port: str, baud_rate: int):
        super().__init__()
        self.__serial = SerialUtils()
        self.__port = port.upper()
        self.__baud_rate = baud_rate

    @property
    def serial_utils(self):
        return self.__serial

    def open(self):
        """
        打开串口
        """
        logger.info("初始化串口")
        logger.info("打开串口")
        buffer = 32768
        self.__serial.connect(port=self.__port, baud_rate=self.__baud_rate)
        logger.info(f"*************串口初始化成功*************")
        self.__serial.serial_port.set_buffer(buffer, buffer)
        logger.info(f"串口缓存为[{buffer}]")

    def close(self):
        """
        关闭串口
        """
        logger.info("关闭串口")
        self.__serial.disconnect()

    def write(self, command: str):
        """
        向串口写入数据
        :param command:
        """
        self.__serial.write(command)

    def read(self) -> str:
        """
        从串口中读取数据
        :return:
        """
        return self.__serial.read()

    def read_lines(self) -> Sequence[str]:
        """
        从串口中读取数据，按行来读取
        :return:
        """
        return self.__serial.read_lines()

    def clear_buffer(self):
        """
        清空串口缓存数据
        """
        self.read()

    def file_exist(self, file: str, check_times: int = None, interval: float = 0.5, timeout: int = 10) -> bool:
        """
        检查文件是否存在

        :param file: 文件名(绝对路径)

        :param check_times:  检查次数

        :param interval:  间隔时间

        :param timeout: 超时时间

        :return: 存在/不存在
        """
        logger.info(f"检查文件{file}是否存在")
        return self.__serial.file_exist(file, check_times, interval, timeout)

    def login(self, username: str, password: str, double_check: bool = False, login_locator: str = "login"):
        """
        登陆系统

        :param username: 用户名

        :param password: 密码

        :param double_check: 登陆后的二次检查

        :param login_locator:  登陆定位符
        """
        logger.info(f"登陆系统，用户名{username}, 密码{password}")
        self.__serial.login(username, password, double_check, login_locator)

    def copy_file(self, remote_folder: str, target_folder: str, system_type: SystemTypeEnum, timeout: float = 300):
        """
        复制文件

        :param remote_folder: 原始文件

        :param target_folder: 目标文件夹

        :param system_type: 系统类型，目前支持QNX和Linux

        :param timeout: 超时时间
        """
        logger.info(f"复制{remote_folder}下面所有的文件到{target_folder}")
        self.__serial.copy_file(remote_folder, target_folder, system_type, timeout)

    def check_text(self, contents: str) -> bool:
        """
        检查是否重启
        :param contents: 重启的标识内容
        :return:
            True： 串口输出找到了匹配的内容
            False: 串口输出没有找到匹配的内容
        """
        logger.warning("使用前请调用clear_buffer方法清除缓存")
        data = self.read()
        result = True
        for content in contents:
            logger.debug(f"现在检查{content}是否在串口数据中存在")
            result = result and content in data
        return result
