# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2021, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        typehint.py
# @Author:      lizhe
# @Created:     2021/11/18 - 22:27
# --------------------------------------------------------
from typing import Union, Dict, List, Tuple, Sequence

# 数字类型
Number = Union[int, float]
Values = Dict[str, str]
SignalType = Dict[str, Union[str, int, float, bool, Values]]
MessageType = Dict[str, Union[str, int, float, bool, List[SignalType]]]
Messages = List[MessageType]
IdMessage = Dict[int, MessageType]
NameMessage = Dict[str, MessageType]
FilterNode = Union[str, Union[Tuple[str, ...], Sequence[str]]]
MessageIdentity = Union[int, str]
