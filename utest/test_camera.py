# -*- coding:utf-8 -*-
# --------------------------------------------------------  
# Copyright (C), 2016-2020, China TSP, All rights reserved
# --------------------------------------------------------                 
# @Name:        test_camera
# @Purpose:     test_camera
# @Author:      lizhe  
# @Created:     2020/2/18 10:30  
# --------------------------------------------------------
import os
from time import sleep

import pytest

from .logger import logger
from .utils import skip
from automotive.tools.camera import Camera
from automotive.tools.utils import Utils

camera = Camera()
temp_folder = os.path.join(os.getcwd(), "utest", "temp")


@pytest.fixture(scope="class", autouse=True)
def suite():
    logger.info("开始测试")
    camera.open_camera()
    yield suite
    camera.close_camera()
    logger.info("结束测试")


@pytest.mark.usefixtures("suite")
class TestUtils(object):

    def test_camera_test(self):
        camera.camera_test(0.1)

    @skip
    def test_get_picture_from_record(self):
        pass

    def test_get_property(self):
        camera_property = self.camera.get_property()
        assert isinstance(camera_property, (str, dict))

    def test_record_video(self):
        file_name = Utils().get_time_as_string()
        file = os.path.join(temp_folder, f"{file_name}.avi")
        logger.info(f"file is {file}")
        continue_time = 2
        camera.record_video(file)
        sleep(continue_time * 60)
        camera.stop_record()
        sleep(1)
        assert os.path.exists(file)

    @skip
    def test_reset_property(self):
        pass

    @skip
    def test_stop_record(self):
        pass

    def test_take_picture(self):
        file_name = Utils().get_time_as_string()
        file = os.path.join(temp_folder, f"{file_name}.jpg")
        logger.info(f"file is {file}")
        camera.take_picture(file)
        assert os.path.exists(file)
