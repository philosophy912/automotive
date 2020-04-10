# -*- coding:utf-8 -*-
# --------------------------------------------------------  
# Copyright (C), 2016-2020, China TSP, All rights reserved
# --------------------------------------------------------                 
# @Name:        screenshot  
# @Purpose:     ScreenShot
# @Author:      lizhe  
# @Created:     2019/12/4 21:56  
# --------------------------------------------------------
import os
import subprocess
import shutil
from time import sleep
from loguru import logger

from .base_screen_shot import BaseScreenShot


class ScreenShot(BaseScreenShot):
    """
    适用于高通820A方案的截屏
    """

    def __init__(self, save_path):
        super().__init__(save_path)
        # 保存的image文件名
        self.__image_name = "screen_shot"
        # device id
        self.__device_id = None
        # adb connect status
        self.__is_connect = False
        # commands root需要的命令
        self.__commands = ["root", "setenforce 0", "remount"]
        # 最大的高
        self.__max_height = 720
        # 最大的宽
        self.__max_width = 1920
        # 板子上的share地址
        self.__share_path = "/tsp"

    def __get_screen_shot_area_command(self, image_name: str, x: int, y: int, width: int, height: int) -> str:
        """
            获取区域命令，后期可以更改
            :return:
        """
        logger.info("screen shot area")
        commands = f"htalk shell 'screen_capture -file={self.__share_path}/{image_name}.bmp " \
                   f"-pos={x},{y} -size={width}x{height}'"
        logger.info(commands)
        return commands

    def __create_root_command(self, switch: bool = False):
        """
            创建root需要的命令行，后期可以从外部传入
            :return:
        """
        logger.info(f"remount可能不成功，如果不成功，请手动remount")
        command1 = f"adb -s {self.__device_id} root > {os.devnull}"
        command2 = f"adb -s {self.__device_id} shell \"setenforce 0\" > {os.devnull}"
        command3 = f"adb -s {self.__device_id} remount > {os.devnull}"
        self.__commands = [command1, command2, command3]
        for command in self.__commands:
            if switch:
                self.__shell_command(command)
            logger.debug(f"root command is [{command}]")

    def __return_shell_command(self):
        pass

    def __root_device(self, commands: list):
        """
            使系统能够root
            :param commands: 命令行
            :return:
        """
        for command in commands:
            if "root" in command or "remount" in command:
                self.__shell_command(command, need_shell=False)
            else:
                self.__shell_command(command)

    def __shell_command_with_return(self, command: str, need_shell: bool = True) -> tuple:
        """
        执行shell命令并有回显
        :param command: shell命令
        :param need_shell:
        :return:  回显字符串
        """
        if need_shell:
            command_line = f"adb -s {self.__device_id} shell {command}"
        else:
            command_line = f"adb -s {self.__device_id} {command}"
        logger.debug(f"command line is [{command_line}]")
        return subprocess.getstatusoutput(command_line)

    def __shell_command(self, command: str, need_shell: bool = True):
        """
            执行shell命令(无回显)
            :param command:  shell命令
        """
        if need_shell:
            command_line = f"adb -s {self.__device_id} shell \"{command}\" > {os.devnull}"
        else:
            command_line = f"adb -s {self.__device_id} \"{command}\" > {os.devnull}"
        logger.debug(f"command line is [{command_line}]")
        os.system(command_line)

    def __system_prepare(self, commands: list):
        """
            保险起见，删除下面所有的bmp文件
            :param commands: root需要的命令列表
            :return:
        """
        logger.debug(f"save path = {self._save_path}")
        if not os.path.exists(self._save_path):
            os.mkdir(self._save_path)
        else:
            shutil.rmtree(self._save_path)
        self.__root_device(commands)
        sleep(0.5)

    def __adb_connect(self, commands: list, board_name: str = "msm8996_gvmq", device_name: str = "1234567"):
        """
            adb连接
            :param commands: root需要的命令列表
            :param board_name: 板子的名字
            :return:
        """
        if not self.__is_connect:
            # 收到返回数据并去掉第一行List of devices attached
            devices = os.popen("adb devices -l").readlines()[1:]
            for device in devices:
                # 如果写了device_name则检查这个
                if "device" in device:
                    if device_name in device:
                        self.__device_id = device_name
                        break
                    elif board_name in device:
                        logger.debug(f"device = {device}")
                        self.__device_id = device.split(" ")[0]
                        break
            self.__is_connect = True if self.__device_id else False
            if self.__is_connect:
                self.__system_prepare(commands)
            logger.info(f"adb connect status is {self.__is_connect}")

    def __screen_shot(self, image_name: str, interval_time: float, sync: bool = True):
        """
            用htalk命令截图
            :param image_name: 图片名称
            :param interval_time: 截图间隔时间
            :param sync: 是否同步共享目录
            :return:
        """
        # logger.info("screen full")
        commands = f"htalk shell 'screenshot -file={self.__share_path}/{image_name}.bmp'"
        self.__shell_command(commands)
        # logger.info(commands)
        sleep(interval_time)
        if sync:
            self.__sync_android_and_qnx()

    def __sync_android_and_qnx(self):
        """
            同步android和qnx的share空间
            :return:
        """
        self.__shell_command("echo 3 > /proc/sys/vm/drop_caches")
        sleep(1)

    def __pull_image(self, image_name: str):
        """
            把主机中的图片拉到本地
            :param image_name: 图片名称
            :return:
        """
        if not os.path.exists(self._save_path):
            os.mkdir(self._save_path)
        command = f"adb -s {self.__device_id} pull {self.__share_path}/{image_name}.bmp " \
                  f"{self._save_path} > {os.devnull}"
        logger.debug(f"command line is [{command}]")
        os.system(command)
        sleep(1)
        image_path = f"{self._save_path}\\{image_name}.bmp"
        logger.debug(f"image path = {image_path}")
        return os.path.exists(image_path)

    def __check_adb_connect(self):
        """
            检查adb是否连接
            :return:
        """
        if not self.__is_connect:
            raise RuntimeError("please connect adb first")

    def __screen_capture(self, image_name: str, x: int, y: int, width: int, height: int,
                         interval_time: float, sync: bool = False):
        """
            按照区域截图
            :param image_name: 图片名称
            :param x: the x-coordinates of the starting point
            :param y: the y-coordinates of the starting point
            :param width: the width of the image
            :param height: the height of the image
            :param interval_time: 多张图片截图间隔时间
            :param sync: 是否同步共享目录
            :return:
        """
        if x > self.__max_width:
            raise ValueError(f"x{x} is bigger than {self.__max_width}")
        if y > self.__max_height:
            raise ValueError(f"y{y} is bigger than {self.__max_height}")
        if (x + width) > self.__max_width:
            raise ValueError(f"x{x} and width {width} is bigger than {self.__max_width}")
        if (y + height) > self.__max_height:
            raise ValueError(f"y{y} and height {height} is bigger than {self.__max_height}")
        command = self.__get_screen_shot_area_command(image_name, x, y, width, height)
        self.__shell_command(command)
        sleep(interval_time)
        if sync:
            self.__sync_android_and_qnx()
            sleep(0.1)

    def screen_shot(self, image_name: str = None, count: int = 1, interval_time: float = 1):
        """
            Use [screenshot] commend to get one image from QNX system, and pull the image through adb commend.
            :param image_name: 要截图的图片名称(仅支持一张照片截图)
            :param count: 截图的张数
            :param interval_time: 多张图片截图间隔时间
            :return:
        """
        if count < 1:
            raise ValueError(f"count must >= 1, but current value is {count}")
        self.__adb_connect(self.__commands)
        self.__create_root_command()
        self.__check_adb_connect()
        image_name = image_name if image_name else self.__image_name
        image_files = []
        for i in range(count):
            # 设置图片的名称，增加前缀
            screen_shot_image_name = f"{i + 1}_{image_name}"
            # 最后一次的时候在sync
            sync = True if i == count - 1 else False
            logger.debug(f"now screen shot {screen_shot_image_name} images and sync is {sync}")
            self.__screen_shot(screen_shot_image_name, interval_time, sync)
            image_files.append(screen_shot_image_name)
        for image_file in image_files:
            self.__pull_image(image_file)
            sleep(0.5)

    def screen_shot_area(self, x: int, y: int, width: int, height: int, image_name: str = None, count: int = 1):
        """
            Use [screen_capture] commend to get one image from QNX system, and pull the image through adb commend.
            :param x: the x-coordinates of the starting point
            :param y: the y-coordinates of the starting point
            :param width: the width of the image
            :param height: the height of the image
            :param image_name: image name
            :param count: 截图的张数
            :return: None
        """
        if count < 1:
            raise ValueError(f"count must >= 1, but current value is {count}")
        if image_name:
            self.__image_name = image_name
        logger.debug(f"image_name = {self.__image_name}")
        self.__adb_connect(self.__commands)
        self.__check_adb_connect()
        image_name = image_name if image_name else self.__image_name
        image_files = []
        for i in range(count):
            # 设置图片的名称，增加前缀
            screen_shot_image_name = f"{i + 1}-{image_name}"
            # 最后一次的时候在sync
            sync = True if i == count - 1 else False
            logger.debug(f"now screen shot {image_name} images and sync is {sync}")
            self.__screen_capture(screen_shot_image_name, x, y, width, height, interval_time=0.1, sync=True)
            image_files.append(screen_shot_image_name)
        for image_file in image_files:
            self.__pull_image(image_file)
            sleep(0.5)
