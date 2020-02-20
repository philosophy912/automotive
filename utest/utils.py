# -*- coding:utf-8 -*-
# --------------------------------------------------------  
# Copyright (C), 2016-2020, China TSP, All rights reserved
# --------------------------------------------------------                 
# @Name:        utils
# @Purpose:     提供未测试方法的装饰器
# @Author:      lizhe  
# @Created:     2020/2/18 11:15  
# --------------------------------------------------------
from loguru import logger
from functools import wraps


def skip(func):
    """
    todo方法装饰器
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.critical(f"function [{func.__name__[5:]}] is not test now")
        return func(*args, **kwargs)

    return wrapper

