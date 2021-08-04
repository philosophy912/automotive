# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        qnx_actions.py
# @Author:      lizhe
# @Created:     2021/5/1 - 23:55
# --------------------------------------------------------
from time import sleep
from automotive.common.api import BaseActions
from .qnx_device import QnxDevice
from automotive.logger import logger


class QnxActions(BaseActions):
    """
    实现相关的操作，若操作方式变换则可以更新该处代码
    """

    def __init__(self, device: QnxDevice):
        self.__device = device

    def __press(self, display: int, x: int, y: int, continue_time: float = 0.2):
        """
        点击或者长按

        :param display: 屏幕

        :param x: x坐标

        :param y: y坐标

        :param continue_time: 持续时间， 默认点击事件0.2秒
        """
        press = f"echo \"{display} 1 {x} {y}\" > /dev/inject_events"
        release = f"echo \"{display} 3 {x} {y}\" > /dev/inject_events"
        commands = [press, release]
        self.__device.send_commands(commands, continue_time)

    def click(self, display: int, x: int, y: int, interval: float = 0.2):
        logger.info(f"click display {display} position[{x},{y}]")
        self.__press(display, x, y, interval)

    def double_click(self, display: int, x: int, y: int, interval: float = 0.2):
        self.click(display, x, y)
        sleep(interval)
        self.click(display, x, y)

    def press(self, display: int, x: int, y: int, continue_time: float):
        logger.info(f"press display {display} position[{x},{y}], continue time is {continue_time} ")
        self.__press(display, x, y, continue_time)

    def swipe(self, display: int, x1: int, y1: int, x2: int, y2: int, continue_time: float):
        logger.info(f"slide display[{display}] from {x1}, {y1} to {x2} {y2} use time {continue_time}")
        commands = []
        # 持续时间如果大于0.1秒则按照此公式计算，如果小于0.1秒则按照实际的时间来计算
        if continue_time > 0.1:
            time = int(continue_time / 0.1)
            if x1 == x2:
                # 纵向滑动
                # 计算滑动的距离
                height = abs(y2 - y1)
                interval_height = int(height / time)
                for i in range(time):
                    if i == 0:
                        command = f"echo \"{display} 1 {x1} {y1}\" > /dev/inject_events"
                    elif i == time - 1:
                        command = f"echo \"{display} 3 {x1} {y2}\" > /dev/inject_events"
                    else:
                        # 上滑
                        if y2 > y1:
                            command = f"echo \"{display} 2 {x1} {y1 + i * interval_height}\" > /dev/inject_events"
                        else:
                            command = f"echo \"{display} 2 {x1} {y1 - i * interval_height}\" > /dev/inject_events"
                    commands.append(command)
            elif y1 == y2:
                # 横向滑动
                width = abs(x2 - x1)
                interval_width = int(width / time)
                for i in range(time):
                    if i == 0:
                        command = f"echo \"{display} 1 {x1} {y1}\" > /dev/inject_events"
                    elif i == time - 1:
                        command = f"echo \"{display} 3 {x1} {y2}\" > /dev/inject_events"
                    else:
                        if x2 > x1:
                            command = f"echo \"{display} 2 {x1 + i * interval_width} {y1}\" > /dev/inject_events"
                        else:
                            command = f"echo \"{display} 2 {x1 - i * interval_width} {y1}\" > /dev/inject_events"
                    commands.append(command)
            else:
                raise RuntimeError(f"x1[{x1}] is not equal x2[{x2}] or y1[{y1}] is not equal y2[{y2}]")
            self.__device.send_commands(commands, 0.1)
        else:
            if x1 == x2:
                command1 = f"echo \"{display} 1 {x1} {y1}\" > /dev/inject_events"
                command2 = f"echo \"{display} 3 {x1} {y2}\" > /dev/inject_events"
            elif y1 == y2:
                command1 = f"echo \"{display} 1 {x1} {y1}\" > /dev/inject_events"
                command2 = f"echo \"{display} 3 {x1} {y2}\" > /dev/inject_events"
            else:
                raise RuntimeError(f"x1[{x1}] is not equal x2[{x2}] or y1[{y1}] is not equal y2[{y2}]")
            commands.append(command1)
            commands.append(command2)
            self.__device.send_commands(commands, continue_time)
