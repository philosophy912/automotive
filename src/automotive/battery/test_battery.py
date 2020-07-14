# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, China TSP, All rights reserved
# --------------------------------------------------------
# @Name:        config.py
# @Purpose:     todo
# @Author:      lizhe
# @Created:     2020/6/19 - 11:20
# --------------------------------------------------------
from automotive.tools.onoff.services.service import Service
from loguru import logger
from time import sleep

device_config = {
    # konstanter配置, 仅配置端口和波特率
    "konstanter": ["com9", 19200],
    # it6831配置, 仅配置端口和波特率
    "it6831": ["com10", 9600],
    # 串口配置, 仅配置端口和波特率
    "serial": ["com7", 115200],
    # CAN配置
    "can": {
        # DBC解析出来的配置，值表示用工具生成出来的文件放置的位置（包名)
        "message": "gse.config.gse",
        # 倒档配置 [messageId, signalName, signalValue]
        "r_shift": [0x256, "r_shift", 1],
        # 空档配置 [messageId, signalName, signalValue]
        "n_shift": [0x256, "n_shift", 1],
        # 快速休眠配置 [messageId, signalName, signalValue, continueTime]
        "fast_sleep": [0x256, "fast_sleep", 1, 5]
    },
    # 环境相关配置
    "environment": {
        # 配置电源  电源可以配置it6831, konstanter 或者数字（表示继电器通道)
        "battery": "it6831",
        # 配置ACC
        "acc": "konstanter",
        # 配置倒车
        "reverse": 5,
        # 配置休眠
        "bus_sleep": "fast_sleep",
        # 配置摄像头（都带默认配置)
        "camera": {
            # 默认调整摄像头时间
            "camera_test": 2,
            # 图片对比的阈值
            "compare_threshold": 10,
            # 图片过滤器的阈值
            "filter_threshold": 10,
            # 基准图片配置(亮图和暗图)
            "base": ["light_template.png", "dark_template.png"]
        },
        # 重启检查字符串
        "serial": ["aaa", "bbb"],
        # 配置基准路径
        "base_path": r"D:\Workspace\python\automatedtest\res\project\temp\screenshot"

    }
}


class TestBattery(object):

    def __init__(self, config: dict):
        # 相关的配置文件
        self.__service = Service(config=config)

    def __setup(self):
        logger.info("准备相关事宜.........")
        logger.info("初始化图片存放位置")
        self.__service.init_pic_save_path()
        logger.info("打开设备")
        self.__service.open_devices()
        logger.info("打开摄像头，请手动调节拍摄位置")
        self.__service.camera_test()

    def __prepare_light(self, startup_time: int):
        logger.info("打开电源并调节电压到12V")
        self.__service.battery_on()
        self.__service.set_voltage_current(12)
        self.__service.acc_on()
        self.__service.sleep(startup_time, "等待开机完成")
        logger.info("拍摄基准图片的亮图")
        self.__service.init_template_light_pic()

    def __prepare_dark(self):
        self.__service.battery_off()
        logger.info("拍摄基准图片的暗图")
        self.__service.init_template_dark_pic()

    def __prepare(self, startup_time: int = None, pic_type: bool = False):
        """
        拍摄初始图片
        正常画面: self.__prepare(12)
        关机画面: self.__prepare()
        两个画面: self.__prepare(12, True)
        :param startup_time: 正常启动时间
        :param pic_type: 类型
        """
        self.__setup()
        if startup_time:
            if pic_type:
                self.__prepare_dark()
            self.__prepare_light(startup_time)
        else:
            self.__prepare_dark()

    def __tear_down(self):
        logger.info("关闭所有设备")
        self.__service.close_devices()
        logger.info("过滤图片，后续人工检查")
        self.__service.filter_saved_images()

    def __close_device(self, startup_time: int, min_: float, max_: float, cycle_time: int,
                       step: float, interval: float, pic_type: bool = False):
        self.__prepare(startup_time, pic_type)
        for i in range(cycle_time):
            logger.info(f"开始进行第{i + 1}次测试")
            self.__change_voltage(min_, max_, step, interval)
            logger.info(f"拍照检查工作是否正常")
            if not self.__service.take_a_picture_and_compare_light():
                logger.error(f"检查到不正常的情况")
                continue
            if self.__service.check_system_available():
                logger.error(f"系统没有恢复正常的情况")
                break
            if self.__service.check_can_available():
                logger.error(f"检查到CAN总线丢失")
                break
            self.__change_voltage(max_, min_, step, interval)
            logger.info(f"拍照检查工作是否正常")
            if self.__service.take_a_picture_and_compare_dark():
                logger.error(f"检查到不正常的情况")
                continue
            if not self.__service.check_system_available():
                logger.error(f"系统仍然正常")
                break
            if self.__service.check_can_available():
                logger.error(f"检查到CAN总线丢失")
                break
        self.__tear_down()

    def __close_display(self, startup_time: int, min_: float, max_: float, cycle_time: int,
                        step: float, interval: float, pic_type: bool = False):
        self.__prepare(startup_time, pic_type)
        for i in range(cycle_time):
            logger.info(f"开始进行第{i + 1}次测试")
            self.__change_voltage(min_, max_, step, interval)
            logger.info(f"拍照检查工作是否正常")
            if not self.__service.take_a_picture_and_compare_light():
                logger.error(f"检查到不正常的情况")
                continue
            if self.__service.check_system_available():
                logger.error(f"系统没有恢复正常的情况")
                break
            if self.__service.check_can_available():
                logger.error(f"检查到CAN总线丢失")
                break
            self.__change_voltage(max_, min_, step, interval)
            logger.info(f"拍照检查工作是否正常")
            if self.__service.take_a_picture_and_compare_dark():
                logger.error(f"检查到不正常的情况")
                continue
            if self.__service.check_system_available():
                logger.error(f"系统没有恢复正常的情况")
                break
            if self.__service.check_can_available():
                logger.error(f"检查到CAN总线丢失")
                break
        self.__tear_down()

    def __raise(self, startup_time: int, start: float, end: float, cycle_time: int, step: float, interval: float,
                pic_type: bool = False):
        self.__prepare(startup_time, pic_type)
        for i in range(cycle_time):
            logger.info(f"开始进行第{i + 1}次测试")
            self.__change_voltage(start, end, step, interval, True)
            logger.info(f"拍照检查工作是否正常")
            if not self.__service.take_a_picture_and_compare_light():
                logger.error(f"检查到不正常的情况")
                continue
            if self.__service.check_system_available():
                logger.error(f"系统没有恢复正常的情况")
                break
            if self.__service.check_can_available():
                logger.error(f"检查到CAN总线丢失")
                break
        self.__tear_down()

    def __change_voltage(self, min_voltage: float, max_voltage: float, step: float, interval: float,
                         cycle: bool = False):
        logger.info(f"调节电压从{min_voltage}到{max_voltage}，每隔{interval}秒变化{step}V")
        self.__service.change_voltage(min_voltage, max_voltage, step, interval)
        sleep(1)
        if cycle:
            logger.info(f"调节电压从{max_voltage}到{min_voltage}，每隔{interval}秒变化{step}V")
            self.__service.change_voltage(max_voltage, min_voltage, step, interval)
            sleep(1)

    def __check_image(self, type_: bool):
        if type_:
            if not self.__service.take_a_picture_and_compare_light():
                logger.error(f"检查到工作不正常的情况")
                return

    def voltage_change_between_normal_min_and_normal_max(self, startup_time: int, min_voltage: float,
                                                         max_voltage: float,
                                                         cycle_time: int, step: float = 0.1, interval: float = 0.1):
        """
        电源在正常电压之间变动，

        :param interval: 电源变动停留时间， 默认停留1秒

        :param step: 电源变化幅度， 默认幅度1V

        :param startup_time: 开机启动完成需要的时间

        :param min_voltage: 正常电压最低电压值

        :param max_voltage: 正常电压最高电压值

        :param cycle_time: 循环测试次数
        """
        # 阈值处理，
        min_ = min_voltage + 0.5
        max_ = max_voltage - 0.5
        self.__prepare(startup_time)
        for i in range(cycle_time):
            logger.info(f"开始进行第{i + 1}次测试")
            self.__change_voltage(min_, max_, step, interval)
            logger.info(f"拍照检查工作是否正常")
            if not self.__service.take_a_picture_and_compare_light():
                logger.error(f"检查到工作不正常的情况")
                continue
            logger.info(f"检查是否有重启的现象")
            if self.__service.judge_text_in_serial():
                logger.error(f"检查到有重启的情况")
                break
            if self.__service.check_can_available():
                logger.error(f"检查到CAN总线丢失")
                break
            self.__change_voltage(max_, min_, step, interval)
            logger.info(f"拍照检查是否正常")
            if not self.__service.take_a_picture_and_compare_dark():
                logger.error(f"检查到不正常的情况")
                continue
            logger.info(f"检查是否有重启的现象")
            if self.__service.judge_text_in_serial():
                logger.error(f"检查到有重启的情况")
                break
            if self.__service.check_can_available():
                logger.error(f"检查到CAN总线丢失")
                break
        self.__tear_down()

    def voltage_low_close_device(self, startup_time: int, low_voltage: float, normal_voltage_min: float,
                                 cycle_time: int):
        """
        电压关机测试

        :param startup_time: 开机启动完成需要的时间

        :param low_voltage:  低电压阈值（关机)

        :param normal_voltage_min: 正常电压的最低值

        :param cycle_time: 循环次数

        """
        # 阈值处理，
        min_ = low_voltage - 0.5
        max_ = normal_voltage_min + 0.5
        self.__close_device(startup_time, min_, max_, cycle_time, 0.1, 0.1)

    def voltage_low_close_display(self, startup_time: int, low_voltage: float, normal_voltage_min: float,
                                  cycle_time: int):
        """
        电压关屏测试

        :param startup_time: 开机启动完成需要的时间

        :param low_voltage:  低电压阈值（关机)

        :param normal_voltage_min: 正常电压的最低值

        :param cycle_time: 循环次数
        """
        # 阈值处理，
        min_ = low_voltage - 0.5
        max_ = normal_voltage_min + 0.5
        self.__close_display(startup_time, min_, max_, cycle_time, 0.1, 0.1)

    def voltage_high_close_device(self, startup_time: int, high_voltage: float, normal_voltage_max: float,
                                  cycle_time: int):
        """
        电压关机测试

        :param startup_time: 开机启动完成需要的时间

        :param high_voltage:  高电压阈值（关机)

        :param normal_voltage_max: 正常电压的最高值

        :param cycle_time: 循环次数
        """
        # 阈值处理
        min_ = normal_voltage_max + 0.5
        max_ = high_voltage - 0.5
        self.__close_device(startup_time, min_, max_, cycle_time, 0.1, 0.1)

    def voltage_high_close_display(self, startup_time: int, low_voltage: float, normal_voltage_min: float,
                                   cycle_time: int):
        """
        电压关屏测试

        :param startup_time: 开机启动完成需要的时间

        :param low_voltage:  低电压阈值（关机)

        :param normal_voltage_min: 正常电压的最低值

        :param cycle_time: 循环次数

        """
        # 阈值处理
        min_ = low_voltage - 0.5
        max_ = normal_voltage_min + 0.5
        self.__close_display(startup_time, min_, max_, cycle_time, 0.1, 0.1)

    def voltage_raise_up_slowly(self, startup_time: int, cycle_time: int):
        """
        电压慢速从12V变化到20V, 步长0.1V, 变化间隔时间0.3S

        :param startup_time: 开机启动完成需要的时间

        :param cycle_time: 循环次数
        """
        self.__raise(startup_time, 12, 20, cycle_time, 0.1, 0.3)

    def voltage_raise_up_quickly(self, startup_time: int, cycle_time: int):
        """
        电压快速从12V变化到20V, 步长0.1V, 变化间隔时间0.1s

        :param startup_time: 开机启动完成需要的时间

        :param cycle_time: 循环次数
        """
        self.__raise(startup_time, 12, 20, cycle_time, 0.1, 0.1)

    def voltage_raise_down_slowly(self, startup_time: int, cycle_time: int):
        """
        电压慢速从12V变化到3V, 步长0.1V, 变化间隔时间0.3S

        :param startup_time: 开机启动完成需要的时间

        :param cycle_time: 循环次数
        """
        self.__raise(startup_time, 12, 3, cycle_time, 0.1, 0.3)

    def voltage_raise_down_quickly(self, startup_time: int, cycle_time: int):
        """
        电压快速从12V变化到20V, 步长0.1V, 变化间隔时间0.1s

        :param startup_time: 开机启动完成需要的时间

        :param cycle_time: 循环次数
        """
        self.__raise(startup_time, 12, 3, cycle_time, 0.1, 0.1)

    def crank_car(self, startup_time: int, cycle_time: int, crank_curve: str):
        """
        正常电压情况下点火

        :param startup_time: 开机启动完成需要的时间

        :param cycle_time: 循环次数

        :param crank_curve: 点火曲线文件
        """
        self.__prepare(startup_time)
        for i in range(cycle_time):
            logger.info(f"开始进行第{i + 1}次测试")
            self.__service.adjust_voltage_by_curve(crank_curve)
            logger.info(f"拍照检查工作是否正常")
            if not self.__service.take_a_picture_and_compare_light():
                logger.error(f"检查到不正常的情况")
                continue
            if self.__service.check_system_available():
                logger.error(f"系统没有恢复正常的情况")
                break
            if self.__service.check_can_available():
                logger.error(f"检查到CAN总线丢失")
                break
        self.__tear_down()

    def acc_on_off(self, startup_time: int, cycle_time: int):
        """
        ACC ON OFF测试

        :param startup_time: 开机启动完成需要的时间

        :param cycle_time: 循环次数
        """
        self.__prepare(startup_time)
        for i in range(cycle_time):
            logger.info(f"开始进行第{i + 1}次测试")
            self.__service.acc_on()
            sleep(startup_time)
            logger.info(f"拍照检查工作是否正常")
            if not self.__service.take_a_picture_and_compare_light():
                logger.error(f"检查到不正常的情况")
                continue
            if self.__service.check_system_available():
                logger.error(f"系统没有恢复正常的情况")
                break
            if self.__service.check_can_available():
                logger.error(f"检查到CAN总线丢失")
                break
            self.__service.acc_off()
            self.__service.bus_sleep()
        self.__tear_down()

    def reverse_car_normal(self, startup_time: int, cycle_time: int):
        """
        正常情况下倒车

        :param startup_time:  开机启动完成需要的时间

        :param cycle_time: 循环次数
        """
        self.__prepare(startup_time)
        for i in range(cycle_time):
            logger.info(f"开始进行第{i + 1}次测试")
            self.__service.reverse_on()
            sleep(5)
            logger.info(f"拍照检查工作是否正常")
            if not self.__service.take_a_picture_and_compare_light():
                logger.error(f"检查到不正常的情况")
                continue
            self.__service.reverse_off()
            sleep(5)
        self.__tear_down()

    def reverse_car_when_battery_on(self, startup_time: int, cycle_time: int):
        """
        battery ON的时候同时倒车

        :param startup_time: 开机启动完成需要的时间

        :param cycle_time: 循环次数
        """
        self.__prepare(startup_time)
        for i in range(cycle_time):
            logger.info(f"开始进行第{i + 1}次测试")
            self.__service.battery_on()
            self.__service.reverse_on()
            sleep(startup_time)
            logger.info(f"拍照检查工作是否正常")
            if not self.__service.take_a_picture_and_compare_light():
                logger.error(f"检查到不正常的情况")
                continue
            self.__service.reverse_off()
            self.__service.battery_off()
            sleep(5)
        self.__tear_down()

    def reverse_car_when_crank(self, startup_time: int, cycle_time: int, crank_curve: str):
        """
        点火的时候同时倒车

        :param startup_time: 开机启动完成需要的时间

        :param cycle_time: 循环次数

        :param crank_curve: 电压曲线
        """
        self.__prepare(startup_time)
        for i in range(cycle_time):
            logger.info(f"开始进行第{i + 1}次测试")
            self.__service.adjust_voltage_by_curve(crank_curve)
            self.__service.reverse_on()
            logger.info(f"拍照检查工作是否正常")
            if not self.__service.take_a_picture_and_compare_light():
                logger.error(f"检查到不正常的情况")
                continue
            self.__service.reverse_off()
            sleep(5)
        self.__tear_down()
