# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2021, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        enums.py
# @Author:      lizhe
# @Created:     2021/11/18 - 22:07
# --------------------------------------------------------
from enum import Enum, unique


@unique
class BaudRateEnum(Enum):
    """
    CAN传输速率

    目前支持HIGH、LOW
    """
    # 高速CAN
    HIGH = 500
    # 低速CAN
    LOW = 125
    # 数据仲裁速率
    DATA = 2000


@unique
class CanBoxDeviceEnum(Enum):
    """
    CAN盒子的类型，目前支持

    PEAKCAN、USBCAN、CANALYST
    """
    # PCAN
    PEAKCAN = "PEAKCAN"
    # USB CAN
    USBCAN = "USBCAN"
    # CAN分析仪
    CANALYST = "CANALYST"
    # 同星
    TSMASTER = "TSMASTER"
    # 爱泰 CAN FD
    # ITEK = "ITEK"

    # CAN LIN Analyser
    # ANALYSER = "ANALYSER"

    @staticmethod
    def from_name(type_: str):
        for key, item in CanBoxDeviceEnum.__members__.items():
            if type_ == item.value.upper():
                return item
        raise ValueError(f"{type_} can not be found in CanBoxDeviceEnum")


@unique
class TraceTypeEnum(Enum):
    """
    枚举类：

        PCAN: PCAN录制的CAN log

        USB_CAN: USB CAN录制的CAN log

        SPY3_CSV: SPY3录制的CAN log(CSV类型)

        SPY3_ASC: SPY3录制的CAN log(ASC类型)

        CANOE_ASC: CANoe录制的CAN log(ASC类型)
    """
    PCAN = "pcan_reader", "PCanReader"
    USB_CAN = "usb_can_reader", "UsbCanReader"
    SPY3_CSV = "vspy_csv_reader", "VspyCsvReader"
    SPY3_ASC = "vspy_ase_reader", "VspyAseReader"
    CANOE_ASC = "canoe_asc_reader", "CanoeAscReader"
