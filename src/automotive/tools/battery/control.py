# -*- coding:utf-8 -*-
# --------------------------------------------------------  
# Copyright (C), 2016-2020, China TSP, All rights reserved
# --------------------------------------------------------                 
# @Name:        KonstanterUtils
# @Purpose:     可编程电源工具类
# @Author:      lizhe  
# @Created:     2019/11/26 17:01  
# --------------------------------------------------------
import math
from loguru import logger
from .konstanter import Konstanter


class KonstanterControl(object):
    """
    Konstanter简化操作类
    """

    def __init__(self, port: str, baud_rate: int = 19200, over_voltage: float = 22.0):
        self.__kon = Konstanter(port=port, baud_rate=baud_rate)
        self.__kon.over_current_protection(True)
        self.__kon.output_off_delay_for_ocp(0.3)
        self.__kon.over_voltage_protection_value(over_voltage)
        self.__kon.output_enable(True)
        if self.__kon.get("IDN") is not None:
            self.connected = True
        else:
            self.connected = False

    def set_limit(self, voltage: float = 20.0, current: float = 20.0):
        """
        设置电压电流的上限值

        :param voltage: 设置的电压上限值，浮点型，范围[0, 20.0]，默认值=20.0

        :param current: 设置的电流上限值，浮点型，范围[0, 20.0]，默认值=20.0
        """
        self.__kon.set_current_limit(current)
        self.__kon.set_voltage_limit(voltage)

    def set_voltage_current(self, voltage: float = None, current: float = None):
        """
        设置输出的电压电流值

        :param voltage: 要设置的电压值，不设置则保持上次的值不修改，浮点型，范围[0, ulimit]

        :param current: 要设置的电流值，不设置则保持上次的值不修改，浮点型，范围[0, ilimit]
        """
        if voltage:
            self.__kon.set_voltage(voltage)
        if current:
            self.__kon.set_current(current)

    def set_raise_down(self, start: float, end: float, step: float, time: float, repeat: int = 1,
                       current: int = 3) -> tuple:
        """
        设置电源的上升或下降的参数，测试电源的电压变动

        :param start: 上升或下降过程中的起点电压值

        :param end: 上升或下降过程中的终点电压值

        :param step: 上升或下降过程中的步进值

        :param time: 每次上升或下降过程的时间

        :param repeat: 重复执行的次数

        :param current: 设置默认的电流

        :return: 起点电压对应的寄存器，终点电压对应的寄存器，再次回到起点电压对应的寄存器
        """
        steps = math.ceil(abs((end - start) / step))
        if start > end:
            step = step * (-1)
        mid_register = 11 + steps
        if mid_register > 255:
            mid_register = 255
        for k in range(11, mid_register):
            self.__kon.store(k, start + step * (k - 11), current, time, 'ON')
        self.__kon.store(mid_register, end, current, time, 'ON')
        if (255 - mid_register) > steps:
            end_register = mid_register + steps
        else:
            end_register = 255
        step = step * (-1)
        for m in range(mid_register + 1, end_register):
            self.__kon.store(m, end + step * (m - mid_register), current, time, 'ON')
        if mid_register != 255:
            self.__kon.store(end_register, start, current, time, 'ON')
        self.__kon.sequence_repetition(repeat)
        result = 11, mid_register, end_register
        logger.info(
            f"power setting register:(11, {mid_register}, {end_register}) maps voltage:({start}, {end}, {start})")
        self.__kon.get_store()
        return result

    def start(self, begin: int, end: int, check_time: int = 1000) -> bool:
        """
        执行设置好的电源参数，即依次调用寄存器， begin以及end可以通过set_user_voltages以及set_voltage_current的返回值得到

        :param begin: 设置要执行的序列的起始寄存器地址

        :param end: 设置要执行的序列的终止寄存器地址

        :param check_time:
            超时设置，当此次数内检测到序列已执行完毕则直接返回，如果一直未检测到序列执行完毕则超过次数后返回，默认=1000次

        :return:
            True:执行成功

            False: 执行失败
        """

        self.__kon.start_stop(begin, end)
        self.__kon.sequence('GO')
        for i in range(int(check_time)):
            status = self.__kon.get('SEQ')
            tmp = status.split()[-1]
            if tmp.split(',')[0] == 'RDY' and tmp.split(',')[1] == '000':
                return True
        return False

    def set_user_voltages(self, voltages: (list, tuple), times: int = 0.01, current: float = 5,
                          repeat: int = 1) -> tuple:
        """
        设置用户自定义的或从文件读取到的电压序列，模拟用户自定义的电压曲线

        :param voltages: 电压值列表，必须为列表或元祖类型

        :param times: 间隔时间，如果为数字则所有电压均应用该值，如果为列表则与电压voltages值一一对应

        :param current: 默认的电流设置值

        :param repeat: 电压曲线自动触发的次数

        :return: (起点电压对应的寄存器，终点电压对应的寄存器)
        """
        if not isinstance(voltages, (list, tuple)):
            self.__kon.close()
            raise ValueError(f"Voltages must be a list or tuple: {voltages}")
        if not isinstance(times, (list, tuple)):
            time_list = [times] * len(voltages)
        else:
            time_list = list(times)
            if len(time_list) < len(voltages):
                time_list = time_list + [time_list[-1]] * (len(voltages) - len(time_list))
        for i, item in enumerate(zip(voltages, time_list)):
            self.__kon.store(11 + i, item[0], current, item[1])
            if 11 + i >= 255:
                break
        registers = 11, 255
        if 11 + len(voltages) - 1 < 255:
            registers = 11, 11 + len(voltages) - 1
        self.__kon.sequence_repetition(repeat)
        self.__kon.get_store()
        return registers

    def close(self, output_off: bool = False):
        """
        程序执行结束后关闭输出，关闭串口

        :param output_off:
            True: 同时关闭输出

            False: 不关闭输出，保持状态
        """
        if output_off:
            self.__kon.output_enable(False)
        self.__kon.close()
        self.connected = False

    def get(self, *args):
        """
        透传Konstanter类中的get方法

        :param args: Konstanter中的get方法支持的args参数
        """
        return self.__kon.get(*args)

    def output_enable(self, switch: bool = True):
        """
        透传Konstanter类中的output_enable方法

        :param switch:
            True表示开通

            False表示关闭
        """
        self.__kon.output_enable(switch)
