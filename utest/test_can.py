# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, China TSP, All rights reserved
# --------------------------------------------------------
# @Name:        test_can.py
# @Purpose:     can单元测试
# @Author:      lizhe
# @Created:     2020/02/13 15:58
# --------------------------------------------------------
import pytest
from .logger import logger
from automotive import CANService
from utest.resources.gse_3j2 import messages
from .utils import skip

can_service = CANService(messages)


@pytest.fixture(scope="class", autouse=True)
def suite():
    logger.info("开始测试")
    can_service.open_can()
    yield suite
    can_service.close_can()
    logger.info("结束测试")


class TestCanService(object):

    @skip
    def test_clear_stack_data(self):
        pass

    @skip
    def test_is_can_bus_lost(self):
        pass

    @skip
    def test_is_lost_message(self):
        pass

    @skip
    def test_is_msg_value_changed(self):
        pass

    @skip
    def test_is_open(self):
        pass

    @skip
    def test_is_signal_value_changed(self):
        pass

    @skip
    def test_receive_can_message(self):
        pass

    @skip
    def test_resume_transmit(self):
        pass

    @skip
    def test_send_can_message(self):
        pass

    @skip
    def test_send_can_message_by_id_or_name(self):
        pass

    @skip
    def test_send_can_signal_message(self):
        pass

    @skip
    def test_stop_transmit(self):
        pass
