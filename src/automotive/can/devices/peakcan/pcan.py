# -*- coding:utf-8 -*-
# --------------------------------------------------------------------------
#  Copyright (C), 2016-2020, China TSP, All rights reserved
# --------------------------------------------------------------------------
# Name:        pcan.py
# Purpose:     用于提供pcan的操作类
# Author:      baiwanhong
# Created:     2019-05-05
# --------------------------------------------------------------------------

# ===============================================================================
# 导入所需模块
from inspect import stack
from ctypes import memmove, c_uint

from loguru import logger
from . import pcanbasic

baud_rate_list = {
    #   波特率
    '5Kbps': pcanbasic.PCAN_BAUD_5K,
    '10Kbps': pcanbasic.PCAN_BAUD_10K,
    '20Kbps': pcanbasic.PCAN_BAUD_20K,
    '33Kbps': pcanbasic.PCAN_BAUD_33K,
    '47Kbps': pcanbasic.PCAN_BAUD_47K,
    '50Kbps': pcanbasic.PCAN_BAUD_50K,
    '83Kbps': pcanbasic.PCAN_BAUD_83K,
    '95Kbps': pcanbasic.PCAN_BAUD_95K,
    '100Kbps': pcanbasic.PCAN_BAUD_100K,
    '125Kbps': pcanbasic.PCAN_BAUD_125K,
    '250Kbps': pcanbasic.PCAN_BAUD_250K,
    '500Kbps': pcanbasic.PCAN_BAUD_500K,
    '800Kbps': pcanbasic.PCAN_BAUD_800K,
    '1000Kbps': pcanbasic.PCAN_BAUD_1M
}

hw_types = {'ISA-82C200': pcanbasic.PCAN_TYPE_ISA,
            'ISA-SJA1000': pcanbasic.PCAN_TYPE_ISA_SJA,
            'ISA-PHYTEC': pcanbasic.PCAN_TYPE_ISA_PHYTEC,
            'DNG-82C200': pcanbasic.PCAN_TYPE_DNG,
            'DNG-82C200 EPP': pcanbasic.PCAN_TYPE_DNG_EPP,
            'DNG-SJA1000': pcanbasic.PCAN_TYPE_DNG_SJA,
            'DNG-SJA1000 EPP': pcanbasic.PCAN_TYPE_DNG_SJA_EPP}

io_ports = {'0100': 0x100, '0120': 0x120, '0140': 0x140, '0200': 0x200, '0220': 0x220, '0240': 0x240,
            '0260': 0x260, '0278': 0x278, '0280': 0x280, '02A0': 0x2A0, '02C0': 0x2C0, '02E0': 0x2E0,
            '02E8': 0x2E8, '02F8': 0x2F8, '0300': 0x300, '0320': 0x320, '0340': 0x340, '0360': 0x360,
            '0378': 0x378, '0380': 0x380, '03BC': 0x3BC, '03E0': 0x3E0, '03E8': 0x3E8, '03F8': 0x3F8}

interrupts = {'3': 3, '4': 4, '5': 5, '7': 7, '9': 9, '10': 10, '11': 11, '12': 12, '15': 15}


# ===============================================================================
# 封装PCANBasic的接口
class PCan(object):
    def __init__(self):
        """
        """
        self.__can_basic = pcanbasic.PCANBasic()
        self.__channel = pcanbasic.PCAN_USBBUS1
        self.is_open = False

    def __check_open(self):
        """
        检查PCAN是否处于打开状态，未打开的时候抛出RuntimeError
        """
        if not self.is_open:
            raise RuntimeError("please open device first")

    def __init_device(self, baud_rate: str, channel: int = None):
        """
        Initializes a PEAK CAN Channel

        :param baud_rate: 波特率

        :param channel: A TPCANHandle representing a PEAK CAN Channel
        """
        channel = self.__channel if channel else pcanbasic.PCAN_USBBUS1
        btr0btr1 = baud_rate_list[baud_rate]
        # TIPS: 目前只支持IPEH-002021 这个型号，该型号不支持CAN FD
        hw_type = hw_types['ISA-82C200']
        io_port = io_ports['0100']
        interrupt = interrupts['11']

        if not self.is_open:
            ret = self.__can_basic.initialize(channel, btr0btr1, hw_type, io_port, interrupt)
            if ret == 0:
                self.is_open = True
            else:
                logger.error(f"Method <{stack()[0][3]}> Init PEAK CAN channel_{hex(channel.value)} Failed.")
                self.is_open = False

    @staticmethod
    def __data_package(frame_length: int, message_id: int, send_type: int, data_length: int, data: list):
        """
        组包CAN发送数据，供VCI_Transmit函数使用。

        :param frame_length: 帧长度

        :param message_id:  11/29-bit message identifier

        :param send_type: Type of the message

        :param data_length: Data Length Code of the message (0..8)

        :param data: Data of the message (DATA[0]..DATA[7])

        :return: 返回组包的帧数据。
        """
        send_data = (pcanbasic.TPCANMsg * frame_length)()

        for i in range(frame_length):
            # 帧ID。32位变量，数据格式为靠右对齐
            send_data[i].id = c_uint(message_id)

            # 发送帧类型。=0时为正常发送（发送失败会自动重发，重发最长时间为1.5-3秒）；
            # =1时为单次发送（只发送一次，不自动重发）；
            # 其它值无效。（二次开发，建议SendType=1，提高发送的响应速度）
            send_data[i].msg_type = pcanbasic.TPCANMessageType(send_type)

            # 数据长度 DLC (<=8)，即CAN帧Data有几个字节。约束了后面Data[8]中的有效字节
            send_data[i].len = data_length

            # CAN帧的数据
            a_data = (pcanbasic.TPCANMessageType * 8)()
            for j, value in enumerate(data):
                a_data[j] = pcanbasic.TPCANMessageType(value)
            memmove(send_data[i].data, a_data, 8)
        return send_data

    @staticmethod
    def __data_package_fd(frame_length: int, message_id: int, send_type: int, data_length: int, data: list):
        """
        组包CAN发送数据，供VCI_Transmit函数使用。

        :param frame_length: 帧长度

        :param message_id:  11/29-bit message identifier

        :param send_type: Type of the message

        :param data_length: Data Length Code of the message (0..8)

        :param data: Data of the message (DATA[0]..DATA[7])

        :return: 返回组包的帧数据。
        """
        send_data = (pcanbasic.TPCANMsgFD * frame_length)()

        for i in range(frame_length):
            # 帧ID。32位变量，数据格式为靠右对齐
            send_data[i].ID = c_uint(message_id)

            # 发送帧类型。=0时为正常发送（发送失败会自动重发，重发最长时间为1.5-3秒）；
            # =1时为单次发送（只发送一次，不自动重发）；
            # 其它值无效。（二次开发，建议SendType=1，提高发送的响应速度）
            send_data[i].MSGTYPE = pcanbasic.TPCANMessageType(send_type)

            # 数据长度 DLC (<=8)，即CAN帧Data有几个字节。约束了后面Data[8]中的有效字节
            send_data[i].DLC = data_length

            # CAN帧的数据
            a_data = (pcanbasic.TPCANMessageType * 8)()
            for j, value in enumerate(data):
                a_data[j] = pcanbasic.TPCANMessageType(value)
            memmove(send_data[i].DATA, a_data, 8)
        return send_data

    def open_device(self, speed: bool = True, channel: int = None):
        """
        打开Pcan设备

        :param speed:
            True: 高速CAN

            False： 低速CAN

        :param channel:
            A TPCANHandle representing a PEAK CAN Channel

        :return: A TPCANStatus error code
        """
        baud_rate = "500Kbps" if speed else '125Kbps'
        logger.info(f"baud_rate is {baud_rate}")
        self.__init_device(baud_rate, channel)

    def close_device(self, channel: int = None):
        """
        Un_initializes one or all PEAK CAN Channels initialized by CAN_Initialize。

        :param channel: A TPCANHandle representing a PEAK CAN Channel

        :return: A TPCANStatus error code
        """
        channel = self.__channel if channel else pcanbasic.PCAN_USBBUS1
        if self.is_open:
            ret = self.__can_basic.uninitialize(channel)
            if ret == pcanbasic.PCAN_ERROR_OK:
                self.is_open = False
            else:
                logger.error(f"Method <{stack()[0][3]}> Close PEAK CAN Failed.")

    def read_board_info(self, channel: int = None) -> bool:
        """
        Gets the current status of a PEAK CAN Channel

        :param channel: A TPCANHandle representing a PEAK CAN Channel

        :return: A TPCANStatus error code

            PCAN_ERROR_OK = TPCANStatus(0x00000)

            PCAN_ERROR_XMTFULL = TPCANStatus(0x00001)

            PCAN_ERROR_OVERRUN = TPCANStatus(0x00002

            PCAN_ERROR_BUSLIGHT = TPCANStatus(0x00004)

            PCAN_ERROR_BUSHEAVY = TPCANStatus(0x00008)

            PCAN_ERROR_BUSOFF = TPCANStatus(0x00010)

            PCAN_ERROR_ANYBUSERR = TPCANStatus(PCAN_ERROR_BUSLIGHT | PCAN_ERROR_BUSHEAVY | PCAN_ERROR_BUSOFF)

            PCAN_ERROR_QRCVEMPTY = TPCANStatus(0x00020)

            PCAN_ERROR_QOVERRUN = TPCANStatus(0x00040)

            PCAN_ERROR_QXMTFULL = TPCANStatus(0x00080)

            PCAN_ERROR_REGTEST = TPCANStatus(0x00100)

            PCAN_ERROR_NODRIVER = TPCANStatus(0x00200)

            PCAN_ERROR_HWINUSE = TPCANStatus(0x00400)

            PCAN_ERROR_NETINUSE = TPCANStatus(0x00800)

            PCAN_ERROR_ILLHW = TPCANStatus(0x01400)

            PCAN_ERROR_ILLNET = TPCANStatus(0x01800)

            PCAN_ERROR_ILLCLIENT = TPCANStatus(0x01C00)

            PCAN_ERROR_ILLHANDLE = TPCANStatus(PCAN_ERROR_ILLHW | PCAN_ERROR_ILLNET | PCAN_ERROR_ILLCLIENT)

            PCAN_ERROR_RESOURCE = TPCANStatus(0x02000)

            PCAN_ERROR_ILLPARAMTYPE = TPCANStatus(0x04000)

            PCAN_ERROR_ILLPARAMVAL = TPCANStatus(0x08000)

            PCAN_ERROR_UNKNOWN = TPCANStatus(0x10000)

            PCAN_ERROR_ILLDATA = TPCANStatus(0x20000)

            PCAN_ERROR_INITIALIZE = TPCANStatus(0x40000)
        """
        channel = self.__channel if channel else pcanbasic.PCAN_USBBUS1
        self.__check_open()
        return self.__can_basic.get_status(channel) == pcanbasic.PCAN_ERROR_OK

    def reset_device(self, channel: int = None):
        """
        Resets the receive and transmit queues of the PEAK CAN Channel

        :param channel: A TPCANHandle representing a PEAK CAN Channel
        """
        channel = self.__channel if channel else pcanbasic.PCAN_USBBUS1
        ret = self.__can_basic.reset(channel)
        if ret != pcanbasic.PCAN_ERROR_OK:
            raise RuntimeError(f"Method <{stack()[0][3]}> Reset PEAK CAN Failed.")

    def transmit(self, frame_length: int, message_id: int, send_type: int,
                 data_length: int, data: list, channel: int = None):
        """
        Transmits a CAN message。

        :param frame_length: 帧长度

        :param message_id: 11/29-bit message identifier

        :param send_type: Type of the message

        :param data_length: Data Length Code of the message (0..8)

        :param data: Data of the message (DATA[0]..DATA[7])

        :param channel:  A TPCANHandle representing a PEAK CAN Channel
        """
        channel = self.__channel if channel else pcanbasic.PCAN_USBBUS1
        p_send = self.__data_package(frame_length, message_id, send_type, data_length, data)
        try:
            ret = self.__can_basic.write(channel, p_send)
            if ret == pcanbasic.PCAN_ERROR_OK:
                logger.debug(f"PEAK CAN channel_{hex(channel.value)} Transmit Success.")
            else:
                raise RuntimeError(f"PEAK CAN channel_{hex(channel.value)} Transmit Failed.")
        except Exception:
            raise RuntimeError('PEAK CAN transmit failed.')

    def transmit_fd(self, frame_length: int, message_id: int, send_type: int,
                    data_length: int, data: list, channel: int = None):
        """
        Transmits a CAN message。

        :param frame_length: 帧长度

        :param message_id: 11/29-bit message identifier

        :param send_type: Type of the message

        :param data_length: Data Length Code of the message (0..8)

        :param data: Data of the message (DATA[0]..DATA[7])

        :param channel:  A TPCANHandle representing a PEAK CAN Channel
        """
        channel = self.__channel if channel else pcanbasic.PCAN_USBBUS1
        p_send = self.__data_package_fd(frame_length, message_id, send_type, data_length, data)
        try:
            ret = self.__can_basic.write_fd(channel, p_send)
            if ret == pcanbasic.PCAN_ERROR_OK:
                logger.debug(f"PEAK CAN channel_{hex(channel.value)} Transmit Success.")
            else:
                raise RuntimeError(f"PEAK CAN channel_{hex(channel.value)} Transmit Failed.")
        except Exception:
            raise RuntimeError('PEAK CAN transmit failed.')

    def receive(self, channel: int = None) -> tuple:
        """
        Reads a CAN message from the receive queue of a PEAK CAN Channel

        :param channel: A TPCANHandle representing a PEAK CAN Channel

        :return: ret, msg, timestamp
        """
        channel = self.__channel if channel else pcanbasic.PCAN_USBBUS1
        try:
            ret, message, timestamp = self.__can_basic.read(channel)
            if ret == pcanbasic.PCAN_ERROR_OK:
                logger.debug(f"PEAK CAN channel_{hex(channel.value)} Receive Success.")
                return message, timestamp
            else:
                raise RuntimeError(f"Method <{stack()[0][3]}> PEAK CAN Receive Failed.")
        except Exception:
            raise RuntimeError('PEAK CAN receive failed.')

    def receive_fd(self, channel: int = None) -> tuple:
        """
        Reads a CAN message from the receive queue of a PEAK CAN Channel

        :param channel: A TPCANHandle representing a PEAK CAN Channel

        :return: ret, msg, timestamp
        """
        channel = self.__channel if channel else pcanbasic.PCAN_USBBUS1
        try:
            ret, message, timestamp = self.__can_basic.read_fd(channel)
            if ret == pcanbasic.PCAN_ERROR_OK:
                logger.debug(f"PEAK CAN channel_{hex(channel.value)} Receive Success.")
                return message, timestamp
            else:
                raise RuntimeError(f"Method <{stack()[0][3]}> PEAK CAN Receive Failed.")
        except Exception:
            raise RuntimeError('PEAK CAN receive failed.')
