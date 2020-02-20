# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, China TSP, All rights reserved
# --------------------------------------------------------
# @Name:        Camera
# @Purpose:     摄像头相关操作
# @Author:      lizhe
# @Created:     2018/12/27 9:47
# --------------------------------------------------------
import os
import cv2
import time
import threading
import sounddevice as sd
from scipy.io import wavfile
from loguru import logger
from ..utils import Utils


class CameraProperty(object):

    def __init__(self):
        # 视频文件的当前位置， 初始值=-1.0
        self.pos_msec = -1.0
        # 当前帧， 初始值 = -1.0
        self.pos_frames = -1.0
        # 当前相对位置[0:从视频起始位置开始, 1:从视频结束位置开始]， 初始值=-1.0
        self.pos_avi_ratio = -1.0
        # 帧宽度, 初始值=640.0
        self.frame_width = 640.0
        # 帧高度, 初始值=480.0
        self.frame_height = 480.0
        # 帧数, 初始值=0.0
        self.fps = 0.0
        # 4字符编码的编码器， 初始值=-466162819.0
        self.fourcc = -466162819.0
        # 获取总帧数， 初始值=-1.0
        self.frame_count = -1.0
        # 视频格式， 初始值=-1.0
        self.format = -1.0
        # 布尔型标记图像是否应该被转换为RGB， 初始值=-1.0
        self.mode = -1.0
        # 亮度， 初始值=128.0, 仅Camera
        self.brightness = 128.0
        # 对比度， 初始值=32.0, 仅Camera
        self.contrast = 32.0
        # 饱和度， 初始值=32.0, 仅Camera
        self.saturation = 32.0
        # 色调， 初始值=175230088.0, 仅Camera
        self.hue = 175230088.0
        # 增益， 初始值=131.0, 仅Camera
        self.gain = 131.0
        # 曝光， 初始值=-5.0, 仅Camera
        self.exposure = -5.0
        # 布尔类型，表示图像是否需要转换成RGB， 初始值=-1.0
        self.convert_rgb = -1.0
        # 白平衡， 初始值=6150.0
        self.white_balance = 6150.0
        # 标定结果校准检验, 初始值=-1.0
        self.rectification = -1.0


class FrameID(object):

    def __init__(self):
        # 视频的当前位置（单位:ms）
        self.pos_msec = cv2.CAP_PROP_POS_MSEC
        # 视频的当前位置（单位：帧数，从0开始计）
        self.pos_frames = cv2.CAP_PROP_POS_FRAMES
        # 视频的当前位置（单位：比率， 0表示开始，1表示结尾）
        self.pos_avi_ratio = cv2.CAP_PROP_POS_AVI_RATIO
        # 帧宽度
        self.frame_width = cv2.CAP_PROP_FRAME_WIDTH
        # 帧高度
        self.frame_height = cv2.CAP_PROP_FRAME_HEIGHT
        # 帧速率
        self.fps = cv2.CAP_PROP_FPS
        # 4-字符表示的视频编码（如：’M‘, ’J‘, ’P‘, ’G‘）
        self.fourcc = cv2.CAP_PROP_FOURCC
        # 总帧数
        self.frame_count = cv2.CAP_PROP_FRAME_COUNT
        # retrieve().调用返回的矩阵格式
        self.format = cv2.CAP_PROP_FORMAT
        # 后端变量指示的当前捕获的模式
        self.mode = cv2.CAP_PROP_MODE
        # 明亮度（仅用于摄像头）
        self.brightness = cv2.CAP_PROP_BRIGHTNESS
        # 对比度（仅用于摄像头）
        self.contrast = cv2.CAP_PROP_CONTRAST
        # 饱和度（仅用于摄像头）
        self.saturation = cv2.CAP_PROP_SATURATION
        # 色调（仅用于摄像头）
        self.hue = cv2.CAP_PROP_HUE
        # 增益（仅用于摄像头）
        self.gain = cv2.CAP_PROP_GAIN
        # 曝光度 （仅用于摄像头）
        self.exposure = cv2.CAP_PROP_EXPOSURE
        # 是否应该将图像转化为RGB图像（布尔值）
        self.convert_rgb = cv2.CAP_PROP_CONVERT_RGB
        # 白平衡（暂不支持 v2.4.3)
        self.white_balance = cv2.CAP_PROP_WHITE_BALANCE_BLUE_U
        # 立体摄像头标定 (目前仅支持 DC1394 v 2.x 后端)
        self.rectification = cv2.CAP_PROP_RECTIFICATION
        self.monochrome = cv2.CAP_PROP_MONOCHROME
        self.sharpness = cv2.CAP_PROP_SHARPNESS
        # 自动曝光（仅用于摄像头）
        self.auto_exposure = cv2.CAP_PROP_AUTO_EXPOSURE
        self.gamma = cv2.CAP_PROP_GAMMA
        self.temperatrue = cv2.CAP_PROP_TEMPERATURE
        self.trigger = cv2.CAP_PROP_TRIGGER
        self.trigger_delay = cv2.CAP_PROP_TRIGGER_DELAY
        self.white_balance_red_v = cv2.CAP_PROP_WHITE_BALANCE_RED_V
        self.zoom = cv2.CAP_PROP_ZOOM
        self.focus = cv2.CAP_PROP_FOCUS
        self.guid = cv2.CAP_PROP_GUID
        self.iso_speed = cv2.CAP_PROP_ISO_SPEED
        self.backlight = cv2.CAP_PROP_BACKLIGHT
        self.pan = cv2.CAP_PROP_PAN
        self.tilt = cv2.CAP_PROP_TILT
        self.roll = cv2.CAP_PROP_ROLL
        self.iris = cv2.CAP_PROP_IRIS
        self.settings = cv2.CAP_PROP_SETTINGS
        self.buffersize = cv2.CAP_PROP_BUFFERSIZE
        self.autofocus = cv2.CAP_PROP_AUTOFOCUS
        self.sar_num = cv2.CAP_PROP_SAR_NUM
        self.sar_den = cv2.CAP_PROP_SAR_DEN
        self.backend = cv2.CAP_PROP_BACKEND
        self.channel = cv2.CAP_PROP_CHANNEL
        self.auto_wb = cv2.CAP_PROP_AUTO_WB
        self.wb_temperatrue = cv2.CAP_PROP_WB_TEMPERATURE


class Mark(object):

    def __init__(self):
        self.mark = False
        self.text = None
        self.location = 10, 60
        self.font_scale = 1
        self.RGB = 0, 0, 255
        self.thick = 1


class Camera(object):
    """
    摄像头工具类，用于拍照、拍视频等操作
    """

    def __init__(self):
        self.__utils = Utils()
        self.__capture = None
        self.__start_time = 0
        self.__current_time = 0
        # 录像停止标识符
        self.__stop_flag = False
        # 用于录像过程中拍照
        self.__frame = None
        # 摄像头的宽
        self.__width = 0
        # 摄像头的高
        self.__height = 0

    def __check_capture_status(self):
        """
        检查当前capture状态
        """
        if not self.__capture:
            raise RuntimeError("please init capture first")

    def __take_frame(self, name: str = 'test.png', gray=False):
        """
        获取一帧图像并保存

        :param name:保存照片的路径,如: D:/GIT/automatedtest_5X3/test.png

        :param gray: [False:拍摄彩色照片, True:拍摄灰度照片]
        """
        self.__check_capture_status()
        ret, frame = self.__capture.read()
        if ret:
            if gray:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            cv2.imwrite(name, frame)
        else:
            raise RuntimeError("Camera read frame error.")

    def __record(self, name: str, fps: float, width: int, height: int, codec: str, mark: Mark):
        """
        录制视频, 仅负责录制，

        :param name: 保存视频的路径, 如: D:/GIT/automatedtest_5X3/test.avi

        :param fps: 帧率设置[5.0, 30.0], default=20

        :param width: 录像视屏的分辨率

        :param height: 录像视屏的分辨率

        :param codec:录像的编码格式，目前只支持MJPG

        :param mark: Mark对象
        """
        # 设置fps，当fps在[5, 30]之外直接设置成20
        fps = fps if 5 <= fps <= 30 else 20
        # 各种编码格式每分钟压缩后大小:MJPG(80M),
        fourcc = cv2.VideoWriter_fourcc(*codec)
        out = cv2.VideoWriter(name, fourcc, fps, (width, height))
        while self.__capture.isOpened() and not self.__stop_flag:
            ret, self.__frame = self.__capture.read()
            # 如果需要生成水印则生成水印，水印内容就是时间戳
            if mark.mark:
                text = mark.text if mark.text else self.__utils.get_time_as_string()
                cv2.putText(self.__frame, text, mark.location,
                            cv2.FONT_HERSHEY_SIMPLEX, mark.font_scale, mark.RGB,
                            mark.thick, cv2.LINE_AA)
            if ret:
                out.write(self.__frame)
        out.release()

    def open_camera(self, camera_id: int = 0, frame_id: FrameID = FrameID()):
        """
        打开摄像头

        :param frame_id: 配置参数, 默认参数参考FrameID类

        :param camera_id:  摄像头序号， 默认为0
        """
        if self.__capture is not None:
            self.close_camera()
        self.__capture = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)
        self.__width = self.__capture.get(int(cv2.CAP_PROP_FRAME_WIDTH))
        self.__height = self.__capture.get(int(cv2.CAP_PROP_FRAME_HEIGHT))
        if not self.__capture.isOpened():
            logger.debug(f"camera is not opened, open it now")
            result = self.__capture.open(camera_id)
            if result:
                self.set_property(frame_id)
            else:
                raise RuntimeError(f"open camera[{camera_id}] failed")
        # logger.debug(f"camera open status {self.__capture.isOpened()}")

    def close_camera(self):
        """
        关闭摄像头
        """
        if self.__capture is not None:
            self.__capture.release()
            cv2.destroyAllWindows()

    def stop_record(self):
        """
        停止录制
        """
        self.__check_capture_status()
        self.__stop_flag = True

    def get_picture_from_record(self, path: str):
        """
        在录像过程中获取照片,与record_video配合使用

        :param path: 截图图片的绝对路径
        """
        cv2.imwrite(path, self.__frame)

    def take_picture(self, path: str, gray: bool = False):
        """
        拍照

        :param path:拍照保存的照片的路径包括文件名以及后缀

        :param gray: 是否拍摄灰度照片
        """
        self.__take_frame(path, gray)

    def record_video(self, name: str, fps: float = 20, total_time: float = None, width: int = None,
                     height: int = None, codec: str = 'MJPG', mark: Mark = Mark()):
        """
        录制视频(请在开始之前调用open_camera打开摄像头，并在结束后调用close_camera关闭摄像头)

        建议使用方法:

        self.open_camera()

        self.record_video(name, fps, width=640, height=480) # 开启了多线程的录制工作

        sleep(minutes * 60) # 或者进行其他的任务，

        self.stop_record() # 停止录像

        self.close_camera()

        Tips： total_time设置会在sleep(total_time * 60)后停止录像，但实际录制的时间与预期可能存在不一致的情况，所以不推荐使用
        total_time参数

        :param name: 保存视频的路径 如D:/GIT/automatedtest_5X3/test.avi

        :param fps: 帧率设置[5.0, 30.0], default=20

        :param total_time: 录制视频的总时长，单位：分钟, 录制时间并不准确。

        :param width: 录像视屏的分辨率

        :param height: 录像视屏的分辨率

        :param codec:录像的编码格式，目前只支持MJPG

        :param mark: 水印
        """
        # 如果没有设置则为读取到的高宽
        width = width if width and 0 <= width <= self.__width else self.__width
        height = height if height and 0 <= height <= self.__height else self.__height
        rec = threading.Thread(target=self.__record, args=(name, fps, width, height, codec, mark))
        rec.setDaemon(False)
        rec.start()
        # 只有设置了时间之后，到时间才会主动停止录像，否则不会主动停止，需要外部调用stop_record停止录像
        if total_time:
            self.__utils.sleep(total_time * 60)
            self.stop_record()

    def camera_test(self, wait: float = 2, frame_id: FrameID = FrameID()):
        """
        测试摄像头摄像，可用于调节摄像头距离，查看录像效果时，一般作为调试使用

        :param wait:等待时间，单位分钟，默认为2分钟

        :param frame_id: 摄像头参数
        """
        self.open_camera(frame_id=frame_id)
        start_time = time.time()
        while self.__capture.isOpened():
            ret, frame = self.__capture.read()
            if ret:
                cv2.imshow('f', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            check_time = time.time()
            if int(check_time - start_time) >= (wait * 60):
                break
        self.close_camera()

    def set_property(self, frame_id: FrameID = FrameID()):
        """
        设置摄像头参数

        :param frame_id: 摄像头参数类
        """
        for key, item in frame_id.__dict__.items():
            self.__capture.set(key, item)

    def reset_property(self):
        """
        重置所有摄像头参数为初始值
        """
        frame_id = FrameID()
        for key, item in frame_id.__dict__.items():
            self.__capture.set(key, item)

    def get_property(self, property_name: str = '') -> (str, dict):
        """
        获取摄像头当前参数设置

        :param property_name: 参考FrameID对象

            如果该参数为空则返回所有参数，否则返回对应参数

        :return: 摄像头对应的参数设置
        """
        if self.__capture is None:
            raise RuntimeError("please open camera first")
        frame_id = FrameID()
        if property_name in frame_id.__dict__.keys():
            return self.__capture.get(frame_id.__dict__[property_name])
        else:
            settings = dict()
            for key in frame_id.__dict__.keys():
                settings[key] = self.__capture.get(frame_id.__dict__[key])
            return settings


class MicroPhone(object):
    """
    音频操作，主要作用为录制音频
    """

    def __init__(self):
        # 采样率
        self.__sample_rate = 44100
        #  声音通道
        self.__channels = 2

    @staticmethod
    def __check_filename(filename: str) -> str:
        """
        检查filename是否符合规范，即是否是以wav结尾的文件
        :param filename:  保存文件名称
        :return: 返回实际的文件路径
        """
        if os.path.isdir(filename):
            return f"{filename}\\record.wav"
        elif filename.endswith(".wav"):
            return filename
        else:
            raise ValueError(f"file type only support .wav")

    def __record_audio(self, filename: str, record_time: int = 30):
        """
        采集声音

        :param filename: 保存文件名称

        :param record_time: 录音时间，单位s, 默认为30秒
        """
        record_file = self.__check_filename(filename)
        logger.debug(f"record_file is {record_file}")
        recoding = sd.rec(record_time * self.__sample_rate, samplerate=self.__sample_rate,
                          channels=self.__channels, blocking=True)
        logger.debug(f"writing record data to file[{record_file}]")
        wavfile.write(record_file, self.__sample_rate, recoding)

    def record_audio(self, filename: str, record_time: int = 30):
        """
        采集声音

        :param filename: 保存文件名称

        :param record_time: 录音时间，单位s, 默认为30秒
        """
        threads = threading.Thread(target=self.__record_audio, args=(filename, record_time))
        threads.setDaemon(False)
        threads.start()
