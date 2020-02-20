# -*- coding:utf-8 -*-
# --------------------------------------------------------  
# Copyright (C), 2016-2020, China TSP, All rights reserved
# --------------------------------------------------------                 
# @Name:        logger
# @Purpose:     logger文件
# @Author:      lizhe  
# @Created:     2020/2/18 10:06  
# --------------------------------------------------------
import os
import sys

from loguru import logger as _logger

# LOG的格式
FORMAT = "<g>[{time:YYYY-MM-DD HH:mm:ss.SSS}]</g>" \
         "<level>[{level: ^9}]</level>|" \
         "<c><i>{file: ^20}</i></c>|<e>MOD:<i>{module: ^20}</i></e>|" \
         "<m>FUNC:<i>{function: ^20}</i></m>|" \
         "<y>Line:{line: >3}</y> " \
         "<b>[LOG]</b> <level><u>{message}</u></level>"
# LOG等级
LEVEL = "INFO"
# 配置文件夹路径
FILE = None
# 文件最大存放数量
ROTATION = "20 MB"

_logger.remove(0)
# 控制台输出
_logger.add(sys.stdout, level=LEVEL, format=FORMAT)

if FILE:
    file_path = FILE
    # 传入的不是文件夹路径则在当前目录下建立log文件夹，然后再进行文件写入
    if not os.path.isdir(FILE):
        file_path = os.getcwd() + "\\logs"
        os.makedirs(file_path)
    _logger.add(os.path.join(file_path, "log_{time}.log"), level=LEVEL, format=FORMAT, rotation=ROTATION)

# 返回logger对象
logger = _logger
