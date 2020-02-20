# -*- coding:utf-8 -*-
# --------------------------------------------------------  
# Copyright (C), 2016-2020, China TSP, All rights reserved
# --------------------------------------------------------                 
# @Name:        test_demo
# @Purpose:     TODO
# @Author:      lizhe  
# @Created:     2020/2/18 10:30  
# --------------------------------------------------------

import pytest

from automotive import Images
from .logger import logger
from .utils import skip

images = Images()


@pytest.fixture(scope="class", autouse=True)
def suite():
    logger.info("开始测试")
    yield suite
    logger.info("结束测试")


@pytest.mark.usefixtures("suite")
class TestImageCompare(object):
    @skip
    def test_compare_image_blink(self):
        pass

    @skip
    def test_compare_image_dark(self):
        pass

    @skip
    def test_compare_image_light(self):
        pass

    @skip
    def test_get_origin_images(self):
        pass


@pytest.mark.usefixtures("suite")
class TestScreenshot(object):

    @skip
    def test_screen_shot(self):
        pass

    @skip
    def test_screen_shot_area(self):
        pass


@pytest.mark.usefixtures("suite")
class TestImages(object):
    @skip
    def test_compare_by_hamming_distance(self):
        pass

    @skip
    def test_compare_by_matrix(self):
        pass

    @skip
    def test_compare_by_matrix_exclude(self):
        pass

    @skip
    def test_compare_by_matrix_in_same_area(self):
        pass

    @skip
    def test_convert_position(self):
        pass

    @skip
    def test_cut_image(self):
        pass

    @skip
    def test_get_position_in_image(self):
        pass

    @skip
    def test_is_image_contain(self):
        pass

    @skip
    def test_rectangle_image(self):
        pass
