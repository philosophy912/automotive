# -*- coding:utf-8 -*-
# --------------------------------------------------------  
# Copyright (C), 2016-2020, China TSP, All rights reserved
# --------------------------------------------------------                 
# @Name:        tools  
# @Purpose:     工具类，主要面向message以及parse使用
# @Author:      lizhe  
# @Created:     2019/8/21 9:47  
# --------------------------------------------------------
from loguru import logger


class Tools(object):
    """
    工具类，单独给CAN Service中的Parser使用，基本上不对外使用

    该类的作用是根据start_bit和bit_length等值计算出来8byte的值或者反向计算。

    如需要可以将该类变成私有类
    """

    @staticmethod
    def get_position(start: int) -> int:
        """
        获取某点在8byte(64bit)的数据中位于第几位

        :param start: 起始点

        :return:
            start=0 -> 7
            start=16 => 24
        """
        # 获取开始点在整个8byte数据的位置
        index = -1
        for i in range(8):
            if 8 * i <= start <= 8 * i + 7:
                index = i
                break
        logger.debug(f"start is in the {index} byte")
        # 获取在单独这个byte中所占据的位置
        byte_index = start - (start // 8 * 8)
        logger.debug(f"start is in byte position is {7 - byte_index}")
        # 获取在整个8byte数据中所处的位置
        actual_index = (index + 1) * 8 - byte_index - 1
        logger.debug(f"start in 8 byte position is {actual_index}")
        return actual_index

    @staticmethod
    def check_value(value: (int, float), min_: (int, float), max_: (int, float)) -> bool:
        """
        校验value是否处于min和max之间[min, max]

        :param value: 要校验的值

        :param min_: 最小值

        :param max_: 最大值

        :return:
            True: 正确
            False: 错误
        """
        return min_ <= value <= max_

    @staticmethod
    def set_msg_data_to_list(data: int) -> list:
        """
        将Long型的8byte数字转换成一个CAN Message的列表

        :param data: 0xff00000000000000

        :return: [0xff, 0, 0, 0, 0, 0, 0, 0]
        """
        logger.debug("bin data is " + str(hex(data)))
        message = []
        temp = 0xff00000000000000
        for i in range(8):
            # 指定要获取数据的位置 temp >> (i * 8)
            # 数据与移位数据做或操作使得不要的数据变成0
            # 然后再将要操作的数据移位到最后成为正确数据
            byte = (data & (temp >> (i * 8))) >> (7 - i) * 8
            # 添加进入列表中
            message.append(byte)
        logger.debug(f"after convert message is {message}")
        return message

    @staticmethod
    def set_list_data_to_msg(data: list) -> int:
        """
        将收到的CAN Message中的8位列表的数字，转换成为一个Long型的数字

        :param data: [0xff, 0, 0, 0, 0, 0, 0, 0]

        :return: 0xff00000000000000
        """
        msg = 0
        for i in range(len(data)):
            msg |= data[7 - i] << (i * 8)
        return msg

    @staticmethod
    def get_position_in_8_bytes(start: int) -> int:
        """
        获取某点在8byte(64bit)的数据中位于第几位

        :param start:  起始点

        :return:
            start=0 -> 7

            start=16 => 24
        """
        # 获取开始点在整个8byte数据的位置
        index = -1
        for i in range(8):
            if 8 * i <= start <= 8 * i + 7:
                index = i
                break
        logger.debug(f"start is in the {index} byte")
        # 获取在单独这个byte中所占据的位置
        byte_index = int(start - (start // 8 * 8))
        logger.debug(f"start is in byte position is {7 - byte_index}")
        # 获取在整个8byte数据中所处的位置
        actual_index = (index + 1) * 8 - byte_index - 1
        logger.debug(f"start in 8 byte position is {actual_index}")
        return actual_index

    @staticmethod
    def set_value_by_bit(data: int, length: int, shift: int, value: int) -> int:
        """
        替换原来数据中从右开始偏移shift长度的值

        即从右（bit63）开始计算偏移量，偏移长度为length的值替换成value的内容

        :param data: 原始数据

        :param length: 要取多少位的数据

        :param shift: 向左移动多少位，即要取的位置距离右边的数据

        :param value: 要设置的数据

        :return: 返回设置后的数据

                如: data=0b11001100 length=2, shift=4, value=0b11， 则返回0b11111100
        """
        mask = (2 ** length - 1) << shift
        return (data & (~mask)) | (value << shift)

    def get_value(self, data: int, start: int, length: int) -> int:
        """
        获取指定位置开始的数据

        :param data: 原始数据

        :param start: 要从那个地方取数据

        :param length: 要取的长度

        :return: 取到的数据长度

            如: data=0xff0000ff00ffff00, start=15, length=8,则取到的数据位0xf
        """
        # 先计算终点的位置
        end_position = self.get_position_in_8_bytes(start)
        # 计算起点的位置
        # start_position = end_position - length
        # 构建length长度的全1数据
        temp = 2 ** length - 1
        # 取的话是从start_position到end_position的数据
        # 计算右边即end_position到63之间的距离
        right_distance = 63 - end_position
        # 左移temp到指定位置
        compare = temp << right_distance
        # &操作取出数据后右移数据到原来位置
        temp_data = (data & compare) >> right_distance
        logger.debug(f"get value is {hex(temp_data)}")
        return temp_data
