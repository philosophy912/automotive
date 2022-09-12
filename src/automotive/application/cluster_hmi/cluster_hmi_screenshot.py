# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        screenshot.py
# @Author:      lizhe
# @Created:     2021/5/1 - 23:53
# --------------------------------------------------------
from typing import Sequence
from time import sleep
from automotive.utils.telnet_utils import TelnetUtils
from automotive.logger.logger import logger
from ..common.interfaces import BaseScreenShot, Position


class ClusterHmiScreenshot(BaseScreenShot):
    """
    nobo的HMI项目截图操作， 目前由telnet的方式实现，后续若关闭telnet可以改为串口方式实现, 使用serial_utils工具已实现登陆

    由于QNX系统自带screenshot截图操作，故实现该截图操作，若改为Linux操作则需要重新实现截图操作
    """

    def __init__(self, telnet: TelnetUtils, save_path: str):
        self.__telnet = telnet
        # 图片保存位置(针对本地地址，即地址为板子上的地址)
        self.__path = save_path

    @property
    def path(self) -> str:
        return self.__path

    def __screen_shot(self, image_name: str, display: int = None):
        """
        执行截图命令

        :param image_name: 图片名字，已包含后缀名
        """
        self.__path = self.__path[1:] if self.__path.startswith("/") else self.__path
        file_name = f"/{self.__path}/{image_name}"
        command = f"screenshot -file={file_name}"
        if display:
            command = f"{command} -display={display}"
        self.__telnet.write(command)

    def screen_shot(self, image_name: str, count: int, interval_time: float, display: int = None) -> Sequence[str]:
        if count < 1:
            raise ValueError(f"count must >= 1, but current value is {count}")
        # 图片列表
        image_files = []
        for i in range(count):
            ex_image_name = image_name.split(".jpg")[0]
            screenshot_image_name = f"{ex_image_name}__{i + 1}.jpg"
            logger.debug(f"screenshot image name is {screenshot_image_name}")
            self.__screen_shot(screenshot_image_name, display=display)
            image_files.append(screenshot_image_name)
            sleep(interval_time)
        return image_files

    def screen_shot_area(self, position: Position, image_name: str, count: int, interval_time: float,
                         display: int = None) -> Sequence[str]:
        raise RuntimeError("not support area screenshot")
