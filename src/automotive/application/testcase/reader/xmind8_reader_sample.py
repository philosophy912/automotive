# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2021, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        xmind8_reader_sample.py
# @Author:      lizhe
# @Created:     2021/12/9 - 22:23
# --------------------------------------------------------
import os
import random
from typing import Dict, Tuple, Sequence, List
from automotive.application.common.constants import REPLACE_CHAR, SPLIT_CHAR, Testcase, REQUIREMENT_PREFIX, RESULTS, \
    MODULE_PREFIX, AUTOMATION_PREFIX, INDEX_LIST
from automotive.logger.logger import logger
from automotive.application.common.interfaces import BaseReader, TestCases
from automotive.application.common.enums import ModifyTypeEnum

try:
    import xmind
except ModuleNotFoundError:
    os.system("pip install xmind")
finally:
    import xmind
    from xmind.core.topic import TopicElement


class Xmind8SampleReader(BaseReader):

    def read_from_file(self, file: str) -> Dict[str, TestCases]:
        module, testcase = self.__read_test_case_from_xmind(file)
        self.__handle_category(module, testcase)
        return {module: testcase}

    def __duplicate(self, modules: list, temple: list) -> int:
        """
        产生随机数字random_id，直到random_id不等于列表（temple）中的元素
        :param modules:模块列表  例如：”冷却液温度"
        :param temple:存放testcase-id的列表
        :return:testcase-ID值
        """
        # second
        random_id = random.randint(1, len(modules) + 200)
        if random_id in temple:
            return self.__duplicate(modules, temple)
        else:
            return random_id

    def __removal_duplicate(self, modules: list, temple: list) -> list:
        """
        补全ID
        :param modules: testcase里面的module值，例如：“冷却液温度”
        :param temple: 存放原始xmind文件中testcase-id值的列表
        :return: 去重后的modules
        """

        for i in range(len(modules) - len(temple)):
            random_id = self.__duplicate(modules, temple)
            temple.append(random_id)
        if len(temple) == len(modules):
            for i in range(len(temple)):
                modules[i] = modules[i] + "_" + str(temple[i])
        else:
            raise RuntimeError(f"id length is error")
        return modules

    def __check_modules(self, testcases: TestCases, template: list) -> TestCases:
        """
        重写testcase.module     加了ID
        :param testcases: 用例类，例如：“冷却液温度”
        :param template: 存放原始xmind文件中testcase-id值的列表
        :return: 去重后的modules
        """
        # 把去重后的module，重新写入testcase.module中
        # temple_modules = []
        temple_modules = list(map(lambda x: x.module, testcases))
        # 去重
        modules = self.__removal_duplicate(temple_modules, template)
        for i in range(len(testcases)):
            testcases[i].module = modules[i]
        return testcases

    @staticmethod
    def __handle_category(module: str, testcases: TestCases):
        for i, testcase in enumerate(testcases):
            if SPLIT_CHAR in module:
                module_list = module.split(SPLIT_CHAR)
            elif REPLACE_CHAR in module:
                module_list = module.split(REPLACE_CHAR)
            else:
                module_list = [module]
            category = module_list.pop(0)
            testcase.category = category
            modules = testcase.module.split(SPLIT_CHAR)
            if module_list:
                module_list.extend(modules)
                # 重置模块名，方便后续统一调用
                modules = module_list
                testcase.module = SPLIT_CHAR.join(modules)
            module_str = REPLACE_CHAR.join(modules)
            testcase.name = f"{category}{REPLACE_CHAR}{module_str}"

    @staticmethod
    def _read_root_topic_data_from_file(xmind_file: str) -> TopicElement:
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
    def _is_xmind8(root_topic: TopicElement) -> bool:
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
        :param file: xmind文件
        :return:  解析出来的测试用例集合,该集合中的对象是Testcase
        """
        logger.debug(f"now read file {file}")
        root_topic = self._read_root_topic_data_from_file(file)
        if not self._is_xmind8(root_topic):
            module_name, module_id = self._parse_id(root_topic.getTitle())
            if module_id != "":
                self.__module_id = module_id
                dict_name = f"{module_name}{REPLACE_CHAR}{module_id}"
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
        """
        title = topic.getTitle()
        logger.debug(f"title = {title}, modules = {modules}")
        if title is None:
            raise RuntimeError(fr"{modules}后面是空节点，请检查")
        # 过滤掉#号开头的内容
        if title and not title.startswith("#"):
            if title.lower().startswith("tc"):
                # 去掉了根模块
                # ["多媒体","显示","中文"] split_char = '-'  "显示 - 中文"
                module = SPLIT_CHAR.join(modules[1:])
                testcases.append((module, topic))
            else:
                # 需要去掉self.__split_char定义的字符串连接符为空字符或者指定支付
                title = title.replace(SPLIT_CHAR, REPLACE_CHAR)
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

    def __convert_testcase(self, test_cases: Sequence[TopicElement]) -> TestCases:
        """
            解析测试用例
            :param test_cases: 测试用例对象（字典结构）
            :return: 测试用例集合
        """
        testcases = []
        # test_cat 类型是 TopicElement
        # 设置一个存放testcaseID的列表
        template = []
        for test_case in test_cases:
            # 这个地方的模块是所有模块的集合
            module, tc = test_case
            # 类对象，相当于数据的封装，这个地方也可以写成自己定义的字典
            testcase = Testcase()
            # 子模块
            modules = []
            # 前置条件
            pre_conditions = []
            # module = [M]初始化界面-HU处于工作状态-初始化APP中
            module_list = module.split(SPLIT_CHAR)
            for module_str in module_list:
                if module_str.startswith(MODULE_PREFIX):
                    modules.append(module_str.replace(MODULE_PREFIX, ""))
                else:
                    pre_conditions.append(module_str)
            testcase.pre_condition = pre_conditions
            title = tc.getTitle()
            # testcaseID inter(判断有没有加case-ID）
            # 去掉TC
            ts_title = title[2:]
            # 如果[A]在title里面，去掉[A],并加自动化标签
            if AUTOMATION_PREFIX in ts_title:
                testcase.automation = True
                ts_title = ts_title.replace(AUTOMATION_PREFIX, "")

            # # 确定有testcase-id的条件是：第一个元素<; && <a>  type(a)=int
            # if ts_title[0] is '<' and isinstance(ts_title[1:ts_title.find('>')], int):
            #     # 取ID号
            #     start_n = ts_title.find('<')
            #     end_n = ts_title.find('>')
            #     # 取到的ID号  inter
            #     inter = ts_title[start_n + 1:end_n]
            #     title = ts_title[end_n + 1:]
            #     # 把ID值放到列表中
            #     template.append(inter)
            # else:
            #     title = title[2:]
            # testcaseID inter(判断有没有加case-ID）
            # if ts_title[0] is '<' and int(ts_title[1:ts_title.find('>')]):
            # 为TC添加testcase-id
            start_n = ts_title.find('<')
            end_n = ts_title.find('>')
            inter = ts_title[start_n + 1:end_n]
            if '_' in inter:
                # if isinstance(inter.split('_')[0], int) and isinstance(inter.split('_')[1], int):
                if inter.split('_')[0].isdigit() and inter.split('_')[1].isdigit():
                    # 去掉<ID>
                    title = ts_title[end_n + 1:]
                    # 存放ID值，用于判断查重
                    template.append(inter)
                else:
                    raise RuntimeError(f"{title}: 该模块没有加<ID>，请检查")

            elif inter.isdigit():
                title = ts_title[end_n + 1:]
                # 存放ID值，用于判断查重
                template.append(inter)

            else:
                raise RuntimeError(f"{title}: 该模块没有加<ID>，请检查")

            # testcase.module = ACC状态显示（模块名M）
            # testcase.module = split_char.join(modules)
            # 给testcase加ID号
            testcase.module = SPLIT_CHAR.join(modules) + '_' + inter
            # 去掉TC和ID
            name = title
            # 考虑TC后有异常符号，做替换处理
            if name.startswith(" ") or name.startswith(",") or name.startswith("_") or name.startswith("-"):
                name = name[1:]
            # 增加异常处理testcase是None时，导致的startswith报错
            if name is None:
                name = ''
            # 这里是测试步骤的名称
            testcase.actions = self.__handle_actions(name)
            # 解析需求以及测试结果还有期望结果三个部分
            requirements, exceptions, result = self.__parse_testcase(tc)
            testcase.requirement = requirements if requirements else None
            testcase.exceptions = exceptions if exceptions else None
            testcase.test_result = result
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
                        priority = int(marker_id.split(SPLIT_CHAR)[1])
                        if priority > 4:
                            priority = 4
                        testcase.priority = priority
                    if marker_id is not None:
                        try:
                            fix_cell = ModifyTypeEnum.read_xmind_from_name(marker_id)
                            testcase.fix = fix_cell
                        except ValueError:
                            logger.debug(f"{marker_id} is not ModifyTypeEnum")

        # 判断ID是否为空
        logger.info(fr"总用例数量{len(template)}")
        for tem in template:
            if template.count(tem) > 1:
                raise RuntimeError(f"{tem} : 此ID有重复值，请检查: ")
        return testcases

    @staticmethod
    def __parse_testcase(testcase: TopicElement) -> Tuple[Sequence[str], Sequence[str], str]:
        requirements = []
        exceptions = []
        result = None
        testcase_title = testcase.getTitle()
        logger.debug(f"testcase is {testcase_title}")
        topics = testcase.getSubTopics()
        for topic in topics:
            title = topic.getTitle()
            title = title.strip()
            if title.startswith(REQUIREMENT_PREFIX):
                requirements.append(title.replace(REQUIREMENT_PREFIX, ""))
            elif title.upper() in RESULTS:
                result = title.upper()
            else:
                exceptions.append(title)
        return requirements, exceptions, result

    def __handle_actions(self, actions: str):
        total = []
        lines = actions.split("\n")
        lines = list(filter(lambda x: x != "", lines))
        temp = []
        for i, line in enumerate(lines):
            if line[0] in INDEX_LIST:
                temp.append(i)
        # 没有序号的情况，即只有一个操作步骤
        if temp:
            # 列表切片操作 0 2
            temp.pop(0)
            start_index = 0
            for t in temp:
                content = "\n".join(lines[start_index:t])
                total.append(content)
                start_index = t
            content = "\n".join(lines[start_index:])
            total.append(content)
        else:
            total.append(actions)
        # 处理掉1.类似的数据
        new_total = []
        for t in total:
            content = self.__handle_prefix_str(t)
            new_total.append(content)
        return new_total

    @staticmethod
    def __handle_prefix_str(content: str) -> str:
        """
        处理1. 2.这种前缀，去掉他们
        :param content:
        :return:
        """
        if content[0] in index_list:
            content = content[1:]
            if content[0] in (".", "。", " "):
                content = content[1:]
        return content
