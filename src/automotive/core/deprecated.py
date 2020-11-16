# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, China TSP, All rights reserved
# --------------------------------------------------------
# @Name:        deprecated
# @Purpose:     废弃类方法
# @Author:      lizhe
# @Created:     2019/12/14 11:31
# --------------------------------------------------------
from functools import wraps
from automotive.logger.logger import logger


def deprecated(new_function: str = None, class_name: str = None):
    """
    废弃方法装饰器(目前没有废弃方法或者废弃函数)

    :param new_function: 函数名

    :param class_name: 类名
    """

    def deprecated_function(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if class_name:
                if new_function:
                    logger.warning(
                        f"class [{class_name}],function [{func.__name__}] is deprecated,"
                        f" please use [{new_function}] to replace it")
            else:
                if new_function:
                    logger.warning(
                        f"function [{func.__name__}] is deprecated, please use [{new_function}] to replace it")
                else:
                    logger.warning(f"function [{func.__name__}] is deprecated")
            return func(*args, **kwargs)

        return wrapper

    return deprecated_function
