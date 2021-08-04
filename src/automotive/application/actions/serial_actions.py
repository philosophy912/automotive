# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        serial_actions.py
# @Author:      lizhe
# @Created:     2021/5/2 - 0:02
# --------------------------------------------------------
from automotive.utils.serial_utils import SerialUtils
from automotive.logger.logger import logger
from automotive.common.api import BaseDevice


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

    def clear_buffer(self):
        """
        清空串口缓存数据
        """
        self.__serial.serial_port.read_all()

    def check_reset_text(self, contents: str) -> bool:
        """
        检查是否重启
        :param contents: 重启的标识内容
        :return:
            True： 串口输出找到了匹配的内容
            False: 串口输出没有找到匹配的内容
        """
        logger.warning("使用前请调用clear_buffer方法清除缓存")
        data = self.__serial.serial_port.read_all()
        result = True
        for content in contents:
            logger.debug(f"现在检查{content}是否在串口数据中存在")
            result = result and content in data
        return result
