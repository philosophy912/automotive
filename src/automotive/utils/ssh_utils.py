# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        ssh_utils.py
# @Author:      lizhe
# @Created:     2021/5/1 - 23:34
# --------------------------------------------------------
import os
import time
from automotive.logger import logger
from time import sleep
from .utils import Utils


class SshUtils(object):
    """
    SSH工具类, 未完成
    后续需要将SSHLibrary导入到其中
    """

    def __init__(self):
        try:
            import paramiko
        except ModuleNotFoundError:
            os.system("pip install paramiko")
        finally:
            import paramiko
            self._ssh = paramiko.SSHClient()
            # 加载创建的白名单
            self._ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self._utils = Utils()
            self._is_connect = False

    def check_status(func):
        """
        检查设备是否已经连接
        :param func: 装饰器函数
        """

        def wrapper(self, *args, **kwargs):
            if not self._is_connect:
                raise RuntimeError("please connect target first")
            return func(self, *args, **kwargs)

        return wrapper

    def connect(self, ipaddress: str, username: str, password: str, port: int = 22, timeout: int = 10):
        """
        连接ssh

        :param ipaddress: 主机ip或者名字

        :param username: 用户名

        :param password: 密码

        :param port: 端口， 默认22

        :param timeout: 超时时间
        """
        try:
            self._ssh.connect(hostname=ipaddress, port=port, username=username, password=password,
                              banner_timeout=timeout, auth_timeout=timeout)
            self._is_connect = True
        except Exception as e:
            self._is_connect = False
            raise RuntimeError(f"telnet connect {ipaddress} with username[{username}] failed, error info is [{e}]")

    def disconnect(self):
        """
        关闭连接
        """
        self._ssh.close()
        self._is_connect = False

    @check_status
    def file_exist(self, file: str, timeout: float = 10, interval: float = 0.5) -> bool:
        """
        检查文件是否存在，

        :param timeout: 检查的超时时间

        :param interval: 检查间隔时间

        :param file: 远程服务器上的文件

        :return: 是否存在
        """
        file_exist = False
        start_time = time.time()
        flag = True
        while flag:
            stdin, stdout, stderr = self.exec_command(f"ls -l {file}")
            logger.debug(f"read content is {stdout}")
            if "No such file or directory" not in stdout:
                logger.debug(f"{file} is exist")
                file_exist = True
                flag = False
            current_time = time.time()
            if current_time - start_time > timeout * 1000:
                flag = False
            sleep(interval)
        return file_exist

    @check_status
    def copy_file(self, remote_folder: str, target_folder: str):
        """
        拷贝远程文件夹下所有的文件到目标文件夹下, 由于ssh是阻塞式，所以无需等待

        :param remote_folder: 远程文件夹

        :param target_folder: 拷贝的文件夹
        """
        # 前台拷贝
        copy_command = f"cp -rv {remote_folder}/* {target_folder}"
        stdin, stdout, stderr = self.exec_command(f"{copy_command}")
        logger.debug(f"stdout  = {stdout}")

    @check_status
    def exec_command(self, cmd: str) -> tuple:
        """
        执行命令

        :param cmd: 命令

        :return:
            stdin: 标准格式的输入，是一个写权限的文件对象

            stdout: 标准格式的输出，是一个读权限的文件对象

            stderr: 标准格式的错误，是一个写权限的文件对象
        """
        logger.debug(f"exec command is {cmd}")
        stdin, stdout, stderr = self._ssh.exec_command(cmd)
        # stdin  标准格式的输入，是一个写权限的文件对象
        # stdout 标准格式的输出，是一个读权限的文件对象
        # stderr 标准格式的错误，是一个写权限的文件对象
        try:
            str_in = stdin.read().decode("utf-8")
        except IOError:
            str_in = None
        try:
            str_out = stdout.read().decode("utf-8")
        except IOError:
            str_out = None
        try:
            str_err = stderr.read().decode("utf-8")
        except IOError:
            str_err = None
        return str_in, str_out, str_err
