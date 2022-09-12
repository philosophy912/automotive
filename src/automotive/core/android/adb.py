# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        adb.py
# @Author:      lizhe
# @Created:     2021/5/1 - 23:47
# --------------------------------------------------------
import os.path
import platform
from time import sleep
from typing import Sequence, Tuple, Optional

from automotive.utils.utils import Utils

from automotive.logger.logger import logger
from .common.enums import KeyCodeEnum


class ADB(object):
    """
    Android ADB相关的命令python化， 对于实际的测试活动中，更多的使用了click/screen_shot两个操作
    """

    @staticmethod
    def __execute(command: str) -> Sequence[str]:
        logger.debug(f"execute command [{command}]")
        stdout, stderr = Utils.exec_command_with_output(command, is_shell=True)
        return stdout.split("\r\n")

    def __adb_command(self, command: str, device_id: Optional[str] = None) -> Sequence[str]:
        """
        执行ADB命令，可以传入如 adb shell dumpsys window，如果传入了device_id则会加上-s参数
        :param command: adb命令
        :param device_id: 设备编号
        """
        if command[:3] == "adb":
            command = command[4:]
        if device_id:
            return self.__execute(f"adb -s {device_id} {command}")
        else:
            return self.__execute(f"adb {command}")

    def devices(self) -> Sequence[str]:
        """
        列出当前ADB连接的设备
        """
        return self.__execute("adb devices")

    def disconnect(self):
        """
        断开所有的ADB连接
        """
        self.__execute("adb disconnect")

    def start_server(self):
        """
        启动ADB服务
        """
        self.__execute("adb start-server")

    def kill_server(self):
        """
        杀掉ADB服务
        """
        self.__execute("adb kill-server")

    def version(self) -> Sequence[str]:
        """
        查看ADB的版本号
        """
        return self.__execute("adb version")

    def root(self):
        """
        ADB ROOT
        """
        self.__execute("adb root")

    def command(self, command: str, device_id: Optional[str] = None):
        return self.__adb_command(command=command, device_id=device_id)

    def push(self, local: str, remote: str, device_id: Optional[str] = None):
        """
        推送文件到服务器

        :param device_id: 设备编号

        :param local:  本地文件

        :param remote:  远程文件地址
        """
        self.__adb_command(f"push {local} {remote}", device_id)

    def pull(self, remote: str, local: str, device_id: Optional[str] = None):
        """
        拉取文件到本地电脑, 并删除远程文件

        :param remote: 远程文件地址

        :param local: 本地文件夹

        :param device_id: 设备编号
        """
        sys = platform.system()
        if sys == "Windows":
            local = f"\"{local}\""
        self.__adb_command(f"pull {remote} {local}", device_id)

    def remove(self, remote: str, device_id: Optional[str] = None):
        """
        删除源文件
        ：param remote:远程文件地址
        """
        self.__adb_command(f"shell rm {remote}", device_id)

    def pull_files(self, files: Sequence[str], local: str, device_id: Optional[str] = None):
        """
        拉取所有文件到本地电脑

        :param files: 文件列表

        :param local:  本地文件夹

        :param device_id: 设备编号
        """
        for file in files:
            self.pull(file, local, device_id)
            sleep(1)
        sleep(1)

    def remove_files(self, files: Sequence[str], device_id: Optional[str] = None):
        for file in files:
            self.remove(file, device_id)
            sleep(1)
        sleep(1)

    def input_text(self, text: str, device_id: Optional[str] = None):
        """
        输入文字到对话框中

        :param text: 文字内容

        :param device_id:  设备编号
        """
        self.__adb_command(f"shell input {text}", device_id)
        sleep(0.1)

    def click(self, x: int, y: int, display_id: Optional[int] = None, device_id: Optional[str] = None):
        """
        利用adb命令点击屏幕

        :param x: 坐标点x

        :param y: 坐标点y

        :param display_id: 要点击的屏幕

        :param device_id: 设备编号
        """
        if display_id and 1 <= display_id <= 3:
            # 利用传入的显示屏来生成用到的屏幕设备
            device = f"/dev/input/event{display_id - 1}"
            sendevent = "sendevent"
            commands = [f"{sendevent} {device} 3 53 {x}",
                        f"{sendevent} {device} 3 54 {y}",
                        f"{sendevent} {device} 1 330 1",
                        f"{sendevent} {device} 0 0 0",
                        f"{sendevent} {device} 1 330 0",
                        f"{sendevent} {device} 0 0 0"]
            for cmd in commands:
                self.__adb_command(cmd, device_id)
        else:
            self.__adb_command(f"shell input tap {x} {y}", device_id)
        sleep(0.1)

    def press_key(self, key_code: KeyCodeEnum, device_id: Optional[str] = None):
        """
        利用adb输入按键事件 设备编号

        :param key_code: 按键类型

        :param device_id:  device id
        """
        self.__adb_command(f"shell input keyevent {key_code.value}", device_id)
        sleep(0.1)

    def screen_cap(self, file_name: str, android_folder: str = "sdcard", device_id: Optional[str] = None):
        """
        截图并拉取到本地
        :param file_name: 文件名，全路径
        :param android_folder: 安卓系统内部路径
        :param device_id: 设备变好
        """
        logger.debug("目前不支持拉取文件到window根目录")
        folder, image_name = os.path.split(file_name)
        if folder == "":
            folder = os.getcwd()
        else:
            if folder.count("\\") == 1:
                folder = os.getcwd()
        if not image_name.endswith("jpg"):
            if "." in image_name:
                image_name = image_name.split(".")[0] + ".jpg"
            else:
                image_name = f"{image_name}.jpg"
        remote_path = f"/{android_folder}/{image_name}"
        logger.info(f"remote_path is {remote_path}")
        self.__adb_command(f"shell screencap -p {remote_path}", device_id)
        sleep(1)
        logger.info(f"file{image_name} will be pull in {folder}")
        self.pull(remote_path, folder, device_id)

    def screen_shot(self, image_name: str, count: int, interval_time: float = 0.1, display: Optional[int] = None,
                    device_id: Optional[str] = None):
        """
        截图操作, 当截图有多张的时候，以__下划线分割并加编号

        :param device_id: 设备编号

        :param image_name: 截图保存图片名称

        :param count: 截图张数

        :param interval_time: 截图间隔时间

        :param display: 屏幕序号
        """
        if image_name.endswith(".jpg"):
            image_name = image_name.split(".jpg")[0]
        for i in range(count):
            image_name = f"{image_name}__{i + 1}.jpg"
            if display:
                self.__adb_command(f"shell screencap -p -d {display} {image_name}", device_id)
            else:
                self.__adb_command(f"shell screencap -p {image_name}", device_id)
            sleep(interval_time)

    def screen_shot_area(self,
                         position: Tuple[int, int],
                         image_name: str,
                         count: int,
                         interval_time: float,
                         display: Optional[int] = None):
        """
        区域截图操作, 由于ADB不支持该操作，所以为空实现
        """
        raise RuntimeError("not support this function")

    def is_keyboard_show(self, device_id: Optional[str] = None) -> bool:
        """
        键盘是否显示

        :param device_id: 设备编号
        """
        results = "".join(self.__adb_command("shell dumpsys input_method", device_id))
        return "mInputShown=true" in results if results else False

    def start_app(self, package: str, activity: str, device_id: Optional[str] = None):
        """
        启动app

        :param device_id:设备编号

        :param package: package

        :param activity: activity
        """
        self.__adb_command(f"shell am start -n {package}/{activity}", device_id)

    def stop_app(self, package: str, device_id: Optional[str] = None):
        """
        关闭app并清理数据app

        :param device_id:设备编号

        :param package: package
        """
        self.__adb_command(f"shell am clear {package}", device_id)

    def force_stop_app(self, package: str, device_id: Optional[str] = None):
        """
        强制停止app

        :param device_id:设备编号

        :param package: package
        """
        self.__adb_command(f"shell am force-stop {package}", device_id)

    def install(self, local_apk: str, device_id: Optional[str] = None):
        """
        安装app
        :param local_apk: 要安装的文件

        :param device_id: 设备编号
        """
        if not local_apk.endswith("apk"):
            raise ValueError(f"local_apk[{local_apk}] not endswith apk")
        cmd = f"install {local_apk}"
        return self.__adb_command(cmd, device_id)

    def uninstall(self, package_name: str, keep_data: bool = False, device_id: Optional[str] = None):
        """
        卸载app
        :param device_id:设备编号

        :param package_name:包名

        :param keep_data: 是否保持文件内容

        :return:
        """
        cmd = f"uninstall {package_name}" if keep_data else f"uninstall -k {package_name}"
        self.__adb_command(cmd, device_id)

    @staticmethod
    def check_adb_connect(device_id: str):
        """
        检查adb是否连接成功, 连接True， 没连接False
        :param device_id: adb的设备序列号
        """
        result = os.popen('adb devices')
        res = result.read()
        logger.debug(fr"命令行: {res}")
        return device_id in res
