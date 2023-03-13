#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/3/2 9:49
# @Author  : zhangvv
# @File    : uds_common.py
# @Software: PyCharm
# @Desc    :
from typing import Union
from ctypes import WinDLL
from automotive import SerialUtils, logger, CanBoxDeviceEnum, BaudRateEnum
from automotive.core.can.can_service import Can
from time import sleep


class UdsCommon(object):

    def __init__(self,
                 request_id: int,
                 response_id: int,
                 funciton_id: int,
                 dll_file: str,
                 can_box_device: Union[CanBoxDeviceEnum, str, None] = None,
                 can_fd: bool = False,
                 is_uds_can_fd: bool = False):

        # self.__dll = WinDLL(dll_file)
        self.can = Can(can_box_device=can_box_device,
                       can_fd=can_fd,
                       is_uds_can_fd=is_uds_can_fd)

        self.can.init_uds(request_id=request_id, response_id=response_id, function_id=funciton_id)
        self.can.open_can()
        self.__dll = WinDLL(dll_file)

    def read_fd_22(self, did: str):
        """
        例如 DID = FD01
        :param did:
        :return:
        """
        did_0, did_1 = self.solve_did(did=did)
        data_22 = [0x22, did_0, did_1]
        response_22 = self.can.send_and_receive_uds_message(message=data_22)
        logger.debug(f'22响应值： {list(response_22)}')
        configures_str = ''.join(list(map(lambda x: f"{hex(x)[2:].zfill(2)}", list(response_22)[3:])))
        return configures_str

    def expand_dialog_10(self):
        message_10 = [0x10, 0x3]
        session_response_data = self.can.send_and_receive_uds_message(message=message_10)
        return session_response_data

    def security_access_0x27(self):
        message_2701 = [0x27, 0x1]
        security_01_response_data = self.can.send_and_receive_uds_message(message=message_2701)
        sleep(0.2)

        data = list(security_01_response_data)
        logger.debug(f"2701响应值： {data}")
        seed_data = data[3:7]
        logger.debug(f"seed_data： {seed_data}")
        # 将4个字节的种子转化成16进制数
        seed = (seed_data[0] << 24) + (seed_data[1] << 16) + (seed_data[2] << 8) + seed_data[3]
        # print(seed)
        # ctypes调用方法
        key = self.__dll.SecM_ComputeKey(seed) & 0xffffffff
        logger.debug(f"算出的key {key}")

        key_list = list(key.to_bytes(4, byteorder="big"))
        messgae_2702 = [0x27, 0x2, key_list[0], key_list[1], key_list[2], key_list[3]]
        security_02_response_data = self.can.send_and_receive_uds_message(message=messgae_2702)
        sleep(0.2)

    def write_data_by_identifier_0x2e(self, data: str, did: str):
        """
        2e写配置字
        :param data:
        :param did:
        :return:
        """
        data = int(data, 16).to_bytes(64, "big")
        did_0, did_1 = self.solve_did(did)
        write_message = [0x2E, did_0, did_1] + list(data)
        # back_write_message = copy.deepcopy(write_message)
        logger.info("即将写入数据")
        write_respond_data = self.can.send_and_receive_uds_message(message=write_message)
        return write_respond_data

    def write_config(self, data: str, did: str):
        #  发1003扩展会话
        self.expand_dialog_10()
        #  发2701 2702安全会话
        self.security_access_0x27()
        sleep(1)
        # 发2e写服务
        response_data_2e = self.write_data_by_identifier_0x2e(data=data, did=did)
        return response_data_2e

    def reset_11(self):
        data_11 = [0x11, 0x01]
        session_response_data = self.can.send_and_receive_uds_message(message=data_11)

    def state_3e(self):
        # 7DF发 02 3E 80
        data_80 = [0x3e, 0x80]
        session_response_data_3e = self.can.send_and_receive_uds_message(message=data_80)

    @staticmethod
    def solve_did(did: str):
        # 处理FD01，拆成2个数据
        did_0 = eval(f"0x{did[:2]}")
        did_1 = eval(f"0x{did[-2:]}")
        return did_0, did_1

    def close_can(self):
        self.can.close_can()

