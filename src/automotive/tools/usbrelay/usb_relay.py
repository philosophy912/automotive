# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, China TSP, All rights reserved
# --------------------------------------------------------
# @Name:        USBRelay
# @Purpose:     继电器相关操作
# @Author:      baiwanhong
# @Created:     2018-12-29
# --------------------------------------------------------
import sys
import os
import platform
from ctypes import c_char_p, c_int, CDLL, byref, c_uint64, Structure, POINTER

from loguru import logger

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


class USBRelay(object):
    """
    USB继电器基础类，利用ctypes操作dll文件
    """
    def __init__(self):
        self.__lib = _LibUsbRelay()
        self.__handle = None
        self.is_open = False
        self.__channel_count = 0

    def open_relay_device(self):
        """
        初始化继电器，并通过继电器的serial号打开该继电器。
        在需要使用继电器时，必须先调用该接口。
        """
        if not self.is_open:
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
                        self.is_open = True
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
                self.is_open = False
            else:
                self.is_open = True

    def one_relay_channel_on(self, channel_index: int):
        """
        闭合继电器的某一个开关。

        :param channel_index: 继电器的开关编号。(从1开始)
        """
        if not self.is_open:
            raise RuntimeError("please open relay device first")
        if not 1 <= channel_index <= self.__channel_count:
            raise RuntimeError(
                f"current relay device only support channel {self.__channel_count} but input {channel_index}")
        if self.__handle:
            if self.__lib.usb_relay_device_open_one_relay_channel(self.__handle, channel_index) != 0:
                raise RuntimeError(f"open channel [{channel_index}] failed")

    def one_relay_channel_off(self, channel_index: int):
        """
        打开继电器的某一个开关。

        :param channel_index: 继电器的开关编号。(从1开始)
        """
        if not self.is_open:
            raise RuntimeError("please open relay device first")
        if not 1 <= channel_index <= self.__channel_count:
            raise RuntimeError(
                f"current relay device only support channel {self.__channel_count} but input {channel_index}")
        if self.__handle:
            if self.__lib.usb_relay_device_close_one_relay_channel(self.__handle, channel_index) != 0:
                raise RuntimeError(f"close channel [{channel_index}] failed")

    def all_relay_channel_on(self):
        """
        闭合继电器的所有开关。
        """
        if not self.is_open:
            raise RuntimeError("please open relay device first")
        if self.__handle:
            if self.__lib.usb_relay_device_open_all_relay_channel(self.__handle) != 0:
                raise RuntimeError(f"open all channel failed")

    def all_relay_channel_off(self):
        """
        关闭继电器的所有开关。
        """
        if not self.is_open:
            raise RuntimeError("please open relay device first")
        if self.__handle:
            if self.__lib.usb_relay_device_close_all_relay_channel(self.__handle) != 0:
                raise RuntimeError(f"close all channel failed")


class _LibUsbRelay(object):
    def __init__(self):
        bit = platform.architecture()[0]
        if bit == '32bit':
            dll_path = '/x86/usb_relay_device.dll'
            logger.info('Load usb_relay_device x86 DLL Library.')
        else:
            dll_path = '/x64/usb_relay_device.dll'
            logger.info('Load Default usb_relay_device x64 DLL Library.')
        current_path = os.path.split(os.path.realpath(__file__))[0]
        file_path = current_path + dll_path
        logger.debug(f"use dll [{file_path}]")
        try:
            self.usbRelayDll = CDLL(file_path)
        except Exception:
            raise RuntimeError(f"dll file[{file_path}] load failed ")

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
        serial_number = c_char_p(serial_number.encode('utf-8'))
        try:
            return self.usbRelayDll.usb_relay_device_open_with_serial_number(serial_number, length)
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
