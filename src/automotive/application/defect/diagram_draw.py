# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        diagram_draw.py
# @Author:      lizhe
# @Created:     2023/3/18 - 19:20
# --------------------------------------------------------
import copy
import os
import warnings
from abc import ABCMeta, abstractmethod

import pandas as pd
from pandas import DataFrame
from pandas.core.common import SettingWithCopyWarning

from .constants import LineDrawImage, BarDrawImage, PieDrawImage
from automotive.logger.logger import logger

warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)
warnings.simplefilter(action="ignore", category=FutureWarning)


class BaseDiagram(metaclass=ABCMeta):

    @abstractmethod
    def analysis(self, df: DataFrame, output_folder: str):
        """
        分析数据，返回分析后的数据
        :return:
        """
        pass


class TotalDiagram(BaseDiagram):
    """
    总缺陷分布图
    """

    @staticmethod
    def __get_data(df: DataFrame) -> DataFrame:
        """
        日期	每天提交Bug数量	累计提交Bug数量
        2022-12-07 00:00:00	3	3
        2022-12-08 00:00:00	0	3
        2022-12-09 00:00:00	0	3
        2022-12-10 00:00:00	0	3
        2022-12-11 00:00:00	0	3
        2022-12-12 00:00:00	0	3
        2022-12-13 00:00:00	1	4
        2022-12-14 00:00:00	1	5
        2022-12-15 00:00:00	6	11
        2022-12-16 00:00:00	21	32
        """
        df["提交时间"] = pd.to_datetime(df["提交时间"])
        # 设置时间列为 DataFrame 的 index
        df.set_index('提交时间', inplace=True)
        # 计算每天提交的Bug数量和总共的Bug数量
        # resample是按照时间来叠加
        daily_count = df.resample('D').count()
        # cumsum: 计算轴向元素累加和，返回由中间结果组成的数组
        cumulative_count = daily_count.cumsum()

        # 将结果保存到新的DataFrame
        result = pd.DataFrame({
            '日期': daily_count.index,
            '每天提交Bug数量': daily_count['BUG号'],
            '累计提交Bug数量': cumulative_count['BUG号']
        })
        result["日期"] = result["日期"].apply(lambda x: x.strftime("%Y-%m-%d"))
        return result

    def analysis(self, df: DataFrame, output_folder: str):
        draw_image = LineDrawImage()
        # 去掉2022年的数据
        df = df.loc[df["提交年份"] == 2023, :]
        df = self.__get_data(df)
        logger.trace(df.head())
        data = {
            "x": df["日期"].to_list(),
            "y": {
                "每天提交Bug数量": df["每天提交Bug数量"].to_list(),
                "累计提交Bug数量": df["累计提交Bug数量"].to_list()
            },
            "title": "总缺陷分布图"
        }
        logger.trace(data)
        abs_file = os.path.join(output_folder, f"总缺陷分布图.html")
        draw_image.draw(data, abs_file)


class SubmissionDiagram(BaseDiagram):
    """
    缺陷提交对比图
    """

    @staticmethod
    def __get_data(df: DataFrame) -> DataFrame:
        """
        提交时间	其他	北斗
        2022-12-07 00:00:00	0	3
        2022-12-13 00:00:00	0	1
        2022-12-14 00:00:00	0	1
        2022-12-15 00:00:00	0	6
        2022-12-16 00:00:00	0	21
        2022-12-19 00:00:00	0	14
        2022-12-20 00:00:00	0	10
        """
        df["提交时间"] = pd.to_datetime(df["提交时间"])
        # 设置时间列为 DataFrame 的 index
        df.set_index('提交时间', inplace=True)

        # 按照提交方和日期进行聚合，并显示每天各方提交的 bug 数量
        result = df.groupby([pd.Grouper(freq='D'), '提交方']).size().unstack(fill_value=0)
        result.insert(0, "提交时间", result.index)
        result["提交时间"] = result["提交时间"].apply(lambda x: x.strftime("%Y-%m-%d"))
        return result

    def analysis(self, df: DataFrame, output_folder: str):
        draw_image = BarDrawImage()
        # 去掉2022年的数据
        df = df.loc[df["提交年份"] == 2023, :]
        df = self.__get_data(df)
        logger.trace(df.head())
        data = {
            "x": df["提交时间"].to_list(),
            "y": {
                "北斗方": df["北斗"].to_list(),
                "其他方": df["其他"].to_list()
            },
            "title": "缺陷提交对比图"
        }
        abs_file = os.path.join(output_folder, f"缺陷提交对比图.html")
        draw_image.draw(data, abs_file)


class ModuleDiagram(BaseDiagram):
    """
    模块提交缺陷分布图
    """

    @staticmethod
    def __get_data(df: DataFrame) -> DataFrame:
        # 按模块名称和提交方分组计算总数
        grouped = df.groupby(['模块名称', '提交方']).size()
        # 将结果转换成DataFrame格式
        result = grouped.reset_index(name='总数').pivot(index='模块名称', columns='提交方', values='总数').fillna(0)
        result.insert(0, "模块名", result.index)
        return result

    def analysis(self, df: DataFrame, output_folder: str):
        draw_image = BarDrawImage()
        df = self.__get_data(df)
        logger.debug(df.head())
        data = {
            "x": df["模块名"].to_list(),
            "y": {
                "北斗": df["北斗"].to_list(),
                "其他": df["其他"].to_list()
            },
            "title": "模块提交缺陷分布图"
        }
        abs_file = os.path.join(output_folder, f"模块提交缺陷分布图.html")
        draw_image.draw(data, abs_file)


class ActiveModuleDiagram(BaseDiagram):
    """
    激活缺陷模块分布图
    """

    @staticmethod
    def __get_data(df: DataFrame) -> DataFrame:
        # 按模块名称和提交方分组计算总数
        grouped = df.groupby(['模块名称', '当前状态']).size()
        # 将结果转换成DataFrame格式
        result = grouped.reset_index(name='总数').pivot(index='模块名称', columns='当前状态', values='总数').fillna(0)
        result.insert(0, "模块名", result.index)
        return result

    def analysis(self, df: DataFrame, output_folder: str):
        draw_image = BarDrawImage()
        df = df.loc[df["当前状态"] != "已关闭", :]
        df = self.__get_data(df)
        data = {
            "x": df["模块名"].to_list(),
            "y": {
                "待修复": df["激活"].to_list(),
                "待关闭": df["已解决"].to_list()
            },
            "title": "激活缺陷模块分布图"
        }
        abs_file = os.path.join(output_folder, f"激活缺陷模块分布图.html")
        draw_image.draw(data, abs_file)


class WeeklyDiagram(BaseDiagram):

    @staticmethod
    def __get_submit(df: DataFrame, column_name: str) -> DataFrame:
        """
        周数	  邹异英(远特)	付小芬(远特)
        1	0	0
        2	0	0
        3	0	0
        """
        df["提交时间"] = pd.to_datetime(df["提交时间"])
        # 将提交时间转换成 datetime，并将其设置为索引
        df.set_index('提交时间', inplace=True)

        # 添加一列周数
        df['周数'] = df.index.week

        # 使用 pivot_table() 方法汇总数据
        weekly_bug_count = pd.pivot_table(df,
                                          index='周数',
                                          columns=column_name,
                                          values='BUG号',
                                          aggfunc='count',
                                          fill_value=0)
        weekly_bug_count.insert(0, "周数", weekly_bug_count.index)

        # 打印结果
        return weekly_bug_count

    def __get_data(self, df: DataFrame, column_name: str) -> DataFrame:
        # df_2022 = df.loc[df["提交年份"] == 2022, :]
        # df_2022 = self.__get_submit(df_2022, column_name)
        # df_2022.insert(0, "提交年份", "2022")
        df = df.loc[df["提交年份"] == 2023, :]
        df = self.__get_submit(df, column_name)
        df.insert(0, "提交年份", "2023")
        df["周数"] = df.apply(lambda x: str(x["提交年份"]) + "CW" + str(x["周数"]), axis=1)
        df.drop(columns=["提交年份"], inplace=True)
        # 去掉Nan变成0
        df.fillna(0, inplace=True)
        return df

    @staticmethod
    def __draw_images(df: DataFrame, output_folder: str, image_title: str):
        # 设置周数为index
        df.set_index("周数", inplace=True)
        # 这个时候的df是每周的数据，需要后续按照每个周的数据生成图形
        # 转置DataFrame
        df = df.T
        # 遍历df，然后生成图形
        for index, col in df.iteritems():
            logger.debug(f"col name is {col.name}")
            folder_name = str(col.name)
            abs_folder = os.path.join(output_folder, folder_name)
            if not os.path.exists(abs_folder):
                os.mkdir(abs_folder)
            draw_image = PieDrawImage()
            new_col = col.sort_values(ascending=False)
            title = f"{col.name}{image_title}"
            data = {
                "data": [list(z) for z in zip(new_col.index.to_list(), new_col.to_list())],
                "title": title
            }
            logger.trace(f"the {index} data is ")
            logger.trace(data["data"])
            abs_file = os.path.join(abs_folder, f"{title}.html")
            draw_image.draw(data, abs_file)

    def analysis(self, df: DataFrame, output_folder: str):
        # 首先需要按照远特来筛选数据
        df = df.loc[df["提交方"] == "北斗", :]
        # 根据集成测试和系统测试来查看所有人提交的缺陷数量
        # 北斗测试
        df_bak = copy.deepcopy(df)
        df_result = self.__get_data(df_bak, "提交人")
        self.__draw_images(df_result, output_folder, "每人提交缺陷数图")
        # 集成测试
        df_bak = copy.deepcopy(df)
        df_bak = df_bak.loc[df_bak["测试类别"] == "集成测试", :]
        df_result = self.__get_data(df_bak, "提交人")
        self.__draw_images(df_result, output_folder, "集成测试每人提交缺陷数图")
        # 系统测试
        df_bak = copy.deepcopy(df)
        df_bak = df_bak.loc[df_bak["测试类别"] == "系统测试", :]
        df_result = self.__get_data(df_bak, "提交人")
        self.__draw_images(df_result, output_folder, "系统测试每人提交缺陷数图")
        # 按照测试类别统计
        df_bak = copy.deepcopy(df)
        df_result = self.__get_data(df_bak, "测试类别")
        self.__draw_images(df_result, output_folder, "每测试类别提交缺陷数图")

        # 按照公司部门统计
        df_bak = copy.deepcopy(df)
        df_result = self.__get_data(df_bak, "公司内部类别")
        self.__draw_images(df_result, output_folder, "每部门提交缺陷数图")


def get_diagram():
    return TotalDiagram(), SubmissionDiagram(), WeeklyDiagram()
