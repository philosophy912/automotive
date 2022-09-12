# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        ftp_utils.py
# @Author:      lizhe
# @Created:     2021/5/1 - 23:33
# --------------------------------------------------------
import os
from time import sleep
from ftplib import FTP
from typing import Sequence, Optional

from ..common.constant import check_connect, connect_tips
from ..logger.logger import logger


class FtpUtils(object):
    """
    FTP工具类，提供下载文件的方法。

    若下载的文件不存在，会抛出运行异常错误
    """

    def __init__(self):
        self.__ftp = FTP()
        self.__flag = False

    def get_filename(self, remote: str):
        return self.__ftp.nlst(remote)

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

    @check_connect("__flag", connect_tips)
    def download_folder(self, remote_folder: str, local_folder: str, filter_type: Optional[str] = None) -> list:
        """
        下载文件夹中的所有文件到本地
        （未测试文件夹中包含文件夹是否成功）

        :param remote_folder: FTP服务器所在的文件夹

        :param local_folder:  本地文件夹

        :param filter_type: 要下载的文件后缀名

        :return: 下载到的本地文件路径
        """
        local_files = []
        # FTP要进入到这个路径下面
        self.__ftp.cwd(remote_folder)
        file_list = self.__ftp.nlst()
        for name in file_list:
            logger.debug(f"remote name is {name}")
            local_file = f"{local_folder}\\{name}"
            logger.debug(f"local name is {local_folder}")
            with open(local_file, "wb") as f:
                # 只下载某些后缀名的文件
                logger.debug(f"start downloading")
                if filter_type:
                    if name.endswith(filter_type):
                        self.__ftp.retrbinary(f"RETR {name}", f.write)
                        local_files.append(local_file)
                else:
                    logger.debug(f"all file and directory")
                    self.__ftp.retrbinary(f"RETR {name}", f.write)
                    local_files.append(local_file)
        return local_files

    @check_connect("__flag", connect_tips)
    def download_files(self, remote_files: Sequence[str], local_folder: str) -> Sequence[str]:
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

    @check_connect("__flag", connect_tips)
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
        # 判断文件是否存在
        remote_file_name = remote_file.split("/")[-1]
        remote_folder = remote_file.replace(f"/{remote_file_name}", "")
        # 列举远程FTP服务器该目录下所有文件
        file_list = self.__ftp.nlst(remote_folder)
        logger.debug(f"file list is {file_list}")
        if remote_file in file_list:
            logger.debug(f"{remote_file} is exist, it will download")
            with open(local_file, "wb") as f:
                self.__ftp.retrbinary(f"RETR {remote_file}", f.write)
            return local_file
        raise RuntimeError(f"{remote_file} is not exist, please check it")

    @check_connect("__flag", connect_tips)
    def upload_file(self, remote_folder: str, local_file: str):
        """
        上传本地文件到ftp服务器位置

        :param remote_folder:  FTP服务器位置

        :param local_file:  本地文件
        """
        if os.path.exists(local_file) and os.path.isfile(local_file):
            buffer_size = 1024
            self.__ftp.cwd(remote_folder)
            with open(local_file, "rb") as f:
                self.__ftp.storbinary(f"STOR {os.path.basename(local_file)}", f, buffer_size)
        else:
            raise RuntimeError(f"{local_file} is not exist or not file")

    @check_connect("__flag", connect_tips)
    def upload_files(self, remote_folder: str, local_files: Sequence[str]):
        """
        上传本地文件列表到ftp服务器位置

        :param remote_folder: FTP服务器位置

        :param local_files: 本地文件列表
        """
        for file in local_files:
            self.upload_file(remote_folder, file)

    @check_connect("__flag", connect_tips)
    def upload_folder(self, remote_folder: str, local_folder: str, filter_type: Optional[str] = None):
        """
        上传本地夹下所有文件到FTP服务器， 仅支持文件夹下所有内容为文件，带文件夹可能会导致错误

        :param filter_type: 要上传的文件后缀名

        :param remote_folder: FTP服务器位置

        :param local_folder: 本地文件列表
        """
        if os.path.exists(local_folder) and os.path.isdir(local_folder):
            upload_files = list(map(lambda x: fr"{local_folder}\{x}", os.listdir(local_folder)))
            if filter_type:
                upload_files = list(filter(lambda x: x.endswith(filter_type), upload_files))
            logger.debug(f"upload_files is {upload_files}")
            for file in upload_files:
                self.upload_file(remote_folder, file)
        else:
            raise RuntimeError(f"{local_folder} is not exist or not folder")

    @check_connect("__flag", connect_tips)
    def download_file_tree(self, local_dir: str, remote_dir: str, filter_type: Optional[str] = None):
        # 下载整个目录下的文件
        logger.debug(f"远程文件夹remote dir: {remote_dir}")
        if not os.path.exists(local_dir):
            os.makedirs(local_dir)
        self.__ftp.cwd(remote_dir)
        remote_names = self.__ftp.nlst()
        logger.debug(f"远程文件目录： {remote_names}")
        for file in remote_names:
            Local = os.path.join(local_dir, file)
            logger.debug(f"正在下载： {self.__ftp.nlst(file)}")
            if filter_type:
                if file.endswith(filter_type):
                    if file.find(".") == -1:
                        if not os.path.exists(Local):
                            os.makedirs(Local)
                        self.download_file_tree(Local, file)
                    else:
                        self.download_file(Local, file)
            else:
                logger.debug(f"all type file is ok")
                if file.find(".") == -1:
                    if not os.path.exists(Local):
                        os.makedirs(Local)
                    self.download_file_tree(Local, file)
                else:
                    self.download_file(Local, file)
        self.__ftp.cwd("..")
        return
