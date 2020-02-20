# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, China TSP, All rights reserved
# --------------------------------------------------------
# @Name:        device.py
# @Purpose:     该类仅配置了device部分的数据
# @Author:      lizhe
# @Created:     2020/02/05 21:12
# --------------------------------------------------------
from .base_config import BaseConfig


class Device(BaseConfig):
    """
    实现了BaseConfig，读取了相关的配置

    该类仅配置了device部分的数据
    """
    def __init__(self):
        # konstanter配置
        self.konstanter = []
        # it6831的配置
        self.it6831 = []
        # serial
        self.serial = []
        # can
        self.can = {
            # can messages
            "messages": None,
            # 倒档
            "r_shift": [],
            # 空挡
            "n_shift": [],
            # 快速休眠
            "fast_sleep": []
        }

    def update(self, device: dict):
        """
            更新从yml文件中读取到的数据
            :param device:  设备配置部分数据（yml中获取）
        """
        self._update(self.__dict__, device, "can")
