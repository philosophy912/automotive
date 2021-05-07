# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        performance.py
# @Author:      lizhe
# @Created:     2021/5/1 - 23:33
# --------------------------------------------------------
import os
import re
import subprocess as sp
import chardet
from time import sleep
from automotive.logger import logger
from automotive.utils import SerialPort


class Performance(object):
    """
    测试CPU以及Memory占用率，使用方法:

    获取QNX的CPU及Memory占用率

    result = per.get_qnx_performance("COM23", 1)

    获取Android的CPU及Memory占用率

    result = per.get_android_performance(10)

    其中result是CPU占用率，内存占用率，内存使用量，内存总量(字符串格式)
    """

    def __init__(self):
        self.__serial = SerialPort()

    def __connect(self, port: str):
        self.__serial.connect(port, 115200)

    def __disconnect(self):
        self.__serial.disconnect()

    @staticmethod
    def __get_matched(content: str, regex: str) -> str:
        return re.search(regex, content).group(0)

    @staticmethod
    def __get_regex_matched(content: str, regexes: list) -> str:
        for regex in regexes:
            content = re.search(regex, content).group(0)
        return content

    @staticmethod
    def __get_average(numbers: (int, float)) -> (int, float):
        total = 0
        for num in numbers:
            total += num
        return total / len(numbers)

    @staticmethod
    def __get_codec(bytes_value: bytes) -> str:
        encode = chardet.detect(bytes_value)
        encoding = encode['encoding']
        return encoding if encoding else "utf-8"

    @staticmethod
    def __get_mb(value: str) -> int:
        """
        获取兆B数据

        :param value: 传入的值，如 8185M

        :return: 8185
        """
        num_value = value[:-1] if len(value) > 1 else value
        logger.debug(f"value = {value} and num_value = {num_value}")
        if "G" in value.upper():
            return int(num_value) * 1024
        elif "M" in value.upper():
            return int(num_value)
        elif "K" in value.upper():
            return int(num_value) // 1024
        else:
            return int(num_value)

    def __get_content_android(self) -> str:
        command = "adb shell top -n 1"
        result = sp.Popen(command, stdout=sp.PIPE, stderr=sp.PIPE)
        contents = list(map(lambda x: x.decode(self.__get_codec(x)), result.stdout.readlines()))
        content = "".join(contents)
        logger.debug(f"content = [{content}]")
        return content

    def __get_content_qnx(self) -> str:
        command = "top -i 1"
        self.__serial.flush_all()
        self.__serial.send(command)
        sleep(2)
        content = self.__serial.read_all()
        logger.debug(f"content is {content}")
        return content

    def __get_content_linux(self) -> str:
        """
        由于有颜色字符的存在，所以需要单独进行处理
        """
        command = "top -n 1"
        self.__serial.flush_all()
        self.__serial.send(command)
        sleep(2)
        content = self.__serial.read_all()
        content = content.replace("[39;49m", "").replace("", "").replace("[1m ", "").replace("[m", "")
        logger.debug(f"content is {content}")
        return content

    def __get_gpu_content_qnx(self, continue_time: int = 10) -> str:
        enter_data = "cd /data"
        self.__serial.send(enter_data)
        slay_ggpm = "slay ggpm"
        self.__serial.send(slay_ggpm)
        record_file = "rm test.txt"
        self.__serial.send(record_file)
        command = "./ggpm a -h 3 >test.txt &"
        self.__serial.send(command)
        sleep(continue_time)
        self.__serial.send(slay_ggpm)
        self.__serial.flush_all()
        read_file = "cat /data/test.txt"
        self.__serial.send(read_file)
        contents = self.__serial.read_all()
        logger.debug(f"contents = {contents}")
        return contents

    def __parse_android_cpu(self, contents: list) -> float:
        """
        安卓CPU占用率

        400%cpu  13%user   3%nice  20%sys 360%idle   3%iow   0%irq   0%sirq   0%host

        :param contents: 内容列表

        :return: total_average, uses_average, percent_average
        """
        cpus = []
        for content in contents:
            total = self.__get_matched(content, r"\d+%cpu")
            idle = self.__get_matched(content, r"\d+%idle")
            # 400%cpu - 360%idle
            cpu = int(total[:-4]) - int(idle[:-5])
            logger.debug(f"cpu value is {cpu}")
            cpus.append(float(cpu))
        cpu_average = self.__get_average(cpus)
        logger.debug(f"cpu average is [{cpu_average}]")
        return cpu_average

    def __parse_android_memory(self, contents: list) -> tuple:
        """
        安卓内存占用率

        Mem:   3442708k total,  2878936k used,   563772k free,    10800k buffers

        :param contents: 内容列表

        :return: total_average, uses_average, percent_average
        """
        totals = []
        uses = []
        for content in contents:
            result = self.__get_matched(content, r"Mem:\s*\d+\w\s*total,\s*\d+\w\s*used")
            # Mem:   3442708k total,  2878936k used
            total, used = result.split(",")
            logger.debug(f"total = {total} and avail = {used}")
            # total = Mem:   3442708k total
            # avail =   2878936k used
            total_memory = total.strip().split(":")[1].strip().split(" ")[0]
            # 3442708k
            used_memory = used.strip().split(" ")[0]
            # 2878936k
            total_memory = self.__get_mb(total_memory)
            used_memory = self.__get_mb(used_memory)
            totals.append(total_memory)
            uses.append(used_memory)
        total_average = self.__get_average(totals)
        uses_average = self.__get_average(uses)
        percent_average = round(uses_average / total_average, 4)
        logger.debug(f"total[{total_average}]M, used[{uses_average}]M, percent[{percent_average * 100}]%")
        return total_average, uses_average, percent_average

    def __parse_cpu(self, contents: list) -> float:
        """
        cpu 占用率

        CPU states: 13.9% user, 7.9% kernel

        :param contents: 内容列表

        :return cpu占用率，百分比
        """
        cpus = []
        for content in contents:
            result = self.__get_matched(content, r"CPU states:\s\d{1,2}.\d%")
            # CPU states: 18.1%
            cpu = result.split(":")[1].strip()[:-1]
            logger.debug(f"cpu value is {cpu}")
            cpus.append(float(cpu))
        cpu_average = self.__get_average(cpus)
        logger.debug(f"cpu average is [{cpu_average}]")
        return cpu_average

    def __parse_memory(self, contents: list) -> tuple:
        """
        获取内存占用率

        :param contents: 内容列表

        :return: total_average, uses_average, percent_average
        """
        totals = []
        uses = []
        for content in contents:
            result = self.__get_matched(content, r"\d+\w*\stotal,\s\d+\w*\savail")
            # 8185M total, 655M avail
            total, avail = result.split(",")
            total_memory = total.strip().split(" ")[0]
            avail_memory = avail.strip().split(" ")[0]
            total_memory = self.__get_mb(total_memory)
            avail_memory = self.__get_mb(avail_memory)
            use_memory = total_memory - avail_memory
            totals.append(total_memory)
            uses.append(use_memory)
        total_average = self.__get_average(totals)
        total_average = total_average if total_average > 1 else 1
        uses_average = self.__get_average(uses)
        percent_average = round(uses_average / total_average, 4)
        logger.debug(f"total[{total_average}]M, used[{uses_average}]M, percent[{percent_average * 100}]%")
        return total_average, uses_average, percent_average

    def __parse_qnx_gpu(self, content: str):
        """
        获取GPU占用率

        :param content: 内容列表

        :return: GPU占用率
        """
        results = re.findall(r"\s\d+.\d+G", content)
        results = list(map(lambda x: float(x[:-1]), results))
        return round(self.__get_average(results), 2)

    def __parse_linux(self, contents: list):
        totals = []
        uses = []
        cpus = []
        for content in contents:
            # 先得到Cpu(s): 10.7 us, 然后得到10.7
            cpu = self.__get_regex_matched(content, [r"Cpu.*:\s\d+.\d\sus", r"\d+.\d+"])
            # 先得到Mem :   755952 total，然后得到755952并加K后缀
            total_memory = self.__get_regex_matched(content, [r"Mem\s*:\s*\d+\stotal", r"\d+"]).strip() + "K"
            # 先得到Mem :   755952 total,   549628 free,    76584 used，然后得到76584 used然后得到76584
            used_memory = self.__get_regex_matched(content, [r"Mem\s*:\s*.*used", r"\d+\sused", r"\d+"]).strip() + "K"
            cpus.append(float(cpu))
            totals.append(self.__get_mb(total_memory))
            uses.append(self.__get_mb(used_memory))
        cpu_average = self.__get_average(cpus)
        total_average = self.__get_average(totals)
        uses_average = self.__get_average(uses)
        percent_average = round(uses_average / total_average, 4)
        return cpu_average, percent_average, uses_average, total_average

    @staticmethod
    def __filter_files(folder: str, extend: str) -> list:
        """
        过滤文件
        """
        files = list(filter(lambda x: x.endswith(extend), os.listdir(folder)))
        return list(map(lambda x: fr"{folder}/{x}", files))

    def get_qnx_performance(self, port: str, count: int, need_test_gpu: bool = True) -> tuple:
        """
        获取QNX的相关性能

        :param need_test_gpu:

        :param port: 串口端口号

        :param count: 测试次数

        :return: CPU占用率，内存占用率，内存使用量，内存总量, GPU占用率
        """
        self.__connect(port)
        contents = []
        for i in range(count):
            logger.info(f"第{i + 1}次获取数据")
            contents.append(self.__get_content_qnx())
        cpu_average = self.__parse_cpu(contents)
        total_average, uses_average, percent_average = self.__parse_memory(contents)
        # 获取GPU的占用率
        content = self.__get_gpu_content_qnx()
        gpu_average = self.__parse_qnx_gpu(content) if need_test_gpu else None
        logger.debug(f"gpu average is {gpu_average}")
        self.__disconnect()
        if gpu_average:
            return f"CPU占用率{cpu_average}%", f"内存占用率{percent_average * 100}%", f"内存使用量{uses_average}M", \
                   f"内存总量{total_average}M", f"GPU占用率{gpu_average}G"
        else:
            return f"CPU占用率{cpu_average}%", f"内存占用率{percent_average * 100}%", f"内存使用量{uses_average}M", \
                   f"内存总量{total_average}M"

    def get_qnx_performance_by_file(self, folder: str, extend: str) -> tuple:
        """
        获取qnx的相关性能（通过文件）

        :param extend: 扩展名
        :param folder: 导出的文件夹

        :return:  CPU占用率，内存占用率，内存使用量，内存总量
        """
        contents = []
        qnx_files = self.__filter_files(folder, extend)
        # 从每一个文件中读取内容
        for qnx in qnx_files:
            with open(qnx, "r") as f:
                content = "".join(f.readlines())
                contents.append(content)
        cpu_average = self.__parse_cpu(contents)
        total_average, uses_average, percent_average = self.__parse_memory(contents)
        return f"CPU占用率{cpu_average}%", f"内存占用率{percent_average * 100}%", f"内存使用量{uses_average}M", \
               f"内存总量{total_average}M"

    def get_android_performance(self, count: int) -> tuple:
        """
        后取安卓的相关性能

        :param count: 测试次数

        :return: CPU占用率，内存占用率，内存使用量，内存总量
        """
        contents = []
        for i in range(count):
            logger.info(f"第{i + 1}次获取数据")
            contents.append(self.__get_content_android())
        cpu_average = self.__parse_android_cpu(contents)
        total_average, uses_average, percent_average = self.__parse_android_memory(contents)
        return f"CPU占用率{cpu_average}%", f"内存占用率{round(percent_average * 100, 2)}%", f"内存使用量{uses_average}M", \
               f"内存总量{total_average}M"

    def get_linux_performance(self, port: str, count: int) -> tuple:
        """
        获取Linux的相关性能
        :param port:  串口串口好
        :param count: 测试次数
        :return:
        """
        self.__connect(port)
        contents = []
        for i in range(count):
            logger.info(f"第{i + 1}次获取数据")
            contents.append(self.__get_content_linux())
        cpu_average, percent_average, uses_average, total_average = self.__parse_linux(contents)
        self.__disconnect()
        return f"CPU占用率{cpu_average}%", f"内存占用率{percent_average * 100}%", f"内存使用量{uses_average}M", \
               f"内存总量{total_average}M"
