# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        player.py
# @Author:      lizhe
# @Created:     2021/5/1 - 23:34
# --------------------------------------------------------
import os

from time import sleep
from typing import Union, Optional

from ..logger.logger import logger


class Player(object):
    """
    播放TTS
    """

    def __init__(self):
        # 避免打印，导入包放到了init的时候再导入
        try:
            import pygame
            import pyttsx3 as tts
            import win32com.client
        except ModuleNotFoundError:
            os.system("pip install pygame")
            os.system("pip install pyttsx3")
        finally:
            import pygame
            import pyttsx3 as tts
            import win32com.client
            self.__pygame = pygame
            self.__pygame.mixer.init()
            self.speaker = win32com.client.Dispatch("SAPI.SpVoice")
            self._tts_play = tts.init()

    def text_to_tts(self, text: Union[str, bytes], rate: int = 150, volume: float = 1):
        """
        将字符串转语音并通过电脑播放，使用tts方式

        :param text: 需要tts播报的文字内容，支持中英文

        :param rate: 语音播报速度，每分钟播报的字数，默认为150[>0]

        :param volume: 播报语音的音量，默认为1[0,1]
        """
        if isinstance(text, bytes):
            text = text.decode('utf-8')
        logger.info(f"it will play text[{text}]")
        if not 0 < rate <= 150:
            raise ValueError(f"rate must in (0, 150], current rate is {rate}")
        if not 0 <= volume <= 1:
            raise ValueError(f"volume must in (0, 1), current volume is {volume}")
        self._tts_play.setProperty('rate', rate)
        self._tts_play.setProperty('volume', volume)
        self._tts_play.say(text)
        self._tts_play.runAndWait()

    def text_to_voice(self, text: Union[str, bytes]):
        """
        将字符串转语音并通过电脑播放

        :param text: 需要tts播报的文字内容，支持中英文
        """
        if isinstance(text, bytes):
            text = text.decode('utf-8')
        self.speaker.Speak(text)

    def play_audio(self, filename: str, playtime: Optional[float] = None, loops: int = 0, start: float = 0.0,
                   timeout: int = 300):
        """
        播放电脑端音频文件

        :param filename: 播放的文件名称（绝对路径）,不支持中文的路径与文件名

        :param playtime: 设置文件播放的时间，默认为完整播放，单位为s

        :param loops: 文件循环播放的次数，默认不循环，单位为int类型

        :param start: 从音频的某个时间点开始播放，默认从头开始播放，单位为s

        :param timeout: 设置播放超时，超时后会强制停止，默认为300s
        """
        self.__pygame.mixer.music.load(filename)
        self.__pygame.mixer.music.play(loops=loops, start=start)
        if playtime:
            sleep(playtime)
            self.__pygame.mixer.music.stop()
        else:
            for i in range(timeout):
                sleep(1)
                # 判断是否已经播放完成
                busy = self.__pygame.mixer.music.get_busy()
                if not busy:
                    break
            self.__pygame.mixer.music.stop()
