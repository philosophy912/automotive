# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        constants.py.py
# @Author:      lizhe
# @Created:     2023/3/18 - 19:14
# --------------------------------------------------------
import os
from abc import ABCMeta, abstractmethod
from collections import namedtuple
from typing import List, Dict

import pandas as pd
from pandas import DataFrame
from pyecharts.charts import Bar, Line, Pie
from pyecharts import options as opts

from automotive.utils.utils import Utils

from automotive.logger.logger import logger

aggregationConfig = namedtuple("AggregationConfig", ["prefix", "suffix", "key_name"])


def get_project_param() -> Dict:
    utils = Utils()
    directory, file = os.path.split(__file__)
    config_file = os.path.join(directory, "defect_config.yml")
    contents = utils.read_yml_full(config_file)
    return contents["project"]


class BaseDrawImage(metaclass=ABCMeta):

    def __init__(self):
        self._width = "1920px"
        self._height = "720px"

    @abstractmethod
    def draw(self, data: Dict, html_file: str):
        pass


class Aggregation(object):

    def __init__(self, aggregation_config: aggregationConfig):
        self.__aggregation_config = aggregation_config
        self.__prefix = self.__aggregation_config.prefix
        self.__suffix = self.__aggregation_config.suffix
        self.__key_name = self.__aggregation_config.key_name

    @staticmethod
    def _get_unique_df_from_files(files: List[str], unique_key: str) -> DataFrame:
        result = None
        for file in files:
            logger.debug(f"handle {file}")
            if result is None:
                result = pd.read_excel(file)
                logger.debug(f"the {file} shape is {result.shape[0]}")
            else:
                data_frame = pd.read_excel(file)
                logger.debug(f"the {file} shape is {data_frame.shape[0]}")
                result = pd.concat([result, data_frame])
                result = result.drop_duplicates(subset=unique_key)
        lines = result.shape[0]
        logger.debug(f"the total shape is {lines}")
        logger.info(f"总计发现了{lines}行数据")
        return result

    def aggregation_data(self, folder_path: str) -> DataFrame:
        """
        读取所有的文件，过滤重复的部分
        """
        # 只扫描第一级目录下面的文件，不扫描文件夹
        folder_files = os.listdir(folder_path)
        # 过滤后的文件绝对路径
        filter_files = list(filter(lambda x: x.startswith(self.__prefix) and x.endswith(self.__suffix), folder_files))
        file_size = len(filter_files)
        if file_size == 0:
            raise RuntimeError(f"folder {folder_path} not have {self.__prefix}*.{self.__suffix} file")
        abs_files = list(map(lambda x: os.path.join(folder_path, x), filter_files))
        return self._get_unique_df_from_files(abs_files, self.__key_name)


class BarDrawImage(BaseDrawImage):

    def __init__(self):
        super().__init__()
        self.__bar = Bar(
            init_opts=opts.InitOpts(
                width=self._width,
                height=self._height,
                page_title="数据统计"
            )
        )

    def draw(self, data: Dict, html_file: str):
        self.__bar.add_xaxis(data["x"])
        for name, y_data in data["y"].items():
            logger.debug(name)
            self.__bar.add_yaxis(name, y_data)
        self.__bar.set_global_opts(
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-15)),
            title_opts=opts.TitleOpts(title=data["title"])
        )
        self.__bar.render(html_file)


class LineDrawImage(BaseDrawImage):

    def __init__(self):
        super().__init__()
        self.__line = Line(
            init_opts=opts.InitOpts(
                width=self._width,
                height=self._height,
                page_title="数据统计"
            )
        )

    def draw(self, data: Dict, html_file: str):
        self.__line.add_xaxis(data["x"])
        for name, y_data in data["y"].items():
            logger.debug(name)
            self.__line.add_yaxis(name, y_data)
        self.__line.set_global_opts(
            title_opts=opts.TitleOpts(title=data["title"]),
            datazoom_opts=opts.DataZoomOpts(is_show=True, type_="slider"),
            tooltip_opts=opts.TooltipOpts(trigger="axis"),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
            xaxis_opts=opts.AxisOpts(type_="category", boundary_gap=False),
        )
        self.__line.render(html_file)


class PieDrawImage(BaseDrawImage):

    def __init__(self):
        super().__init__()
        self.__pie = Pie(
            init_opts=opts.InitOpts(
                width=self._width,
                height=self._height,
                page_title="数据统计"
            )
        )

    def draw(self, data: Dict, html_file: str):
        self.__pie.add("", data["data"])
        self.__pie.set_global_opts(
            title_opts=opts.TitleOpts(title=data["title"]),
            legend_opts=opts.LegendOpts(type_="scroll", pos_left="80%", orient="vertical")
        )
        self.__pie.set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
        self.__pie.render(html_file)
