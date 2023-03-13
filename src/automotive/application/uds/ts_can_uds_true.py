#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：automotive 
@File ：ts_can_uds.py
@Author ：vv.zhang
@Date ：2022/11/21 13:41 
"""
import copy

from automotive import Can, SerialUtils, logger
from time import sleep
import re


class CanUds():

    def __init__(self, port: str, request_id: int, response_id: int, funciton_id: int):

        self.can = Can(can_box_device="TSMASTER")
        self.serial = SerialUtils()
        self.serial.connect(port=port)
        self.can.init_uds(request_id=request_id, response_id=response_id, function_id=funciton_id)
        self.can.open_can()

    def read_serial_did(self):
        """
        # Persistence -g -m config_changan -k config_changan
            Get module: config_changan      key: config_changan
            Result: config_changan=[00,5a,76,cb,d7,3b,0b,93,03,26,51,02,15,40,00,0e,0f,19,20,33,79,38,77,61,1f,f6,e0,bc,68,07,97,ef,df,7f,01,a2,ff,fe,7f,40,af,50,06,07,00,00,06,02,01,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00]

        """
        keyword = "Persistence -g -m config_changan -k config_changan"

        self.serial.write(command=keyword)
        sleep(2)
        lines = self.serial.read()
        # logger.info(lines)
        # [字节]
        match_keyword = re.search('config_changan=\[.*\]', lines)[0]

        words = match_keyword.split("config_changan=")[-1]
        sleep(2)
        logger.debug(f"serial read config : {words}")
        configure_word = re.sub('\W', '', words)
        return configure_word

    def transferSign2Unsign(self, sign):
        return sign & 0xffffffff

    def SecM_ComputeKey(self, seed):
        seed1 = seed
        seed2 = seed
        for i in range(0, 16):
            if self.transferSign2Unsign(0x01 & (seed2 >> i)) != self.transferSign2Unsign(0x01 & (seed2 >> (31 - i))):
                if self.transferSign2Unsign(0x01 & (seed2 >> i)) != 0:
                    seed2 = seed2 & (~(0x01 << i))
                    seed2 = seed2 | (0x01 << (31 - i))
                else:
                    seed2 = seed2 & (~(0x01 << (31 - i)))
                    seed2 = seed2 | ((0x01 << i))

        return self.transferSign2Unsign((seed1 ^ 0x71F96C1D) + (seed2 ^ 0x71F96C1D))

    def clear_serial(self):
        self.serial.read()
        sleep(3)

    def read_fd_22(self):
        data_22 = [0x22, 0xFD, 0x01]
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

        key = self.SecM_ComputeKey(seed=seed)
        logger.debug(f"算出的key {key}")
        # key = self.__dll.SecM_ComputeKey(seed)
        key_list = list(key.to_bytes(4, byteorder="big"))
        messgae_2702 = [0x27, 0x2, key_list[0], key_list[1], key_list[2], key_list[3]]
        security_02_response_data = self.can.send_and_receive_uds_message(message=messgae_2702)
        sleep(0.2)

    def write_data_by_identifier_0x2e(self, data: str):
        data = int(data, 16).to_bytes(64, "big")
        write_message = [0x2E, 0xFD, 0x01] + list(data)
        # back_write_message = copy.deepcopy(write_message)
        logger.info("即将写入数据")
        write_respond_data = self.can.send_and_receive_uds_message(message=write_message)
        print(list(write_respond_data))
        sleep(0.2)
        write_str = ''.join(list(map(lambda x: f"{hex(x)[2:].zfill(2)}", list(write_message)[3:])))
        return write_str

    def reset_11(self):
        data_11 = [0x11, 0x01]
        session_response_data = self.can.send_and_receive_uds_message(message=data_11)

    def state_3e(self):
        data_80 = [0x3e, 0x80]
        session_response_data_3e = self.can.send_and_receive_uds_message(message=data_80)


# 需要持续发送0x7df [02, 3e, 80, 00, 00, 00, 00, 00]
s = CanUds(port="COM3", response_id=0x70e, request_id=0x706, funciton_id=0x7df)


flag = True
time = 0
i = 0
while flag:
    time += 1
    logger.info(f"*********************第{time}次测试*************************")

    logger.info(f"写入第{i+1}个数据")

    fd_write_datas = ["005A76CBD73B0B93032651021540000E0F192033793877611FF6E0BC680797EFDF7F01A2FFFE7F40AF5006070000060201000000000000000000000000000000",
             "005A76CBD73B0B9383A6510215400A0E0F1920337938777D1FF6E0BC680797EFDF7F49A2FFFE7F40AFF006070006060201000000000000000000000000000000",
             "005A76CBD73B0B9383A6510215400A0E0F1920337938777D9FFEEDBC680797EFDF7F49A2FFFE7F40AFF006070012060201000000000000000000000000000000",
             "005A76FBD73B0B9383A651025574AACF4F1D2133793877719FFEEDBC680797EFDF7F01A2FFFE7F40AFF006070014060201000000000000000000000000000000",
             "005A76FBD73B0B9383A651025574AACF4F1D21337938777D9FFEEDBC680797EFDF7F49A2FFFE7F40AFF00607001B060201100000000000000000000000000000",
             "005A76FBE73B4B9383A651025544AACF4F1D21237939777D9FFEEDBC68079FEFDF7F49A2FFFE7F40BFF80607001F060201100000000000000000000000000000"]

    # 1.读串口配置 t1
    t1 = s.read_serial_did()
    logger.debug(f"串口配置字T1 = {t1}")
    if t1 == fd_write_datas[i].lower():
        logger.info(f"T1=T3, 跳到下一次循环")
        i += 1
        continue

    # 2. 22 FD01读配置t4
    t4 = s.read_fd_22()
    logger.debug(f"22读配置T4 = {t4}")

    # 3. 发1003扩展会话
    s.expand_dialog_10()
    # 4. 发2701 2702安全会话
    s.security_access_0x27()

    # 5. 写FD01 写的数据t3
    sleep(1)
    t3 = s.write_data_by_identifier_0x2e(fd_write_datas[i])
    sleep(2)
    s.reset_11()

    sleep(30)
    # 清除串口日志
    s.clear_serial()
    t2 = s.read_serial_did()
    logger.debug(f"串口配置字T2 = {t2}")

    if t1 != t4:
        logger.info("T1 != T4 保留现场")
        flag = False

    if t1 == t2:
        # logger.debug(f"T1=T2 = {t1}")
        logger.info("T1 = T2 保留现场")
        flag = False
    if t3 != t2:
        logger.debug(f"T3 = {t3}")
        logger.debug(f"T2 = {t2}")
        logger.info("T3 != T2 保留现场")
        flag = False
    i += 1

    # 归零，为了循环6个字节写入
    if i > 5:
        i = 0