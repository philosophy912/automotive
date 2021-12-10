# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2021, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        xmind8_reader.py
# @Author:      lizhe
# @Created:     2021/7/3 - 22:03
# --------------------------------------------------------
import os
from typing import Dict, List, Tuple, Optional

from automotive.application.common.constants import replace_char, split_char, Testcase
from automotive.application.common.interfaces import BaseReader, TestCases
from automotive.logger.logger import logger

try:
    import xmind
except ModuleNotFoundError:
    os.system("pip install xmind")
finally:
    import xmind
    from xmind.core.topic import TopicElement


class Xmind8Reader(BaseReader):
    def __init__(self):
        self.__module_id = None

    def read_from_file(self, file: str, ) -> Dict[str, TestCases]:
        """
        从文件中读取内容，返回字典类型
        :param file: xmind文件
        """
        module, testcase = self.__read_test_case_from_xmind(file)
        return {module: testcase}

    @staticmethod
    def __read_root_topic_data_from_file(xmind_file: str) -> TopicElement:
        """
        从xmind文件中读取到了所有的内容
        :param xmind_file: xmind8的文档，
        :return: 返回根节点
        """
        workbook = xmind.load(xmind_file)
        sheet = workbook.getPrimarySheet()
        root_topic = sheet.getRootTopic()
        # 无子节点的情况 sub_topics为空列表
        logger.debug(f"root topic title is {root_topic.getTitle()}")
        return root_topic

    @staticmethod
    def __is_xmind8(root_topic: TopicElement) -> bool:
        """
        xmind版本是否是xind8
        :param root_topic: 根节点
        :return: bool
        """
        root_data = root_topic.getData()
        title = root_data["title"]
        return "Warning" in title and "Attention" in title and "Warnung" in title

    def __read_test_case_from_xmind(self, file: str) -> Tuple[str, TestCases]:
        """
        从xmind8文件中读取测试用例
        xmind8规则
        1. 根节点作为大的模块名称
        2. 子节点如果以#号开头的模块，都不解析
        3. 子节点如果以TC开头的作为测试用例
        4. TC开头的子节点必须有P和S开头的两个节点，分别代表preCondition和Steps
        5. TC子节点如果没有P和S(有且仅有一对)的节点，则该测试用例不会有前置条件和执行步骤
        6. P下面必须至少有一个子节点，否则前置条件为空(出现该情况则TC为空用例)，当然它可以有多个子节点
        7. S下面必须至少有一个子节点和一个子节点的子节点，即有一个操作步骤和一个对应的结果。
        8. S下面子节点代表执行步骤，执行步骤下的子节点代表期望结果，该期望结果可以为空
        9. 执行步骤下面可以有一个或者多个子节点，代表一个操作步骤下面有多个期望结果。
        10. 执行步骤下面也可以没有子节点，代表操作步骤不需要检查期望结果。
        11. S下面至少有一个期望结果。否则测试用例仅有名字
        :param file: xmind文件
        :return:  解析出来的测试用例集合,该集合中的对象是Testcase
        """
        logger.debug(f"now read file {file}")
        root_topic = self.__read_root_topic_data_from_file(file)
        if not self.__is_xmind8(root_topic):
            module_name, module_id = self._parse_id(root_topic.getTitle())
            if module_id != "":
                self.__module_id = module_id
                dict_name = f"{module_name}{replace_char}{module_id}"
            else:
                dict_name = module_name
            testcases = self.__filter_test_case_topic(root_topic)
            logger.info(f"[{file}] contains [{len(testcases)}] testcases")
            return dict_name, testcases
        xmind_url = "https://www.xmind.cn/download/xmind8/"
        raise RuntimeError(f"please convert xmind file by using xmind8, download url is {xmind_url}")

    def __filter_test_case_topic(self, root_topic: TopicElement) -> TestCases:
        """
        根据根节点遍历出来所有的测试用例的对象（规则参考read_test_case的注释)
        :param root_topic: 根节点
        :return: 解析出来的测试用例集合,该集合中的对象是Testcase
        """
        test_cases = []
        modules = []
        # 此时test_cases中的对象仍然是字典
        self.__filter_testcase(root_topic, test_cases, modules)
        # 过滤掉无效的测试用例
        testcases = self.__convert_testcase(test_cases)
        return testcases

    def __filter_testcase(self, topic: TopicElement, testcases: List[Tuple[str, TopicElement]], modules: List[str]):
        """
        递归查找测试用例
        :param topic: 节点
        :param testcases: 测试用例对象列表
        # 实现方式
        传入参数为topic（节点）
        testcases表示测试用例所在节点的列表
        modules表示模块的节点列表
        1、获取当前节点的title
        2、判断当前节点是不是TC开头
        2.1、 如果是TC开头的，表示是测试用例节点
        2.2、 如果不是TC开头，表示不是测试用例节点，是模块节点
        2.2.1、 由于不是测试用例，看下是否存在子节点
        2.2.1.1 、存在子节点： 遍历子节点
        """
        title = topic.getTitle()
        logger.debug(f"title = {title}, modules = {modules}")
        # 过滤掉#号开头的内容
        if title and not title.startswith("#"):
            if title.lower().startswith("tc"):
                # 去掉了根模块
                # ["多媒体","显示","中文"] split_char = '-'  "显示 - 中文"
                module = split_char.join(modules[1:])
                testcases.append((module, topic))
            else:
                # 需要去掉self.__split_char定义的字符串连接符为空字符或者指定支付
                title = title.replace(split_char, replace_char)
                logger.debug(f"modules = {modules} it will append {title}")
                modules.append(title)
                logger.debug(f"after appends modules = {modules}")
                topics = topic.getSubTopics()
                if len(topics) > 0:
                    for t in topics:
                        self.__filter_testcase(t, testcases, modules)
                    logger.debug(f"not found testcase pop module, now modules = {modules}")
                    modules.pop(-1)
                    logger.debug(f"after pop module,  modules = {modules}")
                else:
                    modules.pop(-1)

    @staticmethod
    def __convert_steps_condition(steps: Dict[str, List[str]]) -> Tuple[str, str]:
        """

        :param steps:
        :return:
        """
        steps_contents = []
        exception_contents = []
        if len(steps) > 0:
            # 用于定义主编号
            index = 1
            for key, value in steps.items():
                steps_contents.append(f"{index} {key}")
                value_size = len(value)
                # 用于定义子编号
                if value_size > 0:
                    if value_size == 1:
                        for sub_index, exception in enumerate(value):
                            exception_contents.append(f"{index} {exception}")
                    else:
                        for sub_index, exception in enumerate(value):
                            exception_contents.append(f"{index}.{sub_index + 1} {exception}")
                index += 1
        steps_str = "\n".join(steps_contents)
        exception_str = "\n".join(exception_contents)
        return steps_str, exception_str

    def __convert_testcase(self, test_cases: List[TopicElement]) -> TestCases:
        """
        解析测试用例
        :param test_cases: 测试用例对象（字典结构）
        :return: 测试用例集合
        """
        testcases = []
        # test_cat 类型是 TopicElement
        for test_case in test_cases:
            # 这个地方的模块是所有模块的集合
            module, tc = test_case
            # 类对象，相当于数据的封装，这个地方也可以写成自己定义的字典
            testcase = Testcase()
            testcase.module = module
            # 循环遍历的时候加入module_id
            if self.__module_id:
                testcase.module_id = self.__module_id
            # 测试用例名 TC“推荐”涵盖内容[#512] 用于拆分成测试用例名和禅道的需求ID
            name, name_id = self._parse_id(tc.getTitle()[2:])
            # 考虑TC后有异常符号，做替换处理
            if name.startswith(" ") or name.startswith(",") or name.startswith("_") or name.startswith("-"):
                name = name[1:]
            # 增加异常处理testcase是None时，导致的startswith报错
            if name is None:
                name = ''
            testcase.name = name
            if name_id != "":
                testcase.requirement_id = name_id
            # 解析
            pre_condition_list, steps_dict = self.__parse_testcase(tc)
            if pre_condition_list and steps_dict:
                testcase.pre_condition = pre_condition_list
                testcase.steps = steps_dict
            testcases.append(testcase)
            # 解析优先级
            markers = tc.getMarkers()
            if len(markers) > 0:
                # 可能存在优先级
                for marker in markers:
                    marker_id = str(marker.getMarkerId())
                    logger.debug(f"marker_id = {marker_id}")
                    if marker_id.startswith("priority"):
                        # 该用例存在优先级
                        priority = int(marker_id.split(split_char)[1])
                        if priority > 4:
                            priority = 4
                        testcase.priority = priority
            testcase.calc_hash()
        return testcases

    def __parse_testcase(self, testcase: TopicElement) -> Tuple[Optional[List[str]], Optional[Dict[str, List[str]]]]:
        """
        解析单个测试用例中的测试用例部分

        :param testcase: 单个测试用例对象（字典结构)

        :return: 前置条件, 执行步骤
        """
        testcase_title = testcase.getTitle()
        logger.debug(f"testcase is {testcase_title}")
        topics = testcase.getSubTopics()
        # 要考虑#的情况
        if len(topics) < 2:
            # 只支持一个P和一个S
            logger.debug("子节点长度小于2")
            return None, None
        else:
            pre_condition = None
            steps = None
            for topic in topics:
                title = topic.getTitle()
                if title.startswith("p") or title.startswith("P"):
                    pre_condition = topic
                if title.startswith("S") or title.startswith("s"):
                    steps = topic
            if pre_condition and steps:
                logger.debug(f"pre_condition title is {pre_condition.getTitle()}")
                logger.debug(f"steps title is {steps.getTitle()}")
                # 树形结构的顺序的部分有xmind来保障
                pre_condition_list = self.__parse_pre_condition(pre_condition)
                steps_dict = self.__parse_steps(steps)
                # 保证前置条件必须有，保证执行步骤必须有
                if len(pre_condition_list) > 0 and len(steps_dict) > 0:
                    return pre_condition_list, steps_dict
                else:
                    return None, None
            else:
                # 没有找到一个S和一个P
                return None, None

    @staticmethod
    def __parse_pre_condition(pre_condition: TopicElement) -> List[str]:
        """
        解析precondition， 允许前置条件为空
        :param pre_condition: 前置条件
        :return: 前置条件列表
        """
        logger.debug(f"pre_condition = {pre_condition}")
        pre_conditions = []
        topics = pre_condition.getSubTopics()
        if len(topics) > 0:
            for topic in topics:
                title = topic.getTitle()
                logger.debug(f"title = {title}")
                # 过滤掉#开头的
                if title and not title.startswith("#"):
                    pre_conditions.append(title)
        return pre_conditions

    @staticmethod
    def _convert_pre_condition(pre_conditions: List[str]) -> str:
        """
        先把列表加上序号来进行相关的处理
        :param pre_conditions:前置条件列表
        :return: 要写入excel的文字
        """
        if len(pre_conditions) > 0:
            contents = []
            for i, pre_condition in enumerate(pre_conditions):
                contents.append(f"{i + 1} {pre_condition}")
            return "\n".join(contents)
        else:
            return ""

    def __parse_steps(self, steps: TopicElement) -> Dict[str, List[str]]:
        """
        解析steps
        :param steps: 步骤
        :return: 执行步骤
        """
        logger.debug(f"steps is {steps.getTitle()}")
        actions = dict()
        topics = steps.getSubTopics()
        if len(topics) > 0:
            for topic in topics:
                title = topic.getTitle()
                logger.debug(f"title = {title}")
                if not title.startswith("#"):
                    exception = []
                    exception_topics = topic.getSubTopics()
                    if len(exception_topics) > 0:
                        for exception_topic in exception_topics:
                            exception_title = exception_topic.getTitle()
                            if exception_title is None:
                                exception_title = ''
                            if not exception_title.startswith("#"):
                                exception.append(exception_title)
                        actions[title] = exception
                    else:
                        actions[title] = exception
        if not self.__is_value_correct(actions):
            actions.clear()
        return actions

    @staticmethod
    def __is_value_correct(actions: dict) -> bool:
        """
        判断执行步骤和期望结果是否符合要求
        :param actions:
        :return:
        """
        logger.debug(f"actions = {actions}")
        count = 0
        for key, value in actions.items():
            logger.debug(f"key = {key}")
            if len(value) != 0:
                count += 1
        return count > 0
