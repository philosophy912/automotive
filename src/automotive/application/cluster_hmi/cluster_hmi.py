# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        cluster_hmi.py
# @Author:      lizhe
# @Created:     2021/5/1 - 23:53
# --------------------------------------------------------
import time
from time import sleep
from typing import List

from .cluster_hmi_screenshot import ClusterHmiScreenshot
from automotive.utils.ftp_utils import FtpUtils
from automotive.utils.telnet_utils import TelnetUtils
from automotive.logger.logger import logger
from ..common.interfaces import BaseSocketDevice


_start_service_list = "clusterNormal_service", "safety", "GaugeMagServer", "cluster_iviinterface"


class ClusterHmi(BaseSocketDevice):
    """
    基于nobo 8155实现的代码，

    由于该板子支持telnet进行电脑与板子之间的连接，并且通过FTP的方式进行文件的下载，后续若关闭telnet接口可该用serial的方式进行连接

    若关闭了ftp则可以将该测试从全自动测试变成半自动测试，即与红旗空调屏测试方式一致。

    控制命令的部分需要研发实现相关的操作，后续若完成fdbus的操作可改为自行发送protobuffer数据实现。
    """

    def __init__(self, board_path: str, local_folder: str, test_binary: str = None, cluster: str = None,
                 whud: str = None, service_list: List[str] = _start_service_list):
        """
        初始化

        :param board_path: 板子的地址，用于存放截图和命令

        :param local_folder: 本地的地址， 用于存放截图下载的地址

        :param test_binary: 测试文件的本地文件夹地址

        :param cluster:  cluster软件的地址

        :param whud:  whud软件的地址
        """
        self.__ftp = FtpUtils()
        self.__telnet = TelnetUtils()
        # 本地路径
        self.__local_folder = local_folder
        self.__test_binary = test_binary
        self.__cluster = cluster
        self.__whud = whud
        self.__board_path = board_path
        self.__screenshot = ClusterHmiScreenshot(self.__telnet, board_path)
        self.__service_list = service_list

    def __replace(self, folder: str, application: str, sw_files: str):
        """
        替换application
        :param folder: bin下面的文件夹
        :param application: 应用程序名称
        :param sw_files:  上传的文件夹路径
        """
        self.__telnet.write("cd /")
        sleep(0.5)
        self.__telnet.write(f"slay {application}")
        sleep(2)
        self.__ftp.upload_folder(f"/bin/{folder}", sw_files)
        sleep(1)
        self.__telnet.write(f"chmod 777 /bin/{folder}/{application}")
        sleep(2)
        self.__telnet.write(f"cd /bin/{folder}")
        self.__telnet.write(f".{application} &")
        sleep(2)

    def __prepare(self):
        """
        1、上传cluster代码
        2、上传whub代码
        :return:
        """
        if self.__cluster:
            self.__replace("cluster_HMI", "nobo_cluster", self.__cluster)
        if self.__whud:
            self.__replace("whud_HMI", "nobo_whud", self.__whud)
        if self.__test_binary:
            self.__telnet.write(f"rm -rvf {self.__board_path}")
            self.__telnet.write(f"mkdir {self.__board_path}")
            sleep(1)
            logger.debug(f"upload folder from {self.__test_binary} to {self.__board_path}")
            self.__ftp.upload_folder(self.__board_path, self.__test_binary)
            sleep(1)
            self.__telnet.write(f"chmod -R 777 {self.__board_path}")

        if self.__service_list:
            # 新增两条命令
            self.__telnet.write(f"mount -uw /")
            self.__telnet.write(f"hamctrl -stop")
            sleep(1)
            for service in self.__service_list:
                self.__telnet.write(f"slay {service}")
        self.__telnet.write(f"cd {self.__board_path}")
        self.__telnet.write(f"chmod 777 *")

    def disconnect(self):
        self.__ftp.disconnect()
        self.__telnet.disconnect()

    def connect(self, username: str = None, password: str = None, ipaddress: str = None):
        self.__ftp.connect(ipaddress, username, password)
        self.__telnet.connect(ipaddress, username, password)
        self.__prepare()

    def send_command(self, command: str, interval: float = 0.5):
        logger.info(f"send command is {command}")
        self.__telnet.write(command, interval)
        sleep(interval)

    def read(self) -> str:
        return self.__telnet.read()

    def screen_shot(self, image_name: str, count: int, interval_time: float, timeout: int = 10, display: int = None) -> List[str]:
        """
        """
        # 10张图片
        images = self.__screenshot.screen_shot(image_name, count, interval_time, display)
        start_time = time.time()
        file_exist_flag = False
        result = True

        while result:
            # 超时退出机制，避免死循环
            current_time = time.time()
            if current_time - start_time > timeout:
                result = False
            if self.__check_screenshot_success(images):
                result = False
                file_exist_flag = True
        if not file_exist_flag:
            raise RuntimeError("screenshot failed, please check image in borad or telent command")
        else:
            return images

    def __check_screenshot_success(self, images: List[str]) -> bool:
        """
        只检查文件是否在板子上存在
        """
        count = 0
        # 遍历images，并检查在板子上是否存在截图文件
        for image in images:
            # 板子上的完整路径
            image = f"/{self.__screenshot.path}/{image}"
            if self.__telnet.file_exist(file=image, check_times=10, interval=1):
                # 找到了文件
                count += 1
        # 判断条件是文件截取数量大于0，文件截取都在板子上找到
        return len(images) > 0 and len(images) == count

    def download_image(self, file_name: str) -> str:
        return self.__ftp.download_file(file_name, self.__local_folder)

    def download_images(self, file_names: list) -> list:
        file_names = list(map(lambda x: f"{self.__board_path}/{x}", file_names))
        return self.__ftp.download_files(file_names, self.__local_folder)
