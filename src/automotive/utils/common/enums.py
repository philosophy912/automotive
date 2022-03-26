# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2021, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        enums.py
# @Author:      lizhe
# @Created:     2021/11/18 - 21:24
# --------------------------------------------------------
from enum import Enum, unique


@unique
class ExcelEnum(Enum):
    XLWINGS = "xlwings"
    OPENPYXL = "openpyxl"

    @staticmethod
    def from_name(type_: str):
        for key, item in ExcelEnum.__members__.items():
            if type_.strip() == item.value:
                return item
        raise ValueError(f"{type_} can not be found in ExcelReadEnum")


@unique
class SystemTypeEnum(Enum):
    """
    系统类型
    """
    QNX = "qnx"
    LINUX = "linux"

    @staticmethod
    def from_value(value: str):
        for key, item in SystemTypeEnum.__members__.items():
            if value.upper() == item.value.upper():
                return item
        raise ValueError(f"{value} can not be found in {SystemTypeEnum.__name__}")


@unique
class PinyinEnum(Enum):
    """
    枚举类，仅仅列出了拼音的类型

    DIACRITICAL: 输出的拼音含有声调

    NUMERICAL: 输出拼音音调以数字形式紧随拼音

    STRIP: 不包含声调
    """
    # 输出的拼音含有声调
    DIACRITICAL = "diacritical"
    # 输出拼音音调以数字形式紧随拼音
    NUMERICAL = "numerical"
    # 不包含声调
    STRIP = "strip"

    @staticmethod
    def from_value(value: str):
        for key, item in PinyinEnum.__members__.items():
            if value.upper() == item.value.upper():
                return item
        raise ValueError(f"{value} can not be found in {PinyinEnum.__name__}")


@unique
class EmailTypeEnum(Enum):
    """
    邮箱类型
    """
    # SMTP模式
    SMTP = "smtp"
    # EXCHANGE模式
    EXCHANGE = "exchange"


@unique
class FindTypeEnum(Enum):
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


@unique
class HammingCompareTypeEnum(Enum):
    # 一种汉明距小于阈值
    ONE = "one"
    # 两种汉明距小于阈值
    TWO = "two"
    # 三种汉明距都小于阈值
    THREE = "three"
    # 三种汉明距平均值小于阈值
    AVERAGE = "average"
    # 感知哈希对比
    DEFAULT = "default"


@unique
class ImageCompareTypeEnum(Enum):
    # 汉明距对比
    HAMMING = "hamming"
    # 像素对比
    PIXEL = "pixel"
    # 模糊对比
    VAGUE = "vague"

    @staticmethod
    def from_value(value: str):
        for key, item in ImageCompareTypeEnum.__members__.items():
            if value.upper() == item.value.upper():
                return item
        raise ValueError(f"{value} can not be found in {ImageCompareTypeEnum.__name__}")