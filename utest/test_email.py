# -*- coding:utf-8 -*-
# --------------------------------------------------------  
# Copyright (C), 2016-2020, China TSP, All rights reserved
# --------------------------------------------------------                 
# @Name:        test_email
# @Purpose:     test_email
# @Author:      lizhe  
# @Created:     2020/2/19 15:18  
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
class TestEmail(object):

    @skip
    def test_send_email(self):
        pass

    @skip
    def test_receive_emails(self):
        pass

    @skip
    def test_receive_latest_email(self):
        pass
