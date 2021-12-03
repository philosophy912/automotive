# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        screenshot.py
# @Author:      lizhe
# @Created:     2021/5/1 - 23:55
# --------------------------------------------------------
from time import sleep
from typing import Tuple, List

from .qnx_device import QnxDevice
from automotive.logger.logger import logger
from ..common.interfaces import BaseScreenShot


class QnxLocalScreenShot(BaseScreenShot):
    """
    1、调用qnx中的screenshot命令进行截图操作，图片存放于板子中
    """

    def __init__(self, save_path: str, device: QnxDevice):
        # 图片保存位置(针对本地地址，即地址为板子上的地址)
        self.__path = save_path
        self.__device = device

    def screen_shot(self, image_name: str, count: int, interval_time: float, display: int = None) -> list:
        return self.__screen_shot_image(image_name, count, interval_time, display=display)

    def screen_shot_area(self, position: Tuple[int, int, int, int], image_name: str, count: int, interval_time: float,
                         display: int = None) -> list:
        return self.__screen_shot_image(image_name, count, interval_time, position, display=display)

    def __screen_shot(self, image_name: str, display: int = None):
        """
        执行截图命令

        :param image_name: 图片名字，已包含后缀名
        """
        command = f"screenshot -file=/{self.__path}/{image_name}"
        if display:
            command = f"{command} -display={display}"
        self.__device.send_command(command)

    def __screen_shot_area(self, image_name: str, position: Tuple[int, int, int, int], display: int = None):
        """
        执行截图命令(TODO， 目前QNX系统下不支持区域截图)

        :param image_name: 图片名字，已包含后缀名
        """
        x, y, width, height = position
        command = f"screen_capture -file=/{self.__path}/{image_name} -pos={x},{y} -size={width}x{height}"
        if display:
            command = f"{command} -display={display}"
        logger.error(f"area screenshot command is {command}")
        raise RuntimeError("not support area screenshot")

    def __screen_shot_image(self, image_name: str, count: int, interval_time: float,
                            position: Tuple[int, int, int, int] = None,
                            display: int = None) -> List[str]:
        """
        截图操作，当position为None的时候为全屏截图

        :param image_name: 截图名称

        :param count: 截图数量

        :param interval_time: 截图间隔时间

        :param position: 区域截图位置
        """
        if count < 1:
            raise ValueError(f"count must >= 1, but current value is {count}")
        # 图片列表
        image_files = []
        for i in range(count):
            ex_image_name = image_name.split(".jpg")[0]
            image_name = f"{ex_image_name}__{i + 1}.jpg"
            logger.debug(f"screenshot image name is {image_name}")
            if position:
                self.__screen_shot_area(image_name, position, display=display)
            else:
                self.__screen_shot(image_name, display=display)
            image_files.append(image_name)
            sleep(interval_time)
        return image_files
