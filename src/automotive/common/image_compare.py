# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        image_compare.py
# @Author:      lizhe
# @Created:     2021/5/1 - 23:57
# --------------------------------------------------------
import shutil
from typing import Sequence, Optional

from .typehints import Position, RGB
from ..logger.logger import logger
from ..utils.utils import Utils
from ..common.enums import CompareTypeEnum
from ..utils.images import Images


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

    def set_value(self,
                  name: str,
                  compare_type: str,
                  screen_shot_images_path:
                  str, light_template: str,
                  dark_template: str,
                  positions: Sequence[Position],
                  similarity: float,
                  gray: Optional[bool] = None,
                  gray_threshold: Optional[int] = None):
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
    图片对比， 图片对比会先采用airtest提供的图片对比方法进行对比，如果对比失败，再次使用像素点的方式进行对比。

    由于区域截图并非所有的项目都支持，目前皆不建议进行任何的区域截图对比，虽然区域截图能够提高效率，但是牺牲稳定性并不是自动化测试的方向。

    由于allure的需要，提供了将截图图片进行画框处理后另存到其他路径的方法。
    """

    def __init__(self):
        self.__images = Images()
        self.__utils = Utils()

    def __compare_image_area(self,
                             template_image: str,
                             target_image: str,
                             position: Position,
                             gray: bool,
                             threshold: int,
                             similarity: float,
                             is_area) -> bool:
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
        # 像素对比，暂时没有用
        result1 = self.__images.compare_by_matrix_in_same_area(template_image, target_image, template_position,
                                                               target_position, gray=gray, threshold=threshold)
        matrix_result = result1[0] >= similarity
        logger.debug(f"matrix compare result is {matrix_result}")
        return result is not None

    def __compare_image(self,
                        template_image: str,
                        target_image: str,
                        positions: Sequence[Position],
                        gray: bool,
                        threshold: int,
                        similarity: float,
                        is_area) -> bool:
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

    def __compare_images(self,
                         template_image: str,
                         target_images: Sequence[str],
                         positions: Sequence[Position],
                         gray: bool,
                         threshold: int,
                         similarity: float,
                         light_or_dark: bool = True,
                         is_break: bool = False,
                         is_area: bool = False):
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
        if len(target_images) == 0:
            return False
        for image in target_images:
            logger.debug(f"now compare template_image[{template_image}] and target_image [{image}]")
            if self.__compare_image(template_image, image, positions, gray, threshold, similarity, is_area):
                if light_or_dark:
                    if is_break:
                        logger.debug(f"break compare and return True")
                        return True
                    else:
                        logger.debug(f"compare success")
                        count += 1
                else:
                    # 有一张图片对比相同，则表示对比有问题
                    return False
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
        logger.trace("compare light template file")
        light_or_dark = (compare_property.type == CompareTypeEnum.LIGHT)
        return self.__compare_images(template_image=light_template, target_images=screen_shot_images,
                                     positions=positions, gray=gray, threshold=threshold, similarity=similarity,
                                     light_or_dark=light_or_dark)

    def __compare_dark(self, compare_property: CompareProperty) -> bool:
        """
        对比暗图

        :param compare_property: 图像对比参数

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

    def handle_images(self,
                      compare_property: CompareProperty,
                      temp_folder: str,
                      color: RGB = (255, 255, 255)) -> Sequence[str]:
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
            self.__images.rectangle_image(temp_image, compare_property.positions, color, is_convert=True)
            copied_files.append(temp_image)
        return copied_files
