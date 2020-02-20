# -*- coding:utf-8 -*-
# --------------------------------------------------------  
# Copyright (C), 2016-2020, China TSP, All rights reserved
# --------------------------------------------------------                 
# @Name:        test_android
# @Purpose:     test_android
# @Author:      lizhe  
# @Created:     2020/2/19 17:29  
# --------------------------------------------------------
import pytest
from .logger import logger
from .utils import skip


@pytest.fixture(scope="class", autouse=True)
def suite():
    logger.info("开始测试")
    yield suite
    logger.info("结束测试")


@pytest.mark.usefixtures("suite")
class TestAppiumPythonClient(object):
    pass


@pytest.mark.usefixtures("suite")
class TestADBUtils(object):

    @skip
    def test_application_operate(self):
        pass

    @skip
    def test_execute_adb_cmd(self):
        pass

    @skip
    def test_get_cpu_info(self):
        pass

    @skip
    def test_get_memory_info(self):
        pass

    @skip
    def test_is_visible(self):
        pass

    @skip
    def test_press_key_event(self):
        pass

    @skip
    def test_send_event(self):
        pass

    @skip
    def test_set_keyboard(self):
        pass
