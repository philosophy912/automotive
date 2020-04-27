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
    def __completion_byte(byte_value: str) -> str:
        """
        如果不足8位，补齐8位
        :return:
        """
        # 补齐8位
        while len(byte_value) != 8:
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
        logger.trace(f"byte_index = [{byte_index}]")

        # 获取在单独这个byte中所占据的位置
        bit_index = 7 - (start_bit - (start_bit // 8 * 8))
        logger.trace(f"bit_index = [{bit_index}]")
        return byte_index, bit_index

    @staticmethod
    def __get_values(value: int, byte_index: int, bit_index: int, type_: bool) -> list:
        """
        根据byte_index以及bit_index来划分value所在的byte

        :param value: 要设置的值

        :param byte_index:  8 Byte中占据的位置

        :param bit_index: 1 Byte中占据的位置

        :param type_:
            大端还是小端 1=intel(小端模式) ，0=Motorola（大端模式）

            True表示intel， False表示Motorola

        :return: 占据的每个byte的值
        """
        values = []
        # value转换成bit便于计算
        bin_value = bin(value)[2:]
        # bin_value_length = len(bin_value)
        logger.trace(f"bin_value = [{bin_value}]")
        while bin_value:
            # 第一次处理数据
            if bit_index != -1:
                # 有可能存在bin_value的长度不够bit_index+1的情况
                if len(bin_value) > (bit_index + 1):
                    end_position = len(bin_value) - (bit_index + 1)
                    logger.trace(f"end_position = [{bin(end_position)}]")
                    slice_value = int(bin_value[end_position:], 2)
                    logger.trace(f"slice_value = [{bin(slice_value)}]")
                    # 把数据存起来
                    values.append(slice_value)
                    bin_value = bin_value[0:end_position]
                else:
                    slice_value = int(bin_value, 2)
                    logger.trace(f"slice_value = [{bin(slice_value)}]")
                    # 把数据存起来
                    values.append(slice_value)
                    # 处理完了，所以置空
                    bin_value = None
                bit_index = -1
            else:
                # 剩余的还大于一个byte
                if len(bin_value) > 8:
                    end_position = len(bin_value) - 8
                    logger.trace(f"end_position = [{bin(end_position)}]")
                    # 把数据存起来
                    slice_value = int(bin_value[end_position:], 2)
                    logger.trace(f"slice_value = [{bin(slice_value)}]")
                    values.append(slice_value)
                    # 把剩下的保留
                    bin_value = bin_value[0:end_position]
                else:
                    slice_value = int(bin_value, 2)
                    logger.trace(f"slice_value = [{bin(slice_value)}]")
                    # 把数据存起来
                    values.append(slice_value)
                    # 处理完了，所以置空
                    bin_value = None
            # 针对大小端做不同的处理
            if type_:
                byte_index += 1
            else:
                byte_index -= 1
        return values

    def __set_values(self, values: list, byte_index: int, byte_array: list, bit_index: int, type_: bool):
        """
        把values设置到每一个对应的byte中

        :param values:  拆分后的 values

        :param byte_index:   8 Byte中占据的位置，

        :param byte_array: data拆分后的数据

        :param bit_index: 1 Byte中占据的位置

        :param type_:
            大端还是小端 1=intel(小端模式) ，0=Motorola（大端模式）

            True表示intel， False表示Motorola
        """
        for i, value in enumerate(values):
            if type_:
                index = byte_index + i
            else:
                index = byte_index - i
            logger.trace(f"index = {index}")
            # 补齐8位
            byte_value = self.__completion_byte(bin(byte_array[index])[2:])
            bin_value = bin(value)[2:]
            if i == 0:
                if bit_index + 1 == 8:
                    calc_value = int(bin_value, 2)
                else:
                    # 第一个值可能从Byte的中间开始
                    raw_value = byte_value[bit_index + 1:]
                    logger.trace(f"raw_value = {raw_value} and bin_value = {bin_value}")
                    calc_value = int((bin_value + raw_value), 2)
                logger.trace(f"calc_value = {calc_value}")
                byte_array[index] = calc_value
            elif i == len(values) - 1:
                # 最后一个值Byte不能填满
                raw_value = byte_value[:8 - len(bin_value)]
                calc_value = int((raw_value + bin_value), 2)
                logger.trace(f"calc_value = {calc_value}")
                byte_array[index] = calc_value
            else:
                logger.trace(f"calc_value = {value}")
                byte_array[index] = value
        logger.trace(f"byte_array = [{list(map(lambda x: hex(x), byte_array))}]")

    @staticmethod
    def get_position(start_bit: int) -> int:
        """
        获取某点在8byte(64bit)的数据中位于第几位

        :param start_bit: 起始点

        :return:
            start=0 -> 7
            start=16 => 24
        """
        # 获取开始点在整个8byte数据的位置
        index = -1
        for i in range(8):
            if 8 * i <= start_bit <= 8 * i + 7:
                index = i
                break
        logger.trace(f"start is in the [{index}] byte")
        # 获取在单独这个byte中所占据的位置
        byte_index = start_bit - (start_bit // 8 * 8)
        logger.trace(f"start in one byte position is [{7 - byte_index}]")
        # 获取在整个8byte数据中所处的位置
        actual_index = (index + 1) * 8 - byte_index - 1
        logger.trace(f"start in 64 bit position is [{actual_index}]")
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
    def convert_to_msg(data: int) -> list:
        """
        将Long型的8byte数字转换成一个CAN Message的列表

        :param data: 0xff00000000000000

        :return: [0xff, 0, 0, 0, 0, 0, 0, 0]
        """
        logger.trace("data is " + str(hex(data)))
        message = []
        temp = 0xff00000000000000
        for i in range(8):
            # mask >> (i * 8) 表示移位，如i=1的时候，表示mask移动8位为 0x00ff000000000000
            # data & mask >> (i * 8) 表示把值设置在mask中
            # 把mask移动到最右边得出byte的值是多少
            message.append((data & (temp >> (i * 8))) >> (7 - i) * 8)
        logger.trace(f"after convert message is {list(map(lambda x: hex(x), message))}")
        return message

    @staticmethod
    def convert_to_data(message: list) -> int:
        """
        将收到的CAN Message中的8位列表的数字，转换成为一个Long型的数字

        :param message: [0xff, 0, 0, 0, 0, 0, 0, 0]

        :return: 0xff00000000000000
        """
        msg = 0
        for i, data in enumerate(message):
            # 依次移位构造msg
            msg |= data << (7 - i) * 8
        return msg

    def set_data(self, data: int, start_bit: int, bit_length: int, value: int, type_: bool) -> int:
        """
        用于设置每个Signal后，计算出8Byte的值

        :param type_:
            大端还是小端 1=intel(小端模式) ，0=Motorola（大端模式）

            True表示intel， False表示Motorola

        :param data: 数据

        :param bit_length: signal的bit长度

        :param start_bit: signal开始的bit位

        :param value:  要填入的值

        :return: 处理后的数据
        """
        # 设置的值不能超出范围
        max_value = 2 ** bit_length - 1
        if value > max_value:
            raise RuntimeError(f"value[{value}] need less than {max_value}")

        logger.trace(f"data = [{hex(data)}], bit_length = [{bit_length}], "
                     f"start_bit = [{start_bit}], value = [{value}], type_ = [{type_}]")
        logger.trace(f"value = {bin(value)}")
        # 分成了8个byte存储数据
        byte_array = self.convert_to_msg(data)
        logger.trace(f"byte_array = [{list(map(lambda x: hex(x), byte_array))}]")
        # 获取在Bytes中和Byte中的位置
        byte_index, bit_index = self.__get_position(start_bit)
        # 计算出来占据的值
        values = self.__get_values(value, byte_index, bit_index, type_)
        self.__set_values(values, byte_index, byte_array, bit_index, type_)
        return self.convert_to_data(byte_array)

    def get_data(self, data: int, start_bit: int, bit_length: int, type_: bool) -> int:
        """
        获取指定的signal的值

        :param data: 8 Byte的数据

        :param start_bit:  起始位

        :param bit_length:  长度

        :param type_:
            大端还是小端 1=intel(小端模式) ，0=Motorola（大端模式）

            True表示intel， False表示Motorola

        :return:  signal对应的值
        """
        logger.trace(f"data = [{hex(data)}], bit_length = [{bit_length}], "
                     f"start_bit = [{start_bit}], type_ = [{type_}]")
        # 分成了8个byte存储数据
        byte_array = self.convert_to_msg(data)
        logger.trace(f"byte_array = [{list(map(lambda x: hex(x), byte_array))}]")
        # 获取在Bytes中和Byte中的位置 如byte 1 bit7， length 2
        byte_index, bit_index = self.__get_position(start_bit)
        remainder = None
        # 用于数据存储
        value = ""
        # 计算会占据几个byte
        #  长度小于bit index
        if bit_index > bit_length:
            byte_holder = 1
        #  长度大于了 bit index +1， 比如长度是5， 开始位是3，表示会跨一个byte
        elif bit_length > (bit_index + 1):
            # 计算除了本字节外还会占据多少字节
            length, remainder = (bit_length - bit_index - 1) // 8, (bit_length - bit_index - 1) % 8
            logger.trace(f"length is {length} and remainder is {remainder}")
            # 刚好占一个字节， 只多占一个或者n个字节
            if remainder == 0:
                byte_holder = length + 1
            #  多占一个或者n个字节，但是还要多占一个字节
            else:
                byte_holder = length + 2
        # 长度等于bit index + 1
        else:
            byte_holder = 1
        logger.trace(f"byte_holder is {byte_holder}")
        range_length = byte_index + byte_holder
        if type_:
            for i in range(byte_index, range_length):
                byte_data = self.__completion_byte(bin(byte_array[i])[2:])
                if i == byte_index:
                    value = value + byte_data[:bit_index + 1]
                elif i == range_length - 1:
                    if remainder:
                        value = value + byte_data[:remainder]
                    else:
                        value = value + byte_data
                else:
                    value = value + byte_data
        else:
            for i in range(byte_index, range_length):
                byte_data = self.__completion_byte(bin(byte_array[i]))
                if i == byte_index:
                    value = value + byte_data[bit_index + 1:]
                elif i == range_length - 1:
                    if remainder:
                        value = value + byte_data[remainder:]
                    else:
                        value = value + byte_data
                else:
                    value = value + byte_data
        return int(value, 2)
