# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2021, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        itekbasic.py
# @Author:      lizhe
# @Created:     2021/10/28 - 22:01
# --------------------------------------------------------
from ctypes import c_uint32, Structure, c_uint8, c_uint16, c_int, c_uint64, c_uint, c_int8, c_int16, c_int32, c_int64, \
    c_wchar, c_byte, c_double, c_char_p

U = c_uint
S = c_int
U8 = c_uint8
S8 = c_int8
U16 = c_uint16
S16 = c_int16
U32 = c_uint32
S32 = c_int32
U64 = c_uint64
S64 = c_int64
WCHAR = c_wchar
BYTE = c_byte
DOUBLE = c_double
CHAR_P = c_char_p

A_BAUD_RATE = {
    5: U32(0x01F31302),
    10: U32(0x00F91302),
    20: U32(0x007C1302),
    40: U32(0x00630a02),
    50: U32(0x00311302),
    80: U32(0x001D1204),
    100: U32(0x00181302),
    125: U32(0x00131302),
    200: U32(0x00130A02),
    250: U32(0x00091302),
    400: U32(0x00090A02),
    500: U32(0x00070A02),
    800: U32(0x00021006),
    1000: U32(0x00040702)
}
D_BAUD_RATE = {
    100: U32(0x001D0E30),
    125: U32(0x001F0A20),
    200: U32(0x00130A20),
    250: U32(0x000F0A20),
    400: U32(0x00090A20),
    500: U32(0x00070A20),
    800: U32(0x00040A20),
    1000: U32(0x00040720),
    2000: U32(0x00010A20),
    3000: U32(0x00000D40),
    4000: U32(0x00000A20),
    5000: U32(0x00000720)
}

USBCANFD_X100 = U16(1)
USBCANFD_X200 = U16(2)
NETCANFD_L100 = U16(3)
NETCANFD_L200 = U16(4)

DEVICE_INDEX1 = U16(0)
DEVICE_INDEX2 = U16(1)

CHANNEL = {
    1: U8(0),
    2: U8(1)
}

RESERVED = U32(0)


# <iTek_CANFD_DEVICE_INFO 结构体>
class ITekCanDeviceInfo(Structure):
    _fields_ = [
        # 硬件版本，如 hw_Version={0x01, 0x00, 0x02}，代表 V1.0.2；
        ('hw_Version', c_uint8 * 3),
        # 固件版本，如 fw_Version={0x01, 0x00, 0x03}，代表 V1.0.3；
        ('fw_Version', c_uint8 * 3),
        # 暂不开放
        ('product_Version', c_uint8 * 3),
        # 表示有几路CAN通道。
        ('can_Num', c_uint8),
        # 出厂序列号，以‘\0’结束，如“6120101001” ；
        ('str_Serial_Num', c_uint8 * 20),
        # 出厂序列号，以‘\0’结束，如“6120101001” ；
        ('str_hw_Type', c_uint8 * 40),
        # 系统保留。
        ('reserved', c_uint16)
    ]


# 过滤器组结构体，由帧类型、过滤方式和 ID 寄存器组成。
class FilterData(Structure):
    _fields_ = [
        # 过滤器组结构体，由帧类型、过滤方式和 ID 寄存器组成。
        ("frameType", c_uint8),
        # 过滤器类型，用于说明本组过滤器组的过滤方式； 0=范围 id； 1=明确 id； 2=掩码 id；不同方式的过滤结果见表 3-3；
        ("filterType", c_uint8),
        # ID 寄存器 1；
        ("ID1", c_uint32),
        # ID 寄存器 2；
        ("ID2", c_uint32),
    ]


# 扩展帧过滤器组结构体， 过滤器组数量根据实际使用情况自定义
class FilterDataExtend(Structure):
    _fields_ = [
        # 实际使用扩展帧过滤器组数量，取值范围 0-64，比如： num=2，代表前 2 组有效；
        ("num", c_int),
        # 扩展帧过滤器组寄存器结构体；
        ("FilterDatafilterDataExtends", FilterData * 64)
    ]


# 标准帧过滤器组结构体， 过滤器组数量根据实际使用情况自定义。
class FilterDataStandard(Structure):
    _fields_ = [
        # 实际使用标准帧过滤器组数量，取值范围 0-128，比如： num=5，代表前 5 组有效；
        ("num", c_int),
        # 标准帧过滤器组寄存器结构体；
        ("FilterDatafilterDataStandard", FilterData * 128)
    ]


# <iTek_CANFD_CHANNEL_INIT_CONFIG 结构体>
class ITekCanFdChannelInitConfig(Structure):
    _fields_ = [
        # CAN 协议类型： 0=CAN 协议； 1=CANFD 协议；
        ("can_type", c_uint8),
        # CANFD 标准： 0=ISO 标准； 1=非 ISO 标准；
        ("CANFDStandard", c_uint8),
        # CANFD 是否加速： 0=不加速； 1=加速；
        ("CANFDSpeedup", c_uint8),
        # 仲裁波特率（见表 3-1）；
        ("abit_timing", c_uint32),
        # 数据波特率（见表 3-2）；
        ("dbit_timing", c_uint32),
        # 工作模式， 0=正常工作模式； 1=只听工作模式；
        ("workMode", c_uint8),
        # 保留位
        ("res", c_uint32),
        # 扩展帧过滤器组（见 3.3 节）；
        ("Extend", FilterDataExtend),
        # 标准帧过滤器组（见 3.4 节）；
        ("Standard", FilterDataStandard)
    ]


# CAN(FD)帧信息结构体，包含帧 id、帧格式、帧类型、帧数据等。
class CanFdFrame(Structure):
    _fields_ = [
        # 帧 ID，高 3 位属于标志位，低 29 位 ID 有效位，标志位含义见表 3-4；
        ("can_id", c_uint32),
        # 数据长度，当前 CAN(FD)帧实际数据长度；
        ("len", c_uint8),
        # 错误帧标志位， 0=正常数据帧； 1=错误帧；当 flags=1 时，错误信息通过 CAN 帧数据位 data0-data7 表达，具体定义见表 3-5；
        ("flags", c_uint8),
        # 保留位；
        ("res", c_uint8),
        # CAN 类型， 0 = CAN； 2 = CANFD； 3= CANFD 加速；
        ("cantype", c_uint8),
        # 数据， CAN 帧 data<=8， CANFD 帧<=64;
        ("data", c_uint8 * 64),
    ]


# 接收 CAN(FD)报文信息结构体，包含 CAN 控制器硬件时间戳、 CAN(FD)数据帧等。
class ITekCanFdReceiveData(Structure):
    _fields_ = [
        # CAN(FD)报文信息(见 canfd_frame 结构体定义)；
        ("frame", CanFdFrame),
        # CAN 时间戳，从 CAN 控制器上电开始计时，长度 64 位，单位 us（接收帧有效）；
        ("timestamp", c_uint64)
    ]


# 发送 CAN(FD)报文信息结构体，包含发送类型和 CAN(FD)帧结构。
class ITekCanFdTransmitData(Structure):
    _fields_ = [
        # CAN(FD)报文信息(见 canfd_frame 结构体定义)；
        ("frame", CanFdFrame),
        # 发送方式： 0 = 正常发送； 1 = 自发自收；
        ("send_type", c_uint16)
    ]


# 自动发送报文结构体， 包含自动发送报文的使能位、 索引号、 定时间隔及 CAN(FD)报文参数信息。
class ITekAutoTransmit(Structure):
    _fields_ = [
        # 本条报文使能位， 0 = 不发送本条报文； 1 = 发送本条报文；
        ("enable", c_uint8),
        # 报文索引号，取值范围 0-127；
        ("index", c_uint16),
        # 时间间隔，单位 ms；
        ("interval", c_uint32),
        # CAN(FD)报文结构体信息，见 canfd_frame 结构体定义。
        ("frame", CanFdFrame)
    ]


# IP 信息结构体，包含本机 IP 地址、端口及目标设备 IP 地址、端口信息，适用于 NETCANFD 产品。
class IPInfo(Structure):
    _fields_ = [
        # 本机 TCP 工作模式， 1 = UDP； 2 = TCP Server； 3 = TCP Client；
        ("tcp_mod", c_uint8),
        # 本机 IP 地址（暂不使用）；
        ("local_ip", c_uint8 * 25),
        # 本机端口， TCP Server 模式及 UDP 模式有效；
        ("local_port", c_uint16),
        # 目标设备 IP 地址， 如：“192.168.0.100”，‘\0’ 结束， TCP Client 及 UDP 模式有效；
        ("dest_ip", c_uint8 * 25),
        # 目标设备端口，如： 4000， TCP Client 模式及 UDP 模式有效。
        ("dest_port", c_uint16),
    ]
