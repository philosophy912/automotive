# -*- coding:utf-8 -*-
# --------------------------------------------------------  
# Copyright (C), 2016-2020, China TSP, All rights reserved
# --------------------------------------------------------                 
# @Name:        test_demo
# @Purpose:     test_demo
# @Author:      lizhe  
# @Created:     2020/2/18 10:30  
# --------------------------------------------------------
import pytest
import os

from automotive.tools.onoff import CameraActions, CanActions, It6831Actions, KonstanterActions, RelayActions, \
    SerialActions
from automotive.tools.onoff.config import Config
from .logger import logger
from .utils import skip
from .resources.gse_3j2 import messages

resources = os.path.join(os.getcwd(), "utest", "resources")
config_yml = os.path.join(resources, "config.yml")
test_case_yml = os.path.join(resources, "test_case.yml")

camera_actions = CameraActions()
can_actions = CanActions(messages)
it6831_actions = It6831Actions("com11", 9600)
konstanter_actions = KonstanterActions("com9", 19200)
relay_actions = RelayActions()
serial_actions = SerialActions("com11", 9600)
config = Config(config_yml)


@pytest.fixture(scope="class", autouse=True)
def suite():
    logger.info("开始测试")
    camera_actions.open()
    can_actions.open()
    it6831_actions.open()
    konstanter_actions.open()
    relay_actions.open()
    serial_actions.open()
    yield suite
    serial_actions.close()
    relay_actions.close()
    konstanter_actions.close()
    it6831_actions.close()
    can_actions.close()
    camera_actions.close()
    logger.info("结束测试")


@pytest.mark.usefixtures("suite")
class TestOnOff(object):
    pass


@pytest.mark.usefixtures("suite")
class TestCameraActions(object):

    @skip
    def test_camera_test(self):
        pass

    @skip
    def test_init_template_image(self):
        pass

    @skip
    def test_get_temp_pic(self):
        pass

    @skip
    def test_take_a_pic(self):
        pass


@pytest.mark.usefixtures("suite")
class TestCanActions(object):

    @skip
    def test_bus_sleep(self):
        pass

    @skip
    def test_check_can_available(self):
        pass

    @skip
    def test_reverse_off(self):
        pass

    @skip
    def test_reverse_on(self):
        pass


@pytest.mark.usefixtures("suite")
class TestIt6831Actions(object):

    @skip
    def test_change_voltage(self):
        pass

    @skip
    def test_off(self):
        pass

    @skip
    def test_on(self):
        pass

    @skip
    def test_set_voltage_current(self):
        pass


@pytest.mark.usefixtures("suite")
class TestKonstanterActions(object):

    @skip
    def test_change_voltage(self):
        pass

    @skip
    def test_off(self):
        pass

    @skip
    def test_on(self):
        pass

    @skip
    def test_set_voltage_current(self):
        pass

    @skip
    def test_adjust_voltage_by_curve(self):
        pass


@pytest.mark.usefixtures("suite")
class TestRelayActions(object):

    @skip
    def test_channel_off(self):
        pass

    @skip
    def test_channel_on(self):
        pass

    @skip
    def test_fast_on_off(self):
        pass


@pytest.mark.usefixtures("suite")
class TestSerialActions(object):

    @skip
    def test_clean_serial_data(self):
        pass

    @skip
    def test_judge_text_in_serial(self):
        pass


@pytest.mark.usefixtures("suite")
class TestConfig(object):

    @skip
    def test_check(self):
        pass


@pytest.mark.usefixtures("suite")
class TestCurve(object):

    @skip
    def test_get_voltage_by_csv(self):
        pass


@pytest.mark.usefixtures("suite")
class TestOnOff(object):
    @skip
    def test_run(self):
        pass
