# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, China TSP, All rights reserved
# --------------------------------------------------------
# @Name:        SSHUtils
# @Purpose:     ssh相关操作
# @Author:      lizhe
# @Created:     2018-12-27
# --------------------------------------------------------
import paramiko
from paramiko import AuthenticationException
from paramiko.ssh_exception import NoValidConnectionsError
from loguru import logger
from automotive.tools import Utils


class SSHUtils(object):
    """
    SSH工具类, 未完成
    后续需要将SSHLibrary导入到其中
    """
    def __init__(self):
        self.__ssh = paramiko.SSHClient()
        # 加载创建的白名单
        self.__ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.__utils = Utils()
        self.is_connect = False

    def connect(self, hostname: str, username: str, password: str, port: int = 22):
        """
        连接ssh

        :param hostname: 主机ip或者名字

        :param username: 用户名

        :param password: 密码

        :param port: 端口， 默认22
        """
        try:
            self.__ssh.connect(hostname=hostname, port=port, username=username, password=password)
            self.is_connect = True
        except AuthenticationException as e:
            logger.error(f"username[{username}] or password[******] wrong, please check it, error info is {e}")
            self.is_connect = False
        except NoValidConnectionsError as e:
            logger.error(f"port[{port}] or host[{hostname}] is wrong, please check it, error info is {e}")
            self.is_connect = False

    def disconnect(self):
        """
        关闭连接
        """
        self.__ssh.close()

    def exec_command(self, cmd: str) -> tuple:
        """
        执行命令

        :param cmd: 命令

        :return:
            stdin: 标准格式的输入，是一个写权限的文件对象

            stdout: 标准格式的输出，是一个读权限的文件对象

            stderr: 标准格式的错误，是一个写权限的文件对象
        """
        if self.is_connect:
            stdin, stdout, stderr = self.__ssh.exec_command(cmd)
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
