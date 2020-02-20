# -*- coding:utf-8 -*-
# --------------------------------------------------------  
# Copyright (C), 2016-2020, China TSP, All rights reserved
# --------------------------------------------------------                 
# @Name:        test_serial_port
# @Purpose:     TODO
# @Author:      lizhe  
# @Created:     2020/2/19 15:49  
# --------------------------------------------------------
import pytest

from automotive import SerialPort
from .logger import logger
from .utils import skip

serial_port = SerialPort()


@pytest.fixture(scope="class", autouse=True)
def suite():
    logger.info("开始测试")
    serial_port.connect("com9", 9600)
    yield suite
    serial_port.close()
    logger.info("结束测试")


@pytest.mark.usefixtures("suite")
class TestSerialPort(object):

    @skip
    def test_flush(self):
        pass

    @skip
    def test_flush_input(self):
        pass

    @skip
    def test_flush_output(self):
        pass

    @skip
    def test_get_connection_status(self):
        pass

    @skip
    def test_in_waiting(self):
        pass

    @skip
    def test_out_waiting(self):
        pass

    @skip
    def test_read_all(self):
        pass

    @skip
    def test_read_bytes(self):
        pass

    @skip
    def test_read_line(self):
        pass

    @skip
    def test_read_lines(self):
        pass

    @skip
    def test_reset_input_buffer(self):
        pass

    @skip
    def test_reset_output_buffer(self):
        pass

    @skip
    def test_send(self):
        pass

    @skip
    def test_send_break(self):
        pass

    @skip
    def test_set_buffer(self):
        pass
