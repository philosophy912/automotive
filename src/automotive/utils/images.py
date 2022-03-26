# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        images.py
# @Author:      lizhe
# @Created:     2021/5/1 - 23:33
# --------------------------------------------------------
import cv2
import numpy as np
import imagehash
from PIL import Image
from airtest.aircv import NoModuleError
from typing import List, Optional, Union

# 2960*1440设备 内存耗费： kaze (2GB) >> sift > akaze >> surf > brisk > brief > orb > tpl
# 单纯效果,推荐程度： tpl > surf ≈ sift > kaze > brisk > akaze> brief > orb
# 有限内存,推荐程度： tpl > surf > sift > brisk > akaze > brief > orb >kaze
from airtest.aircv.keypoint_matching import KAZEMatching, BRISKMatching, AKAZEMatching, ORBMatching
from airtest.aircv.keypoint_matching_contrib import SIFTMatching, SURFMatching, BRIEFMatching, \
    NoMatchPointError
from airtest.aircv.template_matching import TemplateMatching
from .common.enums import FindTypeEnum, HammingCompareTypeEnum, ImageCompareTypeEnum
from ..common.typehints import NumpyArray, Position, ImageFile, CompareResult, RGB, AirTestResult
from ..logger.logger import logger


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
    def __binarization(img: NumpyArray, threshold: int) -> NumpyArray:
        """
        灰度图像二值化

        :param img: 需要二值化处理的图像矩阵

        :param threshold: 二值化的阈值，小于该阈值则置0，大于等于该阈值则置255

        :return: 二值化之后的图像矩阵
        """
        res, binary = cv2.threshold(img, threshold, 255, cv2.THRESH_BINARY)
        return binary

    @staticmethod
    def __get_image_nd_array(image: ImageFile, gray: bool = False) -> NumpyArray:
        """
        获取图片的nd array矩阵

        :param image: 需要设置的图片，输入绝对地址或相对地址

        :param gray: 是否需要

        :return:  是否读取灰度图像
        """
        if isinstance(image, NumpyArray):
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
        if end_y < height:
            raise ValueError(f"end_y[{end_y}] need < {height}")
        if end_x < width:
            raise ValueError(f"end_x[{end_x}] need < {width}")
        if start_x >= end_x:
            raise ValueError(f"start_x[{start_x}] >= end_x[{end_x}]")
        if start_y >= end_y:
            raise ValueError(f"start_y[{start_y}] >= end_y[{end_y}]")

    @staticmethod
    def __check_cut_area(cut_start_x: int, cut_start_y: int, cut_end_x: int, cut_end_y: int, origin_width: int, origin_height: int):
        if cut_start_x < 0:
            raise ValueError(f"cut_start_x[{cut_start_x}] need > 0")
        if cut_start_y < 0:
            raise ValueError(f"cut_start_y[{cut_start_y}] need > 0")
        if cut_end_y > origin_height:
            raise ValueError(f"cut_end_y[{cut_end_y}] need < {origin_height}")
        if cut_end_x > origin_width:
            raise ValueError(f"cut_end_x[{cut_end_x}] need < {origin_width}")
        if cut_start_x >= cut_end_x:
            raise ValueError(f"cut_start_x[{cut_start_x}] >= cut_end_x[{cut_end_x}]")
        if cut_start_y >= cut_end_y:
            raise ValueError(f"cut_start_y[{cut_start_y}] >= cut_end_y[{cut_end_y}]")

    @staticmethod
    def __check_area_same(position1: Position, position2: Position):
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
    def __check_image_same_size(image1: NumpyArray, image2: NumpyArray):
        """
        检查两张图片是否相同size, 如果不相同则抛出异常

        :param image1: 图片1

        :param image2: 图片2
        """
        if image1.shape != image2.shape:
            raise ValueError("image1 is not same size with image2")

    def __get_image_matrix(self,
                           image: ImageFile,
                           position: Optional[Position] = None,
                           gray: bool = False) -> NumpyArray:
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
            self.__check_cut_area(start_x, start_y, end_x, end_y, shape[1], shape[0])
            return matrix_image[start_y:end_y, start_x:end_x]
        else:
            return matrix_image

    def __compare_by_matrix(self,
                            image1: ImageFile,
                            image2: ImageFile,
                            gray: bool = False,
                            threshold: Optional[int] = None) -> CompareResult:
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
        matrix_image1 = self.__get_image_nd_array(image1)
        matrix_image2 = self.__get_image_nd_array(image2)
        if gray and threshold:
            matrix_image1 = self.__binarization(matrix_image1, threshold)
            matrix_image2 = self.__binarization(matrix_image2, threshold)
        self.__check_image_same_size(matrix_image1, matrix_image2)
        total_pixel = matrix_image1.size
        if gray:
            temp = matrix_image2 - matrix_image1
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

    def __compare_by_matrix_exclude(self,
                                    image1: ImageFile,
                                    image2: ImageFile,
                                    position: Position,
                                    rgb: RGB = (0, 0, 0),
                                    gray: bool = False,
                                    threshold: Optional[int] = None) -> CompareResult:
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
        image1 = self.set_area_to_white(image=image1, position=position, rgb=rgb, gray=gray)
        image2 = self.set_area_to_white(image=image2, position=position, rgb=rgb, gray=gray)
        return self.__compare_by_matrix(image1, image2, gray, threshold)

    def __compare_by_matrix_in_same_area(self,
                                         image1: ImageFile,
                                         image2: ImageFile,
                                         position1: Position,
                                         position2: Position,
                                         gray: bool = False,
                                         threshold: Optional[int] = None) -> CompareResult:
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
    def __calc_compare_result(different_count: int, total_pixel: int, percent: int = 2) -> CompareResult:
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
    def __find_by_template(small_image: ImageFile,
                           big_image: ImageFile,
                           threshold: float = 0.7,
                           rgb: bool = True,
                           find_type: FindTypeEnum = FindTypeEnum.TEMPLATE) -> AirTestResult:
        if find_type == FindTypeEnum.TEMPLATE:
            # Template matching.
            return TemplateMatching(small_image, big_image, threshold=threshold, rgb=rgb).find_best_result()
        elif find_type == FindTypeEnum.KAZE:
            # 较慢,稍微稳定一点.
            return KAZEMatching(small_image, big_image, threshold=threshold, rgb=rgb).find_best_result()
        elif find_type == FindTypeEnum.BRISK:
            # 快,效果一般,不太稳定
            return BRISKMatching(small_image, big_image, threshold=threshold, rgb=rgb).find_best_result()
        elif find_type == FindTypeEnum.AKAZE:
            # 较快,效果较差,很不稳定
            return AKAZEMatching(small_image, big_image, threshold=threshold, rgb=rgb).find_best_result()
        elif find_type == FindTypeEnum.ORB:
            # 很快,效果垃圾
            return ORBMatching(small_image, big_image, threshold=threshold, rgb=rgb).find_best_result()
        elif find_type == FindTypeEnum.SIFT:
            # 慢,最稳定
            return SIFTMatching(small_image, big_image, threshold=threshold, rgb=rgb).find_best_result()
        elif find_type == FindTypeEnum.SURF:
            # 快,效果不错
            return SURFMatching(small_image, big_image, threshold=threshold, rgb=rgb).find_best_result()
        elif find_type == FindTypeEnum.BRIEF:
            # 识别特征点少,只适合强特征图像的匹配
            return BRIEFMatching(small_image, big_image, threshold=threshold, rgb=rgb).find_best_result()

    @staticmethod
    def __average_hash(img: NumpyArray, hash_size: int = 8):
        pixels = cv2.resize(img, (hash_size, hash_size), interpolation=cv2.INTER_CUBIC)
        avg = np.mean(pixels)
        diff = pixels > avg
        return imagehash.ImageHash(diff)

    @staticmethod
    def __phash(img: NumpyArray, hash_size: int = 8, highfreq_factor: int = 4):
        import scipy.fftpack
        img_size = hash_size * highfreq_factor
        pixels = cv2.resize(img, (img_size, img_size), interpolation=cv2.INTER_CUBIC)
        dct = scipy.fftpack.dct(scipy.fftpack.dct(pixels, axis=0), axis=1)
        dctlowfreq = dct[:hash_size, :hash_size]
        med = np.median(dctlowfreq)
        diff = dctlowfreq > med
        return imagehash.ImageHash(diff)

    @staticmethod
    def __dhash(img: NumpyArray, hash_size: int = 8):
        pixels = cv2.resize(img, (hash_size, hash_size), interpolation=cv2.INTER_CUBIC)
        diff = pixels[:, 1:] > pixels[:, :-1]
        return imagehash.ImageHash(diff)

    def __get_position(self, position: Position, is_convert: bool) -> Position:
        if is_convert:
            x, y, w, h = position
            return self.convert_position(start_x=x, start_y=y, width=w, height=h)
        else:
            return position

    def set_area_to_white(self, image: Image, position: Position, rgb: RGB, gray: bool) -> NumpyArray:
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

    @staticmethod
    def convert_png_to_jpg(origin: str, target: str, color: RGB = (255, 255, 255), quality: int = 100):
        """Alpha composite an RGBA Image with a specified color.

        Simpler, faster version than the solutions above.

        Source: https://stackoverflow.com/a/9459208/284318

        Keyword Arguments:
        image -- PIL RGBA Image object
        color -- Tuple r, g, b (default 255, 255, 255)

        """
        image = Image.open(origin)
        image.load()  # needed for split()
        background = Image.new('RGB', image.size, color)
        background.paste(image, mask=image.split()[2])  # 3 is the alpha channel
        background.save(target, "jpeg", quality=quality)

    @staticmethod
    def convert_position(start_x: int,
                         start_y: int,
                         end_x: Optional[int] = None,
                         end_y: Optional[int] = None,
                         width: Optional[int] = None,
                         height: Optional[int] = None) -> Position:
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

    def cut_image_array(self, image: ImageFile, position: Position, is_convert: bool = False) -> NumpyArray:
        """
        剪切区域图片返回数组
        :param is_convert: 是否需要转换成为start_x, start_y, end_x, end_y模式，可以直接传入x, y, w, h

        :param image:  原始图片

        :param position:  剪贴区域，位置start_x, start_y, end_x, end_y

        :return:NumpyArray
        """
        position = self.__get_position(position, is_convert)
        return self.__get_image_matrix(image, position)

    def cut_image(self, image: ImageFile, target_image: str, position: Position, is_convert: bool = False):
        """
        剪切图片并保存到文件中

        :param is_convert: 是否需要转换成为start_x, start_y, end_x, end_y模式，可以直接传入x, y, w, h

        :param image: 原始图片

        :param target_image: 剪切后图片存放的位置

        :param position: 剪贴区域，位置start_x, start_y, end_x, end_y
        """
        position = self.__get_position(position, is_convert)
        cut_image = self.__get_image_matrix(image, position)
        cv2.imwrite(target_image, cut_image)

    def compare_by_hamming_distance(self,
                                    img1: Image,
                                    img2: Image,
                                    compare_type: HammingCompareTypeEnum = HammingCompareTypeEnum.DEFAULT,
                                    threshold: int = 10) -> bool:
        """
        比较两张图标(汉明距比较），并返回phash（感知哈希算法）， ahash（平均哈希算法），dhash（差异值哈希算法）

        :param compare_type: 比较类型， 一种/两种/三种比较算法都小于阈值  平均值小于阈值

        :param threshold: 阈值, 当阈值不为空的时候，会返回比较的结果

        :param img1: 图片1

        :param img2: 图片2

        :return: a_hash p_hash d_hash
        """
        logger.debug(f"img1 = {img1} and img2 = {img2}")
        image1 = self.__get_image_nd_array(img1)
        image2 = self.__get_image_nd_array(img2)
        a_hash1 = str(self.__average_hash(image1))
        a_hash2 = str(self.__average_hash(image2))
        p_hash1 = str(self.__phash(image1))
        p_hash2 = str(self.__phash(image2))
        d_hash1 = str(self.__dhash(image1))
        d_hash2 = str(self.__dhash(image2))
        a_distance = self.__hamming_distance(a_hash1, a_hash2)
        p_distance = self.__hamming_distance(p_hash1, p_hash2)
        d_distance = self.__hamming_distance(d_hash1, d_hash2)
        logger.info(f"a_distance = {a_distance} and p_distance = {p_distance} and d_distance = {d_distance}")
        if compare_type == HammingCompareTypeEnum.DEFAULT:
            return a_distance < threshold
        elif compare_type == HammingCompareTypeEnum.AVERAGE:
            return (a_distance + p_distance + d_distance) < threshold * 3
        elif compare_type == HammingCompareTypeEnum.ONE:
            return a_distance < threshold or p_distance < threshold or d_distance < threshold
        elif compare_type == HammingCompareTypeEnum.TWO:
            condition1 = a_distance < threshold and p_distance < threshold
            condition2 = p_distance < threshold and d_distance < threshold
            condition3 = a_distance < threshold and d_distance < threshold
            return condition1 or condition2 or condition3
        elif compare_type == HammingCompareTypeEnum.THREE:
            return a_distance < threshold and p_distance < threshold and d_distance < threshold
        else:
            raise RuntimeError("compare type is wrong")

    def compare_by_matrix(self,
                          image1: ImageFile,
                          image2: ImageFile,
                          gray: bool = False,
                          threshold: Optional[int] = None) -> CompareResult:
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

    def compare_by_matrix_exclude(self,
                                  image1: ImageFile,
                                  image2: ImageFile,
                                  position: Position,
                                  rgb: RGB = (0, 0, 0),
                                  gray: bool = False,
                                  threshold: Optional[int] = None,
                                  is_convert: bool = False) -> CompareResult:
        """
        对比image1和image2中position之外的部分

        :param image1: 图片1

        :param image2: 图片2

        :param position: 不对比的区域start_x, start_y, end_x, end_y

        :param rgb: 设置不比较区域的BGR颜色，默认为0， 0， 0

        :param gray: 是否读取灰度图像

        :param threshold: 是否将灰度进行二值化处理后再对比 二值化的阈值, [0, 255]

        :param is_convert: 是否需要转换成为start_x, start_y, end_x, end_y模式，可以直接传入x, y, w, h

        :return:
            same_percent: 相同像素点的百分比

            different_percent: 不同像素点的百分比
        """
        position = self.__get_position(position, is_convert)
        diff, total = self.__compare_by_matrix_exclude(image1, image2, position, rgb, gray, threshold)
        return self.__calc_compare_result(diff, total)

    def compare_by_matrix_in_same_area(self,
                                       image1: Image,
                                       image2: Image,
                                       position1: Position,
                                       position2: Position,
                                       gray: bool = False,
                                       threshold: Optional[int] = None,
                                       is_convert: bool = False) -> CompareResult:
        """
        比较image1和image2图片中指定区域， 其中指定区域必须相同

        :param image1: 图片1

        :param image2: 图片2

        :param position1: 图片1中的指定区域

        :param position2: 图片2中的指定区域

        :param gray: 是否读取灰度图像

        :param threshold: 是否将灰度进行二值化处理后再对比 二值化的阈值, [0, 255]

        :param is_convert: 是否需要转换成为start_x, start_y, end_x, end_y模式，可以直接传入x, y, w, h

        :return:
            same_percent: 相同像素点的百分比

            different_percent: 不同像素点的百分比
        """
        position1 = self.__get_position(position1, is_convert)
        position2 = self.__get_position(position2, is_convert)
        self.__check_area_same(position1, position2)
        diff, total = self.__compare_by_matrix_in_same_area(image1, image2, position1, position2, gray, threshold)
        return self.__calc_compare_result(diff, total)

    def rectangle_image_matrix(self,
                               image: Image,
                               positions: List[Position],
                               color: tuple,
                               is_convert: bool = False) -> NumpyArray:
        """
        在现有的图片上添加指定位置的方形的框

        :param image: 图片

        :param positions: position(x1,y1,x2,y2)列表，表示多个区域

        :param color: 颜色 blue, green, red

        :param is_convert: 是否需要转换成为start_x, start_y, end_x, end_y模式，可以直接传入x, y, w, h

        :return: 添加方框后的matrix
        """
        image_array = self.__get_image_nd_array(image, False)
        for position in positions:
            start_x, start_y, end_x, end_y = self.__get_position(position, is_convert)
            # 图片， 左上角， 右下角， 颜色， 线条粗细， 线条类型，点类型
            cv2.rectangle(image_array, (start_x, start_y), (end_x, end_y), color, 1)
        return image_array

    def rectangle_image(self,
                        image: Image,
                        positions: List[Position],
                        color: RGB,
                        target_image: Optional[str] = None,
                        is_convert: bool = False):
        """
        在现有的图片上添加指定位置的方形的框

        :param image 图片

        :param positions position(x1,y1,x2,y2)列表，表示多个区域

        :param color 颜色 blue, green, red

        :param is_convert: 是否需要转换成为start_x, start_y, end_x, end_y模式，可以直接传入x, y, w, h

        :param target_image 目标图片
        """
        image_array = self.rectangle_image_matrix(image, positions, color, is_convert)
        if target_image:
            cv2.imwrite(target_image, image_array)
        else:
            cv2.imwrite(image, image_array)

    def find_best_result(self,
                         small_image: ImageFile,
                         big_image: ImageFile,
                         threshold: float = 0.7,
                         rgb: bool = True,
                         find_type: FindTypeEnum = FindTypeEnum.TEMPLATE) -> AirTestResult:
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

    def find_best_result_in_templates(self,
                                      small_image: ImageFile,
                                      big_image: ImageFile,
                                      threshold: float = 0.7,
                                      rgb: bool = True) -> AirTestResult:
        """
        查找小图是否在大图中匹配, 当小图在大图中无法找到，尝试所有FindType的所有比较方式

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
        for key, value in FindTypeEnum.__dict__.items():
            if not key.startswith("_"):
                logger.debug(f"current type is {value.name}")
                try:
                    result = self.__find_by_template(small_image, big_image, threshold, rgb, find_type=value)
                    if result:
                        logger.debug(f"result = {result}")
                        if result["confidence"] > confidence:
                            compare_result = result
                except NoMatchPointError:
                    logger.debug(f"skip")
                except NoModuleError:
                    logger.debug(f"skip")
        return compare_result

    def find_best_result_by_position(self,
                                     image1: ImageFile,
                                     image2: ImageFile,
                                     position1: Position,
                                     position2: Optional[Position] = None,
                                     threshold: float = 0.7,
                                     rgb: bool = True,
                                     is_convert: bool = False) -> AirTestResult:
        """
        在两张图片中的相同区域进行图片对比，如果两个区域的位置相同，则position2可以不填
        :param image1: 图1
        :param image2: 图2
        :param position1: 位置1
        :param position2: 位置2
        :param threshold: 阈值，默认0.7
        :param rgb: 默认True
        :param is_convert: 是否需要转换成为start_x, start_y, end_x, end_y模式，可以直接传入x, y, w, h
        :return:
        """
        # 当position2填写的时候需要判断大小是否与position1相同
        position1 = self.__get_position(position1, is_convert)
        image1 = self.cut_image_array(image1, position1)
        if position2:
            position2 = self.__get_position(position2, is_convert)
            self.__check_area_same(position1, position2)
            image2 = self.cut_image_array(image2, position2)
        else:
            image2 = self.cut_image_array(image2, position1)
        return self.find_best_result(image1, image2, threshold, rgb, FindTypeEnum.TEMPLATE)

    def show_images(self, image1: ImageFile, image2: ImageFile, time: float = 0.5):
        """
        拼接两张图片进行显示
        :param image1: 图片1
        :param image2: 图片2
        :param time: 显示时间
        """
        image1 = self.__get_image_nd_array(image1)
        image2 = self.__get_image_nd_array(image2)
        two_images = np.hstack([image1, image2])
        cv2.imshow("compare_images", two_images)
        cv2.waitKey(time * 1000)

    def compare(self,
                compare_type: Union[ImageCompareTypeEnum, str],
                image1: ImageFile,
                image2: ImageFile,
                position1: Position,
                position2: Optional[Position] = None,
                threshold: Optional[int] = None,
                rgb: bool = True,
                is_convert: bool = False) -> bool:
        """
        图片对比，简化版
        :param compare_type: 对比类型，支持汉明距/像素对比/模糊对比
        :param image1: 图片1
        :param position1: 图片区域， 要求填写start_x, start_y, end_x, end_y,如果填写的是x, y, w, h则需要设置is_convert为True
        :param image2: 图片2
        :param position2: 图片区域，要求填写start_x, start_y, end_x, end_y,如果填写的是x, y, w, h则需要设置is_convert为True
        :param threshold: 阈值，按照百分比的方式填写，整数
        :param rgb: 是否灰度对比
        :param is_convert: 当is_convert为True的时候，会把w,h转换成end_x, end_y
        :return: 对比的结果
        """
        if isinstance(compare_type, str):
            compare_type = ImageCompareTypeEnum.from_value(compare_type)
        if compare_type == ImageCompareTypeEnum.HAMMING:
            if threshold is None:
                threshold = 10
            return self.compare_by_hamming_distance(img1=image1, img2=image2, threshold=threshold)
        elif compare_type == ImageCompareTypeEnum.PIXEL:
            if threshold is None:
                threshold = 70
            # same_percent: 相同像素点的百分比
            # different_percent: 不同像素点的百分比
            if position2 is None:
                position2 = position1
            same_percent, different_percent = self.compare_by_matrix_in_same_area(image1=image1, image2=image2,
                                                                                  position1=position1,
                                                                                  position2=position2, gray=rgb,
                                                                                  is_convert=is_convert)
            logger.info(f"compare {compare_type.value} same_percent is {same_percent}")
            return int(same_percent * 100) > threshold
        elif compare_type == ImageCompareTypeEnum.VAGUE:
            compare_threshold = float(threshold / 100) if threshold else 0.7
            result = self.find_best_result_by_position(image1=image1, image2=image2, position1=position1,
                                                       position2=position2, threshold=compare_threshold, rgb=rgb,
                                                       is_convert=is_convert)
            logger.info(f"compare {compare_type.value} result is {result}")
            return result is not None
        else:
            raise RuntimeError("compare_type is error")
