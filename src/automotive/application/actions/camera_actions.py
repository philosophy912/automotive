# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        camera_actions.py
# @Author:      lizhe
# @Created:     2021/5/2 - 0:01
# --------------------------------------------------------
import os
from time import sleep

from automotive.utils.utils import Utils
from automotive.logger.logger import logger
from automotive.utils.camera import Camera
from automotive.common.api import BaseDevice


class CameraActions(BaseDevice):
    """
    摄像头操作类
    """

    def __init__(self, template_folder: str = None):
        super().__init__()
        self.__camera = Camera()
        # 拍摄的图片临时存放的位置
        self.__template_image = None
        folder_name = Utils.get_time_as_string()
        # 定义文件夹，后续拍照的时候才进行判断
        if template_folder and os.path.exists(template_folder) and os.path.isdir(template_folder):
            self.__save_folder = fr"{template_folder}\{folder_name}"
        else:
            self.__save_folder = fr"{os.getcwd()}\{folder_name}"
        self.__folder_flag = False

    def __create_image_folder(self):
        """
        创建文件夹
        """
        if not os.path.exists(self.__save_folder):
            os.mkdir(self.__save_folder)

    @staticmethod
    def __remove_extends(image_name: str) -> str:
        """
        去掉后缀名
        :param image_name:
        """
        if "." in image_name:
            extends = image_name.split(".")[-1]
            image_name = image_name.replace(f".{extends}", "")
            image_name = f"{image_name}.jpg"
        return image_name

    def create_folder(func):
        """
        检查folder是否被创建
        :param func: 装饰器函数
        """

        def wrapper(self, *args, **kwargs):
            if not self.__folder_flag:
                self.__create_image_folder()
                self.__folder_flag = True
            return func(self, *args, **kwargs)

        return wrapper

    @property
    def camera(self):
        return self.__camera

    def open(self):
        """
        打开摄像头
        """
        logger.info("初始化摄像头模块")
        self.__camera.open_camera()
        logger.info(f"*************摄像头模块初始化成功*************")

    def close(self):
        """
        关闭摄像头
        """
        logger.info("关闭摄像头")
        self.__camera.close_camera()

    @create_folder
    def take_picture(self, image_name: str = None) -> str:
        """
        拍照片， 只拍摄jpg照片
        针对image_name做处理， 去掉后缀名
        :param image_name:  拍照的名字
        :return:  生成照片的绝对路径
        """
        if image_name:
            image_file = fr"{self.__save_folder}\{self.__remove_extends(image_name)}"
            logger.debug(f"have name image_file is {image_file}")
        else:
            image_file = fr"{self.__save_folder}\{Utils.get_time_as_string()}.jpg"
            logger.debug(f" no have name image_file is {image_file}")
        self.__camera.take_picture(image_file)
        return image_file

    def camera_test(self, time: int = 2, camera_id: int = None):
        """
        调整摄像头，进行camera测试，默认时长2分钟，可以通过输入q退出调整

        :param time: 测试时间， 默认2分钟
        :param camera_id: 摄像头ID号，默认0，  1是笔记本
        """
        logger.debug("如果摄像头打开，则需要关闭摄像头")
        self.__camera.close_camera()
        logger.debug(f"你有{time}分钟时间调整摄像头位置")
        self.__camera.camera_test(time, camera_id)

    @create_folder
    def take_template_image(self, template_image_name: str):
        """
        根据传入的pic_name拍摄基准图片

        :param template_image_name: 基准图片名字
        """
        logger.info("即将拍摄基准照片")
        logger.debug("如果摄像头没有打开则打开摄像头")
        self.__camera.close_camera()
        sleep(1)
        logger.debug("打开摄像头")
        self.__camera.open_camera()
        sleep(1)
        logger.debug("代码有问题，需要拍两张照片")
        self.__template_image = fr"{self.__save_folder}\{self.__remove_extends(template_image_name)}"
        logger.info(f"拍摄照片[{self.__template_image}]")
        for _ in range(2):
            self.__camera.take_picture(self.__template_image)
            sleep(1)
