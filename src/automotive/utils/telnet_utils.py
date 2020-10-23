# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, China TSP, All rights reserved
# --------------------------------------------------------
# @Name:        telnet_utils.py
# @Purpose:     todo
# @Author:      lizhe
# @Created:     2020/10/22 - 22:19
# --------------------------------------------------------
from telnetlib import Telnet
from automotive.logger.logger import logger
from time import sleep


class TelnetUtils(object):

    def __init__(self):
        self.__tn = Telnet()
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

    @staticmethod
    def __codec(content: str, next_line: bool = True) -> bytes:
        """
        把字符串编码成字节

        :param content:  要编码的字符串

        :param next_line: 是否加入换行符

        :return: 字节内容
        """
        if next_line:
            content = f"{content}\n"
        return content.encode("ascii")

    @staticmethod
    def __decode(content: bytes) -> str:
        """
        把字节以ascii的方法编译成字符串

        :param content: 字节

        :return: 字符串内容
        """
        return content.decode("ascii")

    @check_status
    def write(self, content: str, interval: float = 0.5):
        """
        写入telnet

        :param interval: 发送命令后的间隔时间

        :param content: 内容
        """
        logger.debug(f"send command {content}")
        self.__tn.write(self.__codec(content))
        sleep(interval)

    @check_status
    def read(self) -> str:
        """
        从telnet中读取内容

        :return: 返回读取到的内容
        """
        return self.__decode(self.__tn.read_very_eager())

    def connect(self, ip_address: str, username: str, password: str = "", login_str: str = b"login: ",
                timeout: int = 10, port: int = 23):
        """
        连接telnet客户端

        :param ip_address: ip地址

        :param username: 用户名

        :param password: 密码

        :param login_str: 登陆标识符

        :param timeout: 超时时间

        :param port: 端口，默认23
        """
        if not self.__flag:
            try:
                self.__tn.open(ip_address, port=port, timeout=timeout)
                self.__flag = True
                self.__tn.read_until(login_str, timeout)
                self.write(username)
                self.write(password)
            except ConnectionRefusedError:
                self.__flag = False

    def disconnect(self):
        """
        断开连接
        """
        if not self.__flag:
            self.__tn.close()
            self.__flag = False
