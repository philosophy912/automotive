# -*- coding:utf-8 -*-
# --------------------------------------------------------  
# Copyright (C), 2016-2020, China TSP, All rights reserved
# --------------------------------------------------------                 
# @Name:        study.py
# @Purpose:     TODO
# @Author:      lizhe  
# @Created:     2020/2/19 9:35  
# --------------------------------------------------------
import os
from time import sleep

from automotive.tools.camera.camera import Camera
from automotive.tools.utils import Utils

camera = Camera()

camera.open_camera()
file_name = Utils.get_time_as_string()
file = os.path.join(os.getcwd(), "temp", f"{file_name}.avi")
print(file)
camera.record_video(file, width=1280, height=720)
sleep(60)
camera.stop_record()
sleep(3)
camera.close_camera()
