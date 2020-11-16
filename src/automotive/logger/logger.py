# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, China TSP, All rights reserved
# --------------------------------------------------------
# @Name:        logger.py
# @Purpose:     todo
# @Author:      lizhe
# @Created:     2020/7/22 - 11:00
# --------------------------------------------------------
import os
import sys
import yaml

from loguru import logger as _logger

"""
本模块主要用于自定义logger

使用方法：

    1、 from automotive import logger
    
    2、 在运行代码目录及父目录到根目录的任意目录放置config.yml文件，其中yml中包含level和log_folder用于定义log等级及log存放文件路径
    
    3、 如果找不到配置文件，默认使用info级别输出log，并且不保存log内容到文件
"""

config_file_name = "config.yml"
current_path = os.getcwd()
log_level_type = "trace", "debug", "info", "warning", "error"


def set_logger(level: str = "debug", folder: str = None):
    # LOG的格式
    formats = "<g>[{time:YYYY-MM-DD HH:mm:ss.SSS}]</g>" \
              "<level>[{level: ^9}]</level>|" \
              "<c><i>{file: ^20}</i></c>|<e>MOD:<i>{module: ^20}</i></e>|" \
              "<m>FUNC:<i>{function: ^20}</i></m>|" \
              "<y>Line:{line: >3}</y> " \
              "<b>[LOG]</b> <level><u>{message}</u></level>"
    # LOG等级
    # 文件最大存放数量
    rotation = "20 MB"
    flag = True
    while flag:
        try:
            _logger.remove(0)
        except ValueError:
            _logger.trace("There is no existing handler with id")
            flag = False
    # 控制台输出
    _logger.add(sys.stdout, level=level.upper(), format=formats)

    if folder:
        file_path = folder
        # 传入的不是文件夹路径则在当前目录下建立log文件夹，然后再进行文件写入
        if not os.path.isdir(folder):
            file_path = os.getcwd() + "\\logs"
            if not os.path.exists(file_path):
                os.makedirs(file_path)
        _logger.add(os.path.join(file_path, "log_{time}.log"), level=level.upper(), format=formats, rotation=rotation)


def get_files(folder: str) -> list:
    """
    获取当前文件夹下面的所有文件

    :param folder: 文件夹名

    :return: 文件夹下面的所有文件，不包含子目录下的文件
    """
    file_and_folders = os.listdir(folder)
    files = list(filter(lambda x: os.path.isfile(os.path.join(folder, x)), file_and_folders))
    return files


def get_config(config_file: str) -> tuple:
    """
    读取配置文件中的相关配置
    :param config_file:配置文件
    :return: level, log_folder
    """
    with open(config_file, "r", encoding="UTF-8") as fp:
        content = yaml.full_load(fp)
        try:
            level = content["level"]
        except KeyError:
            _logger.warning("not found level in config file, set level to info")
            level = "info"
            # raise ValueError("not found level in config file")
        try:
            log_folder = content["log_folder"]
            if log_folder and log_folder.lower() == "none":
                log_folder = None
        except KeyError:
            log_folder = None
        return level, log_folder


def find_config_file(folder: str, config_yml_file: str) -> tuple:
    """
    查找指定的配置文件

    1、从传入的目录开始查找是否存在config_file_name文件

    2、如果找不到则在该目录的父目录查找

    :param folder: 要查找的目录

    :param config_yml_file: 配置文件名字

    :return:level, log_folder
    """
    if config_yml_file in get_files(folder):
        config_file = os.path.join(folder, config_file_name)
        return get_config(config_file)
    spilt_char = "\\" if os.name == "nt" else "/"
    while len(folder.split(spilt_char)) != 1:
        paths = folder.split(spilt_char)
        paths.pop(-1)
        if len(paths) == 1:
            # todo 是否适用于linux需要测试
            folder = f"{paths[0]}{spilt_char}"
        else:
            folder = spilt_char.join(paths)
        if config_yml_file in get_files(folder):
            config_file = os.path.join(folder, config_file_name)
            return get_config(config_file)
        if len(paths) == 1:
            break
    return "info", None


# 从文件中读取log等级，然后设置存放文件位置
logger_level, logger_folder = find_config_file(current_path, config_file_name)
if logger_level.lower() not in log_level_type:
    logger_level = "info"
set_logger(logger_level, logger_folder)

# 返回logger对象
logger = _logger