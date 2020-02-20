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

from automotive import SSHUtils
from .logger import logger
from .utils import skip

ssh = SSHUtils()


@pytest.fixture(scope="class", autouse=True)
def suite():
    logger.info("开始测试")
    ssh.connect("10.100.193.59", "lizhe", "lizhe")
    yield suite
    ssh.disconnect()
    logger.info("结束测试")


@pytest.mark.usefixtures("suite")
class TestSSHUtils(object):

    @skip
    def test_exec_command(self):
        pass
