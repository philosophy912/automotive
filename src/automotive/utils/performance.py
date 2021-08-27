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
from functools import reduce
from typing import List, Tuple

from time import sleep

from automotive.utils.utils import Utils
from automotive.logger import logger
from automotive.utils.serial_utils import SerialUtils


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
        self.__serial = SerialUtils()
        self.__serial_command_interval_time = 3

    def __connect(self, port: str):
        self.__serial.connect(port, 115200)

    def __disconnect(self):
        self.__serial.disconnect()

    @staticmethod
    def __get_matched(content: str, regex: str) -> str:
        return re.search(regex, content).group(0)

    @staticmethod
    def __get_regex_matched(content: str, regexes: List[str]) -> str:
        for regex in regexes:
            content = re.search(regex, content).group(0)
        return content

    @staticmethod
    def __get_mb(value: str) -> int:
        """
        获取兆B数据

        :param value: 传入的值，如 8185M

        :return: 8185
        """
        value = value.strip()
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

    def __get_gpu_content_qnx(self, continue_time: int = 10) -> str:
        enter_data = "cd /data"
        self.__serial.write(enter_data)
        slay_ggpm = "slay ggpm"
        self.__serial.write(slay_ggpm)
        record_file = "rm test.txt"
        self.__serial.write(record_file)
        command = "./ggpm a -h 3 >test.txt &"
        self.__serial.write(command)
        sleep(continue_time)
        self.__serial.write(slay_ggpm)
        self.__serial.flush()
        read_file = "cat /data/test.txt"
        self.__serial.write(read_file)
        contents = self.__serial.read_lines()
        logger.debug(f"contents = {contents}")
        return "".join(contents)

    @staticmethod
    def __filter_files(folder: str, extend: str) -> List[str]:
        """
        过滤文件
        """
        files = list(filter(lambda x: x.endswith(extend), os.listdir(folder)))
        return list(map(lambda x: fr"{folder}/{x}", files))

    @staticmethod
    def __parse_qnx_gpu(content: str):
        """
        获取GPU占用率

        :param content: 内容列表

        :return: GPU占用率
        """
        results = re.findall(r"\s\d+.\d+G", content)
        results = list(map(lambda x: float(x[:-1]), results))
        total = reduce(lambda x, y: x + y, results)
        return round(total / len(results), 2)

    def __get_hypervisor_qnx_cpu_use_and_memory_free(self) -> tuple:
        """
        获取cpu占用率以及内存空闲数
        :return: cpu占用率, 内存空闲数  (3.5, 410M)
        """
        command = "top -i 1"
        cpu_use = None
        mem_free = None
        cpu_keywords = "CPU states:"
        mem_keywords = "Memory: "
        self.__serial.flush()
        self.__serial.write(command)
        sleep(self.__serial_command_interval_time)
        lines = self.__serial.read_lines()
        logger.debug(f"get value {lines}")
        for line in lines:
            if line.startswith(cpu_keywords):
                line = line[len(cpu_keywords):]
                cpu_use = line.strip().split("%")[0]
            if line.startswith(mem_keywords):
                line = line[len(mem_keywords):]
                mem_free = line.split(",")[1].replace("avail", "")
        if cpu_use and mem_free:
            return cpu_use, mem_free
        else:
            raise RuntimeError("no cpu use found")

    def __get_hypervisor_qnx_memory_use(self) -> str:
        """
        QNX系统内存使用量
        :return: 131420k
        """
        command = "hogs -i 1"
        self.__serial.flush()
        self.__serial.write(command)
        sleep(self.__serial_command_interval_time)
        lines = self.__serial.read_lines()
        # 去掉前两行，并去空行
        lines = list(map(lambda x: x.replace("\r\n", ""), lines))
        lines = list(filter(lambda x: x != "", lines[2:-1]))
        logger.debug(f"get value {lines}")
        total_memory = 0
        for index, line in enumerate(lines):
            if "PID" in line:
                continue
            else:
                logger.debug(line.replace("\r\n", ""))
                # 20492   smmu_service     1   0%   0%   2284k   1%
                results = list(filter(lambda x: x.endswith("k"), line.split(" ")))
                memory = results[0] if len(results) > 0 else 0
                logger.debug(f"the {index} time memory is {memory}")
                total_memory += int(memory.replace("k", ""))
        if total_memory != 0:
            return f"{total_memory}k"
        else:
            raise RuntimeError("no qnx memory use found")

    def __get_hypervisor_qnx_data(self) -> Tuple:
        """
        获取QNX系统的cpu占用率， 已使用的内存Mb， 总计内存大小

        return: 21.3(float), 300(int), 600(int)
        """
        cpu_use, free_memory = self.__get_hypervisor_qnx_cpu_use_and_memory_free()
        logger.debug(f"cpu_use is {cpu_use} and free_memory is {free_memory}")
        use_memory = self.__get_hypervisor_qnx_memory_use()
        logger.debug(f"use_memory is {use_memory}")
        free_memory = self.__get_mb(free_memory)
        logger.debug(f"free_memory is {free_memory}")
        use_memory = self.__get_mb(use_memory)
        logger.debug(f"use_memory is {use_memory}")
        total_memory = use_memory + free_memory
        return float(cpu_use), use_memory, total_memory

    def __get_content_qnx(self) -> str:
        command = "top -i 1"
        self.__serial.flush()
        self.__serial.write(command)
        sleep(2)
        content = self.__serial.read_lines()
        logger.debug(f"content is {content}")
        return "".join(content)

    def __get_qnx_data(self, content: str) -> Tuple:
        result = self.__get_matched(content, r"CPU states:\s\d{1,2}.\d%")
        # CPU states: 18.1%
        cpu = result.split(":")[1].strip()[:-1]
        logger.debug(f"cpu value is {cpu}")
        result = self.__get_matched(content, r"\d+\w*\stotal,\s\d+\w*\savail")
        # 8185M total, 655M avail
        total, avail = result.split(",")
        total_memory = total.strip().split(" ")[0]
        avail_memory = avail.strip().split(" ")[0]
        total_memory = self.__get_mb(total_memory)
        avail_memory = self.__get_mb(avail_memory)
        use_memory = total_memory - avail_memory
        return float(cpu), f"{use_memory}M", f"{total_memory}M"

    @staticmethod
    def __calc_datum(datum: List) -> Tuple:
        """
        计算平局值

        :param datum: 数据， 包含cpu占用率， 已使用内存，总内存

        :return:  CPU占用率%， 内存占用率%， 已用内存Mb, 总内存Mb，
        """
        cpu_use_total = 0
        use_memory_total = 0
        total_memory_total = 0
        for data in datum:
            cpu_use, use_memory, total_memory = data
            cpu_use_total += cpu_use
            use_memory_total += use_memory
            total_memory_total += total_memory
        datum_size = len(datum)
        cpu_use_average = cpu_use_total / datum_size
        use_memory_average = int(use_memory_total / datum_size)
        total_memory_average = int(total_memory_total / datum_size)
        memory_percent = use_memory_average / total_memory_average
        return round(cpu_use_average, 2), round(memory_percent * 100, 2), use_memory_average, total_memory_average

    @staticmethod
    def __get_android_memory() -> Tuple:
        keyword1 = "Total RAM:"
        keyword2 = " Used RAM:"
        command = "adb shell dumpsys meminfo"
        total = None
        used = None
        stdout, stderr = Utils.exec_command_with_output(command)
        contents = list(map(lambda x: x.replace("\r\n", ""), stdout.split("\n")))
        for content in contents:
            if content.startswith(keyword1):
                content = content[len(keyword1):].split("(")[0]
                total = content.replace(",", "")
            if content.startswith(keyword2):
                content = content[len(keyword2):].split("(")[0]
                used = content.replace(",", "")
        if total and used:
            return total, used
        else:
            raise RuntimeError("get memory failed")

    def __get_android_cpu(self) -> str:
        command = "adb shell top -n 1"
        stdout, stderr = Utils.exec_command_with_output(command)
        total = self.__get_matched(stdout, r"\d+%cpu")
        idle = self.__get_matched(stdout, r"\d+%idle")
        # 400%cpu - 360%idle
        cpu = int(total[:-4]) - int(idle[:-5])
        logger.debug(f"cpu value is {cpu}")
        return f"{cpu}"

    def __get_android_data(self) -> tuple:
        cpu_use = self.__get_android_cpu()
        total, used = self.__get_android_memory()
        return float(cpu_use), self.__get_mb(used), self.__get_mb(total)

    def __get_linux_data(self) -> tuple:
        """
        由于有颜色字符的存在，所以需要单独进行处理
        """
        command = "top -n 1"
        self.__serial.flush()
        self.__serial.write(command)
        sleep(2)
        content = self.__serial.read_lines()
        content = "".join(content)
        content = content.replace("[39;49m", "").replace("", "").replace("[1m ", "").replace("[m", "")
        logger.debug(f"content is {content}")
        # 先得到Cpu(s): 10.7 us, 然后得到10.7
        cpu = self.__get_regex_matched(content, [r"Cpu.*:\s\d+.\d\sus", r"\d+.\d+"])
        # 先得到Mem :   755952 total，然后得到755952并加K后缀
        total_memory = self.__get_regex_matched(content, [r"Mem\s*:\s*\d+\stotal", r"\d+"]).strip() + "K"
        # 先得到Mem :   755952 total,   549628 free,    76584 used，然后得到76584 used然后得到76584
        used_memory = self.__get_regex_matched(content, [r"Mem\s*:\s*.*used", r"\d+\sused", r"\d+"]).strip() + "K"
        return float(cpu), self.__get_mb(used_memory), self.__get_mb(total_memory)

    @staticmethod
    def __show_data(pre: str, cpu_use: float, memory_percent: float, use_memory: int, total_memory: int,
                    gpu_average: int = -1):
        value = f"{pre}: CPU占用率{cpu_use}%, 内存占用率{memory_percent}%, 内存使用{use_memory}M, 总内存大小{total_memory}M"
        if gpu_average != -1:
            value = f"{value}, GPU吞吐量{gpu_average}G"
        return value

    def get_hypervisor_qnx_performance(self, port: str, count: int, need_test_gpu: bool = False) -> str:
        """
        获取高通Hypervisor的性能

        :param need_test_gpu:

        :param port: 串口端口号

        :param count: 测试次数

        :return: CPU占用率，内存占用率，内存使用量，内存总量, GPU吞吐量(当没有的时候为-1)
        """
        self.__connect(port)
        gpu_average = -1
        if need_test_gpu:
            content = self.__get_gpu_content_qnx()
            gpu_average = self.__parse_qnx_gpu(content)
            logger.debug(f"gpu average is {gpu_average}")
        datum = []
        for i in range(count):
            logger.info(f"第{i + 1}次获取数据")
            cpu_use, use_memory, total_memory = self.__get_hypervisor_qnx_data()
            datum.append((cpu_use, use_memory, total_memory))
        self.__disconnect()
        cpu_use, memory_percent, use_memory, total_memory = self.__calc_datum(datum)
        pre = "高通Hypervisor的QNX的性能"
        return self.__show_data(pre, cpu_use, memory_percent, use_memory, total_memory, gpu_average)

    def get_qnx_performance(self, port: str, count: int) -> str:
        """
        获取QNX的性能

        :param port: 端口号

        :param count: 测试次数

        :return: CPU占用率，内存占用率，内存使用量，内存总量,
        """
        self.__connect(port)
        datum = []
        for i in range(count):
            logger.info(f"第{i + 1}次获取数据")
            content = self.__get_content_qnx()
            cpu_use, use_memory, total_memory = self.__get_qnx_data(content)
            datum.append((cpu_use, use_memory, total_memory))
        self.__disconnect()
        cpu_use, memory_percent, use_memory, total_memory = self.__calc_datum(datum)
        pre = "单QNX的性能"
        return self.__show_data(pre, cpu_use, memory_percent, use_memory, total_memory)

    def get_hypervisor_android_performance(self, count: int) -> str:
        """
        后取安卓的相关性能

        :param count: 测试次数

        :return: CPU占用率，内存占用率，内存使用量，内存总量
        """
        datum = []
        for i in range(count):
            logger.info(f"第{i + 1}次获取数据")
            cpu_use, use_memory, total_memory = self.__get_android_data()
            datum.append((cpu_use, use_memory, total_memory))
        cpu_use, memory_percent, use_memory, total_memory = self.__calc_datum(datum)
        pre = "高通Hypervisor的Android的性能"
        return self.__show_data(pre, cpu_use, memory_percent, use_memory, total_memory)

    def get_linux_performance(self, port: str, count: int) -> str:
        """
        获取Linux的相关性能
        :param port:  串口串口好
        :param count: 测试次数
        :return:
        """
        self.__connect(port)
        datum = []
        for i in range(count):
            logger.info(f"第{i + 1}次获取数据")
            cpu_use, memory_percent, use_memory, total_memory = self.__get_linux_data()
            datum.append((cpu_use, use_memory, total_memory))
        self.__disconnect()
        cpu_use, memory_percent, use_memory, total_memory = self.__calc_datum(datum)
        pre = "Linux的性能"
        return self.__show_data(pre, cpu_use, memory_percent, use_memory, total_memory)

    def get_qnx_performance_by_file(self, folder: str, extend: str) -> str:
        """
        获取qnx的相关性能（通过文件）

        :param extend: 扩展名

        :param folder: 导出的文件夹

        :return:  CPU占用率，内存占用率，内存使用量，内存总量
        """
        datum = []
        qnx_files = self.__filter_files(folder, extend)
        # 从每一个文件中读取内容
        for qnx in qnx_files:
            with open(qnx, "r") as f:
                content = "".join(f.readlines())
                cpu_use, use_memory, total_memory = self.__get_qnx_data(content)
                datum.append((cpu_use, use_memory, total_memory))
        cpu_use, memory_percent, use_memory, total_memory = self.__calc_datum(datum)
        pre = "单QNX的性能"
        return self.__show_data(pre, cpu_use, memory_percent, use_memory, total_memory)
