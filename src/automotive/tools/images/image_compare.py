# -*- coding:utf-8 -*-
# --------------------------------------------------------  
# Copyright (C), 2016-2020, China TSP, All rights reserved
# --------------------------------------------------------                 
# @Name:        image_compare  
# @Purpose:     ImageCompare
# @Author:      lizhe  
# @Created:     2019/12/5 10:49  
# --------------------------------------------------------
import os
import shutil

from loguru import logger
from .base_image_compare import ImageProperty
from .base_image_compare import BaseImageCompare
from .base_screen_shot import BaseScreenShot
from ..utils import Utils


class ImageCompare(BaseImageCompare):
    """
        图片对比，用于自动化仪表测试的图片对比。
    """

    def __init__(self, screen_shot_module: (str, BaseScreenShot), template_path: str, screen_shot_path: str, report_path: str,
                 config: (str, dict), color: tuple = (255, 0, 0), default_image_name: str = "1_screen_shot.bmp"):
        """
        :param screen_shot_module:
            通用screenshot模块的完成包名，该模块中必须包含继承（实现)了BaseScreenShot的类。

        :param template_path: 标准图片存放的路径

        :param screen_shot_path: 截图文件存放的路径

        :param report_path: 报告文件存放的路径。

        :param config: 测试生成的json/py文件
        """
        super().__init__(screen_shot_module, template_path, screen_shot_path, report_path,
                         config, color, default_image_name)

    def __compare(self, template_image: str, screen_shot_image: str, image_property: ImageProperty,
                  i: int) -> bool:
        """
        对比单张图片单个或者多个区域

        :param template_image: 标准图片

        :param screen_shot_image: 截图图片

        :param image_property: 对比参数

        :return:
            True 大于阈值
            False 小于阈值
        """

        position = self._images.convert_position(image_property.x[i], image_property.y[i],
                                                 width=image_property.width[i],
                                                 height=image_property.height[i])
        # 全尺寸图片对比
        if image_property.is_area:
            position1 = self._images.convert_position(0, 0, width=image_property.width[i],
                                                      height=image_property.height[i])
            result = self._images.compare_by_matrix_in_same_area(template_image, screen_shot_image,
                                                                 position, position1,
                                                                 gray=image_property.gary)
        # 非全尺寸图片对比
        else:
            result = self._images.compare_by_matrix_in_same_area(template_image, screen_shot_image,
                                                                 position, position,
                                                                 gray=image_property.gary)

        logger.info(
            f"template_image[{template_image}]compare screen_shot_image[{screen_shot_image}] result = {result}")
        return result[0] > image_property.threshold

    def __compare_image(self, template_image: str, screen_shot_image: str, image_property: ImageProperty,
                        is_break=False) -> bool:
        """
        对比单张图片的多个区域

        :param template_image:  标准图片

        :param screen_shot_image: 截图图片

        :param image_property:  对比参数

        :return:
            True: 每个区域都大于阈值

            False: 有至少一个区域小于阈值
        """
        count = 0
        if isinstance(image_property.x, (int, float)):
            area_size = 1
        elif isinstance(image_property.x, (list, tuple)):
            area_size = len(image_property.x)
        else:
            raise ValueError(f"image_property setting failed,")
        for i in range(area_size):
            if self.__compare(template_image, screen_shot_image, image_property, i):
                if is_break:
                    return True
                else:
                    count += 1
        return count == area_size

    def __compare_images(self, template_image: str, screen_shot_images: (list, tuple), image_property: ImageProperty,
                         is_break=False) -> bool:
        """
        对比多张图片(根据image_property.x来判断是单区域对比还是多区域对比)

        :param template_image: 标准图片

        :param screen_shot_images: 截图图片集合

        :param image_property:对比参数

        :return:
            True: 相同

            False: 不相同
        """
        if isinstance(image_property.x, (int, float)):
            for image in screen_shot_images:
                logger.debug(f"image is {image}")
                if self.__compare_image(template_image, image, image_property):
                    return True
            return False
        elif isinstance(image_property.x, (list, tuple)):
            for image in screen_shot_images:
                logger.debug(f"image is {image}")
                if self.__compare_image(template_image, image, image_property, is_break):
                    return True
            return False

    def __get_dark_light_file(self, image_property: ImageProperty) -> tuple:
        """
       获取亮图暗图绝对位置

       :param image_property: 对比属性

       :return: 亮图和暗图的绝对路径
        """
        # 标准图片亮图
        template_light_file = "\\".join([self._template_path, image_property.pic_template_light])
        # 标准图片暗图
        template_dark_file = "\\".join([self._template_path, image_property.pic_template_dark])
        logger.debug(f"template_light_file = {template_light_file} and template_dark_file = {template_dark_file}")
        return template_light_file, template_dark_file

    def __light_or_dark_compare(self, image_property: ImageProperty, template_file: str, image: str) -> tuple:
        """
        亮图或者暗图对比
        :param image_property: 对比参数

        :param template_file: 标注图片路径

        :param image:  要对比的图片路径

        :return:  图片对比结果和拷贝到结果文件夹的路径（用于结果展示)
        """
        if isinstance(image_property.x, (int, float)):
            return self.__compare_image(template_file, image, image_property), \
                   self.__copy_screen_shot_images([image], image_property)
        elif isinstance(image_property.x, (tuple, list)):
            return self.__compare_images(template_file, [image], image_property), \
                   self.__copy_screen_shot_images([image], image_property)

    def __compare_template_image(self, image_property: ImageProperty, is_light=True) -> tuple:
        """
        对比不闪烁的图片[根据image_property的is_area属性来判断是区域截图还是全屏截图]

        :param image_property: 对比属性

        :param is_light: 亮图，暗图开关

        :return: 图片对比结果和拷贝到结果文件夹的路径（用于结果展示)
        """
        template_light_file, template_dark_file = self.__get_dark_light_file(image_property)
        # 区域截图
        if image_property.is_area:
            self._screen_shot.screen_shot_area(x=image_property.x, y=image_property.y,
                                               width=image_property.width, height=image_property.height,
                                               count=image_property.shot_count)
        # 全部截图
        else:
            self._screen_shot.screen_shot(count=image_property.shot_count)
        image = "\\".join([self._screen_shot_path, self._default_image])
        if is_light:
            return self.__light_or_dark_compare(image_property, template_light_file, image)
        else:
            return self.__light_or_dark_compare(image_property, template_dark_file, image)

    def __compare_blink(self, image_property: ImageProperty) -> tuple:
        """
        对比闪烁图片

        :param image_property: 对比属性

        :return: 图片对比结果和拷贝到结果文件夹的路径（用于结果展示)
        """
        template_light_file, template_dark_file = self.__get_dark_light_file(image_property)
        # 区域截图
        if image_property.is_area:
            self._screen_shot.screen_shot_area(x=image_property.x, y=image_property.y,
                                               width=image_property.width, height=image_property.height,
                                               count=image_property.shot_count)
        # 全部截图
        else:
            self._screen_shot.screen_shot(count=image_property.shot_count)
        # 截图图片列表
        screen_shot_image_list = list(
            map(lambda x: self._screen_shot_path + "\\" + x, os.listdir(self._screen_shot_path)))
        # 先比较亮的图片
        light_flag = self.__compare_images(template_light_file, screen_shot_image_list, image_property, is_break=True)
        # 亮图是否找到
        if light_flag:
            dark_flag = self.__compare_images(template_dark_file, screen_shot_image_list, image_property, is_break=True)
        # 没有找到亮图
        else:
            return False, self.__copy_screen_shot_images(screen_shot_image_list, image_property)
        # 暗图是否找到
        if dark_flag:
            logger.info("PASS, Remove the picture.")
            return True, self.__copy_screen_shot_images(screen_shot_image_list, image_property)
        else:
            return False, self.__copy_screen_shot_images(screen_shot_image_list, image_property)

    def __rectangle_image(self, image: str, image_property: ImageProperty):
        """
        在图片上的截图区域画框

        :param image: 图片

        :param image_property: 对比属性
        """
        positions = []
        size = len(image_property.x)
        for i in range(size):
            positions.append(self._images.convert_position(image_property.x[i], image_property.y[i],
                                                           width=image_property.width[i],
                                                           height=image_property.height[i]))
        self._images.rectangle_image(image, positions, self._color)

    def __copy_screen_shot_images(self, screen_shot_image_list: list, image_property: ImageProperty) -> list:
        """
        根据截图的图片，进行完成图片对比后，进行画框处理并拷贝文件到self._report_path中

        :param screen_shot_image_list: 截图图片列表

        :param image_property: 对比属性
        """
        copy_images = []
        # 把图片拷贝到__log_image_path里面
        for index, image in enumerate(screen_shot_image_list):
            copy_image = "\\".join([self._report_path, f"{Utils().get_time_as_string()}_{index}.bmp"])
            copy_images.append(copy_image)
            # 先要处理image文件，在截图区域上画框
            self.__rectangle_image(image, image_property)
            logger.info(f"copy [{image}] to [{copy_image}]")
            shutil.copy(image, copy_image)
        return copy_images

    def compare_image_light(self, name: str) -> tuple:
        """
        对比亮图

        :param name: 函数名字

        :return: 图片对比结果和拷贝到结果文件夹的路径（用于结果展示)
        """
        return self.__compare_template_image(self._properties[name], True)

    def compare_image_dark(self, name: str) -> tuple:
        """
        对比暗图

        :param name: 函数名字

        :return: 图片对比结果和拷贝到结果文件夹的路径（用于结果展示)
        """
        return self.__compare_template_image(self._properties[name], False)

    def compare_image_blink(self, name: str) -> tuple:
        """
        对比闪烁图片

        :param name: 函数名字

        :return: 图片对比结果和拷贝到结果文件夹的路径（用于结果展示)
        """
        return self.__compare_blink(self._properties[name])

    def get_origin_images(self, name: str) -> tuple:
        """
        获取原始图片

        :param name: 函数名字

        :return: 亮图和暗图的绝对路径
        """
        return self.__get_dark_light_file(self._properties[name])
