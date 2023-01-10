# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2021, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        reader.py
# @Author:      lizhe
# @Created:     2021/12/13 - 22:25
# --------------------------------------------------------
import uuid
from typing import Sequence, Dict, Any, Tuple, Optional

from automotive.application.common.constants import GuiConfig, TEXT, ACTIONS, ON, OFF, CHECK_MSGS, VALUES
from automotive.logger.logger import logger
from automotive.application.common.enums import GuiButtonTypeEnum
from automotive.utils.common.interfaces import sht
from automotive.utils.excel_utils import ExcelUtils
from automotive.utils.common.enums import ExcelEnum
from automotive.core.can.can_service import CANService

# 单选框
check_buttons = GuiButtonTypeEnum.CHECK_BUTTON.value[1]
# 时间按钮
thread_buttons = GuiButtonTypeEnum.EVENT_CHECK_BUTTON.value[1]
# 下拉框
comboxs = GuiButtonTypeEnum.COMBOX_BUTTON.value[1]
# 输入框
entries = GuiButtonTypeEnum.INPUT_BUTTON.value[1]
# 普通按钮
buttons = GuiButtonTypeEnum.EVENT_BUTTON.value[1]
# 接收信息校验按钮
receive_buttons = GuiButtonTypeEnum.RECEIVE_BUTTON.value[1]


class ConfigReader(object):

    def __init__(self, can_service: CANService, excel_type: ExcelEnum = ExcelEnum.OPENPYXL):
        """
        初始化，主要设置can service
        :param can_service: can消息，主要用于数据校验
        :param excel_type: excel类型，仅支持openpyxl和xlwings
        """
        self.__utils = ExcelUtils(excel_type)
        self.can_service = can_service

    def read_from_file(self, file: str) -> Dict[str, Dict[str, Any]]:
        """
        从文件中读取到相应的数据并组合成类型
        :param file:
        """
        result = dict()
        wb = self.__utils.open_workbook(file)
        sheets = self.__utils.get_sheets(wb)
        sheet = sheets[0]
        configs = self.__parse(sheet)
        # 先区分tab
        tabs = self._split_tabs(configs)
        for tab, values in tabs.items():
            tab_config = dict()
            # 按照按钮类型来分割
            typed_configs = self._split_type(values)
            # 处理 buttons
            tab_config[check_buttons] = self._handle_check_buttons(typed_configs[GuiButtonTypeEnum.CHECK_BUTTON])
            # 处理 flash_buttons
            tab_config[thread_buttons] = self._handle_event_buttons(typed_configs[GuiButtonTypeEnum.EVENT_CHECK_BUTTON])
            # 处理 comboxs
            tab_config[comboxs] = self._handle_combox(typed_configs[GuiButtonTypeEnum.COMBOX_BUTTON])
            # 处理 entries
            tab_config[entries] = self._handle_entries(typed_configs[GuiButtonTypeEnum.INPUT_BUTTON])
            # 处理 buttons
            tab_config[buttons] = self._handle_buttons(typed_configs[GuiButtonTypeEnum.EVENT_BUTTON])
            # 处理 receive buttons
            tab_config[receive_buttons] = self._handle_receive_buttons(typed_configs[GuiButtonTypeEnum.RECEIVE_BUTTON])
            result[tab] = tab_config
        self.__utils.close_workbook(wb)
        return result

    def __parse(self, sheet: sht) -> Sequence[GuiConfig]:
        """
        解析数据，固定格式，若格式有错误，则无法成功
        :param sheet: sheet对象
        """
        configs = []
        max_row = self.__utils.get_max_rows(sheet) + 1
        # cell_a1 = self.__utils.get_cell_value(sheet, 1, "A")
        max_column = self.__utils.get_max_columns(sheet) + 1
        # 读取第一行获取列名与列序号的对应关系
        result = dict()
        for i in range(1, max_column):
            title = self.__utils.get_cell_value(sheet, 1, i)
            result[title] = i
        for i in range(2, max_row):
            config = GuiConfig()
            config.name = uuid.uuid3(uuid.NAMESPACE_DNS, self.__utils.get_cell_value(sheet, i, result["按钮名称"]))
            config.text_name = self.__utils.get_cell_value(sheet, i, result["按钮名称"])
            config.button_type = GuiButtonTypeEnum.from_name(self.__utils.get_cell_value(sheet, i, result["类型"]))
            column_d = self.__utils.get_cell_value(sheet, i, result["选中"])
            config.selected = self._parse_actions(column_d) if column_d else None
            column_e = self.__utils.get_cell_value(sheet, i, result["未选中"])
            config.unselected = self._parse_actions(column_e) if column_e else None
            config.items = self.__utils.get_cell_value(sheet, i, result["选项名"])
            column_g = self.__utils.get_cell_value(sheet, i, result["操作步骤"])
            config.actions = self._parse_actions(column_g) if column_g else None
            config.tab_name = self.__utils.get_cell_value(sheet, i, result["选项卡名"])
            if "检查" in result.keys():
                column_i = self.__utils.get_cell_value(sheet, i, result["检查"])
                config.check_msgs = self._parse_check_msgs(column_i) if column_i else None
            else:
                column_i = self.__utils.get_cell_value(sheet, i, max_column - 1)
                config.check_msgs = self._parse_check_msgs(column_i) if column_i else None
            configs.append(config)
            logger.debug(f"config = {config}")
        return configs

    @staticmethod
    def _split_tabs(values: Sequence[GuiConfig]) -> Dict[str, Sequence[GuiConfig]]:
        """
        分类tab数据
        :param values: 读取出来的数据
        """
        tab_values = dict()
        tab_set = []  # 将获取的Tab按照顺序填写
        for value in values:
            if value.tab_name not in tab_set:
                tab_set.append(value.tab_name)
        for tab in tab_set:
            tab_values[tab] = list(filter(lambda x: x.tab_name == tab, values))
        return tab_values

    @staticmethod
    def _handle_event_buttons(values: Sequence[GuiConfig]) -> Dict[str, Any]:
        """
        分类事件按钮
        :param values: 读取出来的数据
        """
        result = dict()
        for item in values:
            content = dict()
            content[TEXT] = item.text_name
            content[ACTIONS] = item.actions
            result[item.name] = content
        return result

    @staticmethod
    def _handle_check_buttons(values: Sequence[GuiConfig]) -> Dict[str, Any]:
        """
        分类单选框
        :param values:读取出来的数据
        """
        result = dict()
        for item in values:
            content = dict()
            content[TEXT] = item.text_name
            content[ON] = item.selected
            content[OFF] = item.unselected
            result[item.name] = content
        logger.debug(f"result = {result}")
        return result

    @staticmethod
    def _handle_buttons(values: Sequence[GuiConfig]) -> Dict[str, Any]:
        """
        分类普通按钮
        :param values:读取出来的数据
        """
        result = dict()
        for item in values:
            content = dict()
            content[TEXT] = item.text_name
            content[ACTIONS] = item.actions
            result[item.name] = content
        logger.debug(f"result = {result}")
        return result

    @staticmethod
    def _handle_receive_buttons(values: Sequence[GuiConfig]) -> Dict[str, Any]:
        """
        分类接收分析按钮
        :param values:读取出来的数据
        """
        result = dict()
        for item in values:
            content = dict()
            content[TEXT] = item.text_name
            content[CHECK_MSGS] = item.check_msgs
            result[item.name] = content
        logger.debug(f"result = {result}")
        return result

    @staticmethod
    def _handle_combox(values: Sequence[GuiConfig]) -> Dict[str, Any]:
        """
        处理下拉框数据的读取
        :param values: 读取出来的数据
        """
        result = dict()
        # 当前有多少个按钮
        button_names = []
        for item in values:
            if item.text_name not in button_names:
                button_names.append(item.text_name)
        logger.debug(f"buttons = {button_names}")
        button_objects = []
        for name in button_names:
            button_objects.append(list(filter(lambda x: x.text_name == name, values)))
        for button in button_objects:
            values_dict = dict()
            function_dict = dict()
            for item in button:
                values_dict[item.items] = item.actions
            function_dict[VALUES] = values_dict
            function_dict[TEXT] = button[0].text_name
            result[button[0].name] = function_dict
        logger.debug(f"result = {result}")
        return result

    @staticmethod
    def _handle_entries(values: Sequence[GuiConfig]) -> Dict[str, Any]:
        """
        处理输入框数据的读取
        :param values: 读取出来的数据
        """
        result = dict()
        for item in values:
            content = dict()
            content[TEXT] = item.text_name
            content[ACTIONS] = item.actions
            result[item.name] = content
        logger.debug(f"result = {result}")
        return result

    def _parse_actions(self, actions: str) -> Sequence:
        """
        处理执行动作部分数据
        :param actions: 读取出来的数据
        """
        contents = []
        lines = actions.split("\n")
        lines = list(map(lambda x: x.strip(), lines))
        # logger.info(f"当前信号为{lines}")
        for line in lines:
            # 0x152 BCM_LetfligthSt=0x1
            if line[:2].upper() == "0X":
                index = line.index(" ")
                msg_id = int(line[:index].strip(), 16)
                other = line[index + 1:]
                signal_dict = dict()
                # 0x92 WCBS_ESC_WhlSpdFRVd=0x1, WCBS_ESC_WhlFLSpd=None
                if "," in other:
                    # 表示有多个信号值
                    signals = other.split(",")
                    for signal in signals:
                        values = signal.split("=")
                        key = values[0].strip()
                        value = values[1].strip()
                        signal_dict[key] = self.__handle_signal_value(value)
                else:
                    values = other.split("=")
                    key = values[0].strip()
                    value = values[1].strip()
                    signal_dict[key] = self.__handle_signal_value(value)
                contents.append((msg_id, signal_dict))
            elif "=" in line:
                signal_dict = dict()
                values = line.split("=")
                key = values[0].strip()
                value = values[1].strip()
                signal_dict[key] = self.__handle_signal_value(value)
                msg_id = None
                for msg_name, msg in self.can_service.messages.items():
                    if key in msg.signals:
                        msg_id = msg.msg_id
                        contents.append((msg_id, signal_dict))
                if msg_id is None:
                    logger.info(f"当前信号[ {key} ]在dbc文件中未找到msg_id，请检查信号值书写或dbc文件")
            else:
                contents.append([line, ])
        return contents

    @staticmethod
    def __handle_signal_value(value: str) -> (float, int):
        """
        处理信号值， 可能是数字也可能是信号ID
        :param value: 读取到的值
        """
        if value.upper() == "NONE":
            return None
        else:
            if "0x" in value or "0X" in value:
                return int(value, 16)
            else:
                return float(value)

    @staticmethod
    def _split_type(configs: Sequence[GuiConfig]) -> Dict[GuiButtonTypeEnum, Any]:
        """
        分离类型
        :param configs: 读取出来的数据
        """
        typed_configs = dict()
        for key, item in GuiButtonTypeEnum.__members__.items():
            typed_configs[item] = list(filter(lambda x: x.button_type == item, configs))
        return typed_configs

    def _parse_check_msgs(self, check_value: str) -> Sequence:
        """
        处理信号检查部分的数据，更简化处理，可以不用填写0x的部分
        :param check_value: 读取的数据
        """
        lines = check_value.split("\n")
        lines = list(map(lambda x: x.strip(), lines))
        check_contents= []
        for value in lines:
            if value[:2].upper() == "0X":
                # 0x152=BCM_RightligthSt=0x1=1=True
                values = value.split("=")
                msg_id = self.__handle_signal_value(values[0])
                signal_name = values[1]
                signal_value = self.__handle_signal_value(values[2])
                count = self.__handle_signal_value(values[3])
                expect_value = values[4].upper() == "TRUE"
                check_contents.append((msg_id, signal_name, signal_value, count, expect_value))
            elif value != '':
                # BCM_RightligthSt = 0x1 = 1 = True
                values = value.split("=")
                signal_name = values[0]
                signal_value = self.__handle_signal_value(values[1])
                count = self.__handle_signal_value(values[2])
                expect_value = values[3].upper() == "TRUE"
                msg_id = None
                for msg_name, msg in self.can_service.messages.items():
                    if signal_name in msg.signals:
                        msg_id = msg.msg_id
                if msg_id is None:
                    logger.info(f"当前信号[ {signal_name} ]在dbc文件中未找到msg_id，请检查信号值书写或dbc文件")
                check_contents.append((msg_id, signal_name, signal_value, count, expect_value))
            else:
                continue
        return check_contents
