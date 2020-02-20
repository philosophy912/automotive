# -*- coding:utf-8 -*-
# --------------------------------------------------------  
# Copyright (C), 2016-2020, China TSP, All rights reserved
# --------------------------------------------------------                 
# @Name:        test_ssh
# @Purpose:     TODO
# @Author:      lizhe  
# @Created:     2020/2/19 15:58  
# --------------------------------------------------------
import pytest

from automotive import USBRelay
from .logger import logger
from .utils import skip

relay = USBRelay()


@pytest.fixture(scope="class", autouse=True)
def suite():
    logger.info("开始测试")
    relay.open_relay_device()
    yield suite
    relay.close_relay_device()
    logger.info("结束测试")


@pytest.mark.usefixtures("suite")
class TestSSHUtils(object):

    @skip
    def test_all_relay_channel_off(self):
        pass

    @skip
    def test_all_relay_channel_on(self):
        pass

    @skip
    def test_one_relay_channel_off(self):
        pass

    @skip
    def test_one_relay_channel_on(self):
        pass
