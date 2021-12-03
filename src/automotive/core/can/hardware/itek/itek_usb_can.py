# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2021, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        itek_usb_can.py
# @Author:      lizhe
# @Created:     2021/10/1 - 22:23
# --------------------------------------------------------
import os
import platform
from ctypes import CDLL, byref, memmove, POINTER
from platform import architecture
from typing import Tuple, Any


from .itekbasic import USBCANFD_X100, DEVICE_INDEX1, RESERVED, CHANNEL, \
    ITekCanFdChannelInitConfig, U8, A_BAUD_RATE, D_BAUD_RATE, U32, ITekCanFdReceiveData, CanFdFrame, \
    ITekCanFdTransmitData, U16, ITekCanDeviceInfo, FilterDataExtend, FilterDataStandard, FilterData
from automotive.core.can.message import Message
from automotive.logger.logger import logger
from automotive.common.constant import check_connect, can_tips
from automotive.core.can.common.interfaces import BaseCanDevice
from automotive.core.can.common.enums import BaudRateEnum


class ItekUsbCanDevice(BaseCanDevice):

    def __init__(self, is_fd: bool = True):
        """

        :param is_fd:
        """
        super().__init__()
        # 设备类型号
        self.__device_type = USBCANFD_X100
        # 设备索引号，用于区分一台计算机上使用的多套同类型设备。如只插 1 台USBCANFD 设备， device_index=0；
        self.__device_index = DEVICE_INDEX1
        self.__dll_path = self.__get_dll_path()
        self.__is_fd = is_fd
        # 操作句柄
        self.__device_handle = None
        # init句柄
        self.__channel_handle = None
        logger.debug(f"use dll path is {self.__dll_path}")
        if platform.system() == "Windows":
            self.__lib_can = CDLL(self.__dll_path)
        else:
            raise RuntimeError("can not support linux")

    @staticmethod
    def __get_dll_path():
        system_bit = architecture()[0]
        if system_bit == "32bit":
            dll_path = r'\x86\iTekCANFD.dll'
        else:
            dll_path = r'\x64\iTekCANFD.dll'
        return os.path.split(os.path.realpath(__file__))[0] + dll_path

    def __start_can(self):
        """
        启动 CAN(FD)通道，通道初始化后应调用该函数启动， 之后才能进行数据收发。
        """
        # EXTERNC bool __stdcall iTek_StartCAN(CHANNEL_HANDLE usbhandle);
        result = self.__lib_can.iTek_StartCAN(self.__channel_handle)
        if result:
            self._is_open = True
        else:
            self._is_open = False
            raise RuntimeError("open itek can box failed")

    def __init_can(self, channel: int, baud_rate: BaudRateEnum):
        """
        该函数用于初始化 CAN(FD)通道，将工作模式、波特率、过滤屏蔽码等参数写入 CAN(FD)控制器。
        """
        logger.debug(f"channel is {channel}")
        # 	EXTERNC void* __stdcall iTek_InitCAN(DEVICE_HANDLE usbhandle, uint8_t, iTek_CANFD_CHANNEL_INIT_CONFIG*);
        config = ITekCanFdChannelInitConfig()
        # CAN 协议类型： 0=CAN 协议； 1=CANFD 协议；
        if self.__is_fd:
            config.can_type = U8(1)
        else:
            config.can_type = U8(0)
        # CANFD 标准： 0=ISO 标准； 1=非 ISO 标准；
        config.CANFDStandard = U8(0)
        # CANFD 是否加速： 0=不加速； 1=加速；
        config.CANFDSpeedup = U8(0)
        # 仲裁波特率
        config.abit_timing = A_BAUD_RATE[baud_rate.value]
        # 数据波特率
        config.dbit_timing = D_BAUD_RATE[BaudRateEnum.DATA.value]
        # 工作模式， 0=正常工作模式； 1=只听工作模式；
        config.workMode = U8(0)
        # 保留位
        config.res = RESERVED
        # 扩展帧过滤器组结构体， 过滤器组数量根据实际使用情况自定义
        filter_data_extend = FilterDataExtend()
        filter_data_extend.num = 1
        filter_data_extend_array = (FilterData * 64)()
        filter_data_extend_array[0].frameType = U8(1)
        filter_data_extend_array[0].filterType = U8(0)
        filter_data_extend_array[0].ID1 = U32(0x0)
        filter_data_extend_array[0].ID2 = U32(0x1fffffff)
        memmove(filter_data_extend.FilterDatafilterDataExtends, filter_data_extend_array, 64)
        config.Extend = filter_data_extend
        # 标准帧过滤器组结构体， 过滤器组数量根据实际使用情况自定义。
        filter_data_standard = FilterDataStandard()
        filter_data_standard.num = 1
        # 标准帧过滤器组结构体， 只配置了一组
        filter_data_standard_array = (FilterData * 128)()
        filter_data_standard_array[0].frameType = U8(0)
        filter_data_standard_array[0].filterType = U8(0)
        filter_data_standard_array[0].ID1 = U32(0x0)
        filter_data_standard_array[0].ID2 = U32(0x7ff)
        memmove(filter_data_standard.FilterDatafilterDataStandard, filter_data_standard_array, 128)
        config.Standard = filter_data_standard
        # device_handle = U32(self.__device_handle)
        # USBChannel_Handle iTek_InitCan(DEVICE_HANDLE usbhandle, uint8_t channel, iTek_CANFD_CHANNEL_INIT_CONFIG* config);
        self.__lib_can.iTek_InitCAN.argtypes = [U32, U8, POINTER(ITekCanFdChannelInitConfig)]
        self.__channel_handle = self.__lib_can.iTek_InitCAN(self.__device_handle, CHANNEL[channel], byref(config))
        if self.__channel_handle == 0:
            raise RuntimeError("init failed")

    def __open_device(self):
        """
        描述：打开USB CAN设备，注意一个设备只能打开一次，测试前必须先调用该接口。

        :return: 返回值=1，表示操作成功；

                =0表示操作失败；
        """
        self.__device_handle = self.__lib_can.iTek_OpenDevice(self.__device_type, self.__device_index, RESERVED)
        if self.__device_handle == -1:
            raise RuntimeError("open device failed")

    def __package_can_data(self, message: Message) -> ITekCanFdTransmitData:
        data_length = len(message.data)
        frame = CanFdFrame()
        # 帧 ID，高 3 位属于标志位，低 29 位 ID 有效位
        frame.can_id = U32(message.msg_id)
        # 数据长度，当前 CAN(FD)帧实际数据长度； DLC
        frame.len = U8(self._dlc[data_length])
        # 错误帧标志位， 0=正常数据帧； 1=错误帧；当 flags=1 时，错误信息通过 CAN 帧数据位 data0-data7 表达，
        frame.flags = U8(0)
        # 保留位；
        frame.res = U8(0)
        # CAN 类型， 0 = CAN； 2 = CANFD； 3= CANFD 加速；
        if self.__is_fd:
            frame.cantype = U8(2)
        else:
            frame.cantype = U8(0)

        a_data = (U8 * data_length)()
        for j, value in enumerate(message.data):
            a_data[j] = U8(value)
        memmove(frame.data, a_data, data_length)

        transmit_data = ITekCanFdTransmitData()
        transmit_data.frame = frame
        transmit_data.send_type = U16(0)
        return transmit_data

    def open_device(self, baud_rate: BaudRateEnum = BaudRateEnum.HIGH, channel: int = 1):
        self.__open_device()
        self.__init_can(channel, baud_rate)
        self.__start_can()

    def close_device(self):
        if self._is_open:
            self.__lib_can.iTek_CloseDevice()
            self._is_open = False

    @check_connect("_is_open", can_tips)
    def read_board_info(self) -> ITekCanDeviceInfo:
        # EXTERNC bool __stdcall iTek_GetDeviceInfo(DEVICE_HANDLE usbhandle, iTek_CANFD_DEVICE_INFO*);
        info = ITekCanDeviceInfo()
        result = self.__lib_can.iTek_GetDeviceInfo(self.__channel_handle, byref(info))
        if result:
            return info
        else:
            raise RuntimeError("can not read board info")

    def reset_device(self):
        # EXTERNC bool __stdcall iTek_ResetCAN (CHANNEL_HANDLE usbhandle);
        result = self.__lib_can.iTek_ResetCAN(self.__channel_handle)
        if result:
            logger.info("reset device success")
        else:
            raise RuntimeError("reset device failed")

    @check_connect("_is_open", can_tips)
    def transmit(self, message: Message):
        # uint32_t iTek_Transmit (CHANNEL_HANDLE channel_handle, iTek_CANFD_Transmit_Data* data, uint32_t len);
        data = self.__package_can_data(message)
        self.__lib_can.iTek_Transmit(self.__channel_handle, byref(data), U32(message.frame_length))

    @check_connect("_is_open", can_tips)
    def receive(self) -> Tuple[int, Any]:
        # EXTERNC uint32_t __stdcall iTek_Receive(CHANNEL_HANDLE usbhandle, iTek_CANFD_Receive_Data*, uint32_t, int);
        # uint32_t iTek_Receive(CHANNEL_HANDLE channel_handle, iTek_CANFD_Data* pReceive, uint32_t len, int wait_time)
        # 函数阻塞等待时间，单位毫秒。当读到的数据数目<len时，等待wait_time毫秒后返回。 为-1则表示无超时，一直等待，直到读到数目=len时才返回。
        buffer_size = 2500
        p_receive = (ITekCanFdReceiveData * buffer_size)()
        count = self.__lib_can.iTek_Receive(self.__channel_handle, byref(p_receive), U32(buffer_size), U32(1))
        return count, p_receive
