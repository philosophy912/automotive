# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        testcase_writer.py
# @Author:      lizhe
# @Created:     2022/5/3 - 11:40
# --------------------------------------------------------
import os
from typing import Dict, List, Optional

from automotive.application.common.interfaces import TestCases
from automotive.application.common.constants import Testcase
from automotive.logger.logger import logger
from automotive.utils.common.interfaces import sht
from automotive.utils.utils import Utils
from automotive.utils.excel_utils import ExcelUtils

folder, file = os.path.split(__file__)
__template_file = os.path.join(folder, "template_testcase.xlsx")
# Xmind中只支持SLEEP、LOST、RESUME三个关键词
SLEEP = "sleep"
LOST = "lost"
RESUME = "resume"
# 操作部分中对应到的关键词，即template中表名
CAN_ACTION = "canaction"
SCREENSHOT_ACTION = "screenshotaction"
COMMON = "common"
IMAGE_COMPARE = "imagecompare"
# 对象列表部分，一个对象列表对应一个sheet中的数据
# 测试用例(TestCase)的对象列表
test_case_list = []
# 图片对比(ImageCompare)的对象列表
image_compare_list = []
# 公共函数(Common)的对象列表
common_list = []
# 截图操作(ScreenShotAction)的对象列表
screenshot_action_list = []
# Can信号(CanAction)的对象列表
can_action_list = []
# template表名
can_action_sheet = "Can信号(CanAction)"
screenshot_action_sheet = "截图操作(ScreenShotAction)"
common_sheet = "公共函数(Common)"
image_compare_sheet = "图片对比(ImageCompare)"
testcase_sheet = "测试用例(TestCase)"
# template表对应关系
sheet_names = {
    can_action_sheet: can_action_list,
    screenshot_action_sheet: screenshot_action_list,
    common_sheet: common_list,
    image_compare_sheet: image_compare_list,
    testcase_sheet: test_case_list
}
excel_utils = ExcelUtils()
# 开始写的行数
start_row = 2
# 边框
border = True


class __Testcase(object):
    """对应了模板文件中的测试用例(TestCase)"""

    def __init__(self):
        self.id = ""
        self.name = ""
        self.comments = ""
        self.description = ""
        self.testcase_type = "全自动"
        self.module_name = ""
        self.pre_condition_description = ""
        self.pre_condition = ""
        self.steps_description = ""
        self.steps = ""
        self.expect_description = ""
        self.expect = ""

    def convert(self) -> List:
        return [self.name, self.comments, self.description, self.testcase_type, self.module_name,
                self.pre_condition_description, self.pre_condition, self.steps_description, self.steps,
                self.expect_description, self.expect]


class __ImageCompare(object):
    """对应了模板文件中的图片对比(ImageCompare)"""

    def __init__(self):
        self.id = ""
        self.name = ""
        self.comments = ""
        self.device_type = "QNX"
        self.compare_type = "亮图"
        self.image_name = ""
        self.template_light = ""
        self.template_dark = ""
        self.positions = ""
        self.similarity = ""
        self.is_gray = "否"
        self.threshold = "240"

    def convert(self) -> List:
        return [self.name, self.comments, self.device_type, self.compare_type, self.image_name, self.template_light,
                self.template_dark, self.positions, self.similarity, self.is_gray, self.threshold]


class __Common(object):
    """对应了模板文件中的公共函数(Common)"""

    def __init__(self):
        self.id = ""
        self.name = ""
        self.comments = ""
        self.module_name = "can_service"
        self.function_name = ""
        self.params = ""

    def convert(self) -> List:
        return [self.name, self.comments, self.module_name, self.function_name, self.params]


class __ScreenshotAction(object):
    """对应了模板文件中的截图操作(ScreenShotAction)"""

    def __init__(self):
        self.id = ""
        self.name = ""
        self.comments = ""
        self.screenshot_type = "仪表屏"
        self.display_id = "1"
        self.count = "1"
        self.image_name = ""

    def convert(self) -> List:
        return [self.name, self.comments, self.screenshot_type, self.display_id, self.count, self.image_name]


class __CanAction(object):
    """对应了模板文件中的Can信号(CanAction)"""

    def __init__(self):
        self.id = ""
        self.name = ""
        self.comments = ""
        self.signals = ""

    def convert(self) -> List:
        return [self.name, self.comments, self.signals]


def write_to_template_file(testcase_dict: Dict[str, TestCases], output_file: str = None):
    # 把读取出来的信息填入到相关的类对象中
    for key, testcases in testcase_dict.items():
        logger.debug(f"key = {key}")
        for testcase in testcases:
            logger.debug(testcase)
            __parse_testcase(testcase)
    # 写入类对象
    workbook = excel_utils.open_workbook(__template_file)
    sheet_dict = excel_utils.get_sheet_dict(workbook)
    for key, value in sheet_names.items():
        logger.info(f"写sheet[{key}]")
        __write_sheet(sheet_dict[key], value)
    if not output_file:
        output_file = os.path.join(os.getcwd(), f"template_testcase_{Utils.get_time_as_string()}.xlsx")
    excel_utils.save_workbook(output_file, workbook)
    excel_utils.close_workbook(workbook)


def __write_sheet(sheet: sht, clazz_list: List):
    """
    转化每个sheet对应的class对象为contents二维数组，并添加了序号，写入到对应的sheet中
    """
    contents = []
    for index, clazz in enumerate(clazz_list):
        line = clazz.convert()
        line.insert(0, index + 1)
        contents.append(line)
    for row_index, content in enumerate(contents):
        for column_index, cell_value in enumerate(content):
            excel_utils.set_cell_value(sheet, row_index + start_row, column_index + 1, cell_value, border)


def __parse_testcase(testcase: Testcase):
    """
        处理每个xmind独取出来的testcase对象，转化成每个sheet需要对应的类对象，方便后续写入
    """
    logger.debug(testcase)
    test_case = __Testcase()
    test_case.name = Utils.get_pin_yin(testcase.name)
    # 模块名  (ADAS-ACC自适应巡航-ACC状态显示_1)
    module_name = Utils.get_pin_yin(testcase.module)
    module_name = module_name.split("_")[0]
    test_case.module_name = module_name
    # 中文描述
    testcase_name = testcase.name
    test_case.description = testcase_name
    # 前置条件描述
    pre_conditions = testcase.pre_condition
    test_case.pre_condition_description = "\n".join(pre_conditions)
    pre_conditions_actions = __handle_pre_conditions(pre_conditions, test_case.name)
    # 操作testcase表的内容
    test_case.pre_condition = "\n".join(pre_conditions_actions)
    # 操作步骤描述
    actions = testcase.actions
    logger.debug(f"actions = {actions}")
    test_case.steps_description = "\n".join(actions)
    # 操作步骤
    action_list = test_case.steps_description.split("\n")
    steps_actions = __handle_steps(action_list, test_case.name)
    # 操作testcase表的内容
    test_case.steps = "\n".join(steps_actions)
    # 期望结果描述
    test_case.expect_description = "\n".join(testcase.exceptions)
    expect_actions = __handle_expect(test_case.name)
    test_case.expect = "\n".join(expect_actions)
    test_case_list.append(test_case)


def __handle_expect(testcase_name: str) -> List:
    """
        处理期望结果， 主要是生成期望结果对象，以及testcase sheet页中expect填的内容
    """
    image_compare = __ImageCompare()
    image_compare.name = testcase_name
    image_compare.image_name = testcase_name
    image_compare.template_light = f"{testcase_name}.jpg"
    image_compare.template_dark = f"{testcase_name}.jpg"
    image_compare.similarity = "90"
    image_compare_list.append(image_compare)
    expect_actions = [f"{IMAGE_COMPARE}={image_compare.name}"]
    return expect_actions


def __handle_steps(actions: List, testcase_name: str) -> List:
    """
        处理steps的部分，即读出来的TestCase类中的actions属性
    """
    actions_actions = []
    action_index = 1
    for action in actions:
        action = action.strip()
        if action[:2] in ("0x", "0X"):
            step_actions = __handle_can(action, testcase_name, action_index)
            actions_actions.append(step_actions)
        else:
            step_actions = __handle_other(action, testcase_name, action_index)
            if step_actions:
                actions_actions.append(step_actions)
        action_index += 1
    # 这个时候需要生成截图相关的东西了, 因为只会截图一张，所以直接加就好了
    screenshot_action = __ScreenshotAction()
    screenshot_action.name = testcase_name
    screenshot_action.image_name = testcase_name
    actions_actions.append(f"{SCREENSHOT_ACTION}={screenshot_action.name}")
    screenshot_action_list.append(screenshot_action)
    return actions_actions


def __handle_pre_conditions(pre_conditions: List, testcase_name: str) -> List:
    """
        处理 pre_conditions的部分，即读出来的TestCase类中的pre_condition属性
    """
    pre_conditions_actions = []
    pre_condition_index = 1
    # 操作can action部分的内容
    for pre_condition in pre_conditions:
        if pre_condition[:2] in ("0x", "0X"):
            actions = __handle_can(pre_condition, testcase_name, pre_condition_index)
            pre_conditions_actions.append(actions)
        else:
            actions = __handle_other(pre_condition, testcase_name, pre_condition_index)
            if actions:
                pre_conditions_actions.append(actions)
        pre_condition_index += 1
    return pre_conditions_actions


def __handle_can(content: str, testcase_name: str, index: int) -> str:
    """
        处理涉及到CAN消息的部分，一部分填入CANAction表中，一部分返回内容
    """
    can_action = __CanAction()
    cell_value = __get_can_action(content)
    can_action.name = f"{testcase_name}__{index}"
    can_action.signals = cell_value
    can_action_list.append(can_action)
    return f"{CAN_ACTION}={can_action.name}"


def __handle_other(content: str, testcase_name: str, index: int) -> Optional[str]:
    """
        处理涉及到SLEEP/RESUME/LOST的部分，一部分填入Common表中，一部分返回内容
    """
    if content.lower().startswith(SLEEP):
        # sleep=0.1 直接加进去
        return content
    elif content.lower().startswith(RESUME):
        # resume=0x307
        message_id = content.split("=")[1]
        common = __Common()
        common.name = f"{testcase_name}__{index}"
        common.function_name = "resume_transmit"
        common.params = f"message_id={message_id}"
        common_list.append(common)
        return f"{COMMON}={common.name}"
    elif content.lower().startswith(LOST):
        # lost=0x307
        message_id = content.split("=")[1]
        common = __Common()
        common.name = f"{testcase_name}__{index}"
        common.function_name = "stop_transmit"
        common.params = f"message_id={message_id}"
        common_list.append(common)
        return f"{COMMON}={common.name}"
    else:
        # 描述行，不用处理，返回None对象由调用者判断
        return None


def __get_can_action(content: str) -> str:
    """
        把can消息部分处理成单元格内容
    """
    # if content[:2] in ("0x", "0X"):
    # 0x3FD(BCM_DriveMode=0x1, CM_DriveMode=0x1)
    if "(" in content:
        # BCM_DriveMode=0x1, CM_DriveMode=0x1
        content = content.split("(")[1][:-1]
        cell_value = __handle_comma(content)
    elif "（" in content:
        # BCM_DriveMode=0x1, CM_DriveMode=0x1
        content = content.split("(")[1][:-1]
        cell_value = __handle_comma(content)
    else:
        template_format = "0x3FD(BCM_DriveMode=0x1, CM_DriveMode=0x1)"
        raise RuntimeError(f"content[{content}] is wrong, check it again, template is {template_format}")
    return cell_value


def __handle_comma(content: str) -> str:
    comma_exist = "," in content or "，" in content
    if comma_exist:
        if "," in content:
            template_content = content.split(",")
            template_content = list(map(lambda x: x.strip(), template_content))
            cell_value = "\n".join(template_content)
        elif "，" in content:
            template_content = content.split("，")
            template_content = list(map(lambda x: x.strip(), template_content))
            cell_value = "\n".join(template_content)
        else:
            cell_value = content
    else:
        cell_value = content
    return cell_value
