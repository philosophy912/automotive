# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2021, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        xmind8_writer.py
# @Author:      lizhe
# @Created:     2021/7/3 - 22:31
# --------------------------------------------------------
import os
from typing import Dict, List

from automotive.application.common.constants import split_char, Testcase, automation_prefix, replace_char, \
    module_prefix, requirement_prefix
from automotive.application.common.interfaces import BaseWriter, TestCases
from automotive.logger.logger import logger

try:
    import xlwings as xw
except ModuleNotFoundError:
    os.system("pip install xlwings")
finally:
    import xlwings as xw
    from xlwings import Sheet, Book

try:
    import xmind
except ModuleNotFoundError:
    os.system("pip install xmind")
finally:
    import xmind
    from xmind.core.topic import TopicElement
    from xmind.core.workbook import WorkbookDocument


class Xmind8SampleWriter(BaseWriter):

    def write_to_file(self, file: str, testcases: Dict[str, TestCases], tempfile: str):
        """
        把测试用例写xmind
        :param testcases: 测试用例
        :param file:  输出的文件地址
        """
        self._check_testcases(testcases)
        for module, testcase_list in testcases.items():
            logger.info(f"now write {module} to xmind")
            self.__write_test_case_to_xmind(file, testcase_list, module)
        logger.info("testcase write done")

    def __write_test_case_to_xmind(self, output: str, testcases: TestCases, module: str):
        # 新建xmind
        workbook = xmind.load(output)
        sheet = workbook.createSheet(0)
        sheet.setTitle("画布")
        root_topic = sheet.getRootTopic()
        root_topic.setTitle(module)
        self.__add_test_cases(root_topic, testcases, workbook, module)
        xmind.save(workbook)

    def __add_test_cases(self, root_topic: TopicElement, testcases: TestCases, workbook: WorkbookDocument, module: str):
        """
        遍历所有的测试用例
        :param root_topic:
        :param testcases:
        :param workbook:
        :param module:
        :return:
        """
        # print(module)
        # 自检APP-THU自检
        if split_char in module:
            main_module_name = module.split(split_char)
        elif replace_char in module:
            main_module_name = module.split(replace_char)
        else:
            main_module_name = [module]
        logger.debug(f"main_module_name = {main_module_name}")
        for index, testcase in enumerate(testcases):
            logger.debug(f"now write the {index + 1} testcase")
            # print(testcase.name)
            modules = testcase.name.split(replace_char)
            inter = modules[-1]
            modules.pop(-1)
            for module in main_module_name:
                modules.remove(module)
            # print(module_list)
            # module_str = testcase.module
            # logger.debug(f"module is {module_str}")
            # modules = module_str.split(split_char)
            modules = list(map(lambda x: f"{module_prefix}{x}", modules))
            modules.extend(testcase.pre_condition)
            logger.debug(f"modules = [{modules}]")
            subtopics = root_topic.getSubTopics()
            if len(subtopics) > 0:
                current_topic = root_topic
                for module in modules:
                    try:
                        logger.debug(f"try to found module {module} in {current_topic.getTitle()}")
                        # 先查找当前是否有module的节点，有则继续循环
                        current_topic = self.__get_specific_topic(module, current_topic)
                        continue
                    except RuntimeError:
                        # 没有该节点就添加子节点
                        sub_topic = self.__create_topic(module, workbook)
                        current_topic.addSubTopic(sub_topic)
                        # 因为新添加了节点，所以当前节点变为了父节点
                        current_topic = sub_topic
                        logger.debug(f"create sub topic {sub_topic.getTitle()} in {current_topic.getTitle()}")
            else:
                current_topic = self.__add_subtopic(root_topic, modules, workbook)
            # 当前节点下面就需要创建测试用例节点了
            logger.debug(f"current topic = {current_topic.getTitle()} and module is {modules[-1]}")
            # ……新增一个id参数
           
            self.__create_test_case_node(inter, testcase, current_topic, workbook)

    def __create_test_case_node(self,
                                inter: int,
                                testcase: Testcase,
                                testcase_topic: TopicElement,
                                workbook: WorkbookDocument,
                                result_flag: bool = False,):
        """
        创建测试用例子节点

        :param testcase_topic: 测试用例节点

        :param workbook: xmind文件
        """
        # 添加了测试用例节点, 判断了是否关联了需求ID
        topic_titles = ["TC"]
        topic_titles.append(f"<{inter}>")
        if testcase.automation:
            topic_titles.append(automation_prefix)
        actions = []
        if len(testcase.actions) > 1:
            for i, action in enumerate(testcase.actions):
                actions.append(f"{i + 1}.{action}")
            actions = "\n".join(actions)
        else:
            actions = "\n".join(testcase.actions)
        topic_titles.append(actions)
        if testcase.requirement_id != "":
            topic_titles.append(f"[{testcase.requirement_id}]")
        tc_topic = self.__create_topic("".join(topic_titles), workbook)
        logger.debug(f"testcase.priority = {testcase.priority}")
        # 添加修改记录标签
        if testcase.fix is not None:
            tc_topic.addMarker(testcase.fix)
        if testcase.priority is not None:
            tc_topic.addMarker(f"priority-{testcase.priority}")
        testcase_topic.addSubTopic(tc_topic)
        if testcase.exceptions:
            for exception in testcase.exceptions:
                exe_topic = self.__create_topic(exception, workbook)
                tc_topic.addSubTopic(exe_topic)
        if testcase.requirement:
            for requirement in testcase.requirement:
                req_topic = self.__create_topic(f"{requirement_prefix}{requirement}", workbook)
                tc_topic.addSubTopic(req_topic)
        if result_flag:
            if testcase.test_result:
                res_topic = self.__create_topic(testcase.test_result, workbook)
                tc_topic.addSubTopic(res_topic)

    def __handle_steps(self, s_topic: TopicElement, steps: Dict[str, List[str]], workbook: WorkbookDocument):
        """
        写入执行步骤
        :param s_topic: TC下面的s节点
        :param steps: 执行步骤
        :param workbook: xmind文件
        """
        for key, values in steps.items():
            logger.debug(f"key = {key} and value = {values}")
            step_topic = self.__create_topic(key, workbook)
            s_topic.addSubTopic(step_topic)
            if len(values) > 0:
                for value in values:
                    value_topic = self.__create_topic(value, workbook)
                    step_topic.addSubTopic(value_topic)

    def __handle_pre_condition(self, p_topic: TopicElement, pre_condition: List[str], workbook: WorkbookDocument):
        """
        写入前置条件
        :param p_topic:  TC下面的p节点
        :param pre_condition: 前置条件列表
        :param workbook: xmind文件
        """
        for pre in pre_condition:
            logger.debug(f"pre  = {pre}")
            pre_topic = self.__create_topic(pre, workbook)
            p_topic.addSubTopic(pre_topic)

    @staticmethod
    def __get_specific_topic(module: str, topic: TopicElement) -> TopicElement:
        """
        查找指定的节点
        :param module: 被查找的节点的名称
        :param topic:  节点
        :return: 查找到的节点
        """
        subtopics = topic.getSubTopics()
        for sub_topic in subtopics:
            title = sub_topic.getTitle()
            if module == title:
                logger.debug(f"{module} be founded")
                return sub_topic
        raise RuntimeError(f"no subtopic[{module}] found ")

    def __add_subtopic(self, topic: TopicElement, modules: List[str], workbook: WorkbookDocument) -> TopicElement:
        """
        新文件的时候新增子节点
        :param topic: 根节点
        :param modules: 模块名列表
        :param workbook: xmind文件
        """
        topics = []
        for module in modules:
            sub_topic = self.__create_topic(module, workbook)
            if len(topics) == 0:
                topics.append(topic.addSubTopic(sub_topic))
            else:
                t = topics[-1]
                topics.append(t.addSubTopic(sub_topic))
        return topics[-1]

    @staticmethod
    def __create_topic(module: str, workbook: WorkbookDocument) -> TopicElement:
        """
        新增节点
        :param module: 节点名
        :param workbook: xmind文件
        :return: 节点对象
        """
        logger.debug(f"create topic {module}")
        sub_topic = TopicElement(ownerWorkbook=workbook)
        sub_topic.setTitle(module)
        return sub_topic
