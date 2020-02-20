# -*- coding:utf-8 -*-
# --------------------------------------------------------  
# Copyright (C), 2016-2020, China TSP, All rights reserved
# --------------------------------------------------------                 
# @Name:        base_screen_shot
# @Purpose:     接口类
# @Author:      lizhe  
# @Created:     2020/2/19 11:28  
# --------------------------------------------------------

from abc import ABCMeta, abstractmethod


class BaseScreenShot(metaclass=ABCMeta):
    """
    Screenshot的基类，如果要使用image_compare,必须实现这个基类
    """

    def __init__(self, save_path: str):
        """
            初始化
            :param save_path: 图片保存在电脑上的路径
        """
        self._save_path = save_path

    @abstractmethod
    def screen_shot(self, image_name: str = None, count: int = 1, interval_time: float = 1):
        """
        全屏截图操作
        :param image_name: 要截图的图片名称(仅支持一张照片截图)
        :param count: 截图的张数
        :param interval_time: 多张图片截图间隔时间
        """
        pass

    @abstractmethod
    def screen_shot_area(self, x: int, y: int, width: int, height: int, image_name: str = None, count: int = 1):
        """
        区域截图操作
        :param x: the x-coordinates of the starting point
        :param y: the y-coordinates of the starting point
        :param width: the width of the image
        :param height: the height of the image
        :param image_name: image name
        :param count: 截图的张数
        """
        pass
