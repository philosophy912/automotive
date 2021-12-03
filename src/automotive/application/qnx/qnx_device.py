# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        qnx_device.py
# @Author:      lizhe
# @Created:     2021/5/1 - 23:55
# --------------------------------------------------------

from time import sleep
from automotive.logger.logger import logger
from automotive.utils.serial_utils import SerialUtils
from automotive.utils.utils import Utils
from automotive.utils.common.enums import SystemTypeEnum
from ..common.interfaces import BaseSocketDevice


class QnxDevice(BaseSocketDevice):
    """
    主要实现红旗空调屏相关的一些操作， 如启动InjectEvents服务，删除相关路径下的文件，测试完成后拷贝相关的文件等
    """

    def __init__(self, port: str):
        # 设置串口
        self.serial = SerialUtils()
        # 设置端口
        self.__port = port.upper()

    def send_command(self, command: str):
        """
        发送命令到串口

        :param command: 命令
        """
        logger.debug(f"command is {command}")
        self.serial.write(command)

    def send_commands(self, commands: list, interval: float = 0):
        """
        发送多条命令到串口

        :param commands: 命令列表

        :param interval: 命令之间的间隔时间
        """
        for command in commands:
            self.send_command(command)
            sleep(interval)

    def init_actions_service(self):
        """
        准备屏幕点击操作(启动InjectEvents服务)
        """
        commands = [
            f"cd /usr/bin",
            f"slay InjectEvents",
            f"./InjectEvents &",
            "cd -"
        ]
        self.send_commands(commands, 2)

    def init_screenshot_folder(self, path):
        """
        准备屏幕截图操作

        :param path: 板子上存放截图图片的地址
        """
        commands = ["mount -uw /",
                    f"rm -rvf {path}",
                    f"mkdir {path}"]
        self.send_commands(commands)

    def copy_images_to_usb(self, path):
        """
        拷贝截图文件到USB中

        :param path: 板子上存放截图图片的地址
        """
        usb_path = "/fs/usb0"
        if self.serial.file_exist(usb_path, 5, 1):
            logger.info("usb is plugin and it will create folder to copy images")
            # 创建以时间为结尾的文件夹
            current_time = Utils.get_time_as_string("%Y%m%d%H%M%S")
            target_folder = f"{usb_path}/{current_time}"
            self.serial.write(f"mkdir {target_folder}")
            if self.serial.file_exist(target_folder):
                logger.info("usb folder created success")
                self.serial.copy_file(path, target_folder, SystemTypeEnum.QNX)
                self.serial.write("sync")
            else:
                logger.error(f"usb devices cannot create folder, please copy file {path} manually")
        else:
            logger.error(f"usb device is not exist, please copy file {path} manually")

    def connect(self, username: str = None, password: str = None, ipaddress: str = None):
        try:
            self.serial.connect(self.__port, baud_rate=115200)
        except RuntimeError:
            logger.error(f"connect failed in {self.__port}")
        # 存在用户名和密码的时候就执行登陆操作
        if username and password:
            self.serial.login(username, password)

    def disconnect(self):
        self.serial.disconnect()
