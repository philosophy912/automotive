# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, China TSP, All rights reserved
# --------------------------------------------------------
# @Name:        service
# @Purpose:     on off的测试用例
# @Author:      lizhe
# @Created:     2019/10/25 11:18
# --------------------------------------------------------
import importlib
import os
import shutil
from time import sleep
from loguru import logger
from automotive.tools.images import Images
from automotive.tools import Utils
from ..config.config import Config
from ..config.device_enum import DeviceEnum
from .curve import Curve


class Service(object):
    """
    on off测试中的Service类，提供相关的api接口
    """

    def __init__(self, config: str):
        # 工具类
        self._utils = Utils()
        # 图像对比工具
        self._images = Images()
        # 电压曲线处理工具类
        self.__curve = Curve()
        # 配置的文件所在路径
        self.__config = Config(config)
        # 检查配置文件是否正确
        self.__config.check()
        # 图片存放的位置
        self.__image_save_path = None
        # 拍摄的亮图的绝对路径（需要对比的图片)
        self.__template_light = None
        # 拍摄的暗图的绝对路径（需要对比的图片)
        self.__template_dark = None
        # device实例take_a_picture_and_compare_light
        self.__devices = dict()
        # 初始化设备
        self.__init_devices()

    def __init_devices(self):
        """
        利用importlib动态根据配置即Config中的devices的设备加载各个actions实例
        """
        logger.debug(f"初始化所有配置的设备[{self.__config.devices}]")
        for device in self.__config.devices:
            # 获取设备的包名
            module_name = f"..actions.{device.value}_actions"
            module = importlib.import_module(module_name)
            # 获取类名
            class_name = device.value.capitalize() + "Actions"
            logger.debug(f"class name is {class_name}")
            # 获取类的实例
            # 由于配置了CAN，且can可能会被初始化，所以做判断
            try:
                args = self.__config.device.__dict__[device.value]
            except KeyError:
                logger.debug(f"class Device has no attribute [{device.value}]")
                args = None
            # 当能够在Device类中找到该参数且为list类型，初始化的时候带上参数(TIPS 此处可能会修改)
            if args:
                # 此处针对串口类配置
                if isinstance(args, list):
                    instance = getattr(module, class_name)(*args)
                # 此处针对can的配置(TIPS 此处可能会修改)
                else:
                    instance = getattr(module, class_name)(self.__config.messages)
            else:
                instance = getattr(module, class_name)()
            self.__devices[device] = instance

    def __check_image_save_path(self):
        """
        检查image_save_path是否被初始化
        """
        if not self.__image_save_path:
            raise RuntimeError(f"please use function [init_pic_save_path] first")

    def __two_pic_compare(self, pic1: str, pic2: str, threshold: int) -> bool:
        """
        利用汉明距对比图像

        :param pic1:     图像1

        :param pic2:     图像2

        :param threshold:  阈值

        :return: True/False
        """
        a, p, d = self._images.compare_by_hamming_distance(pic1, pic2)
        logger.debug(f"图片1[{pic1}]和图片2[{pic2}] 相比为[{a}:{p}:{d}], 要对比的阈值[{threshold}]")
        if a > threshold or p > threshold or d > threshold:
            logger.info(f"图片1[{pic1}]和图片2[{pic2}] 相比为[{a}:{p}:{d}], 超过阈值{threshold}")
            return False
        return True

    def __check_template_exist(self, type_: bool):
        """
        检查临时文件是否存在

        :param type_:
            True：亮图

            False： 暗图
        """
        if type_:
            if not self.__template_light or not os.path.exists(self.__template_light):
                raise RuntimeError(f"template light image not exist, please init first[init_template_light_pic] ")
        else:
            if not self.__template_dark or not os.path.exists(self.__template_dark):
                raise RuntimeError(f"template light image not exist ,please init first[init_template_dark_pic] ")

    def __take_a_picture_and_compare(self, type_: bool) -> bool:
        """
        拍照然后对比图片

        :return:  成功/失败
        """
        self.__check_template_exist(type_)
        # 图片对比的阈值
        threshold = self.__config.environment.camera["compare_threshold"]
        # 先拍照
        temp_pic = self.take_a_picture()
        if type_:
            return self.__two_pic_compare(self.__template_light, temp_pic, threshold)
        else:
            return self.__two_pic_compare(self.__template_dark, temp_pic, threshold)

    def sleep(self, time: int, text=None):
        """
        带txt提示的sleep

        :param time: sleep的时间

        :param text: 提示文字，默认没有文字提醒
        """
        self._utils.sleep(time, text)

    def random_sleep(self, min_: (float, int), max_: (float, int)):
        """
        在【min, max】之间随机sleep

        :param min_: 最小的sleep时间

        :param max_:  最大的sleep时间
        """
        self._utils.random_sleep(min_, max_)

    def log(self, content: str, level=None):
        """
        打印文字到控制台

        :param content:  文字

        :param level:  级别，只支持info以及debug， 默认INFO
        """
        self._utils.text(content, level)

    def open_devices(self):
        """
        打开所有配置的设备
        """
        logger.debug(f"配置的设备有[{self.__devices}]")
        # key就是设备的枚举， item是设备相关的actions的实例
        for key, item in self.__devices.items():
            logger.info(f"打开{key.value}")
            item.open()

    def close_devices(self):
        """
        关闭所有打开了得设备
        """
        # key就是设备的枚举， item是设备相关的actions的实例
        for key, item in self.__devices.items():
            logger.info(f"关闭{key.value}")
            item.close()

    def init_pic_save_path(self):
        """
        初始化存放图片的基本路径
        """
        logger.info("初始化存放图片的基本路径")
        self.__image_save_path = self.__config.environment.base_path + "\\" + self._utils.get_time_as_string()
        logger.debug(f"创建文件夹{self.__image_save_path}")
        os.makedirs(self.__image_save_path)

    def camera_test(self):
        """
        进行摄像头测试
        """
        test_time = self.__config.environment.camera["camera_test"]
        if test_time:
            logger.info(f"请调整摄像头，持续时间{test_time}分钟, 如调整完成，可以按q直接退出")
            self.__devices[DeviceEnum.CAMERA].camera_test(test_time)

    def init_template_light_pic(self):
        """
        初始化亮图
        """
        self.__check_image_save_path()
        # 设置亮图图片地址
        self.__template_light = self.__image_save_path + "\\" + self.__config.environment.camera["base"][0]
        logger.debug(f"初始化基准亮图")
        self.__devices[DeviceEnum.CAMERA].init_template_image(self.__template_light)

    def init_template_dark_pic(self):
        """
        初始化亮图
        """
        self.__check_image_save_path()
        # 设置暗图图片地址
        self.__template_light = self.__image_save_path + "\\" + self.__config.environment.camera["base"][1]
        logger.debug(f"初始化基准亮图")
        self.__devices[DeviceEnum.CAMERA].init_template_image(self.__template_dark)

    def filter_saved_images(self):
        """
        过滤测试过程中保存的图片
        """
        self.__check_image_save_path()
        threshold = self.__config.environment.camera["filter_threshold"]
        logger.debug(f"测完后过滤图片阈值是")
        image_files = []
        for dir_, subdir, file_name_list in os.walk(self.__image_save_path):
            for file_name in file_name_list:
                image_files.append(os.path.join(dir_, file_name))
        logger.debug("在当前位置生成新的文件夹")
        temp_folder = self.__image_save_path + "\\" + self._utils.get_time_as_string()
        os.makedirs(temp_folder)
        while len(image_files) > 1:
            first = image_files[0]
            second = image_files[1]
            if not self.__two_pic_compare(first, second, threshold):
                logger.info(f"{first}和{second}比较超过阈值{threshold},两个文件将被拷贝到{temp_folder}文件夹")
                shutil.copy(first, temp_folder)
                shutil.copy(second, temp_folder)
            image_files.pop(0)
        logger.info("图像筛选完成，请手动再次筛选")

    def bus_sleep(self):
        """
        系统休眠
        """
        bus_sleep = self.__config.environment.bus_sleep
        if isinstance(bus_sleep, str):
            self.__devices[DeviceEnum.CAN].bus_sleep()
        else:
            logger.info(f"系统会在{bus_sleep}秒后休眠")
            # 超过1分钟的休眠会分段休息
            if bus_sleep > 60:
                for i in range(bus_sleep):
                    sleep(1)
            else:
                sleep(bus_sleep)

    def take_a_picture(self) -> str:
        """
        拍照

        :return 拍照的图片
        """
        self.__check_image_save_path()
        logger.debug(f"拍照")
        camera_actions = self.__devices[DeviceEnum.CAMERA]
        camera_actions.take_a_pic(self.__image_save_path)
        return camera_actions.get_temp_pic()

    def take_a_picture_and_compare_light(self, is_skip: bool = False) -> bool:
        """
        拍照然后对比亮图

        :param is_skip: 是否跳过，影响返回结果，如果设置True，无论图片对比结果如何都返回True

        :return:
            True 图片对比成功
            False 图片对比失败
        """
        result = self.__take_a_picture_and_compare(True)
        return True if is_skip else result

    def take_a_picture_and_compare_dark(self, is_skip: bool = False) -> bool:
        """
        拍照然后对比暗图

        :param is_skip: 是否跳过，影响返回结果，如果设置True，无论图片对比结果如何都返回True

        :return:
            True 图片对比成功
            False 图片对比失败
        """
        result = self.__take_a_picture_and_compare(False)
        return True if is_skip else result

    def reverse_on(self):
        """
        进入倒车
        """
        reverse = self.__config.environment.reverse
        # 表示用can倒车
        if isinstance(reverse, str):
            can = self.__devices[DeviceEnum.CAN]
            can.reverse_on(reverse)
        # 表示用继电器倒车
        else:
            relay = self.__devices[DeviceEnum.RELAY]
            relay.channel_on(reverse)

    def reverse_off(self):
        """
        退出倒车
        """
        reverse = self.__config.environment.reverse
        # 表示用can倒车
        if isinstance(reverse, str):
            can = self.__devices[DeviceEnum.CAN]
            can.reverse_off(reverse)
        # 表示用继电器倒车
        else:
            relay = self.__devices[DeviceEnum.RELAY]
            relay.channel_off(reverse)

    def fast_on_off(self, duration: int, interval: float, channel: int, stop_status: bool = True):
        """
        快速开关继电器

        :param duration: 持续时间

        :param channel: 通道序号

        :param interval: 操作间隔时间

        :param stop_status:  停留的状态

            True: 开启

            False: 关闭
        """
        relay = self.__devices[DeviceEnum.RELAY]
        relay.fast_on_off(duration, interval, channel, stop_status)

    def battery_on(self):
        """
        通电
        """
        logger.debug(f"电源ON")
        # 由于电源可能配置RELAY，所以要做处理
        battery_type = self.__config.environment.battery
        if isinstance(battery_type, str):
            battery = self.__devices[DeviceEnum.from_value(battery_type)]
            battery.on()
        else:
            relay = self.__devices[DeviceEnum.RELAY]
            relay.channel_on(battery_type)

    def battery_off(self):
        """
        断电
        """
        logger.debug(f"电源OFF")
        # 由于电源可能配置RELAY，所以要做处理
        battery_type = self.__config.environment.battery
        if isinstance(battery_type, str):
            battery = self.__devices[DeviceEnum.from_value(battery_type)]
            battery.off()
        else:
            relay = self.__devices[DeviceEnum.RELAY]
            relay.channel_off(battery_type)

    def acc_on(self):
        """
        acc on
        """
        logger.debug(f"ACC ON")
        # 由于电源可能配置RELAY，所以要做处理
        acc_type = self.__config.environment.acc
        if isinstance(acc_type, str):
            acc = self.__devices[DeviceEnum.from_value(acc_type)]
            acc.on()
        else:
            relay = self.__devices[DeviceEnum.RELAY]
            relay.channel_on(acc_type)

    def acc_off(self):
        """
        acc off
        """
        logger.debug(f"ACC OFF")
        # 由于电源可能配置RELAY，所以要做处理
        acc_type = self.__config.environment.acc
        if isinstance(acc_type, str):
            acc = self.__devices[DeviceEnum.from_value(acc_type)]
            acc.off()
        else:
            relay = self.__devices[DeviceEnum.RELAY]
            relay.channel_off(acc_type)

    def set_voltage_current(self, voltage: float, current: float = 10):
        """
        调节电源，battery必须配置IT6831或者konstanter

        :param voltage: 电压值

        :param current: 电流值，默认10A
        """
        battery_type = self.__config.environment.battery
        try:
            battery = DeviceEnum.from_value(battery_type)
            if battery in (DeviceEnum.KONSTANTER, DeviceEnum.IT6831):
                self.__devices[battery].set_voltage_current(voltage, current)
            else:
                raise RuntimeError(f"KONSTANTER or IT6831 need config in battery, but now config [{battery}]")
        except ValueError:
            raise RuntimeError(f"KONSTANTER or IT6831 need config in battery, but now config [{battery_type}]")

    def change_voltage(self, start: float, end: float, step: float, interval: float = 0.5, current: float = 10) -> bool:
        """
        调节电源变化，battery必须配置IT6831或者konstanter

        :param start: 开始电压

        :param end: 结束电压

        :param step: 调整的步长

        :param interval: 间隔时间， 默认 0.5秒

        :param current: 电流值， 默认10A

        :return: 只针对konstanter有效

            True: 表示成功

            False: 表示失败
        """
        battery_type = self.__config.environment.battery
        try:
            battery = DeviceEnum.from_value(battery_type)
            if battery in (DeviceEnum.KONSTANTER, DeviceEnum.IT6831):
                return self.__devices[battery].change_voltage(start, end, step, interval, current)
            else:
                raise RuntimeError(f"KONSTANTER or IT6831 need config in battery, but now config [{battery}]")
        except ValueError:
            raise RuntimeError(f"KONSTANTER or IT6831 need config in battery, but now config [{battery_type}]")

    def adjust_voltage_by_curve(self, curve: str, current: int = 5, interval: float = 0.01) -> bool:
        """
        按照电压曲线来设置电压

        :param curve: 电压曲线列表（从csv文件中读取的)

        :param current: 最大电流值 (默认5A)

        :param interval 默认间隔时间(10ms)， konstanter最小间隔时间10ms

        :return:
            True: 表示成功

            False: 表示失败
        """
        battery_type = self.__config.environment.battery
        try:
            battery = DeviceEnum.from_value(battery_type)
            if battery == DeviceEnum.KONSTANTER:
                battery_list = self.__curve.get_voltage_by_csv(curve)
                return self.__devices[battery].adjust_voltage_by_curve(battery_list, current, interval)
            else:
                raise RuntimeError(f"only KONSTANTER can be used in battery, but now config [{battery_type}]")
        except ValueError:
            raise RuntimeError(f"only KONSTANTER can be used in battery, but now config [{battery_type}]")
