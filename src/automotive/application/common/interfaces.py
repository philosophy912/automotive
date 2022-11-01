# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2021, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        api1.py.py
# @Author:      lizhe
# @Created:     2021/8/3 - 22:02
# --------------------------------------------------------
from abc import ABCMeta, abstractmethod

from automotive.core.can.can_service import CANService

from .constants import Testcase, REPLACE_CHAR
from typing import Tuple, Sequence, Optional, Dict, List, Union

from automotive.logger.logger import logger
from .enums import SessionControlTypeEnum, EcuResetTypeEnum, CommunicationControlTypeEnum, ControlDTCSettingTypeEnum
from automotive.core.can.message import Message

Position = Tuple[int, int, int, int]
Voltage_Current = Tuple[float, float]
TestCases = Sequence[Testcase]


class BaseDevice(metaclass=ABCMeta):

    @abstractmethod
    def open(self):
        """
        打开设备
        """
        pass

    @abstractmethod
    def close(self):
        """
        关闭设备
        :return:
        """
        pass


class BaseSocketDevice(metaclass=ABCMeta):

    @abstractmethod
    def connect(self,
                username: Optional[str] = None,
                password: Optional[str] = None,
                ipaddress: Optional[str] = None):
        """
        连接并登陆系统

        :param ipaddress: IP地址

        :param username: 用户名

        :param password: 密码

        """
        pass

    @abstractmethod
    def disconnect(self):
        """
        断开
        """
        pass


class BaseScreenShot(metaclass=ABCMeta):

    @abstractmethod
    def screen_shot(self,
                    image_name: str,
                    count: int,
                    interval_time: float,
                    display: Optional[int] = None) -> Sequence[str]:
        """
        截图操作, 当截图有多张的时候，以__下划线分割并加编号

        :param image_name: 截图保存图片名称

        :param count: 截图张数

        :param interval_time: 截图间隔时间

        :param display: 屏幕序号
        """
        pass

    @abstractmethod
    def screen_shot_area(self,
                         position: Position,
                         image_name: str,
                         count: int,
                         interval_time: float,
                         display: Optional[int] = None) -> Sequence[str]:
        """
        区域截图, 当截图有多张的时候，以__下划线分割并加编号

        :param position: 截图区域(x, y, width, height)

        :param image_name: 截图保存图片名称

        :param count: 截图张数

        :param interval_time: 截图间隔时间

        :param display: 屏幕序号
        """
        pass


class BaseActions(metaclass=ABCMeta):

    @abstractmethod
    def click(self,
              display: int,
              x: int,
              y: int,
              interval: float = 0.2):
        """
        屏幕点击

        :param display: 屏幕序号

        :param x: 坐标点x

        :param y: 坐标点y

        :param interval: 按下和弹起的间隔时间
        """
        pass

    @abstractmethod
    def double_click(self,
                     display: int,
                     x: int,
                     y: int,
                     interval: float):
        """
        屏幕双击

        :param display: 屏幕序号

        :param x: 坐标点x

        :param y: 坐标点y

        :param interval: 两次点击之间的间隔时间
        """
        pass

    @abstractmethod
    def press(self,
              display: int,
              x: int,
              y: int,
              continue_time: float):
        """
        长按某个坐标点

        :param display: 屏幕序号

        :param x: 坐标点x

        :param y: 坐标点y

        :param continue_time: 长按持续时间
        """
        pass

    @abstractmethod
    def swipe(self,
              display: int,
              start_x: int,
              start_y: int,
              end_x: int,
              end_y: int,
              continue_time: float):
        """
        滑动页面

        :param display: 屏幕序号

        :param start_x: 起始点x

        :param start_y: 起始点y

        :param end_x: 结束点x

        :param end_y: 结束点y

        :param continue_time: 滑动耗时
        """
        pass


class BasePowerActions(BaseDevice):
    """
    电源相关的操作类，用于统一接口
    """

    def __init__(self):
        super().__init__()

    @abstractmethod
    def on(self):
        """
        打开设备
        """
        pass

    @abstractmethod
    def off(self):
        """
        关闭设备
        """
        pass


class BasePowerAdjustActions(BasePowerActions):
    """
    电源相关的操作类，用于统一接口
    """

    @abstractmethod
    def set_voltage(self, voltage: float):
        """
        设置电源电压

        :param voltage: 电压
        """
        pass

    @abstractmethod
    def set_current(self, current):
        """
        设置电源电流

        :param current: 电流
        """
        pass

    @abstractmethod
    def set_voltage_current(self, voltage: float, current: float = 10):
        """
        设置电源电压电流

        :param voltage: 电压

        :param current: 电流
        """
        pass

    @abstractmethod
    def change_voltage(self,
                       start: float,
                       end: float,
                       step: float,
                       interval: float = 0.5,
                       current: float = 10):
        """
        调节电压

        :param start: 开始电压

        :param end: 结束电压

        :param step: 调整的步长

        :param interval: 间隔时间，默认0.5秒

        :param current: 电流值， 默认10A

        :return: 只针对konstanter实际有效，对IT6831电源则永远返回True
        """
        pass

    @abstractmethod
    def get_current_voltage(self) -> Voltage_Current:
        """
        获取当前电流电压值

        :return 当前电压和电流值
        """
        pass


class BaseTestCase(metaclass=ABCMeta):

    @staticmethod
    def _parse_id(content: str, split_character: Tuple[str, str] = ("[", "]")) -> Tuple[str, str]:
        """
        用于解析数据如 在线音乐[#93] 用以适配禅道的需求导入
        :param split_character: 左右分隔符
        :param content: 模块名
        :return: 在线音乐[#93] -> 在线音乐#93
        """
        content = content.strip()
        left, right = split_character
        if left in content:
            index = content.index(left)
            module = content[:index]
            if content.endswith(right):
                module_id = content[index + 1:-1]
            else:
                module_id = content[index + 1:]
            return module, module_id
        else:
            return content, ""

    @staticmethod
    def _get_module(module: str) -> Tuple[str, str]:
        """
        用于解析module
        :param module:
        :return: module和module_id
        """
        if REPLACE_CHAR in module:
            module_list = module.split(REPLACE_CHAR)
            return module_list[0], module_list[1]
        else:
            return module, ""


class BaseReader(BaseTestCase):
    @abstractmethod
    def read_from_file(self, file: str) -> Dict[str, TestCases]:
        """
        从文件中读取testCase类
        :param file:  文件
        :return: 读取到的测试用例集合
        """
        pass


class BaseWriter(BaseTestCase):
    @abstractmethod
    def write_to_file(self, file: str, testcases: Dict[str, TestCases], temp_file: str = None):
        """
        把测试用例集合写入到文件中
        :param file:  文件
        :param testcases: 测试用例集合
        :param temp_file:excel模板文件地址
        """
        pass

    @staticmethod
    def _check_testcases(testcases: Dict[str, TestCases]):
        if testcases is None:
            raise RuntimeError("testcases is None")
        if len(testcases) == 0:
            raise RuntimeError("no testcase found")


class BaseUdsService(metaclass=ABCMeta):

    def __init__(self, can_service: CANService, request_msg_id: int, response_msg_id: int):
        """
        初始化类
        :param can_service: 传入的CAN Service
        :param request_msg_id:  请求ID
        :param response_msg_id:  响应ID
        """
        self._can_service = can_service
        self._req_id = request_msg_id
        self._res_id = response_msg_id

    def _get_response_value(self) -> Sequence[Sequence[int]]:
        """
        获取返回的数据
        :return:
        """
        filter_messages = []
        messages = self._can_service.get_stack()
        messages = list(filter(lambda x: x.msg_id == self._res_id, messages))
        for message in messages:
            data = message.data
            filter_messages.append(data)
        return filter_messages

    def _send_message(self, data: List, byte_size: int = 8, default_value: int = 0x0):
        """
        填充bytes
        :param data: 传入的数据
        :param byte_size: 字节长度，默认为8
        :param default_value: 填充值，默认为0
        """
        while len(data) < byte_size:
            data.append(default_value)
        message = Message()
        message.msg_id = self._req_id
        message.data = data
        self._can_service.transmit_one(message)

    def diagnostic_session_control_0x10(self,
                                        sub_function: Union[SessionControlTypeEnum, int]) -> Sequence[Sequence[int]]:
        """
        DiagnosticSessionControl 诊断模式控制
        :return:
        """
        self._can_service.clear_stack_data()
        if isinstance(sub_function, SessionControlTypeEnum):
            sub_function = sub_function.value
        data = [0x2, 0x10, sub_function]
        self._send_message(data)
        return self._get_response_value()

    def ecu_reset_0x11(self, sub_function: Union[EcuResetTypeEnum, int]) -> Sequence[Sequence[int]]:
        """
        EcuReset 电控单元复位
        :return:
        """
        self._can_service.clear_stack_data()
        if isinstance(sub_function, EcuResetTypeEnum):
            sub_function = sub_function.value
        data = [0x2, 0x11, sub_function]
        self._send_message(data)
        return self._get_response_value()

    @abstractmethod
    def security_access_0x27(self) -> Sequence[Sequence[int]]:
        """
        SecurityAccess 安全访问
        :return:
        """
        pass

    def communication_control_0x28(self,
                                   sub_function: Union[CommunicationControlTypeEnum, int]) -> Sequence[Sequence[int]]:
        """
        CommunicationControl 通信控制
        :return:
        """
        self._can_service.clear_stack_data()
        if isinstance(sub_function, CommunicationControlTypeEnum):
            sub_function = sub_function.value
        data = [0x3, 0x11, sub_function, 0x2]
        self._send_message(data)
        return self._get_response_value()

    def tester_present_0x3e(self) -> Sequence[Sequence[int]]:
        """
        TesterPresent 诊断设备在线
        :return:
        """
        self._can_service.clear_stack_data()
        data = [0x2, 0x3e]
        self._send_message(data)
        return self._get_response_value()

    def control_dtc_setting_0x85(self, sub_function: Union[ControlDTCSettingTypeEnum, int]) -> Sequence[Sequence[int]]:
        """
        ControlDTCSetting 控制DTC设置
        :return:
        """
        self._can_service.clear_stack_data()
        if isinstance(sub_function, ControlDTCSettingTypeEnum):
            sub_function = sub_function.value
        data = [0x2, 0x85, sub_function]
        self._send_message(data)
        return self._get_response_value()

    @staticmethod
    def link_control_0x87():
        """
        Link Control 链路控制
        :return:
        """
        logger.warning("not implements this function")

    @abstractmethod
    def read_data_by_identifier_0x22(self, did_number: str) -> Sequence[Sequence[int]]:
        """
        ReadDataByIdentifier 读取数据（通过标识）
        :param did_number DID号
        :return:
        """
        pass

    @staticmethod
    def read_memory_by_address_0x23():
        """
        ReadMemoryByAddress 读取内存（通过地址）
        :return:
        """
        logger.warning("not implements this function")

    @staticmethod
    def read_data_by_periodic_identifier_0x2a():
        """
        ReadDataByPeriodicIdentifier 周期读取数据（通过标识）
        :return:
        """
        logger.warning("not implements this function")

    @abstractmethod
    def write_data_by_identifier_0x2e(self) -> Sequence[Sequence[int]]:
        """
        WriteDataByIdentifier 写入数据（通过标识）
        :return:
        """
        pass

    @staticmethod
    def write_memory_by_address_0x3d():
        """
        WriteMemoryByAddress 写入内存（通过地址）
        :return:
        """
        logger.warning("not implements this function")

    @staticmethod
    def dynamically_define_data_identifier_0x2c():
        """
        DynamicallyDefineDataIdentifier 数据标识符动态定义
        :return:
        """
        logger.warning("not implements this function")

    def clear_diagnostic_information_0x14(self) -> Sequence[Sequence[int]]:
        """
        ClearDiagnosticInformation 清除诊断信息
        :return:
        """
        self._can_service.clear_stack_data()
        data = [0x4, 0x14, 0xff, 0xff, 0xff]
        self._send_message(data)
        return self._get_response_value()

    @abstractmethod
    def read_dtc_information_0x19(self) -> Sequence[Sequence[int]]:
        """
        ReadDTCInformation 读取DTC信息
        :return:
        """
        pass

    @staticmethod
    def input_output_control_by_identifier_0x2f():
        """
        InputOutputControlByIdentifier 输入输出控制
        :return:
        """
        logger.warning("not implements this function")

    @staticmethod
    def routine_control_0x31():
        """
        RoutineControl 例程控制
        :return:
        """
        logger.warning("not implements this function")

    @staticmethod
    def request_download_0x34():
        """
        RequestDownload 请求下载
        :return:
        """
        logger.warning("not implements this function")

    @staticmethod
    def transfer_data_0x36():
        """
        TransferData 发送数据
        :return:
        """
        logger.warning("not implements this function")

    @staticmethod
    def request_transfer_exit_0x37():
        """
        RequestTransferExit 请求退出发送
        :return:
        """
        logger.warning("not implements this function")

    @staticmethod
    def request_upload_0x35():
        """
        RequestUpload 请求上传
        :return:
        """
        logger.warning("not implements this function")

    @staticmethod
    def request_file_transfer_0x38():
        """
        RequestFileTransfer 请求文件传输
        :return:
        """
        logger.warning("not implements this function")
