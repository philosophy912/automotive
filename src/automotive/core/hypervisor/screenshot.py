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
        adb = ADB()
        contents = adb.devices()
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

    def __screen_shot(self, image_name: str):
        """
        执行截图命令

        :param image_name: 图片名字，如果图片名字不带.bmp后缀，则增加bmp后缀
        """
        if not image_name.endswith(".bmp"):
            image_name = f"{image_name}.bmp"
        command = f"shell htalk shell 'screenshot -file=/tsp/{image_name}'"
        self.__adb_command(command)

    def __screen_shot_area(self, image_name: str, position: tuple):
        """
        执行截图命令

        :param image_name: 图片名字，如果图片名字不带.bmp后缀，则增加bmp后缀
        """
        if not image_name.endswith(".bmp"):
            image_name = f"{image_name}.bmp"
        x, y, width, height = position
        command = f"shell htalk shell 'screen_capture -file=/tsp/{image_name} -pos={x},{y} -size={width}x{height}'"
        self.__adb_command(command)

    def __sync_space(self):
        """
        同步qnx和android共享分区数据
        """
        commands = [f"shell echo 3 > /proc/sys/vm/drop_caches",
                    f"shell sync"]
        for command in commands:
            self.__adb_command(command)

    def __pull_file(self, image_name: str):
        """
        拉取文件到本地
        :param image_name: 要拉取的图片名称
        """
        command = f"shell pull /tsp/{image_name} {self.__path} > {os.devnull}"
        self.__adb_command(command)
        image_path = "\\".join([self.__path, image_name])
        if not os.path.exists(image_path):
            raise RuntimeError(f"file {image_name} is not pull in local path, please check it again")

    def __screen_shot_image(self, image_name: str, count: int, interval_time: float, position: tuple = None):
        """
        截图操作，当position为None的时候为全屏截图

        :param image_name: 截图名称

        :param count: 截图数量

        :param interval_time: 截图间隔时间

        :param position: 区域截图位置
        """
        if count < 1:
            raise ValueError(f"count must >= 1, but current value is {count}")
        image_files = []
        for i in range(count):
            ex_image_name = image_name.split(".bmp")[0]
            image_name = f"{ex_image_name}__{count + 1}"
            if position:
                self.__screen_shot_area(image_name, position)
            else:
                self.__screen_shot(image_name)
            image_files.append(image_name)
            sleep(interval_time)
        self.__sync_space()
        for image in image_files:
            self.__pull_file(image)
            sleep(0.5)

    def screen_shot(self, image_name: str, count: int, interval_time: float):
        self.__screen_shot_image(image_name, count, interval_time)

    def screen_shot_area(self, position: tuple, image_name: str, count: int, interval_time: float):
        self.__screen_shot_image(image_name, count, interval_time, position)
