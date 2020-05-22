# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, China TSP, All rights reserved
# --------------------------------------------------------
# @Name:        environment.py
# @Purpose:     该类仅配置了environment部分的数据
# @Author:      lizhe
# @Created:     2020/02/05 21:14
# --------------------------------------------------------
from .base_config import BaseConfig


class Environment(BaseConfig):
    """
    实现了BaseConfig，读取了相关的配置

    该类仅配置了environment部分的数据
    """
    def __init__(self):
        # 配置电源
        self.battery = None
        # 配置ACC
        self.acc = None
        # 配置倒车
        self.reverse = None
        # 配置休眠
        self.bus_sleep = None
        # 配置重启检测
        self.reboot = None
        # 配置摄像头(默认配置)
        self.camera = {
            # 默认调整摄像头时间2分钟
            "camera_test": 2,
            # 图片对比的阈值
            "compare_threshold": 10,
            # 图片过滤器的阈值
            "filter_threshold": 10,
            # 基准图片配置（亮图和暗图）
            "base": ["light_template.png", "dark_template.png"]
        }
        # 配置基准路径（必须配置)
        self.base_path = None

    def update(self, environment: dict):
        """
        更新从yml文件中读取到的数据到对象中

        :param environment:  环境配置部分数据（yml中获取）
        """
        self._update(self.__dict__, environment, "camera")
