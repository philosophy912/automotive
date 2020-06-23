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

# 相关的配置文件
service = Service(config=device_config)


def __prepare(startup_time: int):
    logger.info("准备相关事宜.........")
    logger.info("初始化图片存放位置")
    service.init_pic_save_path()
    logger.info("打开设备")
    service.open_devices()
    logger.info("打开摄像头，请手动调节拍摄位置")
    service.camera_test()
    service.battery_off()
    logger.info("拍摄基准图片的暗图")
    service.init_template_dark_pic()
    logger.info("打开电源并调节电压到12V")
    service.battery_on()
    service.set_voltage_current(12)
    service.acc_on()
    service.sleep(startup_time, "等待开机完成")
    logger.info("拍摄基准图片的亮图")
    service.init_template_light_pic()


def voltage_change_between_normal_min_and_normal_max(startup_time: int, min_voltage: float, max_voltage: float,
                                                     cycle_time: int, step: float = 1, interval: float = 1):
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
    __prepare(startup_time)
    for i in range(cycle_time):
        logger.info(f"开始进行第{i + 1}次测试")
        logger.info(f"调节电压从{min_voltage}到{max_voltage}，每隔{interval}秒变化{step}V")
        service.change_voltage(min_, max_, step, interval)
        logger.info(f"拍照检查工作是否正常")
        if service.take_a_picture_and_compare_light():
            logger.error(f"检查到工作不正常的情况")
            continue
        logger.info(f"检查是否有重启的现象")
        if service.judge_text_in_serial():
            logger.error(f"检查到有重启的情况")
            break
        if service.check_can_available():
            logger.error(f"检查到CAN总线丢失")
            break
        logger.info(f"调节电压从{max_voltage}到{min_voltage}，每隔1秒变化1V")
        service.change_voltage(max_, min_, 1, 1)
        logger.info(f"拍照检查工作是否正常")
        if service.take_a_picture_and_compare_light():
            logger.error(f"检查到工作不正常的情况")
            continue
        logger.info(f"检查是否有重启的现象")
        if service.judge_text_in_serial():
            logger.error(f"检查到有重启的情况")
            break
        if service.check_can_available():
            logger.error(f"检查到CAN总线丢失")
            break
    logger.info("关闭所有设备")
    service.close_devices()
    logger.info("过滤图片，后续人工检查")
    service.filter_saved_images()


def voltage_low_close_device(startup_time: int, low_voltage: float, normal_voltage_min: float, cycle_time: int,
                             step: float, interval: float):
    """
    电压关机测试
    :param startup_time: 开机启动完成需要的时间
    :param low_voltage:  低电压阈值（关机)
    :param normal_voltage_min: 正常电压的最低值
    :param cycle_time: 循环次数
    :param step:
    :param interval:
    :return:
    """
    # 阈值处理，
    min_ = low_voltage - 0.5
    max_ = normal_voltage_min + 0.5
    __prepare(startup_time)
    for i in range(cycle_time):
        logger.info(f"开始进行第{i + 1}次测试")
        logger.info(f"调节电压从{min_}到{max_}，每隔{interval}秒变化{step}V")
        service.change_voltage(min_, max_, step, interval)
        logger.info(f"拍照检查工作是否正常")
        if service.take_a_picture_and_compare_light():
            logger.error(f"检查到不正常的情况")
            continue
        if service.check_system_available():
            logger.error(f"系统没有恢复正常的情况")
            break
        if service.check_can_available():
            logger.error(f"检查到CAN总线丢失")
            break
        logger.info(f"调节电压从{min_}到{max_}，每隔{interval}秒变化{step}V")
        service.change_voltage(max_, min_, 1, 1)
        logger.info(f"拍照检查工作是否正常")
        if service.take_a_picture_and_compare_dark():
            logger.error(f"检查到不正常的情况")
            continue
        if not service.check_system_available():
            logger.error(f"系统仍然正常")
            break
        if service.check_can_available():
            logger.error(f"检查到CAN总线丢失")
            break
    logger.info("关闭所有设备")
    service.close_devices()
    logger.info("过滤图片，后续人工检查")
    service.filter_saved_images()


def voltage_low_close_display(startup_time: int, low_voltage: float, normal_voltage_min: float, cycle_time: int,
                              step: float, interval: float):
    """
    电压关屏测试
    :param startup_time: 开机启动完成需要的时间
    :param low_voltage:  低电压阈值（关机)
    :param normal_voltage_min: 正常电压的最低值
    :param cycle_time: 循环次数
    :param step:
    :param interval:
    :return:
    """
    # 阈值处理，
    min_ = low_voltage - 0.5
    max_ = normal_voltage_min + 0.5
    __prepare(startup_time)
    for i in range(cycle_time):
        logger.info(f"开始进行第{i + 1}次测试")
        logger.info(f"调节电压从{min_}到{max_}，每隔{interval}秒变化{step}V")
        service.change_voltage(min_, max_, step, interval)
        logger.info(f"拍照检查工作是否正常")
        if service.take_a_picture_and_compare_light():
            logger.error(f"检查到不正常的情况")
            continue
        if service.check_system_available():
            logger.error(f"系统没有恢复正常的情况")
            break
        if service.check_can_available():
            logger.error(f"检查到CAN总线丢失")
            break
        logger.info(f"调节电压从{min_}到{max_}，每隔{interval}秒变化{step}V")
        service.change_voltage(max_, min_, 1, 1)
        logger.info(f"拍照检查工作是否正常")
        if service.take_a_picture_and_compare_dark():
            logger.error(f"检查到不正常的情况")
            continue
        if service.check_system_available():
            logger.error(f"系统没有恢复正常的情况")
            break
        if service.check_can_available():
            logger.error(f"检查到CAN总线丢失")
            break
    logger.info("关闭所有设备")
    service.close_devices()
    logger.info("过滤图片，后续人工检查")
    service.filter_saved_images()

