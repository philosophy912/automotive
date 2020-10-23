# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, China TSP, All rights reserved
# --------------------------------------------------------
# @Name:        api.py
# @Purpose:     todo
# @Author:      lizhe
# @Created:     2020/8/10 - 11:06
# --------------------------------------------------------
from abc import ABCMeta, abstractmethod


class Device(metaclass=ABCMeta):

    @abstractmethod
    def connect(self, username: str = None, password: str = None):
        """
        连接并登陆系统

        :param username: 用户名

        :param password: 密码

        """
        pass

    @abstractmethod
    def disconnect(self):
        """
        断开
        """
        pass


class SocketDevice(metaclass=ABCMeta):

    @abstractmethod
    def connect(self, ipaddress: str, username: str, password: str):
        """
        连接并登陆系统

        :param ipaddress: ip地址

        :param username: 用户名

        :param password: 密码

        """
        pass

    @abstractmethod
    def disconnect(self):
        """
        断开
        """
        pass


class ScreenShot(metaclass=ABCMeta):

    @abstractmethod
    def screen_shot(self, image_name: str, count: int, interval_time: float, display: int = None) -> list:
        """
        截图操作, 当截图有多张的时候，以__下划线分割并加编号

        :param image_name: 截图保存图片名称

        :param count: 截图张数

        :param interval_time: 截图间隔时间

        :param display: 屏幕序号
        """
        pass

    @abstractmethod
    def screen_shot_area(self, position: tuple, image_name: str, count: int, interval_time: float,
                         display: int = None) -> list:
        """
        区域截图, 当截图有多张的时候，以__下划线分割并加编号

        :param position: 截图区域(x, y, width, height)

        :param image_name: 截图保存图片名称

        :param count: 截图张数

        :param interval_time: 截图间隔时间

        :param display: 屏幕序号
        """
        pass


class Actions(metaclass=ABCMeta):

    @abstractmethod
    def click(self, display: int, x: int, y: int, interval: float = 0.2):
        """
        屏幕点击

        :param display: 屏幕序号

        :param x: 坐标点x

        :param y: 坐标点y

        :param interval: 按下和弹起的间隔时间
        """
        pass

    @abstractmethod
    def double_click(self, display: int, x: int, y: int, interval: float):
        """
        屏幕双击

        :param display: 屏幕序号

        :param x: 坐标点x

        :param y: 坐标点y

        :param interval: 两次点击之间的间隔时间
        """
        pass

    @abstractmethod
    def press(self, display: int, x: int, y: int, continue_time: float):
        """
        长按某个坐标点

        :param display: 屏幕序号

        :param x: 坐标点x

        :param y: 坐标点y

        :param continue_time: 长按持续时间
        """
        pass

    @abstractmethod
    def swipe(self, display: int, start_x: int, start_y: int, end_x: int, end_y: int, continue_time: float):
        """
        滑动页面

        :param display: 屏幕序号

        :param start_x: 起始点x

        :param start_y: 起始点y

        :param end_x: 结束点x

        :param end_y: 结束点y

        :param continue_time: 滑动耗时
        """
        pass
