# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, China TSP, All rights reserved
# --------------------------------------------------------
# @Name:        curve.py
# @Purpose:     解析电压曲线
# @Author:      lizhe
# @Created:     2019/10/30 16:35
# --------------------------------------------------------
import copy
import pandas as pd
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
    def __get_crank_point(voltage_list: list) -> int:
        """
        获取电压变化的点

        :param voltage_list: 电压值

        :return:
        """
        # 定义标杆
        index = 1
        while len(voltage_list) > 1:
            # logger.debug(f"当前位置是{index}")
            first = float(voltage_list[0])
            second = float(voltage_list[1])
            distance = abs(second - first)
            # logger.debug(f"{second} - {first} = {distance}")
            # 判断电压的变化超过2V表示开始点火
            if distance > 2:
                return index
            voltage_list.pop(0)
            index += 1
        return -1

    @staticmethod
    def __get_voltage_normal_position(voltage_list: list) -> int:
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

    def get_voltage_by_csv(self, csv_file: str) -> list:
        """
        从csv文件中获取的点火曲线的值

        电压起始点通过判断当前电压是否下降超过2V来确定。

        读取所有的电压，并找到电压下降的点，从该点开始到电压正常简单的数据计入列表中，并加上电压开始下降之前5个周期和完成
        点火后电压正常的5个周期的数据

        :param csv_file: 示波器采集到的电压曲线并生成的文件

        :return:  电压值列表
        """
        contents = pd.read_csv(csv_file, names=["second", "voltage"])
        contents = contents[self._filter_line:]
        voltage_list = contents["voltage"].values.tolist()
        logger.debug(f"voltage_list length = {len(voltage_list)}")
        # 需要拷贝数组，因为获取点火点的时候有用到了pop方法
        backup_voltage_list = copy.copy(voltage_list)
        index = self.__get_crank_point(backup_voltage_list)
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
        return list(map(lambda x: float(x), crank_list))
