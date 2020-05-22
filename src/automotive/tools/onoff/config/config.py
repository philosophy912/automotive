# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, China TSP, All rights reserved
# --------------------------------------------------------
# @Name:        config.py
# @Purpose:     设备及环境配置类
# @Author:      lizhe
# @Created:     2020/02/04 11:22
# --------------------------------------------------------
import importlib
import os
from loguru import logger
from automotive.can import Parser
from automotive.tools import Singleton, Utils
from .device import Device
from .device_enum import DeviceEnum
from .environment import Environment


class Config(metaclass=Singleton):
    """
    配置类，只允许有一个配置存在
    """

    def __init__(self, file_name: str):
        """
        配置类所在的文件
        :param file_name: yml文件路径
        """
        config = Utils().read_yml_full(file_name)
        # 初始化并设置值更新内容
        self.device = Device()
        self.device.update(config["device_config"])
        # 初始化并设置值更新内容
        self.environment = Environment()
        self.environment.update(config["environment"])
        # 要用到的设备
        self.devices = set()
        # messages模块（自动化生成的dbc)
        self.messages = None

    @staticmethod
    def __check_serial(config: list):
        """
        检查串口类的配置文件

        :param config: 配置
        """
        # 不为空时才检查
        if config:
            port, baud_rate = config
            if not (isinstance(port, str) and port.upper().startswith("COM") and isinstance(baud_rate, int)):
                raise ValueError(f"port[{port}] must start with COM and baud_rate[{baud_rate}] must int")

    @staticmethod
    def __check_can(config: list, id_messages: dict, name_messages: dict):
        """
        检查can配置

        :param config: 配置文件

        :param id_messages: id_messages

        :param name_messages: name_messages
        """
        if config:
            if len(config) == 4:
                msg, signal_name, value, continue_time = config
                if not isinstance(continue_time, int):
                    raise ValueError(f"continue time[{continue_time}] need be int")
            else:
                msg, signal_name, value = config
            if not isinstance(msg, (str, int)):
                raise ValueError(f"msg[{msg}] type is incorrect must str or int")
            if not isinstance(signal_name, str):
                raise ValueError(f"signal_name[{signal_name}] type is incorrect must str")
            if not isinstance(value, int):
                raise ValueError(f"value[{value}] type is incorrect must int")
            if (isinstance(msg, str) and msg in name_messages) or (isinstance(msg, int) and msg in id_messages):
                if isinstance(msg, str):
                    message = name_messages[msg]
                else:
                    message = id_messages[msg]
                # 检查signal_name
                if signal_name in message.signals:
                    signal = message.signals[signal_name]
                    # 检查value是否处于max和min之间
                    if not signal.minimum <= value <= signal.maximum:
                        raise ValueError(f"value[{value}] out of range[{signal.minimum}-{signal.maximum}]")
                else:
                    raise ValueError(f"signal_name[{signal_name}] not found in message")
            else:
                raise ValueError(f"msg[{msg}] not found in messages")

    def __check_camera(self):
        """
        检查camera配置
        """
        # 检查camera，如果所有的camera配置都为空，则不添加camera，否则添加camera
        for item in self.environment.camera.values():
            if item:
                self.devices.add(DeviceEnum.CAMERA)
                # 找到了就加入到设备列表中
                break
        #  检查camera配置是否正确
        for key, item in self.environment.camera.items():
            if key != "base":
                if not isinstance(item, int):
                    raise ValueError(f"camera.{key} config error, only support int, but now is [{item}]")
            else:
                if not isinstance(item, list) or len(item) != 2:
                    raise ValueError(f"base config error, recommend use [light_template.png, dark_template.png]")
                else:
                    for pic in item:
                        if not (pic.endswith(".png") or pic.endswith(".jpg")):
                            raise ValueError(f"pic only support png and jpg")

    def __check_environment(self) -> set:
        """
        扫描environment类，检查battery - reverse类型是否为数字，如果是数字则需要加入继电器
        """
        # 扫描environment类，检查battery - reverse类型是否为数字，如果是数字则需要加入继电器
        # 与串口相关的设备
        serials = DeviceEnum.SERIAL.value, DeviceEnum.KONSTANTER.value, DeviceEnum.IT6831.value
        # 与can相关的设备
        can = "r_shift", "n_shift", "fast_sleep"
        # 外部扫描检查设备
        scan_devices = [self.environment.battery, self.environment.acc,
                        self.environment.reverse, self.environment.bus_sleep]
        # 用到的can信号，便于后面检查
        used_can = set()
        for device in scan_devices:
            logger.debug(f"device is [{device}]")
            if device:
                # 判断是否用到了相关的串口
                if isinstance(device, str) and device in serials:
                    self.devices.add(DeviceEnum.from_value(device))
                # 判断是否用到了can
                elif isinstance(device, str) and device in can:
                    used_can.add(device)
                    self.devices.add(DeviceEnum.CAN)
                # 继电器只允许配置小于8个通道
                elif isinstance(device, int) and 1 <= device <= 8:
                    self.devices.add(DeviceEnum.RELAY)
                else:
                    raise ValueError(f"only support type[{serials}] or relay channel [0-8]")
        logger.info(f"add devices is {self.devices}")
        # 如果base_path不存在，抛出异常
        if not os.path.exists(self.environment.base_path):
            raise ValueError(f"[{self.environment.base_path}] not exist, please check it")
        return used_can

    def __check_devices(self, used_can: set):
        """
        检查self.devices中的对象，根据该对象查找相应的配置

        :param 用到的can信号，方便检查
        """
        logger.debug(f"use can [{used_can}]")
        # 检查self.devices中的对象，根据该对象查找相应的配置
        serials_enum = DeviceEnum.SERIAL, DeviceEnum.KONSTANTER, DeviceEnum.IT6831
        # 检查CAN配置
        if DeviceEnum.CAN in self.devices:
            messages_package = self.device.can["messages"]
            # 表明配置了message
            if messages_package:
                module = importlib.import_module(messages_package)
                self.messages = module.messages
                # 导入数据库方便检查内容
                id_messages, name_messages = Parser.get_message(self.messages)
                # can = fast_sleep
                for can in used_can:
                    can_data = self.device.can[can]
                    if can_data:
                        self.__check_can(can_data, id_messages, name_messages)
                    else:
                        raise ValueError(f"config [{can}] not found")
            else:
                raise ValueError(f"please config message as [automatedtest.lib.can.dbc.gse_3j2] first ")
        # 检查串口相关设备
        for device in self.devices:
            if device in serials_enum:
                item = self.device.__dict__[device.value]
                self.__check_serial(item)

    def check(self):
        """
        检查各个配置是否配置了
        1、检查environment配置是否正确
        2、检查倒车是否配置了
        3、检查devices配置是否正确
        """
        self.__check_camera()
        used_can = self.__check_environment()
        # 检查倒车是否配置了
        reverse = self.environment.reverse
        if isinstance(reverse, str):
            used_can.add("r_shift")
            used_can.add("n_shift")
        self.__check_devices(used_can)
