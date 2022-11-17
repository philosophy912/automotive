# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2021, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        typehint.py
# @Author:      lizhe
# @Created:     2021/11/18 - 22:27
# --------------------------------------------------------
import numpy as np
from typing import Union, Dict, Tuple
# 类型别名
Number = Union[int, float]
NumpyArray = np.ndarray
Position = Tuple[int, int, int, int]
ImageFile = Union[str, NumpyArray]
RGB = Tuple[int, int, int]
AirTestResult = Dict[str, Union[Tuple, float]]
CompareResult = Tuple[Union[float, int], Union[float, int]]
