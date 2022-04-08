# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        usb_relay.py
# @Author:      lizhe
# @Created:     2021/5/1 - 23:34
# --------------------------------------------------------
import sys
import os
import platform
from ctypes import c_char_p, c_int, byref, c_uint64, Structure, POINTER, CDLL
from functools import reduce
from typing import List

from ..common.constant import check_connect, relay_tips
from ..logger.logger import logger
from .serial_port import SerialPort
from .utils import Utils

# C:\Program Files (x86)\Microsoft Visual Studio 12.0\VC\bin\amd64> cl /LD needforspeed.c /o nfs.dll

usb_relay_device_type = {
    1: 'USB_RELAY_DEVICE_ONE_CHANNEL',
    2: 'USB_RELAY_DEVICE_TWO_CHANNEL',
    4: 'USB_RELAY_DEVICE_FOUR_CHANNEL',
    8: 'USB_RELAY_DEVICE_EIGHT_CHANNEL'
}


class UsbRelayDeviceInfo(Structure):
    pass


UsbRelayDeviceInfo._fields_ = [('serial_number', c_char_p),
                               ('device_path', c_char_p),
                               ('type', c_int),
                               ('next', POINTER(UsbRelayDeviceInfo))]


class _LibUsbRelay(object):
    def __init__(self):
        if platform.system() == "Windows":
            bit = platform.architecture()[0]
            if bit == '32bit':
                dll_path = os.sep.join(["usbrelay", "x86", "usb_relay_device.dll"])
                logger.info('Load usb_relay_device x86 DLL Library.')
            else:
                dll_path = os.sep.join(["usbrelay", "x64", "usb_relay_device.dll"])
                logger.info('Load Default usb_relay_device x64 DLL Library.')
            current_path = os.path.split(os.path.realpath(__file__))[0]
            file_path = os.sep.join([current_path, dll_path])
            logger.debug(f"use dll [{file_path}]")
        else:
            raise RuntimeError("only support windows and not support linux")
        try:
            self.usbRelayDll = CDLL(file_path)
        except Exception:
            raise RuntimeError(f"dll file[{file_path}] load failed, please sure if install Visual Studio")

    def usb_relay_init(self):
        """
            /*init the USB Relay Library
            @returns: This function returns 0 on success and -1 on error.
            */
            int EXPORT_API usb_relay_init(void);
        """
        self.usbRelayDll.usb_relay_init.restype = c_int
        try:
            return self.usbRelayDll.usb_relay_init()
        except Exception:
            error = sys.exc_info()
            logger.error('ERROR: ' + str(error[0]) + ' : ' + str(error[1]))
            raise RuntimeError(error[1])

    def usb_relay_exit(self):
        """
            /*Finalize the USB Relay Library.
            This function frees all of the static data associated with
            USB Relay Library. It should be called at the end of execution to avoid
            memory leaks.
            @returns:This function returns 0 on success and -1 on error.
            */
            int EXPORT_API usb_relay_exit(void);
        """
        self.usbRelayDll.usb_relay_exit.restype = c_int
        try:
            return self.usbRelayDll.usb_relay_exit()
        except Exception:
            error = sys.exc_info()
            logger.error('ERROR: ' + str(error[0]) + ' : ' + str(error[1]))
            raise RuntimeError(error[1])

    def usb_relay_device_enumerate(self):
        """
            /*Enumerate the USB Relay Devices.*/
            struct usb_relay_device_info EXPORT_API * usb_relay_device_enumerate(void);
        """
        device = []
        self.usbRelayDll.usb_relay_device_enumerate.argtypes = None
        self.usbRelayDll.usb_relay_device_enumerate.restype = POINTER(UsbRelayDeviceInfo)
        try:
            resp = self.usbRelayDll.usb_relay_device_enumerate()
            p = resp.contents
            while True:
                temp = dict()
                temp['serial_number'] = p.serial_number.decode('utf-8')
                temp['device_path'] = (p.device_path.decode('utf-8'))
                temp['type'] = p.type
                device.append(temp)
                if not p.next:
                    break
                else:
                    p = p.next.contents
            logger.info("usb device list: {}".format(device))
            return device
        except Exception:
            error = sys.exc_info()
            logger.error('ERROR: ' + str(error[0]) + ' : ' + str(error[1]))
            raise RuntimeError(error[1])

    def usb_relay_device_free_enumerate(self, serial_number: str, device_path: str, type_: int):
        """
            /*Free an enumeration Linked List*/
            void EXPORT_API usb_relay_device_free_enumerate(struct usb_relay_device_info*);
        """
        device_info = UsbRelayDeviceInfo()
        device_info.serial_number = serial_number.encode('utf-8')
        device_info.device_path = device_path.encode('utf-8')
        device_info.type = type_
        try:
            self.usbRelayDll.usb_relay_device_free_enumerate(byref(device_info))
        except Exception:
            error = sys.exc_info()
            logger.error('ERROR: ' + str(error[0]) + ' : ' + str(error[1]))
            raise RuntimeError(error[1])

    def usb_relay_device_open_with_serial_number(self, serial_number: str):
        """
            /*open device that serial number is serial_number*/
            /*@return: This function returns a valid handle to the device on success or NULL on failure.*/
            /*e.g: usb_relay_device_open_with_serial_number("abcde", 5")*/
            int EXPORT_API usb_relay_device_open_with_serial_number(const char *serial_number, unsigned len);
        """
        length = len(serial_number)
        self.usbRelayDll.usb_relay_device_open_with_serial_number.argtypes = [c_char_p, c_uint64]
        self.usbRelayDll.usb_relay_device_open_with_serial_number.restype = c_uint64
        serial_number_p = c_char_p(serial_number.encode('utf-8'))
        try:
            return self.usbRelayDll.usb_relay_device_open_with_serial_number(serial_number_p, length)
        except Exception:
            error = sys.exc_info()
            logger.error('ERROR: ' + str(error[0]) + ' : ' + str(error[1]))
            raise RuntimeError(error[1])

    def usb_relay_device_open(self, serial_number: str, device_path: str, type_: int):
        """
            /*open a usb relay device
            @return: This function returns a valid handle to the device on success or NULL on failure.
            */
            int EXPORT_API  usb_relay_device_open(struct usb_relay_device_info* device_info);
        """
        device_info = UsbRelayDeviceInfo()
        device_info.serial_number = serial_number.encode('utf-8')
        device_info.device_path = device_path.encode('utf-8')
        device_info.type = type_

        try:
            return self.usbRelayDll.usb_relay_device_open(byref(device_info))
        except Exception:
            error = sys.exc_info()
            logger.error('ERROR: ' + str(error[0]) + ' : ' + str(error[1]))
            raise RuntimeError(error[1])

    def usb_relay_device_close(self, h_handle: int):
        """
            /*close a usb relay device*/
            void EXPORT_API usb_relay_device_close(int h_handle);
        """
        self.usbRelayDll.usb_relay_device_close.argtypes = [c_uint64]
        try:
            self.usbRelayDll.usb_relay_device_close(h_handle)
        except Exception:
            error = sys.exc_info()
            logger.error('ERROR: ' + str(error[0]) + ' : ' + str(error[1]))
            raise RuntimeError(error[1])

    def usb_relay_device_open_one_relay_channel(self, h_handle: int, index: int):
        """
            /*open a relay channel on the USB-Relay-Device
            @:argument: index -- which channel your want to open
            h_handle -- which usb relay device your want to operate
            @returns: 0 -- success; 1 -- error; 2 -- index is outnumber the number of the usb relay device
            */
            int EXPORT_API usb_relay_device_open_one_relay_channel(int h_handle, int index);
        """
        self.usbRelayDll.usb_relay_device_open_one_relay_channel.argtypes = [c_uint64, c_uint64]
        try:
            return self.usbRelayDll.usb_relay_device_open_one_relay_channel(h_handle, index)
        except Exception:
            error = sys.exc_info()
            logger.error('ERROR: ' + str(error[0]) + ' : ' + str(error[1]))
            raise RuntimeError(error[1])

    def usb_relay_device_open_all_relay_channel(self, h_handle: int):
        """
            /*open all relay channel on the USB-Relay-Device
            @:argument: h_handle -- which usb relay device your want to operate
            @return: 0 -- success; 1 -- error
            */
            int EXPORT_API usb_relay_device_open_all_relay_channel(int h_handle);
        """
        self.usbRelayDll.usb_relay_device_open_all_relay_channel.argtypes = [c_uint64]
        try:
            return self.usbRelayDll.usb_relay_device_open_all_relay_channel(h_handle)
        except Exception:
            error = sys.exc_info()
            logger.error('ERROR: ' + str(error[0]) + ' : ' + str(error[1]))
            raise RuntimeError(error[1])

    def usb_relay_device_close_one_relay_channel(self, h_handle: int, index: int):
        """
            /*close a relay channel on the USB-Relay-Device
            @:argument: index -- which channel your want to close
            h_handle -- which usb relay device your want to operate
            @returns: 0 -- success; 1 -- error; 2 -- index is outnumber the number of the usb relay device
            */
            int EXPORT_API usb_relay_device_close_one_relay_channel(int h_handle, int index);
        """
        self.usbRelayDll.usb_relay_device_close_one_relay_channel.argtypes = [c_uint64, c_uint64]
        try:
            return self.usbRelayDll.usb_relay_device_close_one_relay_channel(h_handle, index)
        except Exception:
            error = sys.exc_info()
            logger.error('ERROR: ' + str(error[0]) + ' : ' + str(error[1]))
            raise RuntimeError(error[1])

    def usb_relay_device_close_all_relay_channel(self, h_handle: int):
        """
            /*close all relay channel on the USB-Relay-Device
            @:argument: h_handle -- which usb relay device your want to operate
            @returns: 0 -- success; 1 -- error
            */
            int EXPORT_API usb_relay_device_close_all_relay_channel(int h_handle);
        """
        self.usbRelayDll.usb_relay_device_close_all_relay_channel.argtypes = [c_uint64]
        try:
            return self.usbRelayDll.usb_relay_device_close_all_relay_channel(h_handle)
        except Exception:
            error = sys.exc_info()
            logger.error('ERROR: ' + str(error[0]) + ' : ' + str(error[1]))
            raise RuntimeError(error[1])

    def usb_relay_device_get_status(self, h_handle: int, status: int):
        """
            /*status bit: High --> Low 0000 0000 0000 0000 0000 0000 0000 0000, one bit indicate a relay status.
            the lowest bit 0 indicate relay one status, 1 -- means open status, 0 -- means closed status.
            bit 0/1/2/3/4/5/6/7/8 indicate relay 1/2/3/4/5/6/7/8 status
            @returns: 0 -- success; 1 -- error
            */
            int EXPORT_API usb_relay_device_get_status(int h_handle, unsigned int *status);
        """
        self.usbRelayDll.usb_relay_device_get_status.argtypes = [c_uint64, c_uint64]
        self.usbRelayDll.usb_relay_device_get_status(h_handle, status)


class USBRelay(object):
    """
    USB继电器基础类，利用ctypes操作dll文件

    使用方法：

    1、使用open_relay_device打开继电器，

    2、并根据通道使用one_relay_channel_on/off选择某一个通道进行开关操作，或者使用all_relay_channel_on/off进行全部的开关操作

    3、完成后调用close_relay_device关闭继电器

    特别注意：

    进行第二步即打开继电器的时候，需要一定的时间，建议的延时时间为1s，否则继电器可能没有实际打开
    """

    def __init__(self):
        self.__lib = _LibUsbRelay()
        self.__handle = None
        self.__is_open = False
        self.__channel_count = 0

    def open_relay_device(self):
        """
        初始化继电器，并通过继电器的serial号打开该继电器。
        在需要使用继电器时，必须先调用该接口。
        """
        if not self.__is_open:
            ret = self.__lib.usb_relay_init()
            logger.debug(f"ret = [{ret}]")
            if not ret:
                try:
                    dev = self.__lib.usb_relay_device_enumerate()
                    logger.debug(f"dev = [{dev}]")
                    if dev:
                        self.__channel_count = dev[0]["type"]
                        serial_number = dev[0]['serial_number']
                        self.__handle = self.__lib.usb_relay_device_open_with_serial_number(serial_number)
                        logger.debug(f"handler: {self.__handle}, type is {type(self.__handle)}")
                        self.__is_open = True
                except Exception:
                    raise RuntimeError("usb relay init failed")

    def close_relay_device(self):
        """
        关闭继电器，测试完毕调用该接口。
        """
        if self.__handle:
            self.__lib.usb_relay_device_close(self.__handle)
            exit_result = self.__lib.usb_relay_exit()
            if exit_result == 0:
                self.__is_open = False
            else:
                self.__is_open = True

    @check_connect("__is_open", relay_tips)
    def one_relay_channel_on(self, channel_index: int):
        """
        闭合继电器的某一个开关。

        :param channel_index: 继电器的开关编号。(从1开始)
        """
        if not self.__is_open:
            raise RuntimeError("please open relay device first")
        if not 1 <= channel_index <= self.__channel_count:
            raise RuntimeError(
                f"current relay device only support channel {self.__channel_count} but input {channel_index}")
        if self.__handle:
            if self.__lib.usb_relay_device_open_one_relay_channel(self.__handle, channel_index) != 0:
                raise RuntimeError(f"open channel [{channel_index}] failed")

    @check_connect("__is_open", relay_tips)
    def one_relay_channel_off(self, channel_index: int):
        """
        打开继电器的某一个开关。

        :param channel_index: 继电器的开关编号。(从1开始)
        """
        if not 1 <= channel_index <= self.__channel_count:
            raise RuntimeError(
                f"current relay device only support channel {self.__channel_count} but input {channel_index}")
        if self.__handle:
            if self.__lib.usb_relay_device_close_one_relay_channel(self.__handle, channel_index) != 0:
                raise RuntimeError(f"close channel [{channel_index}] failed")

    @check_connect("__is_open", relay_tips)
    def all_relay_channel_on(self):
        """
        闭合继电器的所有开关。
        """
        if self.__handle:
            if self.__lib.usb_relay_device_open_all_relay_channel(self.__handle) != 0:
                raise RuntimeError(f"open all channel failed")

    @check_connect("__is_open", relay_tips)
    def all_relay_channel_off(self):
        """
        关闭继电器的所有开关。
        """
        if self.__handle:
            if self.__lib.usb_relay_device_close_all_relay_channel(self.__handle) != 0:
                raise RuntimeError(f"close all channel failed")


class SerialRelay(object):
    """
    串口命令式的继电器
    吸合（通）的设置， 根据通道计算，首先是01代表 通道， 最后一位是计算出来的校验值，所有的值相加的结果
    RELAY_01_SUCTION = "55 01 32 00 00 00 01 89"
    断开的设置
    RELAY_01_OPEN = "55 01 31 00 00 00 01 88"
    """

    def __init__(self, port: str, baud_rate: int = 9600, max_channel: int = 32):
        self.__utils = SerialPort()
        self.__port = port
        self.__baud_rate = baud_rate
        self.__max_channel = max_channel

    def __channel_calc(self, channel_index: int, type_: bool = False) -> List[int]:
        """
        :param channel_index:
        :param type_: 真表示接通，值为32， 假表示断开， 值为31
        :return:
        """
        if channel_index < 0 or channel_index > self.__max_channel:
            raise RuntimeError(f"{channel_index} only support [0, {self.__max_channel}]")
        status_value = 0x32 if type_ else 0x31
        command_list = [0x55, 0x01, status_value, 0x00, 0x00, 0x00, channel_index]
        value = reduce(lambda x, y: x + y, command_list)
        command_list.append(value)
        return command_list

    def __send_command(self, command_list: List[int]):
        """
        TODO 需要吹转换错误
        :param command_list:
        :return:
        """
        commands = Utils.to_hex_list(command_list)
        command_line = " ".join(commands)
        logger.debug(f"command_line is {command_line}")
        command = bytes.fromhex(command_line)
        self.__utils.send(command, False)

    def open_relay_device(self):
        self.__utils.connect(self.__port, self.__baud_rate)

    def close_relay_device(self):
        self.__utils.disconnect()

    def one_relay_channel_on(self, channel_index: int):
        command_list = self.__channel_calc(channel_index, True)
        self.__send_command(command_list)

    def one_relay_channel_off(self, channel_index: int):
        command_list = self.__channel_calc(channel_index, False)
        self.__send_command(command_list)

    def all_relay_channel_on(self):
        command_list = [0x55, 0x01, 0x33, 0xff, 0xff, 0xff, 0xff, 0x85]
        self.__send_command(command_list)

    def all_relay_channel_off(self):
        command_list = [0x55, 0x01, 0x33, 0x00, 0x00, 0x00, 0x00, 0x89]
        self.__send_command(command_list)
