# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        screenshot.py
# @Author:      lizhe
# @Created:     2021/5/1 - 23:55
# --------------------------------------------------------
import os
import re
from time import sleep
from typing import Tuple, List

from automotive.core.android.adb import ADB
from automotive.logger.logger import logger
from ..common.interfaces import BaseScreenShot


class HypervisorScreenShot(BaseScreenShot):
    """
    目前高通方案截图流程，

    1、调用adb -s device shell htalk shell 'screenshot -file=/tsp/xxx.bmp' 方式截图并存放在qnx系统中

    其中/tsp表示QNX系统和安卓系统共享分区

    2、调用adb -s device shell echo 3 > /proc/sys/vm/drop_caches 命令同步共享区间

    3、调用adb -s device shell sync 写入到安卓空间

    4、调用adb -s device shell pull /tsp/xxx.bmp save_path > os.devnull  拉取到本地

    若无htalk调用qnx的串口进行截图操作，则可以使用串口的方式进行截图，或者使用ssh/telnet的方式操作，若无法拉取到电脑，

    则把全自动化测试变为半自动化测试
    """

    def __init__(self, save_path: str, device_id: str = None, need_sync_space: bool = True):
        # 图片保存位置
        self.__path = save_path
        self.__adb = ADB()
        self.__need_sync_space = need_sync_space
        if device_id:
            # 安卓device_id
            self.__device_id = device_id
        else:
            self.__connect()

    @property
    def adb(self):
        return self.__adb

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
        command = f"shell htalk shell 'screenshot -file=/{self.__path}/{image_name}'"
        if display:
            command = f"{command} -display={display}"
        self.__adb_command(command)

    def __screen_shot_area(self, image_name: str, position: Tuple[int, int, int, int], display: int = None):
        """
        执行截图命令

        :param image_name: 图片名字，如果图片名字不带.bmp后缀，则增加bmp后缀

        :param display 屏幕序号
        """
        x, y, width, height = position
        command = f"shell htalk shell 'screen_capture -file=/{self.__path}/{image_name} -pos={x},{y} " \
                  f"-size={width}x{height}'"
        if display:
            command = f"{command} -display={display}"
        self.__adb_command(command)

    def __sync_space(self):
        """
        同步qnx和android共享分区数据
        """
        commands = [f"shell \"echo 3 > /proc/sys/vm/drop_caches\"",
                    f"shell htalk shell 'sync'",
                    f"shell sync"
                    ]
        for command in commands:
            self.__adb_command(command)

    def __screen_shot_image(self, image_name: str, count: int, interval_time: float,
                            position: Tuple[int, int, int, int] = None,
                            display: int = None) -> List[str]:
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
            screenshot_image_name = f"{ex_image_name}__{i + 1}.jpg"
            if position:
                self.__screen_shot_area(screenshot_image_name, position, display)
            else:
                self.__screen_shot(screenshot_image_name, display)
            image_files.append(screenshot_image_name)
            sleep(interval_time)
        if self.__need_sync_space:
            self.__sync_space()
        return image_files

    def screen_shot(self, image_name: str, count: int, interval_time: float, display: int = None) -> List[str]:
        return self.__screen_shot_image(image_name, count, interval_time)

    def screen_shot_area(self, position: Tuple[int, int, int, int], image_name: str, count: int, interval_time: float,
                         display: int = None) -> List[str]:
        return self.__screen_shot_image(image_name, count, interval_time, position)

    def remove_file(self, remote: str):
        """
        htalk命令，删除单个文件
        :param remote: 远程文件地址
        :return:
        """
        self.__adb_command(f"shell htalk shell 'rm {remote}'")

    def remove_files(self, files: List[str]):
        """
        htalk命令，删除多个文件
        :param files: 存放文件地址的列表
        """
        for file in files:
            self.remove_file(file)
            sleep(1)
        sleep(1)

    def remove_folder(self, folder: str):
        """
        htalk命令，删除文件夹
        :param folder: 文件目录，不以分隔符结尾，例如、/log
        """
        self.__adb_command(f"shell htalk shell 'rm -r {folder}'")
