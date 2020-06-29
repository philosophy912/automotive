# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, China TSP, All rights reserved
# --------------------------------------------------------
# @Name:        PictureCompare
# @Purpose:     图像对比
#               读取图片并实现图片对比功能，可以截取图片一部分
#               进行对比，遮挡一部分对比剩余部分图片，对比
#               图片1的左上角和图片2的右下角
# @Author:      liluo
# @Created:     2018-09-12
# --------------------------------------------------------
import copy
from enum import Enum

import cv2
import numpy as np
import imagehash
from PIL import Image
from loguru import logger
from automotive.tools.deprecated import deprecated

# 2960*1440设备 内存耗费： kaze (2GB) >> sift > akaze >> surf > brisk > brief > orb > tpl
# 单纯效果,推荐程度： tpl > surf ≈ sift > kaze > brisk > akaze> brief > orb
# 有限内存,推荐程度： tpl > surf > sift > brisk > akaze > brief > orb >kaze
from automotive.tools.images.aircv.keypoint_matching import KAZEMatching, BRISKMatching, AKAZEMatching, ORBMatching
from automotive.tools.images.aircv.keypoint_matching_contrib import SIFTMatching, SURFMatching, BRIEFMatching, \
    NoMatchPointError
from automotive.tools.images.aircv.template_matching import TemplateMatching


class FindType(Enum):
    """
    2960*1440设备 内存耗费： kaze (2GB) >> sift > akaze >> surf > brisk > brief > orb > tpl
    单纯效果,推荐程度： tpl > surf ≈ sift > kaze > brisk > akaze> brief > orb
    有限内存,推荐程度： tpl > surf > sift > brisk > akaze > brief > orb >kaze
    """
    TEMPLATE = "tpl"
    # 慢,最稳定
    SIFT = "sift"
    # 较快,效果较差,很不稳定
    AKAZE = "akaze"
    # 较慢,稍微稳定一点.
    KAZE = "kaze"
    # 快,效果不错
    SURF = "surf"
    # 快,效果一般,不太稳定
    BRISK = "brisk"
    # 识别特征点少,只适合强特征图像的匹配
    BRIEF = "brief"
    # 很快,效果垃圾
    ORB = "orb"


class Images(object):
    """
    图片相关的工具类，主要有基于像素点的图片对比，mask部分图片对比，汉明距图片对比等功能
    """

    # 计算汉明距
    @staticmethod
    def __hamming_distance(hash1: str, hash2: str) -> int:
        """
        比较两个哈希值之间的差异，即汉明距

        :param hash1: 哈希值1

        :param hash2: 哈希值2

        :return: 差异值
        """
        num = 0
        for i in range(len(hash1)):
            if hash1[i] != hash2[i]:
                num += 1
        return num

    @staticmethod
    def __binarization(img: np.ndarray, threshold: int) -> np.ndarray:
        """
        灰度图像二值化

        :param img: 需要二值化处理的图像矩阵

        :param threshold: 二值化的阈值，小于该阈值则置0，大于等于该阈值则置255

        :return: 二值化之后的图像矩阵
        """
        res, binary = cv2.threshold(img, threshold, 255, cv2.THRESH_BINARY)
        return binary

    @staticmethod
    def __get_image_nd_array(image: (str, np.ndarray), gray: bool = False) -> np.ndarray:
        """
        获取图片的nd array矩阵

        :param image: 需要设置的图片，输入绝对地址或相对地址

        :param gray: 是否需要

        :return:  是否读取灰度图像
        """
        if isinstance(image, np.ndarray):
            return image
        else:
            if gray:
                return cv2.imread(image, cv2.IMREAD_GRAYSCALE)
            elif image.endswith(".png"):
                return cv2.imread(image, cv2.IMREAD_UNCHANGED)
            else:
                return cv2.imread(image)

    @staticmethod
    def __check_area(start_x: int, start_y: int, end_x: int, end_y: int, width: int, height: int):
        """
        检查区域输入是否正常

        :param start_x: 起始的x坐标

        :param start_y: 起始的y坐标

        :param end_x:  结束的x坐标

        :param end_y:  结束的y坐标

        :param width: 宽度

        :param height: 高度

        """
        if start_x < 0:
            raise ValueError(f"start_x[{start_x}] need > 0")
        if start_y < 0:
            raise ValueError(f"start_y[{start_y}] need > 0")
        if end_y > height:
            raise ValueError(f"end_y[{end_y}] need < {height}")
        if end_x > width:
            raise ValueError(f"end_x[{end_x}] need < {width}")
        if start_x >= end_x:
            raise ValueError(f"start_x[{start_x}] >= end_x[{end_x}]")
        if start_y >= end_y:
            raise ValueError(f"start_y[{start_y}] >= end_y[{end_y}]")

    @staticmethod
    def __check_area_same(position1: tuple, position2: tuple):
        x1, y1, x2, y2 = position1
        x3, y3, x4, y4 = position2
        width1 = x2 - x1
        height1 = y2 - y1
        width2 = x4 - x3
        height2 = y4 - y3
        if width1 != width2 or height1 != height2:
            raise ValueError(f"position1[{position1}] area is not equal position2[{position2}]")

    @staticmethod
    def __check_threshold(value: int):
        """
        检查阈值是否在0-255之间

        :param value: 阈值
        """
        if not 0 <= value <= 255:
            raise ValueError(f"value[{value}] is incorrect, need to [0,255]")

    @staticmethod
    def __check_image_same_size(image1: np.ndarray, image2: np.ndarray):
        """
        检查两张图片是否相同size, 如果不相同则抛出异常

        :param image1: 图片1

        :param image2: 图片2
        """
        if image1.shape != image2.shape:
            raise ValueError("image1 is not same size with image2")

    def __get_image_matrix(self, image: str, position: tuple = None, gray: bool = False) -> np.ndarray:
        """
        获取图片的矩阵

        :param image: 图片

        :param position: 起始x, 起始y, 结束x, 结束y

        :param gray: 是否灰度

        :return: position未设置的时候直接返回原始图片的matrix，否则返回position的matrix
        """
        matrix_image = cv2.imread(image, cv2.IMREAD_GRAYSCALE) if gray else cv2.imread(image)
        if matrix_image is None:
            raise RuntimeError(f"no image [{image}] found")
        if position:
            shape = matrix_image.shape
            start_x, start_y, end_x, end_y = position
            self.__check_area(start_x, start_y, end_x, end_y, shape[1], shape[0])
            return matrix_image[start_y:end_y, start_x:end_x]
        else:
            return matrix_image

    def __set_area_to_white(self, image: (str, np.ndarray), position: tuple, rgb: tuple, gray: bool) -> np.ndarray:
        """
        设置一个图片的区域为白色

        :param image: 需要设置的图片，输入绝对地址或相对地址

        :param position: start_x, start_y, end_x, end_y

        :param rgb: R G B 设置的颜色BGR=[0, 255]

        :param gray: 是否读取灰度图像

        :return: 白色化指定区域后的图片矩阵
        """
        image = self.__get_image_matrix(image, gray=gray)
        start_x, start_y, end_x, end_y = position
        blue, green, red = rgb
        if gray:
            image[start_y:end_y, start_x:end_x] = 0
        else:
            image[start_y:end_y, start_x:end_x] = (blue, green, red)
        return image

    def __compare_by_matrix(self, image1: (str, np.ndarray), image2: (str, np.ndarray),
                            gray: bool = False, threshold: int = None) -> tuple:
        """
        对比两张图片， 返回差异点像素和总共像素的数量

        :param image1: 图片1/图片1矩阵

        :param image2: 图片2/图片2矩阵

        :param gray: 是否以灰度的方式进行对比

        :param threshold: 是否将灰度进行二值化处理后再对比 二值化的阈值, [0, 255]

        :return:
            different_count: 两张图片不同的像素点的个数

            total_pixel: 两张图片每一张的总像素点的个数
        """
        if threshold:
            self.__check_threshold(threshold)
        matrix_image1 = cv2.imread(image1) if isinstance(image1, str) else image1
        matrix_image2 = cv2.imread(image2) if isinstance(image2, str) else image2
        if gray and threshold:
            matrix_image1 = self.__binarization(matrix_image1, threshold)
            matrix_image2 = self.__binarization(matrix_image2, threshold)
        self.__check_image_same_size(matrix_image1, matrix_image2)
        total_pixel = matrix_image1.size
        if gray:
            temp = matrix_image2 - matrix_image2
            different_count = np.count_nonzero(temp)
            logger.debug(f"gray different_count = {different_count}")
        else:
            total_pixel = total_pixel // 3
            b1, g1, r1 = cv2.split(matrix_image1)
            b2, g2, r2 = cv2.split(matrix_image2)
            temp_b = b2 - b1
            temp_g = g2 - g1
            temp_r = r2 - r1
            temp = np.abs(temp_b) + np.abs(temp_g) + np.abs(temp_r)
            different_count = np.count_nonzero(temp)
            logger.debug(f"different_count = {different_count}")
        logger.debug(f"different_count[{different_count}] and total_pixel[{total_pixel}]")
        return different_count, total_pixel

    def __compare_by_matrix_exclude(self, image1: str, image2: str, position: tuple, rgb: tuple = (0, 0, 0),
                                    gray: bool = False, threshold=None) -> tuple:
        """
        对比image1和image2中position之外的部分

        :param image1: 图片1

        :param image2: 图片2

        :param position: 不对比的区域start_x, start_y, end_x, end_y

        :param rgb: 设置不比较区域的BGR颜色，默认为0， 0， 0

        :param gray: 是否读取灰度图像

        :param threshold: 是否将灰度进行二值化处理后再对比 二值化的阈值, [0, 255]

        :return:
            different_count: 两张图片不同的像素点的个数

            total_pixel: 两张图片每一张的总像素点的个数
        """
        image1 = self.__set_area_to_white(image=image1, position=position, rgb=rgb, gray=gray)
        image2 = self.__set_area_to_white(image=image2, position=position, rgb=rgb, gray=gray)
        return self.__compare_by_matrix(image1, image2, gray, threshold)

    def __compare_by_matrix_in_same_area(self, image1: str, image2: str, position1: tuple, position2: tuple,
                                         gray: bool = False, threshold: int = None) -> tuple:
        """
        比较image1和image2图片中指定区域， 其中指定区域必须相同

        :param image1: 图片1

        :param image2: 图片2

        :param position1: 图片1中的指定区域

        :param position2: 图片2中的指定区域

        :param gray: 是否读取灰度图像

        :param threshold: 是否将灰度进行二值化处理后再对比 二值化的阈值, [0, 255]

        :return:
            different_count: 两张图片不同的像素点的个数

            total_pixel: 两张图片每一张的总像素点的个数
        """
        logger.debug(f"image1 = {image1}")
        logger.debug(f"image2 = {image2}")
        image1 = self.__get_image_matrix(image=image1, position=position1, gray=gray)
        image2 = self.__get_image_matrix(image=image2, position=position2, gray=gray)
        return self.__compare_by_matrix(image1, image2, gray, threshold)

    @staticmethod
    def __calc_compare_result(different_count: int, total_pixel: int, percent: int = 2) -> tuple:
        """
        计算比较的结果，返回比例

        :param percent: 截取小数点后多少位，默认2为

        :param different_count: 不同像素点

        :param total_pixel:  总共像素点

        :return:
            same_percent: 相同像素点的百分比

            different_percent: 不同像素点的百分比
        """
        same_percent = float((total_pixel - different_count) / total_pixel) * 100
        different_percent = float(different_count / total_pixel) * 100
        return round(same_percent, percent), round(different_percent, percent)

    @staticmethod
    def convert_png_to_jpg(origin: str, target: str, color: tuple = (255, 255, 255), quality: int = 100):
        """Alpha composite an RGBA Image with a specified color.

        Simpler, faster version than the solutions above.

        Source: http://stackoverflow.com/a/9459208/284318

        Keyword Arguments:
        image -- PIL RGBA Image object
        color -- Tuple r, g, b (default 255, 255, 255)

        """
        image = Image.open(origin)
        image.load()  # needed for split()
        background = Image.new('RGB', image.size, color)
        background.paste(image, mask=image.split()[3])  # 3 is the alpha channel
        background.save(target, "jpeg", quality=quality)

    @staticmethod
    def convert_position(start_x: int, start_y: int, end_x: int = None, end_y: int = None, width: int = None,
                         height: int = None) -> tuple:
        """
        位置转换器，可以讲x, y, width, height转换成start_x, start_y, end_x, end_y

        :param start_x: 起始的坐标x

        :param start_y: 起始的坐标y

        :param end_x: 终止的坐标x（可选）

        :param end_y: 终止的坐标y（可选）

        :param width: 宽度(可选）

        :param height: 高度（可选）

        :return: start_x, start_y, end_x, end_y
        """
        if end_x and end_y:
            logger.debug(f"start_x[{start_x}], start_y[{start_y}], end_x[{end_x}], end_y[{end_y}]")
            return start_x, start_y, end_x, end_y
        if width and height:
            end_x = start_x + width
            end_y = start_y + height
            logger.debug(f"start_x[{start_x}], start_y[{start_y}], end_x[{end_x}], end_y[{end_y}]")
            return start_x, start_y, end_x, end_y
        raise ValueError(f"only support both end_x and  end_y or width and height")

    @deprecated
    def is_image_contain(self, small_image: str, big_image: str, small_position: tuple = None,
                         big_position: tuple = None, gray: bool = False, threshold: int = None) -> bool:
        """
        传入的small_image能否在big_image中找到

        :param small_image: 小图片

        :param big_image: 大图片

        :param small_position: 包含start_x, start_y, end_x, end_y的small_image的位置（用于缩小查找范围)

        :param big_position: 包含start_x, start_y, end_x, end_y的big_image的位置（用于缩小查找范围)

        :param gray: 是否以灰度的方式进行对比

        :param threshold: 是否将灰度进行二值化处理后再对比 二值化的阈值, [0, 255]

        :return:
            True: 包含

            False： 不包含
        """
        small_image_matrix = self.__get_image_matrix(small_image, position=small_position, gray=gray)
        big_image_matrix = self.__get_image_matrix(big_image, position=big_position, gray=gray)
        find_x, find_y = self.get_position_in_image(small_image_matrix, big_image_matrix, gray=gray,
                                                    threshold=threshold)
        logger.debug(f"find_x [{find_x}] and find_y[{find_y}]")
        return find_x != -1 or find_y != -1

    def cut_image_array(self, image: str, position: tuple) -> np.ndarray:
        """
        剪切区域图片返回数组
        :param image:  原始图片

        :param position:  剪贴区域，位置start_x, start_y, end_x, end_y

        :return: np.ndarray
        """
        return self.__get_image_matrix(image, position)

    def cut_image(self, image: str, target_image: str, position: tuple):
        """
        剪切图片并保存到文件中

        :param image: 原始图片

        :param target_image: 剪切后图片存放的位置

        :param position: 剪贴区域，位置start_x, start_y, end_x, end_y
        """
        cut_image = self.__get_image_matrix(image, position)
        cv2.imwrite(target_image, cut_image)

    @deprecated
    def get_position_in_image(self, image1: (str, np.ndarray), image2: (str, np.ndarray),
                              gray: bool = False, threshold: int = None) -> tuple:
        """
        查找图片1在图片2中的位置，返回x, y在图片2中的位置，如果找不到则返回-1,-1

        :param image1: 图片1/图片1矩阵

        :param image2: 图片2/图片2矩阵

        :param gray: 是否以灰度的方式进行对比

        :param threshold: 是否将灰度进行二值化处理后再对比 二值化的阈值, [0, 255]

        :return: 图片1在图片2中的位置（x,y)，如果找不到则返回(-1,-1)
        """
        if threshold:
            self.__check_threshold(threshold)
        matrix_image1 = cv2.imread(image1) if isinstance(image1, str) else image1
        matrix_image2 = cv2.imread(image2) if isinstance(image2, str) else image2

        # backup BGR picture for color compare
        matrix_image1_bgr = copy.deepcopy(matrix_image1)
        matrix_image2_bgr = copy.deepcopy(matrix_image2)
        matrix_image1 = cv2.cvtColor(matrix_image1, cv2.COLOR_BGR2GRAY)
        matrix_image2 = cv2.cvtColor(matrix_image2, cv2.COLOR_BGR2GRAY)

        # check picture size
        matrix_image1_shape = matrix_image1.shape
        matrix_image2_shape = matrix_image2.shape
        if matrix_image2_shape[0] < matrix_image1_shape[0] or matrix_image2_shape[1] < matrix_image1_shape[1]:
            raise ValueError(f"please check image1 is smaller than image2")

        # transmit gray picture to histgram list
        matrix_image1_hist = cv2.calcHist([matrix_image1], [0], None, [256], [0, 256])
        matrix_image2_hist = cv2.calcHist([matrix_image2], [0], None, [256], [0, 256])
        matrix_image1_hist = [int(i[0]) for i in matrix_image1_hist]
        matrix_image2_hist = [int(j[0]) for j in matrix_image2_hist]

        # find the gray level which has smallest number of count in histgram list
        gray_level = 0
        min_gray_count = matrix_image2_shape[0] * matrix_image2_shape[1]
        for i, value in enumerate(matrix_image2_hist):
            if matrix_image1_hist[i] == 0 or matrix_image2_hist[i] == 0:
                continue
            if value < min_gray_count:
                min_gray_count = value
                gray_level = i

        # get all points in bigger picture using found gray level
        matrix_image1_points = np.where(matrix_image1 == gray_level)
        matrix_image2_points = np.where(matrix_image2 == gray_level)

        # compare small picture with big picture at every point found above
        diff_count = matrix_image1.size
        if not gray:
            matrix_image2 = matrix_image2_bgr
            matrix_image1 = matrix_image1_bgr
        elif threshold:
            matrix_image2 = self.__binarization(matrix_image2, threshold)
            matrix_image1 = self.__binarization(matrix_image1, threshold)
        find_x = -1
        find_y = -1
        for m, n in zip(matrix_image2_points[0], matrix_image2_points[1]):
            start_y = m - matrix_image1_points[0][0]
            end_y = m - matrix_image1_points[0][0] + matrix_image1_shape[0]
            start_x = n - matrix_image1_points[1][0]
            end_x = n - matrix_image1_points[1][0] + matrix_image1_shape[1]
            if start_y < 0 or end_y > matrix_image2_shape[0]:
                continue
            if start_x < 0 or end_x > matrix_image2_shape[1]:
                continue
            tmp = matrix_image2[start_y:end_y, start_x:end_x]
            if gray:
                delta = tmp - matrix_image1
            else:
                b1, g1, r1 = cv2.split(tmp)
                b2, g2, r2 = cv2.split(matrix_image1)
                delta_b = b1 - b2
                delta_g = g1 - g2
                delta_r = r1 - r2
                delta = np.abs(delta_b) + np.abs(delta_g) + np.abs(delta_r)
            count = np.count_nonzero(delta)
            if count < diff_count:
                diff_count = count
                find_x = start_x
                find_y = start_y
                if count == 0:
                    break
        return find_x, find_y

    def compare_by_hamming_distance(self, img1: str, img2: str) -> tuple:
        """
        比较两张图标(汉明距比较），并返回phash（感知哈希算法）， ahash（平均哈希算法），dhash（差异值哈希算法）

        :param img1: 图片1

        :param img2: 图片2

        :return: a_hash p_hash d_hash
        """
        image1 = Image.open(img1)
        image2 = Image.open(img2)
        a_hash1 = str(imagehash.average_hash(image1))
        a_hash2 = str(imagehash.average_hash(image2))
        p_hash1 = str(imagehash.phash(image1))
        p_hash2 = str(imagehash.phash(image2))
        d_hash1 = str(imagehash.dhash(image1))
        d_hash2 = str(imagehash.dhash(image2))
        a_distance = self.__hamming_distance(a_hash1, a_hash2)
        p_distance = self.__hamming_distance(p_hash1, p_hash2)
        d_distance = self.__hamming_distance(d_hash1, d_hash2)
        logger.debug(f"a_distance = {a_distance} and p_distance = {p_distance} and d_distance = {d_distance}")
        return a_distance, p_distance, d_distance

    def compare_by_matrix(self, image1: (str, np.ndarray), image2: (str, np.ndarray),
                          gray: bool = False, threshold: int = None) -> tuple:
        """
        通过像素矩阵对比两张图片

        :param image1: 图片1/图片1矩阵

        :param image2: 图片2/图片2矩阵

        :param gray: 是否以灰度的方式进行对比

        :param threshold: 是否将灰度进行二值化处理后再对比 二值化的阈值, [0, 255]

        :return:
            same_percent: 相同像素点的百分比
            different_percent: 不同像素点的百分比
        """
        diff, total = self.__compare_by_matrix(image1, image2, gray, threshold)
        return self.__calc_compare_result(diff, total)

    def compare_by_matrix_exclude(self, image1: str, image2: str, position: tuple, rgb: tuple = (0, 0, 0),
                                  gray: bool = False, threshold=None) -> tuple:
        """
        对比image1和image2中position之外的部分

        :param image1: 图片1

        :param image2: 图片2

        :param position: 不对比的区域start_x, start_y, end_x, end_y

        :param rgb: 设置不比较区域的BGR颜色，默认为0， 0， 0

        :param gray: 是否读取灰度图像

        :param threshold: 是否将灰度进行二值化处理后再对比 二值化的阈值, [0, 255]

        :return:
            same_percent: 相同像素点的百分比

            different_percent: 不同像素点的百分比
        """
        diff, total = self.__compare_by_matrix_exclude(image1, image2, position, rgb, gray, threshold)
        return self.__calc_compare_result(diff, total)

    def compare_by_matrix_in_same_area(self, image1: str, image2: str, position1: tuple, position2: tuple,
                                       gray: bool = False, threshold: int = None) -> tuple:
        """
        比较image1和image2图片中指定区域， 其中指定区域必须相同

        :param image1: 图片1

        :param image2: 图片2

        :param position1: 图片1中的指定区域

        :param position2: 图片2中的指定区域

        :param gray: 是否读取灰度图像

        :param threshold: 是否将灰度进行二值化处理后再对比 二值化的阈值, [0, 255]

        :return:
            same_percent: 相同像素点的百分比

            different_percent: 不同像素点的百分比
        """
        self.__check_area_same(position1, position2)
        diff, total = self.__compare_by_matrix_in_same_area(image1, image2, position1, position2, gray, threshold)
        return self.__calc_compare_result(diff, total)

    def rectangle_image(self, image: str, positions: list, color: tuple, target_image: str = None):
        """
        在现有的图片上添加指定位置的方形的框

        :param image 图片

        :param positions position(x,y,width,height)列表，表示多个区域

        :param color 颜色 blue, green, red

        :param target_image 目标图片
        """
        image_array = self.__get_image_nd_array(image, False)
        for position in positions:
            start_x, start_y, end_x, end_y = position
            # 图片， 左上角， 右下角， 颜色， 线条粗细， 线条类型，点类型
            cv2.rectangle(image_array, (start_x, start_y), (end_x, end_y), color, 1)
        if target_image:
            cv2.imwrite(target_image, image_array)
        else:
            cv2.imwrite(image, image_array)

    def find_best_result(self, small_image: (str, np.array), big_image: (str, np.array), threshold: float = 0.7,
                         rgb: bool = True, find_type: FindType = FindType.TEMPLATE) -> dict:
        """
        查找小图是否在大图中匹配, 当小图在大图中无法找到，则返回None

        :param small_image: 小图片

        :param big_image: 大图片

        :param threshold: 阈值，默认0.7

        :param rgb: 默认True

        :param find_type: 默认tpl方式

        :return: 返回了五个坐标点以及对比结果

            {

            "result": (center_x,center_y),

            "rectangle": (

                          (left_top_x, left_top_y),

                          (left_bottom_x, left_bottom_y),

                          (right_bottom_x, right_bottom_y),

                          (right_top_x, right_top_y)

                         )

            "confidence": 0.99999

            }
        """
        small_image = self.__get_image_nd_array(small_image)
        big_image = self.__get_image_nd_array(big_image)
        return self.__find_by_template(small_image, big_image, threshold=threshold, rgb=rgb, find_type=find_type)

    def find_best_result_in_templates(self, small_image: (str, np.array), big_image: (str, np.array),
                                      threshold: float = 0.7, rgb: bool = True) -> dict:
        """
        查找小图是否在大图中匹配, 当小图在大图中无法找到，则返回None

        :param small_image: 小图片

        :param big_image: 大图片

        :param threshold: 阈值，默认0.7

        :param rgb: 默认True

        :return: 返回了五个坐标点以及对比结果

            {

            "result": (center_x,center_y),

            "rectangle": (

                          (left_top_x, left_top_y),

                          (left_bottom_x, left_bottom_y),

                          (right_bottom_x, right_bottom_y),

                          (right_top_x, right_top_y)

                         )

            "confidence": 0.99999

            }
        """
        small_image = self.__get_image_nd_array(small_image)
        big_image = self.__get_image_nd_array(big_image)
        compare_result = None
        confidence = 0
        for key, value in FindType.__dict__.items():
            logger.debug(f"current type is {value}")
            try:
                result = self.__find_by_template(small_image, big_image, threshold, rgb, find_type=value)
                if result:
                    logger.debug(f"result = {result}")
                    if result["confidence"] > confidence:
                        compare_result = result
            except NoMatchPointError:
                logger.debug(f"skip")
        return compare_result

    @staticmethod
    def __find_by_template(small_image: (str, np.array), big_image: (str, np.array), threshold: float = 0.7,
                           rgb: bool = True, find_type: FindType = FindType.TEMPLATE):
        if find_type == FindType.TEMPLATE:
            # Template matching.
            return TemplateMatching(small_image, big_image, threshold=threshold, rgb=rgb).find_best_result()
        elif find_type == FindType.KAZE:
            # 较慢,稍微稳定一点.
            return KAZEMatching(small_image, big_image, threshold=threshold, rgb=rgb).find_best_result()
        elif find_type == FindType.BRISK:
            # 快,效果一般,不太稳定
            return BRISKMatching(small_image, big_image, threshold=threshold, rgb=rgb).find_best_result()
        elif find_type == FindType.AKAZE:
            # 较快,效果较差,很不稳定
            return AKAZEMatching(small_image, big_image, threshold=threshold, rgb=rgb).find_best_result()
        elif find_type == FindType.ORB:
            # 很快,效果垃圾
            return ORBMatching(small_image, big_image, threshold=threshold, rgb=rgb).find_best_result()
        elif find_type == FindType.SIFT:
            # 慢,最稳定
            return SIFTMatching(small_image, big_image, threshold=threshold, rgb=rgb).find_best_result()
        elif find_type == FindType.SURF:
            # 快,效果不错
            return SURFMatching(small_image, big_image, threshold=threshold, rgb=rgb).find_best_result()
        elif find_type == FindType.BRIEF:
            # 识别特征点少,只适合强特征图像的匹配
            return BRIEFMatching(small_image, big_image, threshold=threshold, rgb=rgb).find_best_result()

    def find_best_result_by_position(self, small_image: (str, np.array), big_image: (str, np.array),
                                     position1: tuple, position2: tuple = None, threshold: float = 0.7,
                                     rgb: bool = True) -> dict:
        # 当position2填写的时候需要判断大小是否与position1相同
        image1 = self.cut_image_array(small_image, position1)
        if position2:
            self.__check_area_same(position1, position2)
            image2 = self.cut_image_array(big_image, position2)
        else:
            image2 = self.cut_image_array(big_image, position1)
        return self.find_best_result(image1, image2, threshold, rgb, FindType.TEMPLATE)
