# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2021, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        reader.py
# @Author:      lizhe
# @Created:     2021/12/13 - 22:25
# --------------------------------------------------------
import os
from typing import List, Dict, Any

from automotive.logger.logger import logger
from automotive.application.common.enums import GuiButtonTypeEnum

try:
    import xlwings as xw
except ModuleNotFoundError:
    os.system("pip install xlwings")
finally:
    import xlwings as xw
    from xlwings import Sheet, Book


class GuiConfig(object):

    def __init__(self):
        self.name = None
        self.text_name = None
        self.button_type = None
        self.selected = None
        self.unselected = None
        self.items = None
        self.actions = None

    def __str__(self):
        values = []
        # exclude = "category", "module", "module_id", "requirement_id", "keywords", "test_case_type", "phase", "status"
        exclude = []
        for key, value in self.__dict__.items():
            if key not in exclude:
                values.append(f"{key}={value}")
        return ",".join(values)


class ConfigReader(object):

    def read_from_file(self, file: str) -> Dict[str, Any]:
        result = dict()
        app = xw.App(visible=False, add_book=False)
        app.display_alerts = False
        app.screen_updating = False
        wb = app.books.open(file)
        sheet = wb.sheets["sheet"]
        configs = self.__parse(sheet)
        # 按照按钮类型来分割
        typed_configs = self.__split_type(configs)
        # 处理 buttons
        result["buttons"] = self.__handle_buttons(typed_configs[GuiButtonTypeEnum.CHECK_BUTTON])
        # 处理 flash_buttons
        result["flash_buttons"] = self.__handle_event_buttons(typed_configs[GuiButtonTypeEnum.EVENT_CHECK_BUTTON])
        # 处理 comboxs
        result["comboxs"] = self.__handle_combox(typed_configs[GuiButtonTypeEnum.COMBOX_BUTTON])
        # 处理 entries
        result["entries"] = self.__handle_entries(typed_configs[GuiButtonTypeEnum.INPUT_BUTTON])
        wb.close()
        app.quit()
        try:
            app.kill()
        except AttributeError:
            logger.debug("app kill fail")
        return result

    @staticmethod
    def __handle_event_buttons(values: List[GuiConfig]) -> Dict[str, Any]:
        result = dict()
        for item in values:
            content = dict()
            content["text"] = item.text_name
            content["actions"] = item.actions
            result[item.name] = content
        return result

    @staticmethod
    def __handle_buttons(values: List[GuiConfig]) -> Dict[str, Any]:
        result = dict()
        for item in values:
            content = dict()
            content["text"] = item.text_name
            content["on"] = item.selected
            content["off"] = item.unselected
            result[item.name] = content
        return result

    @staticmethod
    def __handle_combox(values: List[GuiConfig]) -> Dict[str, Any]:
        result = dict()
        # 当前有多少个按钮
        button_names = set()
        for item in values:
            button_names.add(item.text_name)
        logger.debug(f"buttons = {button_names}")
        buttons = []
        for name in button_names:
            buttons.append(list(filter(lambda x: x.text_name == name, values)))
        for button in buttons:
            values_dict = dict()
            function_dict = dict()
            for item in button:
                values_dict[item.items] = item.actions
            function_dict["values"] = values_dict
            function_dict["text"] = button[0].text_name
            result[button[0].name] = function_dict
        return result

    @staticmethod
    def __handle_entries(values: List[GuiConfig]) -> Dict[str, Any]:
        result = dict()
        for item in values:
            content = dict()
            content["text"] = item.text_name
            content["actions"] = item.actions
            result[item.name] = content
        return result

    def __parse(self, sheet: Sheet) -> List[GuiConfig]:
        configs = []
        max_row = sheet.used_range.last_cell.row
        for i in range(2, max_row + 1):
            config = GuiConfig()
            config.name = sheet.range(f"A{i}").value
            config.text_name = sheet.range(f"B{i}").value
            config.button_type = GuiButtonTypeEnum.from_name(sheet.range(f"C{i}").value)
            column_d = sheet.range(f"D{i}").value
            config.selected = self.__parse_actions(column_d) if column_d else None
            column_e = sheet.range(f"E{i}").value
            config.unselected = self.__parse_actions(column_e) if column_e else None
            config.items = sheet.range(f"F{i}").value
            column_g = sheet.range(f"G{i}").value
            config.actions = self.__parse_actions(column_g) if column_g else None
            configs.append(config)
        return configs

    def __parse_actions(self, actions: str) -> List:
        contents = []
        lines = actions.split("\n")
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
                contents.append(line)
        return contents

    @staticmethod
    def __handle_signal_value(value: str):
        if value.upper() == "NONE":
            return None
        else:
            if "0x" in value or "0X" in value:
                return int(value, 16)
            else:
                return float(value)

    @staticmethod
    def __split_type(configs: List[GuiConfig]) -> Dict[GuiButtonTypeEnum, Any]:
        typed_configs = dict()
        for key, item in GuiButtonTypeEnum.__members__.items():
            typed_configs[item] = list(filter(lambda x: x.button_type == item, configs))
        return typed_configs

# reader = ConfigReader()
# json_dict = reader.read_from_file(r"C:\Users\lizhe\Desktop\按钮设计.xlsx")
# print(json_dict)
