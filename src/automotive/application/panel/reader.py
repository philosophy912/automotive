# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2021, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        reader.py
# @Author:      lizhe
# @Created:     2021/12/13 - 22:25
# --------------------------------------------------------
from typing import List, Dict, Any, Tuple, Optional

from automotive.application.common.constants import GuiConfig, TEXT, ACTIONS, ON, OFF, CHECK_MSGS, VALUES
from automotive.logger.logger import logger
from automotive.application.common.enums import GuiButtonTypeEnum
from automotive.utils.common.interfaces import sht
from automotive.utils.excel_utils import ExcelUtils
from automotive.utils.common.enums import ExcelEnum


check_buttons = GuiButtonTypeEnum.CHECK_BUTTON.value[1]
thread_buttons = GuiButtonTypeEnum.EVENT_CHECK_BUTTON.value[1]
comboxs = GuiButtonTypeEnum.COMBOX_BUTTON.value[1]
entries = GuiButtonTypeEnum.INPUT_BUTTON.value[1]
buttons = GuiButtonTypeEnum.EVENT_BUTTON.value[1]
receive_buttons = GuiButtonTypeEnum.RECEIVE_BUTTON.value[1]


class ConfigReader(object):

    def __init__(self, type_: ExcelEnum = ExcelEnum.OPENPYXL):
        self.__utils = ExcelUtils(type_)

    def read_from_file(self, file: str) -> Dict[str, Dict[str, Any]]:
        result = dict()
        wb = self.__utils.open_workbook(file)
        sheet = self.__utils.get_sheet(wb, "sheet")
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

    def __parse(self, sheet: sht) -> List[GuiConfig]:
        configs = []
        max_row = self.__utils.get_max_rows(sheet) + 1
        for i in range(2, max_row):
            config = GuiConfig()
            config.name = self.__utils.get_cell_value(sheet, i, "A")
            config.text_name = self.__utils.get_cell_value(sheet, i, "B")
            config.button_type = GuiButtonTypeEnum.from_name(self.__utils.get_cell_value(sheet, i, "C"))
            column_d = self.__utils.get_cell_value(sheet, i, "D")
            config.selected = self._parse_actions(column_d) if column_d else None
            column_e = self.__utils.get_cell_value(sheet, i, "E")
            config.unselected = self._parse_actions(column_e) if column_e else None
            config.items = self.__utils.get_cell_value(sheet, i, "F")
            column_g = self.__utils.get_cell_value(sheet, i, "G")
            config.actions = self._parse_actions(column_g) if column_g else None
            config.tab_name = self.__utils.get_cell_value(sheet, i, "H")
            column_i = self.__utils.get_cell_value(sheet, i, "I")
            config.check_msgs = self._parse_check_msgs(column_i) if column_i else None
            configs.append(config)
            logger.debug(f"config = {config}")
        return configs

    @staticmethod
    def _split_tabs(values: List[GuiConfig]) -> Dict[str, List[GuiConfig]]:
        tab_values = dict()
        tab_set = []#将获取的Tab按照顺序填写
        for value in values:

            if value.tab_name not in tab_set:
                tab_set.append(value.tab_name)

        for tab in tab_set:
            tab_values[tab] = list(filter(lambda x: x.tab_name == tab, values))
        return tab_values

    @staticmethod
    def _handle_event_buttons(values: List[GuiConfig]) -> Dict[str, Any]:
        result = dict()
        for item in values:
            content = dict()
            content[TEXT] = item.text_name
            content[ACTIONS] = item.actions
            result[item.name] = content
        return result

    @staticmethod
    def _handle_check_buttons(values: List[GuiConfig]) -> Dict[str, Any]:
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
    def _handle_buttons(values: List[GuiConfig]) -> Dict[str, Any]:
        result = dict()
        for item in values:
            content = dict()
            content[TEXT] = item.text_name
            content[ACTIONS] = item.actions
            result[item.name] = content
        logger.debug(f"result = {result}")
        return result

    @staticmethod
    def _handle_receive_buttons(values: List[GuiConfig]) -> Dict[str, Any]:
        result = dict()
        for item in values:
            content = dict()
            content[TEXT] = item.text_name
            content[CHECK_MSGS] = item.check_msgs
            result[item.name] = content
        logger.debug(f"result = {result}")
        return result

    @staticmethod
    def _handle_combox(values: List[GuiConfig]) -> Dict[str, Any]:
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
    def _handle_entries(values: List[GuiConfig]) -> Dict[str, Any]:
        result = dict()
        for item in values:
            content = dict()
            content[TEXT] = item.text_name
            content[ACTIONS] = item.actions
            result[item.name] = content
        logger.debug(f"result = {result}")
        return result

    def _parse_actions(self, actions: str) -> List:
        contents = []
        lines = actions.split("\n")
        lines = list(map(lambda x: x.strip(), lines))
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
            else:
                contents.append((line,))
        return contents

    @staticmethod
    def __handle_signal_value(value: str) -> (float, int):
        if value.upper() == "NONE":
            return None
        else:
            if "0x" in value or "0X" in value:
                return int(value, 16)
            else:
                return float(value)

    @staticmethod
    def _split_type(configs: List[GuiConfig]) -> Dict[GuiButtonTypeEnum, Any]:
        typed_configs = dict()
        for key, item in GuiButtonTypeEnum.__members__.items():
            typed_configs[item] = list(filter(lambda x: x.button_type == item, configs))
        return typed_configs

    def _parse_check_msgs(self, value: str) -> Tuple[int, str, int, Optional[int], bool]:
        value = value.strip()
        values = value.split("=")
        msg_id = self.__handle_signal_value(values[0])
        signal_name = values[1]
        signal_value = self.__handle_signal_value(values[2])
        count = self.__handle_signal_value(values[3])
        expect_value = values[4].upper() == "TRUE"
        return msg_id, signal_name, signal_value, count, expect_value
