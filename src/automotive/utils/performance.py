# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        performance_utils.py
# @Author:      lizhe
# @Created:     2022/8/15 - 22:09
# --------------------------------------------------------
import re
from time import sleep
from typing import Sequence, Tuple, Dict
from collections import namedtuple

from .utils import Utils
from .serial_utils import SerialUtils
from automotive.logger.logger import logger

QNX = namedtuple("QNX", ["cpu_usage", "memory_usage", "data"])
Android = namedtuple("Android", ["cpu_usage", "memory_usage", "top_data", "dumpsys_data"])
App = namedtuple("App", ["cpu_usage", "memory_usage", "top_data", "dumpsys_data"])


class Performance(object):
    """
    性能测试类
    """

    def __init__(self, interval_time: int = 3, columns: int = 512):
        """
        初始化性能测试
        :param interval_time: 串口命令间的间隔时间
        """
        self.__utils = Utils()
        self.__serial = SerialUtils()
        self.__serial_interval_time = interval_time
        # COLUMNS=512
        self.__columns = columns
        # grep
        self.__grep_command = "grep"

    @staticmethod
    def __get_regex_matched(content: str, regexes: Sequence[str]) -> str:
        for regex in regexes:
            content = re.search(regex, content).group(0)
        return content

    @staticmethod
    def __get_matched(content: str, regex: str) -> str:
        return re.search(regex, content).group(0)

    def connect(self, port: str):
        """
        由于QNX系统目前仅仅能够通过串口连接，所以需要串口连接
        :param port:
        :return:
        """
        self.__serial.connect(port, 115200)

    def disconnect(self):
        """
        由于QNX系统目前仅仅能够通过串口连接，所以需要串口断开
        :return:
        """
        self.__serial.disconnect()

    @staticmethod
    def __filter_lines(lines: Sequence[str]) -> Sequence[str]:
        """
        过滤无用的内容
        :return:
        """
        # 去掉\r\n \n
        new_lines = list(map(lambda x: x.replace("\r\n", "").replace("\n", ""), lines))
        # 去掉空行
        lines = list(filter(lambda x: x != "", new_lines))
        return lines

    def __exec_command(self, command: str, use_serial: bool = False) -> Sequence[str]:
        """
        执行命令，并返回回显
        :param command: 命令
        :param use_serial: 是否使用串口
        :return:  回显
        """
        if use_serial:
            # 先清空串口输出
            self.__serial.flush()
            # 执行命令
            self.__serial.write(command)
            # 等待回显，默认时间3秒
            sleep(self.__serial_interval_time)
            # 读取回显信息
            lines = self.__serial.read_lines()
            line = "\n".join(lines)
            logger.debug(f"lines = [{line}]")
            # 返回字符串，后续可以自行拆解
            return self.__filter_lines(lines)
        else:
            logger.debug(f"execute command is [{command}]")
            stdout, stderr = self.__utils.exec_command_with_output(command)
            logger.debug(f"stdout = [{stdout}]")
            lines = stdout.split("\n")
            return self.__filter_lines(lines)

    def __exec_qnx_top_command(self) -> Sequence[str]:
        """
        执行top -i 1命令
        :return: 执行命令后的回显
        """
        command = "top -i 1"
        lines = self.__exec_command(command, True)
        return self.__filter_lines(lines)

    def __exec_qnx_hogs_command(self) -> Sequence[str]:
        """
        执行hogs -i 1命令
        :return: 执行命令后的回显
        """
        command = "hogs i 1"
        lines = self.__exec_command(command, True)
        return self.__filter_lines(lines)

    def __exec_linux_top_command(self) -> Sequence[str]:
        """
        执行top -n 1命令
        :return: 执行命令后的回显
        """
        command = "top -n 1"
        lines = self.__exec_command(command, True)
        return self.__filter_lines(lines)

    def __exec_adb_top_command(self, device_id: str = None, app_name: str = None) -> Sequence[str]:
        """
        基础命令 adb -s 1234567 shell COLUMNS=512 top -n 1 | grep "com.chinatsp.ui"
        :param device_id: adb的device id
        :param app_name: app的packagename
        :return: 执行命令后的回显
        """
        commands = ["adb"]
        if device_id:
            commands.append("-s")
            commands.append(device_id)
        commands.append("shell")
        commands.append(f"COLUMNS={self.__columns}")
        commands.append('top')
        if app_name:
            commands.append("-b")
        commands.append('-n')
        commands.append('1')
        if app_name:
            commands.append("|")
            commands.append(self.__grep_command)
            commands.append(f"\"{app_name}\"")
        command = " ".join(commands)
        lines = self.__exec_command(command)
        return self.__filter_lines(lines)

    def __exec_adb_procrank(self, device_id: str = None, app_name: str = None) -> Sequence[str]:
        """
        adb -s 1234567 shell COLUMNS=512 procrank | grep "com.chinatsp.ui"
        :param device_id: adb的device id
        :param app_name: app的packagename
        :return: 执行命令后的回显
        """
        commands = ["adb"]
        if device_id:
            commands.append("-s")
            commands.append(device_id)
        commands.append("shell")
        commands.append(f"COLUMNS={self.__columns}")
        commands.append("procrank")
        if app_name:
            commands.append("|")
            commands.append(self.__grep_command)
            commands.append(f"\"{app_name}\"")
        command = " ".join(commands)
        lines = self.__exec_command(command)
        return self.__filter_lines(lines)

    def __exec_adb_dumpsys_meminfo(self, device_id: str = None, app_name: str = None) -> Sequence[str]:
        """
        adb -s 1234567 shell COLUMNS=512 dumpsys meminfo | grep "com.chinatsp.ui"
        :param device_id: adb的device id
        :param app_name: app的packagename
        :return: 执行命令后的回显
        """
        commands = ["adb"]
        if device_id:
            commands.append("-s")
            commands.append(device_id)
        commands.append("shell")
        commands.append(f"COLUMNS={self.__columns}")
        commands.append("dumpsys")
        commands.append("meminfo")
        if app_name:
            commands.append("|")
            commands.append(self.__grep_command)
            commands.append(f"\"{app_name}\"")
        command = " ".join(commands)
        lines = self.__exec_command(command)
        return self.__filter_lines(lines)

    def __exec_adb_dumpsys_meminfo_by_process_id(self, process_id: int, device_id: str = None) -> Sequence[str]:
        """
        adb -s 1234567 shell COLUMNS=512 dumpsys meminfo | grep "com.chinatsp.ui"
        :param device_id: adb的device id
        :param process_id: 进程号
        :return: 执行命令后的回显
        """
        commands = ["adb"]
        if device_id:
            commands.append("-s")
            commands.append(device_id)
        commands.append("shell")
        commands.append(f"COLUMNS={self.__columns}")
        commands.append("dumpsys")
        commands.append("meminfo")
        commands.append(f"{process_id}")
        command = " ".join(commands)
        lines = self.__exec_command(command)
        return self.__filter_lines(lines)

    def __exec_adb_dumpsys_meminfo_use_process(self, device_id: str = None, app_name: str = None,
                                               is_single: bool = True) -> Sequence[Sequence[str]]:
        """
        利用adb top命令获取到进程号
        根据进程号来获取内存占用率
        :param device_id: adb的device id
        :param app_name: app的packagename
        :param is_single: 是否只收一个
        :return:
        """
        contents = []
        lines = self.__exec_adb_top_command(device_id, app_name)
        # 由于解析的时候不知道是否是单app，所以这个地方做过滤
        if app_name:
            lines = list(
                filter(lambda x: app_name in x[-50:] and f"COLUMNS={self.__columns}" not in x and "grep" not in x,
                       lines))
        logger.debug(f"lines = {lines}")
        process_ids = self.__get_process_id(app_name, lines)
        for key, value in process_ids.items():
            if is_single:
                if "u10" in key:
                    process_id_contents = self.__exec_adb_dumpsys_meminfo_by_process_id(value, device_id)
                    contents.append(process_id_contents)
            else:
                process_id_contents = self.__exec_adb_dumpsys_meminfo_by_process_id(value, device_id)
                contents.append(process_id_contents)
        return contents

    @staticmethod
    def __get_process_id(app_name: str, lines: Sequence[str]) -> Dict[str, int]:
        """
        获取进程号
        2922 u10_system   12  -8  18G 397M 287M S 23.3   6.2  68:00.64 com.chinatsp.launcher
        9596 shell        20   0  12G 2.9M 2.3M S  0.0   0.0   0:00.00 grep com.chinatsp.launcher
        :param app_name app的packagename
        :param lines: 执行__exec_adb_top_command获取的回显
        :return: process_ids
        """
        process_ids = dict()
        for line in lines:
            if app_name in line:
                contents = line.split()
                # 杜绝shell的存在
                if contents[1] != "shell" or "grep" not in contents[-1]:
                    process_id = contents[0]
                    logger.debug(f"process_id = {process_id}")
                    process_ids[contents[1]] = int(process_id)
        if not process_ids:
            raise RuntimeError(f"{app_name} not found in process")
        else:
            return process_ids

    def __parse_adb_top_cpu_usage(self, lines: Sequence[str], app_name: str = None) -> float:
        """
        获取安卓的cpu占用率
        :param app_name app的packagename
        :param lines: 执行__exec_adb_top_command获取的回显
        :return: CPU占用率
        """
        if app_name:
            cpu_uses = []
            for line in lines:
                if app_name in line[-50:] and f"COLUMNS={self.__columns}" not in line and "grep" not in line:
                    logger.debug(f"available line is {line}")
                    split_contents = line.split()
                    cpu_use = split_contents[-4]
                    cpu_uses.append(cpu_use)
                    logger.debug(f"cpu_use is {cpu_use}")
            if cpu_uses:
                total_cpu_use = 0
                for cpu_use in cpu_uses:
                    total_cpu_use += float(cpu_use)
                return total_cpu_use
            else:
                line_str = "\n".join(lines)
                raise RuntimeError(f"请手动查看top -i 1命令执行是否有返回值， 目前输入的解析内容是{line_str}")
        else:
            content = "\n".join(lines)
            if "cpu" not in content or "idle" not in content:
                raise RuntimeError(f"请手动查看top -i 1命令执行是否有返回值， 目前输入的解析内容是{content}")
            # 获取总的CPU占用率
            # 400%cpu - 360%idle
            total = self.__get_matched(content, r"\d+%cpu")
            idle = self.__get_matched(content, r"\d+%idle")
            total_cpu = int(total[:-4])
            idle_cpu = int(idle[:-5])
            usage = float((total_cpu - idle_cpu) / total_cpu * 100)
            return usage

    @staticmethod
    def __parse_qnx_top_cpu_memory_usage(lines: Sequence[str]) -> Tuple[float, float, float]:
        """
        解析 top -i 1中的CPU占用率
        :param lines: 执行__exec_qnx_top_command方法后的返回值
        :return: cpu的使用率, 内存使用率（总共的), 内存总量  单位MByte
        """
        cpu_use = None
        memory_use = None
        memory_total = None
        cpu_keywords = "CPU states:"
        memory_keywords = "Memory: "
        for line in lines:
            # CPU states: 22.0% user, 0.5% kernel
            if line.startswith(cpu_keywords):
                line = line[len(cpu_keywords):]
                cpu_use = line.strip().split("%")[0]
            # Memory: 12279M total, 922M avail, page size 4K
            if line.startswith(memory_keywords):
                # 12279M total, 922M avail, page size 4K
                line = line[len(memory_keywords):]
                parts = line.split(", ")
                total_memory = parts[0].split()[0][:-1]
                avail_memory = parts[1].split()[0][:-1]
                logger.debug(f"total_memory = {total_memory}")
                logger.debug(f"avail_memory = {avail_memory}")
                memory_total = float(total_memory)
                memory_use = memory_total - float(avail_memory)
        if cpu_use is None or memory_use is None or memory_total is None:
            line_str = "\n".join(lines)
            raise RuntimeError(f"请手动查看top -i 1命令执行是否有返回值， 目前输入的解析内容是{line_str}")
        else:
            return float(cpu_use), memory_use, memory_total

    @staticmethod
    def __parse_adb_dumpsys_meminfo_usage(lines: Sequence[str]):
        """
        解析adb shell dumpsys meminfo  针对安卓系统
        :param lines: 执行__exec_adb_dumpsys_meminfo方法后的返回值,不带app name
        :return: 使用的内存和总共的内存 单位KByte
        """
        keyword1 = "Total RAM:"
        keyword2 = "Used RAM:"
        use_memory = None
        total_memory = None
        for line in lines:
            new_line = line.strip()
            # Total RAM: 6,475,168K (status normal)
            if new_line.startswith(keyword1):
                content = new_line[len(keyword1):]
                content = content.split("(")[0].strip()[:-1].replace(",", "")
                logger.debug(f"content is {content}")
                total_memory = int(content)
            # Used RAM: 3,157,956K (2,613,100K used pss +   544,856K kernel)
            if new_line.startswith(keyword2):
                content = new_line[len(keyword2):]
                content = content.split("(")[0].strip()[:-1].replace(",", "")
                logger.debug(f"content is {content}")
                use_memory = int(content)
        if use_memory is None or total_memory is None:
            line_str = "\n".join(lines)
            raise RuntimeError(f"请手动查看dumpsys meminfo命令执行是否有返回值, 目前输入的解析内容是{line_str}")
        return use_memory, total_memory

    @staticmethod
    def __parse_adb_dumpsys_meminfo_app_usage(lines: Sequence[str]) -> Tuple[int, int]:
        """
        解析adb shell dumpsys meminfo | grep com.chinatsp.launcher 针对APP
        :param lines: 执行__exec_adb_dumpsys_meminfo方法后的返回值
        :return: PSS和RSS的值，单位KBytes
        """
        keyword1 = "TOTAL PSS:"
        keyword2 = "TOTAL RSS:"
        keyword3 = "TOTAL SWAP (KB):"
        pss = None
        rss = None
        # TOTAL PSS:    10447            TOTAL RSS:    92168      TOTAL SWAP (KB):        0
        for line in lines:
            if keyword1 in line and keyword2 in line and keyword3 in line:
                line = line.strip()
                logger.debug(f"line is  {line}")
                pss = line[len(keyword1) + 1:].strip().split(keyword2)[0].strip()
                rss = line[len(keyword1) + 1:].strip().split(keyword2)[1].strip().split(keyword3)[0].strip()
                logger.debug(f"pss is {pss} and rss is {rss}")
                break
        if pss is None or rss is None:
            line_str = "\n".join(lines)
            raise RuntimeError(
                f"请手动查看dumpsys meminfo (package name) 命令执行是否有返回值, 目前输入的解析内容是{line_str}")
        return int(pss), int(rss)

    def __parse_adb_dumpsys_meminfo_app_by_process_id_usage(self, lines: Sequence[Sequence[str]]) -> Tuple[int, int]:
        """
        解析adb shell dumpsys meminfo
        :param lines: 执行__exec_adb_dumpsys_meminfo方法后的返回值
        :return: PSS和RSS的值
        """
        total_rss, total_pss = 0, 0
        for line in lines:
            logger.debug(f"line is [{line}]")
            pss, rss = self.__parse_adb_dumpsys_meminfo_app_usage(line)
            total_pss += pss
            total_rss += rss
        logger.debug(f"根据长安的要求，计算PSS的值{total_pss}")
        return total_rss, total_pss

    @staticmethod
    def __parse_qnx_hogs_memory_usage(lines: Sequence[str]):
        """
        通过qnx的hogs方式获取使用的内存，如果需要获取总共的内存，需要使用self.__parse_qnx_top_cpu_memory_usage方法获取
        :param lines: 执行__exec_qnx_hogs_command方法后的返回值
        :return: 总共的内存用量，单位KByte
        """
        total_memory = 0
        for index, line in enumerate(lines):
            if "PID" not in line:
                # 过滤内容
                # 20492   smmu_service     1   0%   0%   2284k   1%
                results = list(filter(lambda x: x.endswith("k"), line.split()))
                memory = results[0].strip()[:-1] if len(results) > 0 else 0
                logger.debug(f"memory is {memory}")
                total_memory += int(memory)
        if total_memory == 0:
            line_str = "\n".join(lines)
            raise RuntimeError(f"请手动查看hogs -i 1命令执行是否有返回值, 目前输入的解析内容是{line_str}")
        return total_memory

    @staticmethod
    def __parse_qnx_hogs_cpu_usage(lines: Sequence[str]):
        """
        通过qnx的hogs方式获取使用的内存，如果需要获取总共的内存，需要使用self.__parse_qnx_top_cpu_memory_usage方法获取
        :param lines: 执行__exec_qnx_hogs_command方法后的返回值
        :return: 总共的内存用量，单位KByte
        """
        total_memory = 0
        for index, line in enumerate(lines):
            if "PID" not in line:
                # 过滤内容
                # 20492   smmu_service     1   0%   0%   2284k   1%
                if "idle" not in line:
                    results = list(filter(lambda x: x.endswith("%"), line.split()))
                    memory = results[-1].strip()[:-1] if len(results) > 0 else 0
                    logger.debug(f"cpu usage is {memory}")
                    total_memory += int(memory)
        if total_memory == 0:
            line_str = "\n".join(lines)
            raise RuntimeError(f"请手动查看hogs -i 1命令执行是否有返回值, 目前输入的解析内容是{line_str}")
        return total_memory

    @staticmethod
    def __parse_procrank_memory_usage(lines: Sequence[str]):
        """
        解析procrank的内存占用，
        :param lines: 使用self.__exec_adb_procrank方法获取的返回值
        :return: 空闲的内存使用量， 总共的内存容量 单位KByte
        """
        keyword = "RAM:"
        total_memory, free_memory = None, None
        for line in lines:
            logger.debug(f"line is {line}")
            new_line = line.strip()
            # RAM: 6475168K total, 793016K free, 38488K buffers, 2590720K cached, 14256K shmem, 299480K slab
            if new_line.startswith(keyword):
                content = new_line[len(keyword):]
                contents = content.split(",")
                for value in contents:
                    if "total" in value:
                        total_memory = int(value.split()[0][:-1])
                    if "free" in value:
                        free_memory = int(value.split()[0][:-1])
        if total_memory is None or free_memory is None:
            line_str = "\n".join(lines)
            raise RuntimeError(f"请手动查看hogs -i 1命令执行是否有返回值, 目前输入的解析内容是{line_str}")
        return free_memory, total_memory

    def __parse_linux_usage(self, lines: Sequence[str]) -> Tuple[float, int, int]:
        """
        解析Linux的使用
        :param lines: 使用self.__exec_linux_top_command方法获取的回显
        :return: cpu占用率， 使用的内存， 总共的内存(KByte)
        """
        line_str = "\n".join(lines)
        content = line_str.replace("[39;49m", "").replace("", "").replace("[1m ", "").replace("[m", "")
        # 先得到Cpu(s): 10.7 us, 然后得到10.7
        cpu = float(self.__get_regex_matched(content, [r"Cpu.*:\s\d+.\d\sus", r"\d+.\d+"]))
        # 先得到Mem :   755952 total，然后得到755952并加K后缀
        total_memory = int(self.__get_regex_matched(content, [r"Mem\s*:\s*\d+\stotal", r"\d+"]).strip())
        # 先得到Mem :   755952 total,   549628 free,    76584 used，然后得到76584 used然后得到76584
        used_memory = int(self.__get_regex_matched(content, [r"Mem\s*:\s*.*used", r"\d+\sused", r"\d+"]).strip())
        return cpu, used_memory, total_memory

    def get_qnx_data(self) -> QNX:
        """
        获取qnx的cpu占用率， 内存占用率
        :return: QNX命名元组, CPU和内存使用率为100%基准
        """
        logger.info("获取qnx的测试数据")
        data = self.__exec_qnx_top_command()
        cpu_use, memory_use, memory_total = self.__parse_qnx_top_cpu_memory_usage(data)
        memory_percent = round(float(memory_use / memory_total * 100), 2)
        return QNX(cpu_use, memory_percent, data)

    def get_android_data(self, device_id: str = None) -> Android:
        """
        获取android的CPU占用率以及内存占用率
        :return: Android命名元组，CPU和内存使用率为100%基准
        """
        logger.info("获取android系统的测试数据")
        top_data = self.__exec_adb_top_command(device_id=device_id)
        dumpsys_data = self.__exec_adb_dumpsys_meminfo(device_id=device_id)
        cpu_usage = self.__parse_adb_top_cpu_usage(top_data)
        use_memory, total_memory = self.__parse_adb_dumpsys_meminfo_usage(dumpsys_data)
        memory_usage = round(float(use_memory / total_memory * 100), 2)
        return Android(cpu_usage, memory_usage, total_memory, dumpsys_data)

    def get_android_app_data(self, app_name: str, device_id: str = None) -> App:
        """
        获取android app的CPU占用率以及内存占用情况
        :param app_name: app的package name
        :param device_id: 设备ID
        :return: App命令元组, CPU使用率为100%基准， 内存使用率为MByte
        """
        logger.info("获取android系统单APP的测试数据")
        top_data = self.__exec_adb_top_command(device_id=device_id, app_name=app_name)
        # 只取了u10的数据
        dumpsys_data = self.__exec_adb_dumpsys_meminfo_use_process(device_id=device_id, app_name=app_name,
                                                                   is_single=False)
        cpu_usage = self.__parse_adb_top_cpu_usage(lines=top_data, app_name=app_name)
        total_rss, total_pss = self.__parse_adb_dumpsys_meminfo_app_by_process_id_usage(dumpsys_data)
        pss = round(float(total_pss / 1024), 2)
        return App(cpu_usage, pss, top_data, dumpsys_data)

    def get_performance(self, port: str, cycle_time: int = 5, device_id: str = None,
                        file: Tuple[str, str, str, str] = None) -> Tuple:
        self.connect(port)
        content_list = []
        for i in range(cycle_time):
            logger.info(f"第{i + 1}次测试")
            logger.debug("get android top")
            android_top_timestamp = self.__utils.get_time_as_string("%Y-%m-%d %H:%M:%S")
            android_top_data = self.__exec_adb_top_command(device_id=device_id)
            logger.debug("get android dumpsys meminfo")
            dumpsys_timestamp = self.__utils.get_time_as_string("%Y-%m-%d %H:%M:%S")
            dumpsys_data = self.__exec_adb_dumpsys_meminfo(device_id=device_id)
            self.__utils.random_sleep(1.0, 2.0)
            logger.debug("get qnx top")
            top_timestamp = self.__utils.get_time_as_string("%Y-%m-%d %H:%M:%S")
            qnx_top_data = self.__exec_qnx_top_command()
            test_result_tuple = android_top_timestamp, android_top_data, dumpsys_timestamp, dumpsys_data, top_timestamp, qnx_top_data
            content_list.append(test_result_tuple)
            # 执行并返回结果需要时间有点久，所以不停止直接运行了
        qnx_top = []
        android_top = []
        dumpsys_meminfo = []
        performance_info = []
        total_qnx_cpu, total_qnx_memory, total_android_cpu, total_android_memory = 0, 0, 0, 0
        for content in content_list:
            android_top_timestamp, android_top_data, dumpsys_timestamp, dumpsys_data, top_timestamp, qnx_top_data = content
            qnx_top.append(qnx_top_data)
            android_top.append(android_top_data)
            dumpsys_meminfo.append(dumpsys_data)
            cpu_usage = self.__parse_adb_top_cpu_usage(android_top_data)
            use_memory, total_memory = self.__parse_adb_dumpsys_meminfo_usage(dumpsys_data)
            memory_usage = round(float(use_memory / total_memory * 100), 2)
            cpu_use, memory_use, memory_total = self.__parse_qnx_top_cpu_memory_usage(qnx_top_data)
            memory_percent = round(float(memory_use / memory_total * 100), 2)
            # qnx的CPU占用率
            total_qnx_cpu += cpu_use
            # qnx的内存占用率
            total_qnx_memory += memory_percent
            # android的CPU占用率
            total_android_cpu += cpu_usage
            # android的内存占用率
            total_android_memory += memory_usage
        self.disconnect()
        average_qnx_cpu = round(total_qnx_cpu / cycle_time, 2)
        average_qnx_memory = round(total_qnx_memory / cycle_time, 2)
        average_android_cpu = round(total_android_cpu / cycle_time, 2)
        average_android_memory = round(total_android_memory / cycle_time, 2)
        performance_info.append(f"QNX CPU占用率{average_qnx_cpu}%, 内存占用率{average_qnx_memory}%")
        performance_info.append(f"Android CPU占用率{average_android_cpu}%, 内存占用率{average_android_memory}%")
        # 写入文档
        if file:
            # 对内容处理
            android, dumpsys, qnx = [], [], []
            for content in content_list:
                android_top_timestamp, android_top_data, dumpsys_timestamp, dumpsys_data, top_timestamp, qnx_top_data = content
                android_top_data = list(map(lambda x: f"{android_top_timestamp} - {x}", android_top_data))
                dumpsys_data = list(map(lambda x: f"{dumpsys_timestamp} - {x}", dumpsys_data))
                qnx_top_data = list(map(lambda x: f"{top_timestamp} - {x}", qnx_top_data))
                android.append("\n".join(android_top_data))
                dumpsys.append("\n".join(dumpsys_data))
                qnx.append("\n".join(qnx_top_data))
            qnx_top_str = "\n".join(qnx)
            android_str = "\n".join(android)
            dumpsys_str = "\n".join(dumpsys)
            performance_str = "\n".join(performance_info)
            qnx_file, android_file, dumpsys_meminfo_file, performance_file = file
            with open(qnx_file, "w", encoding="utf-8") as f:
                f.write(qnx_top_str)
            with open(android_file, "w", encoding="utf-8") as f:
                f.write(android_str)
            with open(dumpsys_meminfo_file, "w", encoding="utf-8") as f:
                f.write(dumpsys_str)
            with open(performance_file, "w", encoding="utf-8") as f:
                f.write(performance_str)
        return average_qnx_cpu, average_qnx_memory, average_android_cpu, average_android_memory
