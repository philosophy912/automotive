# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, China TSP, All rights reserved
# --------------------------------------------------------
# @Name:        serial_actions.py
# @Purpose:     串口操作
# @Author:      lizhe
# @Created:     2020/02/05 21:33
# --------------------------------------------------------
from loguru import logger

from automotive.tools.serial_port import SerialPort
from .base_actions import BaseActions


class SerialActions(BaseActions):
    """
    串口操作类
    """

    def __init__(self, port: str, baud_rate: int):
        super().__init__()
        self.__serial = SerialPort()
        self.__port = port.upper()
        self.__baud_rate = baud_rate

    def open(self):
        """
        打开串口
        """
        logger.info("初始化串口")
        logger.info("打开串口")
        buffer = 32768
        self.__serial.connect(port=self.__port, baud_rate=self.__baud_rate)
        logger.info(f"*************串口初始化成功*************")
        self.__serial.set_buffer(buffer, buffer)
        logger.info(f"串口缓存为[{buffer}]")

    def close(self):
        """
        关闭串口
        """
        logger.info("关闭串口")
        self.__serial.disconnect()

    def judge_text_in_serial(self, contents: list) -> bool:
        """
        判断串口是否有指定的内容

        :param contents: 内容

        :return:
            True： 串口输出找到了匹配的内容
            False: 串口输出没有找到匹配的内容
        """
        data = self.__serial.read_all(True)
        result = True
        for content in contents:
            logger.debug(f"现在检查{content}是否在串口数据中存在")
            result = result and content.encode("utf-8") in data
        return result

    def clean_serial_data(self):
        """
        清空串口缓存数据
        """
        self.__serial.read_all()

    def check_can_available(self) -> bool:
        self.__serial.flush()
        self.__serial.send("ls", type_=False)
        content = self.__serial.read_lines()
        return len(content) > 0

