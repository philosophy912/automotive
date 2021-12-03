# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        air_condition.py
# @Author:      lizhe
# @Created:     2021/5/1 - 23:55
# --------------------------------------------------------
from typing import Tuple

from .qnx_device import QnxDevice
from .qnx_actions import QnxActions
from .qnx_local_screenshot import QnxLocalScreenShot
from ..common.interfaces import BaseScreenShot, BaseActions, BaseSocketDevice


class AirCondition(BaseScreenShot, BaseActions, BaseSocketDevice):
    """
    空调屏的操作，基于红旗空调屏特有的inject_events操作，可以实现屏幕的滑动、点击、长按、双击等操作，该操作方式主要由串口实现，

    若需要更改为telnet操作可以进行相关的组合即可。
    """

    def __init__(self, save_path: str, port: str):
        self.__device = QnxDevice(port)
        self.__actions = QnxActions(self.__device)
        self.__screen_shot = QnxLocalScreenShot(save_path, self.__device)
        self.__path = save_path

    def connect(self, username: str = None, password: str = None, ipaddress: str = None):
        self.__device.connect(username, password)
        self.__device.init_actions_service()
        self.__device.init_screenshot_folder(self.__path)

    def disconnect(self):
        # 由于拷贝存在问题，暂时注释，需要手动拷贝文件
        # self.__device.copy_images_to_usb(self.__path)
        self.__device.disconnect()

    def screen_shot(self, image_name: str, count: int, interval_time: float, display: int = None) -> list:
        return self.__screen_shot.screen_shot(image_name, count, interval_time, display)

    def screen_shot_area(self, position: Tuple[int, int, int, int], image_name: str, count: int, interval_time: float,
                         display: int = None) -> list:
        return self.__screen_shot.screen_shot_area(position, image_name, count, interval_time, display)

    def click(self, display: int, x: int, y: int, interval: float = 0.2):
        self.__actions.click(display, x, y, interval)

    def double_click(self, display: int, x: int, y: int, interval: float):
        self.__actions.double_click(display, x, y, interval)

    def press(self, display: int, x: int, y: int, continue_time: float):
        self.__actions.press(display, x, y, continue_time)

    def swipe(self, display: int, start_x: int, start_y: int, end_x: int, end_y: int, continue_time: float):
        self.__actions.swipe(display, start_x, start_y, end_x, end_y, continue_time)
