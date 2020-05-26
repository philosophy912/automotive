# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, China TSP, All rights reserved
# --------------------------------------------------------
# @Name:        power_on&off
# @Purpose:     TODO
# @Author:      zhongtingwei
# @Created:     2020-04-03
# --------------------------------------------------------
import os
from time import sleep
from automotive import CANService, Camera, Utils, Images
from automotive.tools.onoff.actions.relay_actions import RelayActions

from utest.resources.dbc.faw import messages
from loguru import logger


def on_off_test(path: str, cycle_times: int, channel: int, threshold: int = 6):
    template = rf"{path}\template.bmp"
    images = Images()
    relay = RelayActions()
    camera = Camera()
    can = CANService(messages)
    # 初始化并上电拍摄
    can.open_can()
    can.send_can_signal_message(0x232, {"PowerMode": 0x4})
    relay.open()
    relay.channel_on(channel)
    sleep(2)
    # 调整摄像头位置并拍摄基准图片
    camera.camera_test()
    camera.open_camera()
    sleep(2)
    camera.take_picture(template)
    # 下电
    relay.channel_off(channel)
    sleep(5)
    # 循环测试
    cycle(relay, cycle_times, channel, path, camera, images, template, threshold)
    # 把屏幕点亮，关闭所有的设备
    camera.close_camera()
    logger.info(f"继电器继续开启15秒以便机器启动正常后关闭can和继电器")
    relay.channel_on(channel)
    sleep(15)
    relay.close()
    can.close_can()


def cycle(relay: RelayActions, cycle_times: int, channel: int, path: str, camera: Camera, images: Images, template: str,
          threshold: int):
    # 开始测试
    for i in range(cycle_times):
        logger.info(f"第{i + 1}次测试")
        relay.channel_on(channel)
        sleep(15)
        current_time = Utils.get_time_as_string()
        pic = rf"{path}\{i + 1}_{current_time}.png"
        camera.take_picture(pic)
        p, a, d = images.compare_by_hamming_distance(template, pic)
        if p > threshold or a > threshold or d > threshold:
            logger.error(f"template[{template}] is different of image[{pic}], p={p}, a={a}, d={d}")
            val = input(f"手工对比图片[{pic}]后,确定是否继续？继续请输入y....")
            if val == "y":
                logger.info("程序继续执行")
                continue
            else:
                confirm = input("确认退出, 确认请输入y....")
                if confirm == "y":
                    logger.info(f"程序退出")
                    return
                else:
                    continue
        relay.channel_off(channel)
        sleep(2)


screen_shot_path = fr"d:\temp\test\{Utils.get_time_as_string()}"
os.mkdir(screen_shot_path)
on_off_test(screen_shot_path, 100000, 1, threshold=6)

# camera = Camera()
# camera.open_camera()
# camera.take_picture(fr"{screen_shot_path}\screen_shot_path.bmp")
# sleep(2)
# camera.close_camera()
