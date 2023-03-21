# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        data_analysis.py
# @Author:      lizhe
# @Created:     2023/3/18 - 19:30
# --------------------------------------------------------
import copy
import os.path
from typing import Dict

import pandas as pd
from pandas import DataFrame

from .constants import aggregationConfig, Aggregation
from .data_clean import CommonDataClean
from .diagram_draw import get_diagram
from automotive.utils.utils import Utils
from automotive.logger.logger import logger

_test = False
_skip = False


class DataAnalysis(object):

    def __init__(self, issue_folder_path: str, project_name: str, config_file: str = None, output_folder: str = None):
        """
        初始化，需要传入问题路径
        :param issue_folder_path: DTM，禅道下载的文件路径
        :param project_name: 项目名称，配置文件夹中配置的部分
        """
        self.__utils = Utils()
        self.__issue_folder_path = issue_folder_path
        self.__project_name = project_name
        if not os.path.exists(issue_folder_path):
            raise RuntimeError(f"{issue_folder_path} not exist, please check it")
        if not os.path.isdir(issue_folder_path):
            raise RuntimeError(f"{issue_folder_path} is not directory, please check it")
        self.__project = self.__get_project(project_name, config_file)
        self.__real_output_folder = None
        self.__get_output_folder(output_folder)

    def __get_output_folder(self, output_folder: str = None):
        folder_name = "diagrams"
        if output_folder is not None:
            if os.path.exists(output_folder):
                if os.path.isfile(output_folder):
                    raise RuntimeError(f"{output_folder} is file, please check it")
                if os.path.isdir(output_folder):
                    self.__utils.delete_folder(output_folder)
                    os.mkdir(output_folder)
                    self.__real_output_folder = output_folder
        else:
            current_folder = os.getcwd()
            abs_output_folder = os.path.join(current_folder, folder_name)
            if os.path.exists(abs_output_folder):
                self.__utils.delete_folder(abs_output_folder)
            os.mkdir(abs_output_folder)
            self.__real_output_folder = abs_output_folder

    def __get_project(self, project_name: str, config_file: str = None) -> Dict:
        """
        根据project_name查找相关配置，必须存在扫描配置、测试类别、公司内部类别三个选项
        :param project_name:
        :param config_file:
        :return: project配置
        """
        if config_file is None:
            directory, file = os.path.split(__file__)
            abs_file = os.path.join(directory, "defect_config.yml")
        else:
            if not os.path.exists(config_file):
                raise RuntimeError(f"{config_file} is not exist, please check it")
            abs_file = config_file
        contents = self.__utils.read_yml_full(abs_file)
        if "projects" not in contents:
            raise RuntimeError(f"{config_file} is not correct, please check it, it must contain projects config")
        projects = contents["projects"]
        if project_name not in projects:
            raise RuntimeError(f"{project_name} can not be found in project")
        project = projects[project_name]
        if "扫描配置" not in project:
            raise RuntimeError(f"扫描配置 can not be found in {project_name} config")
        if "测试类别" not in project:
            raise RuntimeError(f"测试类别 can not be found in {project_name} config")
        if "测试类别" not in project:
            raise RuntimeError(f"测试类别 not be found in {project_name} config")
        return project

    def __aggregation_data(self, issue_folder_path: str) -> Dict[str, DataFrame]:
        """
        根据配置的方式来分析
        :param issue_folder_path:
        :return:
        """
        df_dict = dict()
        scan_config = self.__project["扫描配置"]
        for key, value in scan_config.items():
            aggregation_config = aggregationConfig(*value)
            aggregation = Aggregation(aggregation_config)
            df = aggregation.aggregation_data(issue_folder_path)
            df_dict[key] = df
        return df_dict

    def __clean_data(self, project_name: str, issue_folder_path: str, project: Dict) -> DataFrame:
        """
        清理数据， 首先获取扫描配置下面的内容，然后进行相关处理
        :param project_name:
        :param issue_folder_path:
        :return:
        """
        df_list = []
        # 获取相关数据
        df_dict = self.__aggregation_data(issue_folder_path)
        directory, file = os.path.split(__file__)
        abs_data_clean = os.path.join(directory, "data_clean.py")
        logger.debug(f"abs_data_clean script is {abs_data_clean}")
        module = self.__utils.get_module_from_script(abs_data_clean)
        for key, value in df_dict.items():
            # 对应到DtmDataClean和ZentaoDataClean
            clazz_instance = getattr(module, f"{key}DataClean")(project)
            df = clazz_instance.clean_data(value, project_name)
            df_list.append(df)
        logger.debug(f"concat dtm and zentao data")
        df = pd.concat(df_list)
        data_clean = CommonDataClean()
        df = data_clean.clean(df)
        logger.info(f"数据清洗已完成， 当前项目发现了{df.shape[0]}个缺陷")
        return df

    def analysis(self):
        if self.__real_output_folder is None:
            raise RuntimeError("output folder is wrong, please checkit output folder param")
        df = self.__clean_data(self.__project_name, self.__issue_folder_path, self.__project)
        if _test:
            df.to_excel("result.xlsx")
        if _skip:
            df = pd.read_excel("result.xlsx")
        diagrams = get_diagram()
        for diagram in diagrams:
            bak_df = copy.deepcopy(df)
            diagram.analysis(bak_df, self.__real_output_folder)
