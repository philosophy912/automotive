# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, China TSP, All rights reserved
# --------------------------------------------------------
# @Name:        qnx_device.py
# @Purpose:     todo
# @Author:      lizhe
# @Created:     2020/8/10 - 13:01
# --------------------------------------------------------
from ..singleton import Singleton
from time import sleep
from automotive.logger import logger
from automotive.utils.serial_port import SerialPort
from automotive.utils.utils import Utils


class QnxDevice(metaclass=Singleton):

    def __init__(self, port: str):
        # 设置串口
        self.serial = SerialPort()
        # 设置端口
        self.__port = port.upper()

    def __login(self, username: str, password: str, double_check: bool = False):
        """
        登陆系统

        :param username: 用户名

        :param password: 密码

        :param double_check: 二次确认
        """
        self.serial.flush_output()
        self.send_command("\r\n")
        sleep(0.5)
        output = self.serial.read_all()
        if "login" in output:
            logger.debug(f"input login username[{username}]")
            self.send_command(username)
            sleep(1)
            output = self.serial.read_all()
            if "Password" in output:
                logger.debug(f"input login password[{password}]")
                self.send_command(password)
        if double_check:
            # 再次校验是否登陆成功
            self.serial.flush_output()
            self.send_command("\r\n")
            sleep(0.5)
            output = self.serial.read_all()
            if "login" in output:
                logger.warning("login failed")

    def __check_copy_status(self):
        """
        检查copy文件是否完成
        """
        flag = True
        i = 1
        while flag:
            logger.info("copy is processing")
            self.serial.flush_output()
            command = f"pidin | grep cp"
            self.send_command(command)
            results = self.serial.read_lines()
            logger.debug(f"第{i}次结果{results}")
            for result in results:
                if "Done" in result:
                    flag = False
            sleep(1)
            i += 1
        logger.info("copy is finished")

    def send_command(self, command: str):
        """
        发送命令到串口

        :param command: 命令
        """
        logger.debug(f"command is {command}")
        self.serial.send(command)

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
        logger.warning(f"please check usb device whether plugin, copy will process after 10 seconds later")
        sleep(10)
        current_time = Utils.get_time_as_string("%Y%m%d%H%M%S")
        usb_path = "/fs/usb0"
        self.serial.flush_output()
        self.serial.flush_input()
        self.send_commands([f"cd /", f"ls -l"])
        results = self.serial.read_lines()
        usb_exist = False
        for result in results:
            if result.strip().endswith("fs"):
                usb_exist = True
        if usb_exist:
            logger.info("usb device is found, now copy......")
            screenshot_path = f"{usb_path}/screenshot"
            current_time_path = f"{screenshot_path}/{current_time}"
            commands = [
                f"mkdir {screenshot_path}",
                f"rm -rvf {current_time_path}",
                f"mkdir {current_time_path}",
                f"cp {path}/* {current_time_path}/ &"
                f"sync"
            ]
            self.send_commands(commands, 1)
            self.__check_copy_status()
        else:
            logger.info("usb device is not found, please copy file manual")

    def connect(self, username: str = None, password: str = None):
        try:
            self.serial.connect(self.__port, baud_rate=115200)
        except RuntimeError:
            logger.error(f"connect failed in {self.__port}")
        # 存在用户名和密码的时候就执行登陆操作
        if username and password:
            self.__login(username, password)

    def disconnect(self):
        self.serial.disconnect()
