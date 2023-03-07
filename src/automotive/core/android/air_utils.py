# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        utils.py
# @Author:      lizhe
# @Created:     2023/1/17 - 10:37
# --------------------------------------------------------
import cv2
from automotive.utils.images import Images
from automotive.utils.utils import Utils
from automotive.logger.logger import logger
from airtest.core.api import *
from PIL import Image
from poco.drivers.android.uiautomation import AndroidUiautomationPoco


class AirUtils(object):

    def __init__(self, temp_folder: str = None):
        """
        主要用于存放截图，
            temp_folder = None  创建在当前工作目录下的temple目录
                                若temple存在，在temple下创建以时间命名的子目录
            文件夹不存在时，自动创建文件夹， 截图放在子目录（以时间命名的子文件夹）下
        :param temp_folder: 截图存放位置
        例如
        """
        # 考虑没有传参的时候需要初始化文件夹，当文件夹不存在的时候，你要怎么创建文件夹，或者是不是要求必须要传
        self.__template_folder = temp_folder if temp_folder else os.getcwd()
        self._image = Images()
        self._utils = Utils()
        # 没有传入temp_folder时，创建temple
        if not temp_folder:
            self.__template_folder = fr"{self.__template_folder}\temple"
            if not os.path.exists(self.__template_folder):
                os.makedirs(self.__template_folder)
                logger.debug(fr"create screenshot folder {self.__template_folder}")
            else:
                self.__template_folder = fr"{self.__template_folder}\{self._utils.get_time_as_string()}"
                logger.debug(fr"create screenshot folder {self.__template_folder}")
                os.makedirs(self.__template_folder)

        # 传入了文件夹 文件夹不存在时，自动创建传入的文件夹
        else:
            if not os.path.exists(temp_folder):
                os.makedirs(self.__template_folder)
                logger.debug(fr"temp文件夹不存在，自动创建")
            else:
                # 传了temp_folder时，再创建子文件
                self.__template_folder = fr"{self.__template_folder}\{self._utils.get_time_as_string()}"
                os.makedirs(self.__template_folder)

    def get_position_by_image(self, small_image: str, big_image: str) -> list[tuple]:
        """
        获取小截图在整张图片的坐标点
        :param small_image:截图
        :param big_image:整张图片
        :return:中心点、左上、左下、右下、右上的坐标点
        """
        small_img = cv2.imread(small_image)
        big_img = cv2.imread(big_image)
        result = self._image.find_best_result(small_image=small_img, big_image=big_img)
        pt = [result["result"]]
        for position in result["rectangle"]:
            pt.append(position)
        return pt

    def get_compare_result_by_image(self, small_image: str, big_image: str, threshold: float):
        """
        大图中寻找小图,并获取结果
        :param small_image:
        :param big_image:
        :param threshold:
        :return: 不匹配返回None
        """
        small_img = cv2.imread(small_image)
        big_img = cv2.imread(big_image)
        result = self._image.find_best_result(small_image=small_img, big_image=big_img, threshold=threshold)
        return result

