# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        usb_can.py
# @Author:      lizhe
# @Created:     2021/5/1 - 23:44
# --------------------------------------------------------
# 导入所需模块
import sys
import os
from ctypes import c_ubyte, c_ushort, c_char, c_uint, Structure, windll, c_int, byref, POINTER, memmove, c_long
from time import time
from platform import architecture
from inspect import stack
from automotive.logger.logger import logger
from ..api import CanBoxDevice, BaseCanDevice, BaudRate
from ..message import Message, control_decorator

# ===============================================================================
# 定义数据类型


UBYTE = c_ubyte
USHORT = c_ushort
CHAR = c_char
UINT = c_uint
DWORD = c_uint
BYTE = c_ubyte
UCHAR = c_ubyte
# ===============================================================================
# 定义波特率对应的Timing0和Timing1的取值
band_rate_list = {
    #   波特率  Timing0 Timing1
    '10Kbps': (0x31, 0x1C),
    '20Kbps': (0x18, 0x1C),
    '40Kbps': (0x87, 0xFF),
    '50Kbps': (0x09, 0x1C),
    '80Kbps': (0x83, 0xFF),
    '100Kbps': (0x04, 0x1C),
    '125Kbps': (0x03, 0x1C),
    '200Kbps': (0x81, 0xFA),
    '250Kbps': (0x01, 0x1C),
    '400Kbps': (0x80, 0xFA),
    '500Kbps': (0x00, 0x1C),
    '666Kbps': (0x80, 0xB6),
    '800Kbps': (0x00, 0x16),
    '1000Kbps': (0x00, 0x14),
    '33.33Kbps': (0x09, 0x6F),
    '66.66Kbps': (0x04, 0x6F),
    '83.33Kbps': (0x03, 0x6F)
}


# ===============================================================================
# 定义结构体
# 包含USB-CAN系列接口卡的设备信息，结构体将在VCI_ReadBoardInfo函数中被填充
class VciBoardInfo(Structure):
    _fields_ = [
        # 硬件版本号，用16进制表示。比如0x0100表示V1.00。
        ('hw_Version', USHORT),
        # 固件版本号， 用16进制表示。比如0x0100表示V1.00
        ('fw_Version', USHORT),
        # 驱动程序版本号， 用16进制表示。比如0x0100表示V1.00。
        ('dr_Version', USHORT),
        # 接口库版本号， 用16进制表示。比如0x0100表示V1.00。
        ('in_Version', USHORT),
        # 保留参数。
        ('irq_Num', USHORT),
        # 表示有几路CAN通道。
        ('can_Num', BYTE),
        # 此板卡的序列号。
        ('str_Serial_Num', CHAR * 20),
        # 硬件类型，比如“USBCAN V1.00”（注意：包括字符串结束符’\0’）
        ('str_hw_Type', CHAR * 40),
        # 系统保留。
        ('Reserved', USHORT)
    ]


# CAN帧结构体，即1个结构体表示一个帧的数据结构。
# 在发送函数VCI_Transmit和接收函数VCI_Receive中，被用来传送CAN信息帧
class VciCanObj(Structure):
    _fields_ = [
        # 帧ID。 32位变量，数据格式为靠右对齐。
        ('id', UINT),
        # 设备接收到某一帧的时间标识。 时间标示从CAN卡上电开始计时，计时单位为0.1ms。
        ('time_stamp', UINT),
        # 是否使用时间标识，为1时TimeStamp有效， TimeFlag和TimeStamp只在此帧为接收帧时有意义。
        ('time_flag', BYTE),
        # 发送帧类型。
        # 0时为正常发送（发送失败会自动重发，重发最长时间为1.5-3秒）；
        # 1时为单次发送（只发送一次，不自动重发）；
        ('send_type', BYTE),
        # 是否是远程帧。 =0时为为数据帧， =1时为远程帧（数据段空）
        ('remote_flag', BYTE),
        # 是否是扩展帧。 =0时为标准帧（11位ID）， =1时为扩展帧（29位ID）。
        ('extern_flag', BYTE),
        # 数据长度 DLC (<=8)，即CAN帧Data有几个字节。约束了后面Data[8]中的有效字节。
        ('data_len', BYTE),
        # CAN帧的数据。由于CAN规定了最大是8个字节，所以这里预留了8个字节的空间
        # 受DataLen约束。如DataLen定义为3，即Data[0]、 Data[1]、 Data[2]是有效的。
        ('data', BYTE * 8),
        # 系统保留。
        ('reserved', BYTE * 3)
    ]


# 定义了初始化CAN的配置。结构体将在VCI_InitCan函数中被填充，
# 即初始化之前，要先填好这个结构体变量
class VciInitConfig(Structure):
    _fields_ = [
        # 验收码。 SJA1000的帧过滤验收码。对经过屏蔽码过滤为“有关位”进行匹配，全部匹
        # 配成功后，此帧可以被接收。否则不接收。
        ('AccCode', DWORD),
        # 屏蔽码。 SJA1000的帧过滤屏蔽码。对接收的CAN帧ID进行过滤，对应位为0的是“有
        # 关位”，对应位为1的是“无关位”。屏蔽码推荐设置为0xFFFFFFFF，即全部接收
        ('AccMask', DWORD),
        # 保留
        ('Reserved', DWORD),
        # 滤波方式，允许设置为0-3
        # 0/1 接收所有类型 滤波器同时对标准帧与扩展帧过滤
        # 2 只接收标准帧  滤波器只对标准帧过滤，扩展帧将直接被滤除
        # 3 只接收扩展帧  滤波器只对扩展帧过滤， 标准帧将直接被滤除
        ('Filter', UCHAR),
        # 波特率定时器 0（BTR0）。
        ('Timing0', UCHAR),
        # 波特率定时器 1（BTR1）。
        ('Timing1', UCHAR),
        # 模式。
        # =0表示正常模式（相当于正常节点），
        # =1表示只听模式（只接收，不影响总线），
        # =2表示自发自收模式（环回模式）
        ('Mode', UCHAR)
    ]


class UsbCan(BaseCanDevice):
    """
    用于同一接口
    """

    def __init__(self, can_box_device: CanBoxDevice, device_type: int = 4, device_index: int = 0):
        """
        初始化类

        :param can_box_device: CAN BOX类型，支持 CanBoxDevice.USBCAN, CanBoxDevice.CANALYST

        :param device_type:
            设备类型。 对应不同的产品型号

            设备的类型，VCI_USBCAN2的类型值固定为4，包括CANalyst-II；

        :param device_index:

            设备索引，比如当只有一个USB-CAN适配器时，索引号为0，

            这时再插入一个USB-CAN适配器那么后面插入的这个设备索引号就是1，以此类推。
        """
        self.__dll_path = self.__get_dll_path(can_box_device)
        logger.debug(f"use dll path is {self.__dll_path}")
        self.__lib_can = windll.LoadLibrary(self.__dll_path)
        self.__start_time = 0
        self.__device_type = device_type
        self.__device_index = device_index
        # 过滤器 - 接收所有类型(1) 滤波方式，允许设置为0-3，
        self.__filter = 1
        # 工作模式 - 正常模式(1)
        #  =0表示正常模式（相当于正常节点），
        #  =1表示只听模式（只接收，不影响总线），
        #  =2表示自发自收模式（环回模式）
        self.__mode = 0
        # 验收码。 SJA1000的帧过滤验收码。对经过屏蔽码过滤为“有关位”进行匹配，
        # 全部匹配成功后，此帧可以被接收。否则不接收。
        self.__access_code = 0
        #  CAN通道索引。 第几路 CAN。即对应卡的CAN通道号， CAN1为0， CAN2为1
        self.__can_index = 0
        self.is_open = False

    def check_status(func):
        """
        检查设备是否已经连接
        :param func: 装饰器函数
        """

        def wrapper(self, *args, **kwargs):
            if not self.is_open:
                raise RuntimeError("please open pcan device first")
            return func(self, *args, **kwargs)

        return wrapper

    @staticmethod
    def __get_string(raw: int) -> str:
        return str(hex(raw)[2]) + '.' + str(hex(raw)[-2:])

    @staticmethod
    def __get_access_code_and_mask(access_code: int = None) -> tuple:
        """
        获取设备初始化的AccCode和AccMask信息。

        :param access_code:

            验收码。 SJA1000的帧过滤验收码。对经过屏蔽码过滤为“有关位”进行匹配，

            全部匹配成功后，此帧可以被接收。否则不接收。

        :return:返回AccCode和AccMask。
        """
        # TODO 后续根据需求再设计。
        if not access_code:
            return 0x00000000, 0xFFFFFFFF
        return None, None

    @staticmethod
    def __get_timing0_and_timing1(baud_rate: str) -> tuple:
        """
        从定义的波特率对应表中获取定时器0和定时器1的取值。

        :param baud_rate: 波特率(band_rate_list列出来的)

        :return: 返回相应波特率对应的Timing0和Timning1的取值。
        """
        if baud_rate in band_rate_list:
            return band_rate_list[baud_rate]
        else:
            raise ValueError(f"baud_rat is {baud_rate} only support {band_rate_list.keys()}")

    @staticmethod
    def __get_dll_path(can_box_device: CanBoxDevice) -> str:
        """
        获取dll的绝对路径路径

        :param can_box_device: CanBoxDevice枚举对象

        :return 返回dll所在的绝对路径
        """
        if can_box_device == CanBoxDevice.PEAKCAN:
            raise ValueError(f"can_box_device not support peak can")
        system_bit = architecture()[0]
        if can_box_device == CanBoxDevice.USBCAN:
            if system_bit == "32bit":
                dll_path = r'\usbcan\x86\ControlCAN'
            else:
                dll_path = r'\usbcan\x64\ControlCAN'
        elif can_box_device == CanBoxDevice.CANALYST:
            if system_bit == "32bit":
                dll_path = r'\canalyst\x86\ControlCAN'
            else:
                dll_path = r'\canalyst\x64\ControlCAN'
        elif can_box_device == CanBoxDevice.ANALYSER:
            if system_bit == "32bit":
                dll_path = r'\analyser\x86\ControlCAN'
            else:
                dll_path = r'\analyser\x64\ControlCAN'
        else:
            raise ValueError(f"can box device type is error, {can_box_device} not support")
        return os.path.split(os.path.realpath(__file__))[0] + dll_path

    def __get_init_config(self, filters: int, mode: int, access_code: int, baud_rate: str) -> VciInitConfig:
        """
        获取pInitConfig对象

        :param filters: 滤波方式，允许设置为0-3，

        :param mode: 模式

            =0表示正常模式（相当于正常节点），

            =1表示只听模式（只接收，不影响总线），

            =2表示自发自收模式（环回模式）

        :param access_code:

            验收码。 SJA1000的帧过滤验收码。对经过屏蔽码过滤为“有关位”进行匹配，

            全部匹配成功后，此帧可以被接收。否则不接收。

        :param baud_rate: 波特率(band_rate_list列出来的)

        :return: 初始化的VciInitConfig对象
        """
        init_config = VciInitConfig()
        init_config.Filter = UCHAR(filters)
        init_config.Mode = UCHAR(mode)
        acc_code, acc_mask = self.__get_access_code_and_mask(access_code)
        init_config.AccCode = DWORD(acc_code)
        init_config.AccMask = DWORD(acc_mask)
        timing0, timing1 = self.__get_timing0_and_timing1(baud_rate)
        if timing0 is not None:
            init_config.Timing0 = UCHAR(timing0)
            init_config.Timing1 = UCHAR(timing1)
        else:
            init_config.Timing0 = UCHAR(0x00)
            init_config.Timing1 = UCHAR(0x1C)
        init_config.Reserved = DWORD(0)
        return init_config

    @control_decorator
    def __init_device(self, baud_rate: str) -> int:
        """
        初始化指定的CAN通道。有多个CAN通道时，需要多次调用。

        :param baud_rate: 波特率(band_rate_list列出来的)
        """
        init_config = self.__get_init_config(self.__filter, self.__mode, self.__access_code, baud_rate)
        self.__lib_can.VCI_InitCAN.argtypes = [c_int, c_int, c_int, POINTER(VciInitConfig)]
        return self.__lib_can.VCI_InitCAN(self.__device_type, self.__device_index, self.__can_index, byref(init_config))

    def __data_package(self, frame_length: int, message_id: int, time_flag: int, send_type: int, remote_flag: int,
                       external_flag: int, data_length: int, data: list, reserve: list):
        """
        组包CAN发送数据，供VCI_Transmit函数使用。

        :param frame_length: 要发送的帧结构体数组的长度（发送的帧数量）。 最大为1000,高速收发时推荐值为48。

        :param message_id:  # 帧ID。 32位变量，数据格式为靠右对齐。

        :param time_flag:  是否使用时间标识，为1时TimeStamp有效， TimeFlag和TimeStamp只在此帧为接收帧时有意义。

        :param send_type:  发送帧类型

            0时为正常发送（发送失败会自动重发，重发最长时间为1.5-3秒）

            1时为单次发送（只发送一次，不自动重发）

        :param remote_flag:  是否是远程帧。

            =0时为为数据帧，

            =1时为远程帧（数据段空）

        :param external_flag:  是否是扩展帧。

            =0时为标准帧（11位ID），

            =1时为扩展帧（29位ID）。

        :param data_length:  数据长度 DLC (<=8)，即CAN帧Data有几个字节。约束了后面Data[8]中的有效字节。

        :param data:  data

            CAN帧的数据。由于CAN规定了最大是8个字节，所以这里预留了8个字节的空间

            受data_length约束。如data_length定义为3，即Data[0]、 Data[1]、 Data[2]是有效的。

        :param reserve:  系统保留

        :return: 返回组包的帧数据。
        """
        send_data = (VciCanObj * frame_length)()

        for i in range(frame_length):
            # 帧ID。32位变量，数据格式为靠右对齐
            send_data[i].id = UINT(message_id)

            # 是否使用时间标识，为1时TimeStamp有效，TimeFlag和TimeStamp只在此帧为接收帧时有意义
            if time_flag == 1:
                # 设备接收到某一帧的时间标识。时间标示从CAN卡上电开始计时，计时单位为0.1ms
                send_data[i].times_tamp = UINT(int(time() * 1000 - float(self.__start_time)))
                send_data[i].time_flag = BYTE(1)
            else:
                send_data[i].times_tamp = UINT(0)
                send_data[i].time_flag = BYTE(0)

            # 发送帧类型。=0时为正常发送（发送失败会自动重发，重发最长时间为1.5-3秒）；
            # =1时为单次发送（只发送一次，不自动重发）；
            # 其它值无效。（二次开发，建议SendType=1，提高发送的响应速度）
            send_data[i].send_type = BYTE(send_type)

            # 是否是远程帧。=0时为为数据帧，=1时为远程帧（数据段空）
            send_data[i].remote_flag = BYTE(remote_flag)

            # 是否是扩展帧。=0时为标准帧（11位ID），=1时为扩展帧（29位ID）
            send_data[i].extern_flag = BYTE(external_flag)

            # 数据长度 DLC (<=8)，即CAN帧Data有几个字节。约束了后面Data[8]中的有效字节
            send_data[i].data_len = data_length

            # CAN帧的数据
            a_data = (BYTE * 8)()
            for j, value in enumerate(data):
                a_data[j] = BYTE(value)
            memmove(send_data[i].data, a_data, 8)

            # 系统保留
            r_data = (BYTE * 3)()

            if reserve:
                for j, value in enumerate(reserve):
                    r_data[j] = BYTE(value)
            else:
                for j in range(3):
                    r_data[j] = BYTE(0)
            memmove(send_data[i].reserved, r_data, 3)
        return send_data

    @control_decorator
    def __open_device(self, reserved: int = 0) -> int:
        """
        描述：打开USB CAN设备，注意一个设备只能打开一次，测试前必须先调用该接口。

        :param reserved:  保留参数，通常为 0

        :return: 返回值=1，表示操作成功；

                =0表示操作失败；
        """
        return self.__lib_can.VCI_OpenDevice(self.__device_type, self.__device_index, reserved)

    @control_decorator
    def __start_device(self):
        """
        启动CAN卡的某一个CAN通道。有多个CAN通道时，需要多次调用。

        :return: 返回值=1，表示操作成功；

                =0表示操作失 败。
        """
        return self.__lib_can.VCI_StartCAN(self.__device_type, self.__device_index, self.__can_index)

    def open_device(self, baud_rate: BaudRate = BaudRate.HIGH, reserved: int = 0):
        """
        打开USB CAN设备，注意一个设备只能打开一次，测试前必须先调用该接口。

        :param baud_rate: CAN速率，HIGH表示高速，LOW表示低速

        :param reserved: 保留参数，通常为 0
        """
        # 当前设备处于打开状态
        if not self.is_open:
            if self.__open_device() == 1:
                self.is_open = True
            else:
                self.is_open = False
        if self.is_open:
            logger.debug(f"device is opened")
            if self.__init_device(baud_rate.value) == 1:
                self.__start_device()
            else:
                raise RuntimeError("open can box failed")
        else:
            raise RuntimeError("can box is not opened")

    def close_device(self):
        """
        关闭USB CAN设备，测试结束时调用该接口。
        """
        if self.is_open:
            if self.__lib_can.VCI_CloseDevice(self.__device_type, self.__device_index) == 1:
                self.is_open = False
                logger.debug(f"device is closed")

    @check_status
    def read_board_info(self) -> VciBoardInfo:
        """
        获取设备信息。

        :return: VciBoardInfo对象
        """
        p_info = VciBoardInfo()
        try:
            ret = self.__lib_can.VCI_ReadBoardInfo(self.__device_type, self.__device_index, byref(p_info))
            if ret == 1:
                hw_version = self.__get_string(p_info.hw_Version)
                fw_version = self.__get_string(p_info.fw_Version)
                dr_version = self.__get_string(p_info.dr_Version)
                in_version = self.__get_string(p_info.in_Version)
                irq_num = hex(p_info.irq_Num)
                can_num = p_info.can_Num
                str_serial_num = p_info.str_Serial_Num
                str_hw_type = p_info.str_hw_Type
                logger.trace(f"Read usb CAN Success.")
                logger.trace(f'硬件版本: V{hw_version}')
                logger.trace(f'固件版本: V{fw_version}')
                logger.trace(f"驱动版本: V{dr_version}")
                logger.trace(f"动态库版本: V{in_version}")
                logger.trace(f"板载中断: {irq_num}")
                logger.trace(f"CAN通道数: {can_num}")
                logger.trace(f"板卡序列号: {str_serial_num}")
                logger.trace(f"硬件类型: {str_hw_type}")
                return p_info
            elif ret == 0:
                raise RuntimeError("Read usb CAN Failed.")
            elif ret == -1:
                raise RuntimeError('Method <{}> usb CAN not exist.'.format(stack()[0][3]))
            else:
                raise RuntimeError("Unknown error.")
        except RuntimeError:
            error = sys.exc_info()
            logger.error('ERROR: ' + str(error[0]) + ' : ' + str(error[1]))
            raise RuntimeError(error[1])

    @check_status
    def get_hw_type(self) -> str:
        """
        获取硬件类型

        :return: 硬件类型
        """
        self.open_device()
        hw_type = self.read_board_info().str_hw_Type
        self.close_device()
        return hw_type

    @check_status
    @control_decorator
    def reset_device(self, can_index: int = 0) -> bool:
        """
        复位 CAN。主要用与 VCI_StartCAN配合使用，无需再初始化，即可恢复CAN卡的正常状态。

        比如当CAN卡进入总线关闭状态时，可以调用这个函数。

        :param can_index: CAN通道索引。第几路 CAN。即对应卡的CAN通道号，CAN1为0，CAN2为1。

        :return:
            True: 成功

            False: 失败
        """
        return self.__lib_can.VCI_ResetCAN(self.__device_type, self.__device_index, can_index) == 1

    @check_status
    @control_decorator
    def clear_buffer(self, can_index: int = 0):
        """
        清空指定CAN通道的缓冲区。主要用于需要清除接收缓冲区数据的情况,同时发送缓冲区数据也会一并清除。

        :param can_index:CAN通道索引。第几路 CAN。即对应卡的CAN通道号，CAN1为0，CAN2为1。

        :return:
            True: 成功

            False: 失败
        """
        return self.__lib_can.VCI_ClearBuffer(self.__device_type, self.__device_index, can_index) == 1

    @check_status
    @control_decorator
    def get_receive_num(self, can_index: int = 0) -> int:
        """
        获取指定CAN通道的接收缓冲区中，接收到但尚未被读取的帧数量。主要用途是配合VCI_Receive使用，即缓冲区有数据，再接收。
        实际应用中，用户可以忽略该函数，直接循环调用VCI_Receive，可以节约PC系统资源，提高程序效率。

        :param can_index: CAN通道索引。第几路 CAN。即对应卡的CAN通道号，CAN1为0，CAN2为1。

        :return: 返回尚未被读取的帧数；
        """
        return self.__lib_can.VCI_GetReceiveNum(self.__device_type, self.__device_index, can_index)

    @check_status
    def transmit(self, message: Message):
        """
        发送函数。

        :param message: Message

        """
        p_send = self.__data_package(message.frame_length, message.msg_id, message.time_flag, message.usb_can_send_type,
                                     message.remote_flag, message.external_flag, message.data_length, message.data,
                                     message.reserved)
        self.__lib_can.VCI_Transmit.restype = DWORD
        try:
            ret = self.__lib_can.VCI_Transmit(self.__device_type, self.__device_index, self.__can_index, byref(p_send),
                                              message.frame_length)
            logger.trace(f"ret = {ret}")
            if ret > 0:
                logger.trace(f"Usb CAN CAN{self.__can_index} Transmit Success.")
            elif ret == 0:
                raise RuntimeError(f"Usb CAN CAN{self.__can_index} Transmit Failed.")
            elif ret == -1:
                reason = stack()[0][3]
                raise RuntimeError(f"Method <{reason}> Usb CAN not exist.")
            else:
                raise RuntimeError("Unknown error.")
        except Exception:
            error = sys.exc_info()
            logger.trace('ERROR: ' + str(error[0]) + ' : ' + str(error[1]))
            raise RuntimeError(error[1])

    @check_status
    def receive(self, frame_length: int = 2500, wait_time: int = 100) -> tuple:
        """
        接收函数。此函数从指定的设备CAN通道的接收缓冲区中读取数据。

        :param frame_length:

            用来接收的帧结构体数组的长度（本次接收的最大帧数，实际返回值小于等于这个值）。
            该值为所提供的存储空间大小，适配器中为每个通道设置了2000帧的接收缓存区，用户根据
            自身系统和工作环境需求， 在1到2000之间选取适当的接收数组长度。 一般pReceive数组大
            小与Len都设置大于2000，如： 2500为宜，可有效防止数据溢出导致地址冲突。 同时每隔30ms
            调用一次VCI_Receive为宜。 （在满足应用的时效性情况下，尽量降低调用VCI_Receive的频
            率，只要保证内部缓存不溢出，每次读取并处理更多帧，可以提高运行效率。）

        :param wait_time: 保留参数。


        :return: 返回实际读取的帧数
        """
        p_receive = (VciCanObj * frame_length)()
        self.__lib_can.VCI_Receive.restype = c_long
        try:
            ret = self.__lib_can.VCI_Receive(self.__device_type, self.__device_index, self.__can_index,
                                             byref(p_receive), frame_length, wait_time)
            if ret > 0:
                logger.trace(f"Usb CAN CAN{self.__can_index} Receive Success.")
                return ret, p_receive
            elif ret == 0:
                raise RuntimeError(f"Usb CAN CAN{self.__can_index} Transmit Failed.")
            elif ret == -1:
                reason = stack()[0][3]
                raise RuntimeError(f"Method <{reason}> Usb CAN not exist.")
            else:
                raise RuntimeError("Unknown error.")
        except Exception:
            error = sys.exc_info()
            logger.trace('ERROR: ' + str(error[0]) + ' : ' + str(error[1]))
            raise RuntimeError(error[1])

    def get_status(self) -> bool:
        return self.is_open
