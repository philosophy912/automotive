# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        camera_actions.py
# @Author:      lizhe
# @Created:     2021/5/2 - 0:01
# --------------------------------------------------------
from time import sleep
from automotive.logger.logger import logger
from automotive.utils.camera import Camera
from automotive.common.api import BaseActions


class CameraActions(BaseActions):
    """
    摄像头操作类
    """

    def __init__(self):
        super().__init__()
        self.__camera = Camera()
        # 拍摄的图片临时存放的位置
        self._temp_image = None

    def init_template_image(self, pic_name: str):
        """
        根据传入的pic_name拍摄基准图片

        :param pic_name: 基准图片名字
        """
        logger.info("即将拍摄基准照片")
        logger.debug("如果摄像头没有打开则打开摄像头")
        self.__camera.close_camera()
        sleep(1)
        logger.debug("打开摄像头")
        self.__camera.open_camera()
        sleep(1)
        logger.debug("代码有问题，需要拍两张照片")
        logger.info(f"拍摄照片[{pic_name}]")
        for i in range(2):
            self.__camera.take_picture(pic_name)
            sleep(1)

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

    def camera_test(self, time: int = 2):
        """
        调整摄像头，进行camera测试，默认时长2分钟，可以通过输入q退出调整

        :param time: 测试时间， 默认2分钟
        """
        logger.debug("如果摄像头打开，则需要关闭摄像头")
        self.__camera.close_camera()
        logger.debug(f"你有{time}分钟时间调整摄像头位置")
        self.__camera.camera_test(time)

    def take_a_pic(self, image_save_path: str, pic_type: str = "light"):
        """
        拍照片

        :param pic_type: 亮图还是暗图，标识符
        :param image_save_path: 图片存放的位置
        """
        self._temp_image = f"{image_save_path}\\{pic_type}_{self._utils.get_time_as_string()}.png"
        self.__camera.take_picture(self._temp_image)

    def get_temp_pic(self):
        """
        获取当前拍照的图片
        """
        return self._temp_image
