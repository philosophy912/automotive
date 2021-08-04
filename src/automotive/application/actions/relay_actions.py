# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        relay_actions.py
# @Author:      lizhe
# @Created:     2021/5/2 - 0:02
# --------------------------------------------------------
from time import sleep
from automotive.logger.logger import logger
from automotive.utils.usb_relay import USBRelay
from automotive.common.api import BaseDevice


class RelayActions(BaseDevice):

    def __init__(self):
        super().__init__()
        self.__relay = None

    @property
    def relay(self):
        return self.__relay

    def open(self):
        """
        打开继电器
        """
        logger.info(f"初始化继电器模块")
        self.__relay = USBRelay()
        self.__relay.open_relay_device()
        logger.info(f"*************继电器模块初始化成功*************")

    def close(self):
        """
        关闭继电器
        """
        logger.info("关闭继电器")
        self.__relay.close_relay_device()

    def channel_on(self, channel: int = None, interval: float = 1, reverse: bool = False):
        """
        打开继电器通道

        :param reverse: 翻转状态

        :param channel: 通道序号

        :param interval: 打开通道后的间隔时间，默认1秒
        """
        if channel:
            logger.debug(f"打开继电器的{channel}通道")
            if reverse:
                self.__relay.one_relay_channel_on(channel)
            else:
                self.__relay.one_relay_channel_off(channel)
        else:
            self.__relay.all_relay_channel_on()
        sleep(interval)

    def channel_off(self, channel: int = None, interval: float = 1, reverse: bool = False):
        """
        关闭继电器通道

        :param reverse: 翻转状态

        :param channel: 通道序号

        :param interval: 打开通道后的间隔时间，默认1秒
        """
        if channel:
            logger.debug(f"关闭继电器的{channel}通道")
            if reverse:
                self.__relay.one_relay_channel_off(channel)
            else:
                self.__relay.one_relay_channel_on(channel)
        else:
            self.__relay.all_relay_channel_off()
        sleep(interval)

    def fast_on_off(self, duration: int, interval: float, channel: int, stop_status: bool = True):
        """
        快速开关继电器

        :param duration: 持续时间

        :param channel: 通道序号

        :param interval: 操作间隔时间

        :param stop_status:  停留的状态

            True: 开启

            False: 关闭
        """
        total_time = int(duration / interval)
        logger.debug(f"继电器{channel}，通断持续时间{duration}, 间隔时间{interval}")
        for i in range(total_time):
            self.channel_on(channel, interval)
            self.channel_off(channel, interval)
        if stop_status:
            self.channel_on(channel, interval)
        else:
            self.channel_off(channel, interval)
        sleep(1)
        logger.info(f"随机{duration}开关继电器通道{channel}结束")
