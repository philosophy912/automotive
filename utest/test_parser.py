# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, China TSP, All rights reserved
# --------------------------------------------------------
# @Name:        test_parser.py
# @Purpose:     todo
# @Author:      lizhe
# @Created:     2020/04/12 22:14
# --------------------------------------------------------
import pytest
from .logger import logger
from automotive.can.interfaces.parser import Parser
from utest.resources.dbc.b31 import messages as b31_msg
from utest.resources.dbc.dayun import messages as dayun_msg
from utest.resources.dbc.faw import messages as faw_msg
from utest.resources.dbc.gse import messages as gse_msg
from utest.resources.dbc.s101 import messages as s101_msg

parser = Parser()


@pytest.fixture(scope="class", autouse=True)
def suite():
    logger.info("开始测试")
    yield suite
    logger.info("结束测试")


class TestParser(object):

    def test_b31(self):
        id_msg, name_msg = parser.get_message(b31_msg)
        msg1 = name_msg["HU_ESPSwch"]
        msg1.signals['HU_TowMod'].physical_value = 3
        msg1.signals['HU_HDCSwch'].physical_value = 3
        msg1.signals['HU_ACUWarnLampStsFb'].physical_value = 2
        msg1.signals['HU_ESPSwch'].physical_value = 2
        msg1.signals['HU_AutoHoldSwch'].physical_value = 1
        msg1.signals['HU_TotlOdo'].physical_value = 96231.1
        msg1.update(True)
        assert [0xaf, 0x40, 0x0, 0x0, 0x0, 0xe, 0xaf, 0x7] == msg1.data

    def test_dayun(self):
        id_msg, name_msg = parser.get_message(dayun_msg)

    def test_faw(self):
        id_msg, name_msg = parser.get_message(faw_msg)
        msg1 = name_msg["ABS_1"]
        msg1.signals['Checksum_ABS_1'].physical_value = 52
        msg1.signals['VehicleSpeed'].physical_value = 13983
        msg1.signals['LiveCounter_ABS_1'].physical_value = 6
        msg1.update(True)
        assert [0x34, 0x0, 0x0, 0x0, 0x0, 0x9f, 0x36, 0x60] == msg1.data
        msg1 = name_msg["ADV_1"]
        msg1.signals['Checksum_ADV_1'].physical_value = 65
        msg1.signals['ADV_ParkStatus'].physical_value = 3
        msg1.signals['LiveCounter_ADV_1'].physical_value = 10
        msg1.update(True)
        assert [0x41, 0x30, 0x0, 0x0, 0x0, 0x0, 0x0, 0xA0] == msg1.data
        msg1 = name_msg["ADV_5"]
        msg1.signals['LiveCounter_ADV_5'].physical_value = 1
        msg1.signals['ADV_HPAParkOutAvaialble'].physical_value = 1
        msg1.signals['ADV_HPAParkInAvaialble'].physical_value = 1
        msg1.signals['ADV_HPANaviAvaialble'].physical_value = 1
        msg1.signals['ADV_AVPParkOutAvaialble'].physical_value = 1
        msg1.signals['ADV_AVPParkInAvaialble'].physical_value = 1
        msg1.signals['ADV_AVPNaviAvaialble'].physical_value = 1
        msg1.signals['Checksum_ADV_5'].physical_value = 52
        msg1.update(True)
        assert [0X34, 0x0, 0x0, 0x9C, 0x3, 0x0, 0x0, 0x10] == msg1.data
        msg1 = name_msg["BCM1_1"]
        msg1.signals['HighBeamSt'].physical_value = 1
        msg1.signals['LowBeamSt'].physical_value = 1
        msg1.signals['PositionLightSt'].physical_value = 1
        msg1.update(True)
        assert [0X41, 0x2, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0] == msg1.data
        msg1 = name_msg["HU_14"]
        msg1.signals['DisplayTheme'].physical_value = 7
        msg1.update(True)
        assert [0X0, 0x0, 0x0, 0x7, 0x0, 0x0, 0x0, 0x0] == msg1.data

    def test_gse(self):
        id_msg, name_msg = parser.get_message(gse_msg)
        msg1 = name_msg["EPBR_150h"]
        msg1.signals['EPB_Brake_Lights_Request_R'].physical_value = 1
        msg1.signals['EPB_SwitchSta_R'].physical_value = 3
        msg1.signals['EPB_WarnLampSta_R'].physical_value = 3
        msg1.signals['EPB_ParkLampSta_R'].physical_value = 3
        msg1.signals['EPB_ActuatorSt_R'].physical_value = 3
        msg1.signals['EPB_DisplayMsgID_R'].physical_value = 3
        msg1.signals['EPB_150h_RollingCounter'].physical_value = 4
        msg1.signals['EPB_150h_CheckSUM'].physical_value = 65
        msg1.update(True)
        assert [0xfe, 0x18, 0x0, 0x3, 0x0, 0x0, 0x4, 0x41] == msg1.data

    def test_s101(self):
        id_msg, name_msg = parser.get_message(s101_msg)
