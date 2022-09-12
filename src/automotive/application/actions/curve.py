# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        curve.py
# @Author:      lizhe
# @Created:     2021/5/2 - 0:02
# --------------------------------------------------------
import copy
import os
from typing import Sequence, Tuple, List

from automotive.logger.logger import logger


class Curve(object):
    """
    电压曲线操作类，通过pandas及相关算法获取到电压曲线的列表，用于给konstanter调用
    """

    def __init__(self):
        # 点火前后多取的周期
        self._cycle = 5
        # 每个电压之间间隔的时间（默认1ms，所以间隔为10)
        self._step = 10
        # 过滤的行数
        self._filter_line = 2
        # 电压正常的值
        self._voltage_normal_value = 12

    @staticmethod
    def __get_crank_point(voltage_list: List[float], threshold: float = 0.5) -> int:
        """
        获取电压变化的点

        :param voltage_list: 电压值

        :param threshold: 阈值， 默认0.5，即电压降幅超过0.5则表示开始点火了

        :return:
        """
        # 定义标杆
        index = 1
        while len(voltage_list) > 1:
            # logger.debug(f"当前位置是{index}")
            first = float(voltage_list[0])
            second = float(voltage_list[1])
            distance = abs(second - first)
            logger.debug(f"{second} - {first} = {distance}")
            # 判断电压的变化超过thresholdV表示开始点火
            if distance > threshold:
                logger.debug(f"index = {index}")
                return index
            voltage_list.pop(0)
            index += 1
        raise RuntimeError(f"no value distance is less than {threshold}, please adjust threshold and try again")

    @staticmethod
    def __get_voltage_normal_position(voltage_list: Sequence[float]) -> int:
        """
        从点火开始到电压正常的序号

        :param voltage_list: 电压的list

        :return: 点火开始点在list中的位置
        """
        for index, value in enumerate(voltage_list):
            # 恢复电压正常的值，以12V来进行判断
            if float(value) > 12:
                return index
        return -1

    def __get_csv_value(self, csv_file: str, use_cols: Sequence[int] = None, steps: int = None) -> Tuple:
        """
        从csv中读取数据
        :param csv_file: 示波器抓取的csv文件
        :param use_cols: 使用的列序号
        :param steps: 步长，即多少格表示1ms
        :return:
        """
        try:
            import pandas as pd
        except ModuleNotFoundError:
            os.system("pip install pandas")
        finally:
            import pandas as pd
        df = pd.read_csv(csv_file, names=["second", "voltage"], usecols=use_cols)
        df = df[self._filter_line:]
        voltage_list = df["voltage"].values.tolist()
        time_list = df["second"].values.tolist()
        if steps:
            return time_list[::steps], voltage_list[::steps]
        else:
            return time_list, voltage_list

    def get_voltage_by_csv(self, csv_file: str, use_cols: Sequence[int] = None, steps: int = None,
                           threshold: float = 0.5) -> Sequence[float]:
        """
        从csv文件中获取的点火曲线的值

        电压起始点通过判断当前电压是否下降超过2V来确定。

        读取所有的电压，并找到电压下降的点，从该点开始到电压正常简单的数据计入列表中，并加上电压开始下降之前5个周期和完成
        点火后电压正常的5个周期的数据

        :param threshold: 阈值， 默认0.5，即电压降幅超过0.5则表示开始点火了

        :param steps: 步长，即多少格表示1ms

        :param use_cols: 使用的列序号

        :param csv_file: 示波器采集到的电压曲线并生成的文件

        :return:  电压值列表
        """
        time_list, voltage_list = self.__get_csv_value(csv_file, use_cols, steps)
        logger.debug(f"voltage_list length = {len(voltage_list)}")
        # 需要拷贝数组，因为获取点火点的时候有用到了pop方法
        backup_voltage_list = copy.copy(voltage_list)
        index = self.__get_crank_point(backup_voltage_list, threshold)
        logger.debug(f"点火从{index}开始,值为{voltage_list[index]}")
        logger.debug(f"voltage_list length {len(voltage_list)}")
        before_crank = []
        # 截取5个之前的数据
        for i in range(self._cycle):
            before_crank.append(voltage_list[index - (i + 1) * self._step])
        logger.debug(f"之前的数据[{before_crank}]")
        # crank开始之后的数据
        after_crank_list = voltage_list[index::self._step]
        normal_index = self.__get_voltage_normal_position(after_crank_list)
        # 电压正常后仍然去了5个周期数据
        crank_to_normal = after_crank_list[:normal_index + 1 + self._cycle]
        logger.debug(f"crank点开始之后的数据{crank_to_normal}")
        crank_list = before_crank + crank_to_normal
        logger.debug(f"点火曲线是{crank_list}")
        # 处理字符串变成float类型
        return list(map(lambda x: round(float(x), 2), crank_list))
