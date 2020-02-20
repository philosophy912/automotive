# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, China TSP, All rights reserved
# --------------------------------------------------------
# @Name:        test_utils.py
# @Purpose:     utils测试类
# @Author:      lizhe
# @Created:     2020/02/13 9:19
# --------------------------------------------------------
import os

import pytest
from .logger import logger
from automotive.tools.utils import Utils
from .utils import skip

utils = Utils()
temp_folder = os.path.join(os.getcwd(), "utest", "temp")


@pytest.fixture(scope="class", autouse=True)
def suite():
    logger.info("开始测试")
    yield suite
    logger.info("结束测试")


@pytest.mark.usefixtures("suite")
class TestUtils(object):

    def test_get_time_as_string(self):
        year = "2020"
        time1 = utils.get_time_as_string()
        time2 = utils.get_time_as_string("%Y")
        time3 = utils.get_time_as_string("%Y-%m-%d-%H-%M-%S")
        assert time1[0:4] == year
        assert time2 == year
        assert "_" not in time3 and "-" in time3 and time3[0:4] == year

    def test_random_decimal(self):
        number = utils.random_decimal(1, 3)
        assert 1 < number < 3

    def test_random_int(self):
        number = utils.random_decimal(1, 6)
        assert 1 < number < 6

    def test_get_pinyin(self):
        name = "毛泽东"
        pinyin1 = utils.get_pin_yin(name, is_first=False)
        pinyin2 = utils.get_pin_yin(name, is_first=True)
        assert pinyin1 == "maozedong"
        assert pinyin2 == "mzd"

    def test_is_type_correct(self):
        a = "123"
        assert utils.is_type_correct(a, str)
        assert not utils.is_type_correct(a, int)

    def test_get_current_function_name(self):
        name = "test_get_current_function_name"
        assert utils.get_current_function_name() == name

    def test_is_sub_list(self):
        list1 = [1, 2, 3]
        list2 = [1, 2, 3, 4]
        list3 = [2, 3, 4]
        assert utils.is_sub_list(list1, list2)
        assert not utils.is_sub_list(list1, list3)

    def test_sleep(self):
        utils.sleep(5, "sleep")
        utils.sleep(5)

    def test_random_sleep(self):
        utils.random_sleep(3, 5)

    def test_text(self):
        utils.text("hello world")

    @skip
    def test_get_folder_path(self):
        pass

    @skip
    def test_zip_file(self):
        pass

    @skip
    def test_get_json_obj(self):
        pass

    @skip
    def test_read_yml_full(self):
        pass

    @skip
    def test_read_yml_safe(self):
        pass

    @skip
    def test_read_yml_un_safe(self):
        pass
