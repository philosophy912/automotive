# -*- coding:utf-8 -*-
# --------------------------------------------------------  
# Copyright (C), 2016-2020, China TSP, All rights reserved
# --------------------------------------------------------                 
# @Name:        test_konstanter
# @Purpose:     TODO
# @Author:      lizhe  
# @Created:     2020/2/18 11:35  
# --------------------------------------------------------
import pytest
from time import sleep
from .logger import logger
from .utils import skip
from automotive.tools.battery import KonstanterControl

control = KonstanterControl("com9")


@pytest.fixture(scope="class", autouse=True)
def suite():
    logger.info("开始测试")
    yield suite
    control.close()
    logger.info("结束测试")


@pytest.mark.usefixtures("suite")
class TestKonstanterControl(object):

    @skip
    def test_get(self):
        pass

    def test_output_enable(self):
        control.output_enable(True)
        sleep(5)
        control.output_enable(False)

    def test_set_limit(self):
        control.set_limit()

    def test_set_raise_down(self):
        begin, last, interrupt = 2, 12, 1
        times = (last - begin) / interrupt
        start, middle, end = self.control.set_raise_down(begin, last, interrupt, 0.2)
        assert start == 11
        assert middle == start + times
        assert end == middle + times

    def test_set_user_voltages(self):
        voltages = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        start, end = control.set_user_voltages(voltages, 1)
        assert start == 11
        assert end == start + len(voltages) - 1

    def test_set_voltage_current(self):
        control.set_voltage_current(12, 10)

    def test_start(self):
        voltages = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        start, end = control.set_user_voltages(voltages, 1)
        control.start(start, end)
