# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, China TSP, All rights reserved
# --------------------------------------------------------
# @Name:        hypervisor.py
# @Purpose:     todo
# @Author:      lizhe
# @Created:     2020/08/09 21:46
# --------------------------------------------------------
import os
import re
from time import sleep

from ..api import ScreenShot
from ..android.adb import ADB
from automotive.logger import logger


class HypervisorScreenShot(ScreenShot):
    """
    目前高通方案截图流程

    1、调用adb -s device shell htalk shell 'screenshot -file=/tsp/xxx.bmp' 方式截图并存放在qnx系统中

    其中/tsp表示QNX系统和安卓系统共享分区

    2、调用adb -s device shell echo 3 > /proc/sys/vm/drop_caches 命令同步共享区间

    3、调用adb -s device shell sync 写入到安卓空间

    4、调用adb -s device shell pull /tsp/xxx.bmp save_path > os.devnull  拉取到本地
    """

    def __init__(self, save_path: str, device_id: str = None):
        # 图片保存位置
        self.__path = save_path
        self.adb = ADB()
        if device_id:
            # 安卓device_id
            self.__device_id = device_id
        else:
            self.__connect()

    def __connect(self):
        """
        连接并查询
        :return:
        """
        contents = self.adb.devices()
        contents.pop(0)
        # 把第一行内容去掉再进行查找
        content = "".join(list(map(lambda x: str(x), contents)))
        logger.debug(f"{content}")
        try:
            line = re.search(r"\w+\sdevice", content).group(0)
            self.__device_id = line.split("device")[0].strip()
            logger.debug(f"{self.__device_id}")
        except AttributeError:
            logger.warning(f"please check adb connect first")

    def __adb_command(self, command: str):
        """
        执行adb命令, 已经带了adb -s device_id参数

        :param command: adb命令
        """
        command = f"adb -s {self.__device_id} {command}"
        os.system(command)

    def __screen_shot(self, image_name: str, display: int = None):
        """
        执行截图命令

        :param image_name: 图片名字，如果图片名字不带.bmp后缀，则增加bmp后缀

        :param display 屏幕序号
        """
        command = f"shell htalk shell 'screenshot -file=/tsp/{image_name}'"
        if display:
            command = f"{command} -display={display}"
        self.__adb_command(command)

    def __screen_shot_area(self, image_name: str, position: tuple, display: int = None):
        """
        执行截图命令

        :param image_name: 图片名字，如果图片名字不带.bmp后缀，则增加bmp后缀

        :param display 屏幕序号
        """
        x, y, width, height = position
        command = f"shell htalk shell 'screen_capture -file=/tsp/{image_name} -pos={x},{y} -size={width}x{height}'"
        if display:
            command = f"{command} -display={display}"
        self.__adb_command(command)

    def __sync_space(self):
        """
        同步qnx和android共享分区数据
        """
        commands = [f"shell \"echo 3 > /proc/sys/vm/drop_caches\"",
                    f"shell sync"]
        for command in commands:
            self.__adb_command(command)

    def __screen_shot_image(self, image_name: str, count: int, interval_time: float, position: tuple = None,
                            display: int = None) -> list:
        """
        截图操作，当position为None的时候为全屏截图

        :param image_name: 截图名称

        :param count: 截图数量

        :param interval_time: 截图间隔时间

        :param position: 区域截图位置

        :param display 屏幕序号
        """
        if count < 1:
            raise ValueError(f"count must >= 1, but current value is {count}")
        image_files = []
        for i in range(count):
            ex_image_name = image_name.split(".jpg")[0]
            image_name = f"{ex_image_name}__{i + 1}.jpg"
            if position:
                self.__screen_shot_area(image_name, position, display)
            else:
                self.__screen_shot(image_name, display)
            image_files.append(image_name)
            sleep(interval_time)
        self.__sync_space()
        return image_files

    def screen_shot(self, image_name: str, count: int, interval_time: float, display: int = None) -> list:
        return self.__screen_shot_image(image_name, count, interval_time)

    def screen_shot_area(self, position: tuple, image_name: str, count: int, interval_time: float,
                         display: int = None) -> list:
        return self.__screen_shot_image(image_name, count, interval_time, position)
