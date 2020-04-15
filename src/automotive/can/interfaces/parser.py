# -*- coding:utf-8 -*-
# --------------------------------------------------------  
# Copyright (C), 2016-2020, China TSP, All rights reserved
# --------------------------------------------------------                 
# @Name:        parser  
# @Purpose:     Parser
# @Author:      lizhe  
# @Created:     2019/12/4 10:26  
# --------------------------------------------------------
from loguru import logger
from automotive.tools import Utils
from .message import Message


class Parser(object):

    @staticmethod
    def get_message(messages: (str, list), encoding: str = "utf-8") -> tuple:
        """
        从Json或者python文件中获取id和name的message字典

        :param messages: json文件所在位置或者dbc转换出的python文件中的messages

        :param encoding: 编码格式，默认utf-8

        :return: （id_messages, name_messages）

            id_message是以id开头的字典类型，如{0x150: Message1, 0x151: Message2}, 其中Message1参考Message对象；

            name_message是以name开头的字典类型，如{"name1": Message1, "name2": Message2}, 其中Message1参考Message对象;

        """
        id_messages = dict()
        name_messages = dict()
        if isinstance(messages, str):
            messages = Utils().get_json_obj(messages, encoding=encoding)["messages"]
        for msg in messages:
            message = Message()
            message.set_value(msg)
            id_messages[message.msg_id] = message
            name_messages[message.msg_name] = message
        logger.trace(f"total read message is {len(id_messages)}")
        return id_messages, name_messages
