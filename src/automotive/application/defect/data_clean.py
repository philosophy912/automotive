# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        data_clean.py
# @Author:      lizhe
# @Created:     2023/3/18 - 19:26
# --------------------------------------------------------
from abc import ABCMeta, abstractmethod
from typing import Dict

import pandas as pd
from pandas import DataFrame
from automotive.logger.logger import logger


class BaseDataClean(metaclass=ABCMeta):

    def __init__(self, project: Dict):
        self._columns = "BUG号", "BUG标题", "提交人", "提交时间", "当前状态", "模块名称", "严重程度", "关闭时间"
        # 选项: 北斗、其他
        self.__submit_part = "提交方"
        # 选项: 系统测试、集成测试、自动化测试、其他
        self.__software_submit_type = "测试类别"
        # 选项: 奥莫软件、实习生、外包、产品技术中心、其他
        self.__company_part = "公司内部类别"
        # project这层就是236这层
        self.__project = project

    def __get_type(self, x: DataFrame, separate_type: str):
        separate_value = "其他"
        submitter = x["提交人"].strip().replace("(远特)", "")
        config = self.__project[separate_type]
        for key, value in config.items():
            if submitter in value:
                separate_value = key
        return separate_value

    def _add_submit_part(self, df: DataFrame, clean_tag: bool):
        """
        【提交方, 软件测试类别，北斗测试方】
        增加了提交方，区分北斗和其他方
        增加了
        :param df:
        :return: DataFrame
        """
        if clean_tag:
            df.loc[:, self.__submit_part] = df.apply(lambda x: "北斗" if "远特" in x["提交人"] else "其他", axis=1)
        df.loc[:, self.__software_submit_type] = df.apply(self.__get_type, args=(self.__software_submit_type,), axis=1)
        df.loc[:, self.__company_part] = df.apply(self.__get_type, args=(self.__company_part,), axis=1)
        # 清理提交人中的空格部分
        df["提交人"] = df.apply(lambda x: x["提交人"].strip(), axis=1)

    @abstractmethod
    def clean_data(self, df: DataFrame, project_name: str = None) -> DataFrame:
        """
        清理数据
        """
        pass


class DtmDataClean(BaseDataClean):

    def clean_data(self, df: DataFrame, project_name: str = None) -> DataFrame:
        # 过滤project
        if project_name is not None:
            df = df.loc[df["产品系列"] == project_name, :]
            # df = df.apply(lambda x: x["产品系列"] != project_name, axis=1)
        logger.trace(df.head())
        filter_title = "问题单号", "问题简要描述", "问题单创建人", "创建时间", "流程状态", "模块/零部件", "严重程度", "关闭时间"
        df = df.loc[:, filter_title]
        df.columns = self._columns
        self._add_submit_part(df, True)
        # 去掉远特的标签
        df["提交人"] = df.apply(lambda x: x["提交人"].replace("(远特)", ""), axis=1)
        return df


class ZentaoDataClean(BaseDataClean):
    """
    新禅道的
    """

    def clean_data(self, df: DataFrame, project_name: str = None) -> DataFrame:
        filter_title = "Bug编号", "Bug标题", "由谁创建", "创建日期", "Bug状态", "所属模块", "严重程度", "关闭日期"
        df = df.loc[:, filter_title]
        df["关闭日期"] = df.apply(lambda x: "1970-01-01" if x["关闭日期"] == "0000-00-00" else x["关闭日期"], axis=1)
        df.columns = self._columns
        df.loc[:, "提交方"] = df.apply(lambda x: "北斗", axis=1)
        self._add_submit_part(df, False)
        return df


class CommonDataClean(object):

    def __init__(self):
        self._priority_dict = {
            '一般(B)': "B",
            '严重(A)': "A",
            '提示(C)': "C",
            '致命(S)': "S",
            "S": "S",
            "A": "A",
            "B": "B",
            "C": "C"
        }
        self._status_dict = {
            '修改实施': "激活",
            '③修改审核': "激活",
            "回归测试": "已解决",
            "结束": "已关闭",
            '测试(开发)经理审核分流': "已解决",
            "重新提交问题单": "无效BUG",
            "[1]提单": "激活",
            "激活": "激活",
            "已解决": "已解决",
            "已关闭": "已关闭"
        }

    @staticmethod
    def __get_module_name(x: DataFrame):
        """
        TODO
        处理模块名称，后续如果要做归一化，这块需要处理
        :param x:
        :return:
        """
        current_module_name = x["模块名称"]
        # print(f"======================>{current_module_name}")
        if not current_module_name.startswith("/"):
            second_part = current_module_name
        elif current_module_name.startswith("/中控"):
            array = current_module_name.split("/")
            second_part = array[2] if len(array) > 3 else "中控"
        elif current_module_name.startswith("/仪表"):
            array = current_module_name.split("/")
            second_part = array[2] if len(array) > 3 else "仪表"
        else:
            second_part = current_module_name.split("/")[1]
        second_part = second_part.replace("(#0)", "未知模块").replace("电源管理(#11424)", "电源管理") \
            .replace("非需求清单功能(#10105)", "非需求清单功能").replace("工程模式(#10134)", "工程模式") \
            .replace("日常(#10106)", "日常")
        # print(second_part)
        return second_part

    def clean(self, df: DataFrame) -> DataFrame:
        # 需要清理一下张秦华，把张秦华1变成张秦华
        df["提交人"] = df.apply(lambda x: "张秦华" if x["提交人"] == "张秦华1" else x["提交人"], axis=1)
        # 需要清理掉当前状态为na的缺陷
        df.dropna(subset=["当前状态"], inplace=True)
        # 清理没有设置严重程度的问题
        df["严重程度"].fillna("C", inplace=True)
        df["严重程度"] = df.apply(lambda x: self._priority_dict[x["严重程度"]], axis=1)
        df["当前状态"] = df.apply(lambda x: self._status_dict[x["当前状态"]], axis=1)
        # 替换模块名称中的nan为其他
        df["模块名称"].fillna("未知模块", inplace=True)
        # 替换关闭时间
        df["关闭时间"].fillna("1970-01-01 00:00:00", inplace=True)
        # 处理提交时间和关闭时间
        df["提交时间"] = pd.to_datetime(df["提交时间"], errors='coerce')
        df["关闭时间"] = pd.to_datetime(df["关闭时间"], errors='coerce')
        df["提交时间"] = df.apply(lambda x: x["提交时间"].strftime("%Y-%m-%d"), axis=1)
        df["关闭时间"] = df.apply(lambda x: x["关闭时间"].strftime("%Y-%m-%d"), axis=1)
        # 处理模块名称
        df["模块名称"] = df.apply(self.__get_module_name, axis=1)
        df.loc[:, "提交年份"] = df.apply(lambda x: int(x["提交时间"].split("-")[0]), axis=1)
        return df
