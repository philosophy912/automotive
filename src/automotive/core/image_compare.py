# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, China TSP, All rights reserved
# --------------------------------------------------------
# @Name:        image_compare.py
# @Purpose:     todo
# @Author:      lizhe
# @Created:     2020/08/09 16:41
# --------------------------------------------------------
import shutil
from enum import Enum, unique

from automotive.logger import logger
from automotive.utils.utils import Utils
from automotive.utils.images import Images


@unique
class CompareTypeEnum(Enum):
    """
    图片对比

    亮图、暗图、闪烁
    """
    LIGHT = "light", "亮图"
    DARK = "dark", "暗图"
    BLINK = "blink", "闪烁图"

    @staticmethod
    def from_value(value: str):
        for key, item in CompareTypeEnum.__members__.items():
            if value in item.value:
                return item
        raise ValueError(f"can not cast value{value} to CompareTypeEnum")


class CompareProperty(object):
    """
        图片对比的属性

        self.name: 图片对比函数名

        self.type: 对比类型 CompareTypeEnum枚举，只支持LIGHT/DARK/BLINK

        self.screen_shot_images: 根据name从传入的screen_shot_images_path中查询到的所有图片文件

        self.light_template: 模板亮图

        self.dark_template: 模板暗图

        self.positions: (x, y, width, height) 对比区域, 列表类型

        self.similarity: 相似度

        self.gray: 是否灰度对比

        self.gray_threshold: 灰度二值化阈值
    """

    def __init__(self):
        self.name = None
        self.type = None
        self.screen_shot_images = None
        self.light_template = None
        self.dark_template = None
        self.positions = None  # (x, y, width, height)
        self.similarity = None
        self.gray = False
        self.gray_threshold = 240

    def set_value(self, name: str, compare_type: str, screen_shot_images_path: str, light_template: str,
                  dark_template: str, positions: list, similarity: float, gray: bool = None,
                  gray_threshold: int = None):
        self.name = name
        self.type = CompareTypeEnum.from_value(compare_type)
        self.screen_shot_images = Utils.filter_images(screen_shot_images_path, name)
        self.light_template = light_template
        self.dark_template = dark_template
        self.positions = positions
        self.similarity = similarity
        if gray:
            self.gray = gray
        if gray_threshold:
            self.gray_threshold = gray_threshold


class ImageCompare(object):
    """
        图片对比
    """

    def __init__(self):
        self.__images = Images()
        self.__utils = Utils()

    def __compare_image_area(self, template_image: str, target_image: str, position: tuple, gray: bool,
                             threshold: int, similarity: float, is_area) -> bool:
        """
        对比单张图片单个区域

        :param template_image: 要比较的图片（原图中的LIGHT或者DARK)

        :param target_image: 截图图片

        :param position: 截图区域（列表）

        :param gray: 是否灰度对比

        :param threshold: 灰度对比阈值

        :param similarity: 相似度（百分比)

        :param is_area: target_image是否是区域截图的产物（区域截图对比方式和全图截图对比方式不同)

        :return:
            True: 大于阈值

            False: 小于阈值
        """
        logger.debug(
            f"compare template_image[{template_image}] and target_image={target_image} in position[{position}]")
        x, y, width, height = position
        template_position = self.__images.convert_position(x, y, width=width, height=height)
        target_position = self.__images.convert_position(0, 0, width=width,
                                                         height=height) if is_area else template_position
        # 先按照air test方式对比
        result = self.__images.find_best_result_by_position(template_image, target_image, template_position,
                                                            target_position, threshold=float(similarity / 100),
                                                            rgb=True)
        if not result:
            result = self.__images.compare_by_matrix_in_same_area(template_image, target_image, template_position,
                                                                  target_position, gray=gray, threshold=threshold)
            return result[0] >= similarity
        else:
            return True

    def __compare_image(self, template_image: str, target_image: str, positions: list, gray: bool,
                        threshold: int, similarity: float, is_area) -> bool:
        """
        对比图片的多个区域

        :param template_image: 要比较的图片（原图中的LIGHT或者DARK)

        :param target_image: 截图图片

        :param positions: 对比区域

        :param gray: 是否灰度对比

        :param threshold: 灰度对比阈值

        :param similarity: 相似度（百分比)

        :param is_area: target_image是否是区域截图的产物（区域截图对比方式和全图截图对比方式不同)

        :return:
            True: 大于阈值

            False: 小于阈值
        """
        count = 0
        if len(positions) == 0:
            return False
        for position in positions:
            if self.__compare_image_area(template_image, target_image, position, gray, threshold, similarity, is_area):
                count += 1
        return count == len(positions)

    def __compare_images(self, template_image: str, target_images: list, positions: list, gray: bool,
                         threshold: int, similarity: float, is_break: bool = False, is_area: bool = False):
        """
        对比多张图片的单个区域或者多个区域

        :param template_image: 要比较的图片（原图中的LIGHT或者DARK)

        :param target_images: 截图图片列表

        :param positions:  截图区域（列表）

        :param gray: 是否灰度对比

        :param threshold: 灰度对比阈值

        :param similarity: 相似度（百分比)

        :param is_area: 是否区域对比

        :param is_break: 是否找到一张图片相同就退出

        :return:
            True: 相同

            False: 不同
        """
        count = 0
        for image in target_images:
            logger.debug(f"now compare template_image[{template_image}] and target_image [{image}]")
            if self.__compare_image(template_image, image, positions, gray, threshold, similarity, is_area):
                if is_break:
                    logger.debug(f"break compare and return True")
                    return True
                else:
                    logger.debug(f"compre success")
                    count += 1
        return count == len(target_images)

    def __compare_normal(self, compare_property: CompareProperty) -> bool:
        """
        对比亮图或者暗图

        :param compare_property:图像对比参数

        :return:
            True: 相同

            False: 不同
        """
        screen_shot_images = compare_property.screen_shot_images
        logger.debug(f"screen_shot_images = [{screen_shot_images}]")
        light_template = compare_property.light_template
        dark_template = compare_property.dark_template
        positions = compare_property.positions
        logger.debug(
            f"light_template = {light_template} and dark_template = {dark_template} and positions = {positions}")
        gray = compare_property.gray
        threshold = compare_property.gray_threshold
        similarity = compare_property.similarity
        logger.debug(f"similarity is {similarity}")
        if compare_property.type == CompareTypeEnum.LIGHT:
            logger.trace("compare light template file")
            return self.__compare_images(light_template, screen_shot_images, positions, gray, threshold, similarity)
        else:
            logger.trace("compare dark template file")
            return self.__compare_images(dark_template, screen_shot_images, positions, gray, threshold, similarity)

    def __compare_blink(self, compare_property: CompareProperty) -> bool:
        """
        对比闪图

        :param compare_property:图像对比参数

        :return:
            True: 相同

            False: 不同
        """
        screen_shot_images = compare_property.screen_shot_images
        light_template = compare_property.light_template
        dark_template = compare_property.dark_template
        positions = compare_property.positions
        gray = compare_property.gray
        threshold = compare_property.gray_threshold
        similarity = compare_property.similarity
        # 先比较亮图
        light = self.__compare_images(light_template, screen_shot_images, positions, gray, threshold, similarity,
                                      is_break=True)
        # 亮图是否找到
        if light:
            # 找暗图
            return self.__compare_images(dark_template, screen_shot_images, positions, gray, threshold, similarity,
                                         is_break=True)
        else:
            return False

    def compare(self, compare_property: CompareProperty) -> bool:
        """
        图片对比

        :param compare_property: 图像对比参数

        :return: 成功/失败
        """
        if compare_property.type == CompareTypeEnum.BLINK:
            return self.__compare_blink(compare_property)
        else:
            return self.__compare_normal(compare_property)

    def handle_images(self, compare_property: CompareProperty, temp_folder: str,
                      color: tuple = (255, 255, 255)) -> list:
        """
        处理图片： 把截图图片(screen_shot_images)拷贝到temp_folder中，并依次在截图区域上画框

        :param compare_property: 图像对比参数

        :param temp_folder: 临时文件夹路径

        :param color: 画框颜色

        :return: 拷贝后的文件列表
        """
        copied_files = []
        # 拷贝截图图片到temp_folder中
        for index, image in enumerate(compare_property.screen_shot_images):
            temp_image = "\\".join([temp_folder, f"{self.__utils.get_time_as_string()}_{index}.bmp"])
            shutil.copy(image, temp_image)
            # 处理temp_image图片，在上面画框
            self.__images.rectangle_image(temp_image, compare_property.positions, color)
            copied_files.append(temp_image)
        return copied_files
