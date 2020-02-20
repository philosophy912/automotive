# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, China TSP, All rights reserved
# --------------------------------------------------------
# @Name:        on_off.py
# @Purpose:     OnOff类，用于执行测试用例
# @Author:      lizhe
# @Created:     2020/02/06 20:49
# --------------------------------------------------------
import os
from loguru import logger
from automotive.tools import Utils
from .services.service import Service
from .services.test_case import OnOffTestCase


class OnOff(object):
    """
    用例执行类

    一般使用用到这个类，需要放置两类配置文件到文件夹下
    1、config类配置 2、testcase类配置

    文件必须以config开头的yml文件和以test_case开头的yml文件。

    可以配对使用，如: config_test.yml和test_case_test.yml两个文件就是一对， 当没有配置配对的config文件，
    会以默认的config文件作为test_case的配置文件使用

    config.yml配置如下:

    # 设备相关配置

    device_config:

      # konstanter配置

      konstanter: [com9, 115200]

      # it6831的配置

      it6831: [com10, 9600]

      # serial的配置

      serial: [com7, 9600]

      # can的配置

      can:

        # dbc转换的来的文件

        message: automatedtest.lib.can.dbc.gse_3j2

        # 倒档配置

        r_shift: [0x256, signal_name, 1]

        # 空挡配置

        n_shift: [0x256, signal_name, 1]

        # 快速休眠

        fast_sleep: [0x256, signal_name, 1, 5]

    # 环境相关配置

    environment:

      # 配置电源

      battery: it6831

      # 配置ACC

      acc: konstanter

      # 配置倒车

      reverse: 5

      # 配置休眠

      bus_sleep: fast_sleep

      # 配置摄像头（都带默认配置)

      camera:

        # 默认调整摄像头时间

        camera_test: 2

        # 图片对比的阈值

        compare_threshold: 10

        # 图片过滤器的阈值

        filter_threshold: 10

        # 基准图片配置(亮图和暗图)

        "base": ["light_template.png", "dark_template.png"]

      # 配置基准路径

      base_path: D:\\Workspace\\python\\automatedtest\\res\\project\\temp\\screenshot

    test_case.yml配置如下:

        # 前置准备

        prepare:

          - init_pic_save_path

          - open_devices

        # 前置条件

        precondition:

          - init_template_light_pic

          - battery_on

        # 操作步骤

        step:

          # 循环次数

          loop_time: 5

          # 循环步骤

          loop:

            - text: ACC ON

            - acc_on

            - sleep 15

            - reverse_on

            # - take_a_picture （只拍照，拍照带对比选择take_a_picture_and_compare_light）

            - break: take_a_picture_and_compare_light

        # 结果检查

        result:

          - close_devices

          - filter_saved_images

    """

    def __init__(self, folder: str):
        """
        初始化

        :param folder: 用例所在的文件夹
        """
        files = self.__get_files(folder)
        # test case必须以test_case开头， config必须以config开头
        # test_case和config必须配对使用，但如果只有test_case没有config则使用默认的config.yml文件
        self.__test_cases = self.__filter_test_case(files)

    @staticmethod
    def __get_files(folder: str):
        """
        获取文件夹下所有的yml文件
        """
        files = os.listdir(folder)
        return list(filter(lambda x: x.endswith(".yml"), files))

    def __run_test_case(self, test_case_file: str, config: str):
        """
        执行测试用例

        :param test_case_file: 测试用例文件

        :param config: config文件
        """
        content = Utils().read_yml_full(test_case_file)
        test_case = OnOffTestCase()
        # 从设置到类中
        test_case.update(content)
        # 检查设置的是否正确
        test_case.check()
        service = Service(config)
        try:
            logger.info("开始执行测试用例prepare部分")
            for action in test_case.prepare:
                self.__run_actions(action, service)
            logger.info("开始执行测试用例precondition部分")
            for action in test_case.precondition:
                self.__run_actions(action, service)
            loop_time = test_case.step["loop_time"]
            logger.info(f"开始循环执行测试用例step中的loop部分，循环次数为{loop_time}")
            for i in range(loop_time):
                logger.info(f"开始第{i + 1}次循环")
                for action in test_case.step["loop"]:
                    result = self.__run_actions(action, service)
                    if isinstance(result, bool) and not result:
                        logger.critical(f"比较图片失败，跳出循环")
                        break
                # 跳出最外层循环
                else:
                    continue
                break
            logger.info("开始执行测试用例result部分")
            for action in test_case.result:
                self.__run_actions(action, service)
        # 捕获到异常后直接调用service关闭所有设备
        except Exception as e:
            logger.exception(e)
            getattr(service, "close_devices")()

    @staticmethod
    def __run_actions(action: (str, dict), service: Service):
        """
        返回执行结果Any
        """
        if isinstance(action, str):
            logger.info(f"执行函数[{action}]")
            return getattr(service, action)()
        elif isinstance(action, dict):
            for key, item in action.items():
                logger.info(f"执行函数[{key}], 参数是[{item}]")
                if isinstance(item, list):
                    return getattr(service, key)(*item)
                else:
                    return getattr(service, key)(item)

    @staticmethod
    def __filter_test_case(files: list) -> dict:
        """
        按照定义的规则过滤文件并组织成键值对

        :param files: yml文件

        :return: {key-value}

            :key: test_case文件

            :value: config文件
        """
        test_case_dict = dict()
        # 过滤出来test case开头的yml文件
        test_cases = list(filter(lambda x: x.startswith("test_case"), files))
        logger.debug(f"test_cases  = {test_cases}")
        # 过滤出来config开头的yml文件
        configs = list(filter(lambda x: x.startswith("config"), files))
        logger.debug(f"configs  = {configs}")
        # config文件是否存在
        default_config = "config.yml" in configs
        if default_config:
            configs.remove("config.yml")
        logger.debug(f"after remove configs  = {configs}")
        # 去掉了config和yml的名字
        config_names = list(map(lambda x: x[len("config"):-len(".yml")], configs))
        for test_case in test_cases:
            # 去掉了test_case和yml后缀的名字
            test_case_name = test_case[len("test_case"):-len(".yml")]
            if test_case_name in config_names:
                test_case_dict[test_case] = f"config{test_case_name}.yml"
            # 有默认的config则用默认的config，便于一个config多个test_case使用
            elif default_config:
                test_case_dict[test_case] = "config.yml"
        logger.debug(f"collect yml files [{test_case_dict}]")
        return test_case_dict

    def run(self):
        """
        执行测试用例
        """
        for test_case, config in self.__test_cases.items():
            logger.info(f"执行测试用例[{test_case}]， 对应的配置文件是[{config}]")
            self.__run_test_case(test_case, config)
