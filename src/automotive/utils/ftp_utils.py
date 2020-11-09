# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, China TSP, All rights reserved
# --------------------------------------------------------
# @Name:        ftp_utils.py
# @Purpose:     todo
# @Author:      lizhe
# @Created:     2020/10/22 - 22:42
# --------------------------------------------------------
import os
from time import sleep
from ftplib import FTP
from automotive.logger.logger import logger


class FtpUtils(object):
    """
    FTP工具类，提供下载文件的方法，暂无上传文件功能
    """

    def __init__(self):
        self.__ftp = FTP()
        self.__flag = False

    def check_status(func):
        """
        检查设备是否已经连接
        :param func: 装饰器函数
        """

        def wrapper(self, *args, **kwargs):
            if not self.__flag:
                raise RuntimeError("please connect target first")
            return func(self, *args, **kwargs)

        return wrapper

    def connect(self, ipaddress: str, username: str, password: str, port: int = 21, timeout: int = 10):
        """
        连接FTP服务器

        :param ipaddress: FTP服务器地址

        :param username:  用户名

        :param password: 密码

        :param port:  端口，默认21

        :param timeout: 连接超时时间
        """
        if not self.__flag:
            try:
                self.__ftp.connect(ipaddress, port=port, timeout=timeout)
                self.__ftp.login(username, password)
                self.__flag = True
                logger.debug(f"login {ipaddress} with {username} success")
            except TimeoutError as e:
                logger.error(f"TimeoutError {e}")
                self.__flag = False
            except ConnectionRefusedError as e:
                logger.error(f"ConnectionRefusedError {e}")
                self.__flag = False

    def disconnect(self):
        """
        断开当前FTP连接
        """
        if self.__flag:
            self.__ftp.quit()

    @check_status
    def download_folder(self, remote_folder: str, local_folder: str, filter_type: str = None) -> list:
        """
        下载文件夹中的所有文件到本地
        （未测试文件夹中包含文件夹是否成功）

        :param remote_folder: FTP服务器所在的文件夹

        :param local_folder:  本地文件夹

        :param filter_type: 要下载的文件后缀名

        :return: 下载到的本地文件路径
        """
        local_files = []
        self.__ftp.cwd(remote_folder)
        file_list = self.__ftp.nlst()
        for name in file_list:
            logger.debug(f"remote name is {name}")
            local_file = f"{local_folder}\\{name}"
            with open(local_file, "wb") as f:
                if filter_type:
                    if name.endswith(filter_type):
                        self.__ftp.retrbinary(f"RETR {name}", f.write)
                        local_files.append(local_file)
                else:
                    self.__ftp.retrbinary(f"RETR {name}", f.write)
                    local_files.append(local_file)
        return local_files

    @check_status
    def download_files(self, remote_files: list, local_folder: str) -> list:
        """
        下载文件列表到本地

        :param remote_files: 要下载的FTP服务器文件的路径

        :param local_folder: 本地的文件夹

        :return:  下载到的本地文件路径
        """
        local_files = []
        for file in remote_files:
            local_files.append(self.download_file(file, local_folder))
            sleep(1)
        return local_files

    @check_status
    def download_file(self, remote_file: str, local_folder: str) -> str:
        """
        下载文件到本地
        :param remote_file: 要下载的FTP服务器文件的路径

        :param local_folder: 本地的文件夹

        :return: 下载到的本地文件路径
        """
        logger.debug(f"remote_file name is {remote_file}")
        # remote_file = "/tsp/aaaa__1.jpg"
        file_name = remote_file.split("/")[-1]
        local_file = f"{local_folder}\\{file_name}"
        with open(local_file, "wb") as f:
            self.__ftp.retrbinary(f"RETR {remote_file}", f.write)
        return local_file

    @check_status
    def upload_file(self, remote_folder: str, local_file: str):
        """
        上传本地文件到ftp服务器位置

        :param remote_folder:  FTP服务器位置

        :param local_file:  本地文件
        """
        buffer_size = 1024
        self.__ftp.cwd(remote_folder)
        with open(local_file, "rb") as f:
            self.__ftp.storbinary(f"STOR {os.path.basename(local_file)}", f, buffer_size)

    @check_status
    def upload_files(self, remote_folder: str, local_files: list):
        """
        上传本地文件列表到ftp服务器位置

        :param remote_folder: FTP服务器位置

        :param local_files: 本地文件列表
        """
        for file in local_files:
            self.upload_file(remote_folder, file)

    @check_status
    def upload_folder(self, remote_folder: str, local_folder: str, filter_type: str = None):
        """
        上传本地夹下所有文件到FTP服务器， 仅支持文件夹下所有内容为文件，带文件夹可能会导致错误

        :param filter_type: 要上传的文件后缀名

        :param remote_folder: FTP服务器位置

        :param local_folder: 本地文件列表
        """
        upload_files = list(map(lambda x: fr"{local_folder}\{x}", os.listdir(local_folder)))
        if filter_type:
            upload_files = list(filter(lambda x: x.endswith(filter_type), upload_files))
        logger.debug(f"upload_files is {upload_files}")
        for file in upload_files:
            self.upload_file(remote_folder, file)
