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
    def __completion_byte(byte_value: str, size: int = 8) -> str:
        """
        如果不足size位，补齐size位
        :return:
        """
        # 补齐8位
        while len(byte_value) != size:
            byte_value = "0" + byte_value
        return byte_value

    @staticmethod
    def __get_position(start_bit: int) -> tuple:
        """
        获取start_bit在整个8Byte中占据的位置以及在1 Byte中的位置

        :param start_bit: 起始点

        :return: 8 Byte中占据的位置，1 Byte中占据的位置
        """
        # 根据start_bit以及bin_value_length计算占据的byte有几个
        # 计算start_bit是在第几个byte中，以及在byte中占据第几个bit
        # 获取开始点在整个8byte数据的位置
        byte_index = -1
        for i in range(8):
            if 8 * i <= start_bit <= 8 * i + 7:
                byte_index = i
                break
        # 获取在单独这个byte中所占据的位置
        bit_index = 7 - (start_bit - (start_bit // 8 * 8))
        logger.trace(f"byte_index = [{byte_index}] && bit_index = [{bit_index}]")
        return byte_index, bit_index

    @staticmethod
    def __split_bytes(value: str, length: int, bit_index: int, byte_type: bool) -> list:
        """
        根据bit_index和length来算value拆分成几个byte
        :param value:  要设置的值
        :param length: 长度
        :param bit_index: start_bit在一个byte中的位置
        :return: byte集合
        """
        logger.trace(f"length is {length}, bit_index = {bit_index}")
        values = []
        if byte_type:
            if length > bit_index + 1:
                values.append(value[-bit_index - 1:])
                # 把剩下的拿出来
                value = value[:-bit_index - 1]
                logger.trace(f"rest value is [{value}]")
                while len(value) > 8:
                    # 当剩余数据长度大于8表示还有一个byte， 先把数据加入列表中
                    values.append(value[-8:])
                    # 然后截取剩余的部分
                    value = value[:-8]
                # 最后把剩余的部分加到列表中
                values.append(value)
            else:
                # 只有一个byte
                values.append(value)
        else:
            if length > (8 - bit_index):
                values.append(value[:8 - bit_index])
                # 把剩下的拿出来
                value = value[8 - bit_index:]
                logger.trace(f"rest value is [{value}]")
                while len(value) > 8:
                    # 当剩余数据长度大于8表示还有一个byte， 先把数据加入列表中
                    values.append(value[:8])
                    # 然后截取剩余的部分
                    value = value[8:]
                # 最后把剩余的部分加到列表中
                values.append(value)
            else:
                # 只有一个byte
                values.append(value)
        return values

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

    def set_data(self, data: list, start_bit: int, byte_type: bool, value: int, bit_length: int):
        """
        用于设置每个Signal后，计算出8Byte的值

        :param bit_length: signal 长度

        :param value:  signal总线值

        :param byte_type:  True表示Intel， False表示Motorola MSB模式, DBC解析出来只支持MSB模式, 不支持LSB模式，

            对于LSB来说，在变成DBC的时候就处理了start bit

        :param start_bit: 起始位

        :param data: 总线8Byte数据
        """
        logger.trace(f"data = {list(map(lambda x: hex(x), data))}), start_bit = [{start_bit}], "
                     f"byte_type = [{byte_type}], value = [{value}], bit_length = [{bit_length}]")
        byte_index, bit_index = self.__get_position(start_bit)
        # True表示Intel， False表示Motorola MSB模式, DBC解析出来只支持MSB模式, 不支持LSB模式，
        # 对于LSB来说，在变成DBC的时候就处理了start bit
        # 根据位数来算， 其中把value转换成了二进制的字符串
        bin_value = self.__completion_byte(bin(value)[2:], bit_length)
        logger.trace(f"bin_value = {bin_value}")
        # 计算占据几个byte
        holder_bytes = self.__split_bytes(bin_value, bit_length, bit_index, byte_type)
        logger.trace(f"holder_bytes = {holder_bytes}")
        for index, byte in enumerate(holder_bytes):
            actual_index = byte_index + index
            logger.trace(f"actual index = {actual_index}")
            byte_value = self.__completion_byte(bin(data[actual_index])[2:])
            logger.trace(f"the [{byte_index}] value is [{byte_value}]")
            length = len(byte)
            logger.trace(f"byte  = {byte}")
            # 填充第一位
            if index == 0:
                if byte_type:
                    logger.trace(f"intel mode")
                    byte_value = byte_value[:bit_index + 1 - length] + byte + byte_value[bit_index + 1:]
                else:
                    logger.trace("motorola mode")
                    byte_value = byte_value[:bit_index] + byte + byte_value[bit_index + length:]
                logger.trace(f"first byte value = {byte_value}")
            # 填充最后一位
            elif index == len(holder_bytes) - 1:
                if byte_type:
                    byte_value = byte_value[:8 - length] + byte
                else:
                    byte_value = byte_value[:-length] + byte
                logger.trace(f"last byte value = {byte_value}")
            # 填充中间的数据
            else:
                byte_value = byte
            logger.trace(f"after handle byte_value = {byte_value}")
            logger.trace(f"set {actual_index} data {bin(data[actual_index])[2:]} to {byte_value}")
            # 把计算后的值设置会data中去, 此处注意字符串要转成2进制
            data[actual_index] = int(byte_value, 2)
        logger.trace(f"parser data is = {list(map(lambda x: hex(x), data))}")

    def get_data(self, data: list, start_bit: int, byte_type: bool, bit_length: int) -> int:
        """
        根据data计算出来每个signal的值

        :param bit_length: signal 长度

        :param byte_type:  True表示Intel， False表示Motorola MSB模式, DBC解析出来只支持MSB模式, 不支持LSB模式，

            对于LSB来说，在变成DBC的时候就处理了start bit

        :param start_bit: 起始位

        :param data: 8 byte数据

        :return 查询到的值
        """
        logger.trace(f"data = {list(map(lambda x: hex(x), data))}), start_bit = [{start_bit}], "
                     f"byte_type = [{byte_type}], bit_length = [{bit_length}]")
        byte_index, bit_index = self.__get_position(start_bit)
        byte_value = self.__completion_byte(bin(data[byte_index])[2:])
        logger.trace(f"the [{byte_index}] value is [{byte_value}]")
        if byte_type:
            logger.trace(f"intel mode")
            if bit_length > bit_index + 1:
                signal_value = byte_value[:bit_index + 1]
                logger.trace(f"intel first signal_value = {signal_value}")
                rest_length = bit_length - bit_index - 1
                logger.trace(f"intel rest length = {rest_length}")
                while rest_length > 8:
                    byte_index += 1
                    byte_value = self.__completion_byte(bin(data[byte_index])[2:])
                    logger.trace(f"the [{byte_index}] value is [{byte_value}]")
                    signal_value = byte_value[:8] + signal_value
                    logger.trace(f"intel middle signal_value = {signal_value}")
                    rest_length = rest_length - 8
                # 最后一个value
                byte_index += 1
                byte_value = self.__completion_byte(bin(data[byte_index])[2:])
                logger.trace(f"the [{byte_index}] value is [{byte_value}]")
                logger.trace(f"rest_length = {rest_length}")
                signal_value = byte_value[-rest_length:] + signal_value
                logger.trace(f"intel last signal_value = {signal_value}")
            else:
                signal_value = byte_value[bit_index + 1 - bit_length:bit_index + 1]
                logger.trace(f"only one byte value = {signal_value}")
        else:
            logger.trace(f"motorola mode")
            if bit_length > (8 - bit_index):
                signal_value = byte_value[bit_index:]
                logger.trace(f"motorola first signal_value = {signal_value}")
                rest_length = bit_length - (8 - bit_index)
                logger.trace(f"rest length = {rest_length}")
                while rest_length > 8:
                    byte_index += 1
                    byte_value = self.__completion_byte(bin(data[byte_index])[2:])
                    logger.trace(f"the [{byte_index}] value is [{byte_value}]")
                    signal_value = signal_value + byte_value[:8]
                    logger.trace(f"motorola middle signal_value = {signal_value}")
                    rest_length = rest_length - 8
                # 最后一个value
                byte_index += 1
                byte_value = self.__completion_byte(bin(data[byte_index])[2:])
                logger.trace(f"the [{byte_index}] value is [{byte_value}]")
                logger.trace(f"rest_length = {rest_length}")
                signal_value = signal_value + byte_value[:rest_length]
                logger.trace(f"motorola last signal_value = {signal_value}")
            else:
                signal_value = byte_value[bit_index:bit_index + bit_length]
        # 字符串转换成数字
        return int(signal_value, 2)
