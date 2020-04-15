# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, China TSP, All rights reserved
# --------------------------------------------------------
# @Name:        adb_utils
# @Purpose:     adb相关的命令
# @Author:      liluo
# @Created:     2019/8/21 9:47
# --------------------------------------------------------
import subprocess as sp
from loguru import logger


class ADBUtils(object):
    """
        adb 工具类，主要用于处理ADB相关的命令
    """

    @staticmethod
    def __operation(keyboards: list, flag: bool):
        """
        执行操作

        :param keyboards: 操作关键字

        :param flag:

            True: enable

            False: disable
        """
        for keyboard in keyboards:
            if flag:
                cmd = "enable"
            else:
                cmd = "disable"
            execute = "adb shell ime " + cmd + " " + keyboard
            sp.Popen(execute, stdout=sp.PIPE, stderr=sp.PIPE).wait()

    @staticmethod
    def execute_adb_cmd(cmd: str) -> bool:
        """
        执行ADB命令，需要传入完整的ADB命令，如adb devices。

        如： execute_adb_cmd("adb devices")

        :param cmd: 完整的adb命令

        :return:
            True: 操作成功

            False: 操作失败
        """
        logger.debug(f"command is {cmd}")
        result = sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.PIPE).wait()
        return True if result == 0 else False

    def application_operate(self, operate: str, package: str) -> bool:
        """
        针对app进行启动、 停止、清除等操作。

        打开：使用 application_operate("start", "com.baidu.input/.ImeService")

        强制停止: application_operate("force-stop", "com.baidu.input")

        关闭并清理数据: application_operate("clear", "com.baidu.input")

        :param operate:
            start: 打开app

            force-stop: 强制停止app

            clear: 关闭app并清理数据

        :param package:
            打开app时需要传package/activity，其他均只需要package

        :return:
            True: 操作成功

            False: 操作失败
        """
        operate = operate.lower()
        operates = "start", "force-stop", "clear"
        if operate not in operates:
            raise ValueError(f"operate is {operate}, only support {operates}")
        if operate == "start":
            cmd = "adb shell am start -n " + package
        elif operate == "force-stop":
            cmd = "adb shell am force-stop " + package
        else:
            cmd = "adb shell pm clear " + package
        return self.execute_adb_cmd(cmd)

    @staticmethod
    def tap_event(x: int, y: int):
        """
        通过ADB input tap <x> <y>的方式点击屏幕

        :param x: 被点击点的X坐标位置

        :param y: 被点击点的y坐标位置
        """
        cmd = f"adb input tap {x}, {y}"
        sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.PIPE).wait()

    @staticmethod
    def send_event(x: int, y: int, display_id: int = 1):
        """
        通过屏幕的坐标点进行点击， 本质为sendevent的模拟， 即发送点击信号

        最大支持3个屏幕，以实际支持的屏幕为准，否则点击仍然是无效的

        :param x: 被点击点的X坐标位置

        :param y: 被点击点的y坐标位置

        :param display_id: 屏幕序号
        """
        if not 1 <= display_id <= 3:
            raise ValueError(f"display id only support [1,3] but now value is {display_id}")
        # 利用传入的显示屏来生成用到的屏幕设备
        device = f"/dev/input/event{display_id - 1}"
        commands = ["sendevent " + device + " 3 53 " + str(x),
                    "sendevent " + device + " 3 54 " + str(y),
                    "sendevent " + device + " 1 330 1",
                    "sendevent " + device + " 0 0 0",
                    "sendevent " + device + " 1 330 0 ",
                    "sendevent " + device + " 0 0 0"]
        for command in commands:
            cmd = "adb shell " + command
            sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.PIPE).wait()

    @staticmethod
    def press_key_event(key_code: str, device_id: str):
        """
        通过ADB命令的方式模拟输入按键

        :param key_code: 按键对应的值

            KEYCODE_UNKNOWN=0;|KEYCODE_DPAD_CENTER=23;|KEYCODE_R=46;|KEYCODE_MINUS=69;

            KEYCODE_SOFT_LEFT=1;|KEYCODE_VOLUME_UP=24;|KEYCODE_S=47;|KEYCODE_EQUALS=70;

            KEYCODE_SOFT_RIGHT=2;|KEYCODE_VOLUME_DOWN=25;|KEYCODE_T=48;|KEYCODE_LEFT_BRACKET=71;

            KEYCODE_HOME=3;|KEYCODE_POWER=26;| KEYCODE_U=49;|KEYCODE_RIGHT_BRACKET=72;

            KEYCODE_BACK=4;|KEYCODE_CAMERA=27;|KEYCODE_V=50;|KEYCODE_BACKSLASH=73;

            KEYCODE_CALL=5;|KEYCODE_CLEAR=28;|KEYCODE_W=51;|KEYCODE_SEMICOLON=74;

            KEYCODE_ENDCALL=6;|KEYCODE_A=29;|KEYCODE_X=52;|KEYCODE_APOSTROPHE=75;

            KEYCODE_0=7;|KEYCODE_B=30;|KEYCODE_Y=53;|KEYCODE_SLASH=76;

            KEYCODE_1=8;|KEYCODE_C=31;|KEYCODE_Z=54;|KEYCODE_AT=77;

            KEYCODE_2=9;|KEYCODE_D=32;|KEYCODE_COMMA=55;|KEYCODE_NUM=78;

            KEYCODE_3=10;|KEYCODE_E=33;|KEYCODE_PERIOD=56;|KEYCODE_HEADSETHOOK=79;

            KEYCODE_4=11;|KEYCODE_F=34;|KEYCODE_ALT_LEFT=57;|KEYCODE_FOCUS=80;

            KEYCODE_5=12;|KEYCODE_G=35;|KEYCODE_ALT_RIGHT=58;|KEYCODE_PLUS=81;

            KEYCODE_6=13;|KEYCODE_H=36;|KEYCODE_SHIFT_LEFT=59;|KEYCODE_MENU=82;

            KEYCODE_7=14;|KEYCODE_I=37;|KEYCODE_SHIFT_RIGHT=60;|KEYCODE_NOTIFICATION=83;

            KEYCODE_8=15;|KEYCODE_J=38;|KEYCODE_TAB=61;|KEYCODE_SEARCH=84;

            KEYCODE_9=16;|KEYCODE_K=39;|KEYCODE_SPACE=62;|KEYCODE_MEDIA_PLAY_PAUSE=85;

            KEYCODE_STAR=17;| KEYCODE_L=40;|KEYCODE_SYM=63;|KEYCODE_MEDIA_STOP=86;

            KEYCODE_POUND=18;|KEYCODE_M=41;|KEYCODE_EXPLORER=64;|KEYCODE_MEDIA_NEXT=87;

            KEYCODE_DPAD_UP=19;|KEYCODE_N=42;|KEYCODE_ENVELOPE=65;|KEYCODE_MEDIA_PREVIOUS=88;

            KEYCODE_DPAD_DOWN=20;|KEYCODE_O=43;|KEYCODE_ENTER=66;|KEYCODE_MEDIA_REWIND=89;

            KEYCODE_DPAD_LEFT=21;|KEYCODE_P=44;|KEYCODE_DEL=67;|KEYCODE_MEDIA_FAST_FORWARD=90;

            KEYCODE_DPAD_RIGHT=22;|KEYCODE_Q=45;|KEYCODE_GRAVE=68;|KEYCODE_MUTE=91;

        :param device_id: 通过adb devices获取到的设备编号，当存在两个及以上设备时需要使用该参数进行区分
        """
        if key_code.isalpha():
            key_code = key_code.upper()
        if device_id:
            cmd = "adb -s " + device_id + " shell input keyevent " + key_code
        else:
            cmd = "adb shell input keyevent " + key_code
        sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.PIPE).wait()

    @staticmethod
    def get_cpu_info(filename: str, times: int = 1):
        """
        获取android的CPU信息

        :param filename 记录的文件路径

        :param times: 获取方式为adb shell top -n [times], times表示连续保存times次CPU信息
        """
        log = open(filename, 'w')
        cmd = "adb shell top -n 1"
        for i in range(times):
            sp.Popen(cmd, stdout=log, stderr=sp.PIPE).wait()
        log.close()

    @staticmethod
    def get_memory_info(filename: str, times: int = 1):
        """
        获取android内存信息

        :param filename:记录的文件路径

        :param times:获取方式为adb shell procrank, times表示连续保存times次memory信息
        """
        log = open(filename, 'w')
        # 方式1
        cmd1 = "adb shell procrank"
        # 方式2
        cmd2 = "adb shell cat /sys/kernel/debug/ion/heaps/system"
        for i in range(times):
            sp.Popen(cmd1, stdout=log, stderr=sp.PIPE).wait()
            sp.Popen(cmd2, stdout=log, stderr=sp.PIPE).wait()
        log.close()

    def set_keyboard(self, flag: bool = None, input_apps: list = None):
        """
        设置键盘类型， 默认输入法有百度和搜狗两种

        可以打开或者关闭某个输入法， 默认关闭输入法之后再打开输入法

        :param flag: 打开/关闭输入法

        :param input_apps: 输入法的package和activity， 如com.sohu.inputmethod.sogou/.SogouIME
        """
        keyboards = ["com.baidu.input/.ImeService", "com.sohu.inputmethod.sogou/.SogouIME"]
        if input_apps:
            for app in input_apps:
                keyboards.append(app)
        if flag is None:
            # 先disable输入法，之后再打开
            self.__operation(keyboards, False)
            self.__operation(keyboards, True)
        else:
            self.__operation(keyboards, flag)

    @staticmethod
    def is_visible(window: str = 'InputMethod', device_id: str = '1234567') -> bool:
        """
        查看屏幕是否处于可视状态，底层代码使用【adb -s 123456 shell dumpsys window windows】实现

        根据输出，判断无activity的应用窗口是否可见。

        :param window:
            需要查看的应用窗口，在输出中的字段

            如： 输出Window #4 Window{aed2c2 u0 InputMethod}中的InputMethod即为需要的参数。

        :param device_id: 测试设备的序列号

        :return:
            True: 窗口当前的可见

            False： 窗口当前不可见
        """
        cmd = "adb "
        if device_id:
            cmd = cmd + '-s ' + device_id + ' '
        cmd = cmd + 'shell dumpsys window windows'
        logger.debug('执行命令：{}'.format(cmd))
        ter = sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
        lines = ter.stdout.readlines()
        new_lines = []
        for line in lines:
            new_lines.append(line.decode('utf-8'))
        logger.debug(f'执行命令输出的文件为：{new_lines}')
        count = 0
        begin, end = 0, 0
        for line in new_lines:
            if count == 1 and 'Window #' in line:
                end = new_lines.index(line)
                logger.debug(f'结束行数为：{end}')
                break
            if window in line and 'Window #' in line:
                begin = new_lines.index(line)
                logger.debug(f'开始行数为：{begin}')
                count = count + 1
        if count == 0:
            return False
        new_output = new_lines[begin:end]
        logger.debug(f'筛选出来的结果：{new_output}')
        return 'is_visible=true' in new_output[-1]
