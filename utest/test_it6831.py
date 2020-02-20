# -*- coding:utf-8 -*-
# --------------------------------------------------------  
# Copyright (C), 2016-2020, China TSP, All rights reserved
# --------------------------------------------------------                 
# @Name:        test_it6831
# @Purpose:     TODO
# @Author:      lizhe  
# @Created:     2020/2/18 10:30  
# --------------------------------------------------------
import pytest
from time import sleep

from .logger import logger
from .utils import skip
from automotive.tools.battery.it6831 import IT6831

it6831 = IT6831("com11")


@pytest.fixture(scope="class", autouse=True)
def suite():
    logger.info("开始测试")
    it6831.set_power_control_mode(True)
    yield suite
    it6831.close()
    logger.info("结束测试")


@pytest.mark.usefixtures("suite")
class TestIT6831(object):

    def test_get_all_status(self):
        status = it6831.get_all_status()
        assert status.remote

    def test_get_power_calibrate_protect_status(self):
        assert it6831.get_power_calibrate_protect_status()

    @skip
    def test_set_current_value(self):
        pass

    @skip
    def test_set_power_calibrate_protect_status(self):
        pass

    def test_set_power_output_status(self):
        it6831.set_power_output_status(False)
        sleep(5)
        it6831.set_power_output_status(True)

    @skip
    def test_set_power_supply_address(self):
        pass

    @skip
    def test_set_voltage_limit(self):
        pass

    def test_set_voltage_value(self):
        it6831.set_power_output_status(True)
        it6831.set_voltage_value(5)
        sleep(5)
        it6831.set_voltage_value(12)
        sleep(5)
        it6831.set_power_output_status(False)
