#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/2/27 11:13
# @Author  : zhangvv
# @File    : con_gui.py
# @Software: PyCharm
# @Desc    :
import os.path
import time
from time import sleep
from typing import Dict
from uds_common import UdsCommon
from automotive import logger
from ..common.constants import CONFIG_UDS, GUI_SIZE, BUTTON_WIDTH, FM_TEXT, FM_BUTTON
from automotive.utils.excel_utils import ExcelUtils
import re
import json
import tkinter as tk


# 读取json，以面板形式进行uds配置字的读写操作


class ReaderConfig(object):
    def __init__(self):
        self.excel_utils = ExcelUtils()

    def get_car_type_config_from_excel(self, excel_file: str, car_row: int, config_row: int,
                                       sheet_name: str = "Sheet1") -> dict:
        """
        从excel表中获取车型：配置字.格式：{车型n：{车型详细名称：配置字}}
        :param config_row:配置字所在行
        :param car_row:excel车型所在行
        :param excel_file:excel文件完整路径
        :param sheet_name:sheet页名称，默认Sheet1
        :return:
        """
        configuration = {}
        workbook = self.excel_utils.open_workbook(file=excel_file)
        sheet = self.excel_utils.get_sheet(workbook=workbook, sheet_name=sheet_name)
        columns = self.excel_utils.get_max_columns(sheet=sheet)
        for j in range(columns):
            # 车型
            car_type = self.excel_utils.get_cell_value(sheet=sheet, row_index=car_row, column_index=j + 1)
            # 配置字
            configure = self.excel_utils.get_cell_value(sheet=sheet, row_index=config_row, column_index=j + 1)

            configuration[fr"车型{j + 1}"] = {car_type: configure}
        return configuration

    @staticmethod
    def dict_transformation_json(input_data: dict, out_file: str):
        """
        字典存储到json文件中
        :param input_data:要写入json文件的字典数据
        :param out_file:输出的json文件完整路径
        :return:
        """
        # out = json.dumps(input_data)
        with open(out_file, 'w', encoding='utf-8') as json_file:
            json_file.write(json.dumps(input_data, ensure_ascii=False, indent=4))

    @staticmethod
    def read_data_from_json(file: str) -> Dict:
        """
        读取json里面的配置字
        :param file:json文件完整路径
        :return:字典
        """
        with open(file, mode='r', encoding='utf-8') as f:
            datas = json.load(f)
        return datas

    @staticmethod
    def get_file_name(file: str) -> str:
        """
        获取json文件的文件名，不带后缀
        :param file:json文件完整路径
        :return:不带后缀的文件名
        """
        if os.path.isfile(file):
            basename = os.path.split(file)[-1]
        else:
            raise RuntimeError("Error, 请检查输入文件路径")
        return basename.split('.')[0]


class ConfigurationGui(object):
    def __init__(self, json_file: str):

        # 获取配置信息
        service = ReaderConfig()
        configure = service.read_data_from_json(file=json_file)

        # 定义gui
        self.root = tk.Tk()
        # 设置界面
        title = service.get_file_name(file=json_file)
        self.root.title()
        self.root.geometry(f'{GUI_SIZE[0]}x{GUI_SIZE[1]}+{GUI_SIZE[2]}+{GUI_SIZE[3]}')  # 设置主窗口长宽以及窗口在屏幕的位置 宽x高+x+y

        if title == "车型配置":

            # 按钮的框架
            self.fm_b = tk.Frame(self.root)
            self.fm_b.pack(fill="both")

            # 文本输出框和标签的框架
            self.fm_t = tk.Frame(self.root)
            self.fm_t.pack(fill='both', expand=0)

            l2 = tk.Label(self.fm_t, text='实时终端控制台', font=('微软雅黑', 10, 'bold'), width=500, justify='left',
                          anchor='w')  # justify控制对其方向，anchor控制位置 共同使文本靠左
            l2.pack()
            self.s2 = tk.Scrollbar(self.fm_t)  # 设置垂直滚动条
            self.b2 = tk.Scrollbar(self.fm_t, orient='horizontal')  # 水平滚动条
            self.s2.pack(side='right', fill='y')  # 靠右，充满Y轴
            self.b2.pack(side='bottom', fill='x')  # 靠下，充满x轴

            # wrap=word 单词换行 char 字符换行 none不换行
            self.text = tk.Text(self.fm_t, font=('Consolas', 9), undo=True, autoseparators=False,
                                wrap='none', xscrollcommand=self.b2.set,
                                yscrollcommand=self.s2.set)  # , state=DISABLED, wrap='none'表示不自动换行
            self.text.pack(fill='x', side="bottom")

            # 获取request\response\function id的值，并移除
            request_id = self.str16_to_hex(configure["request_id"])
            response_id = self.str16_to_hex(configure["response_id"])
            function_id = self.str16_to_hex(configure["function_id"])
            can_box_device = configure["can_box_device"]

            # did属性值
            self.did = configure["did"]
            # dll_file
            dll_file = configure["dll_file"]
            can_fd = configure["can_fd"]
            is_uds_can_fd = configure["is_uds_can_fd"]

            # 删除除车型之外的其他几个键值对
            del configure["request_id"]
            del configure["response_id"]
            del configure["function_id"]
            del configure["did"]
            del configure["dll_file"]
            del configure["can_box_device"]
            del configure["can_fd"]
            del configure["is_uds_can_fd"]

            # 定义CAN
            self.uds = UdsCommon(can_box_device=can_box_device,
                                 can_fd=can_fd,
                                 is_uds_can_fd=is_uds_can_fd,
                                 request_id=request_id,
                                 response_id=response_id,
                                 dll_file=dll_file,
                                 function_id=function_id)

            # 车型配置
            self.car_type_config(configure=configure)
        else:
            pass

        self.s2.config(command=self.text.yview)  # Text随着滚动条移动被控制移动
        self.b2.config(command=self.text.xview)
        self.root.protocol("WM_DELETE_WINDOW", self.exit_root)
        self.root.mainloop()

    @staticmethod
    def str16_to_hex(number: str):
        return int(number, 16)

    # 控制台输出
    def terminal_print(self, msg, info_type):
        """
        规范终端文本框的输出格式
        :param msg: 显示的内容
        :param info_type: 抬头显示
        :return:
        """
        self.text.insert('end', "\n%s [%s] %s" % (time.strftime('%Y-%m-%d %H:%M:%S'), info_type.upper(), msg))
        self.text.update()

    @staticmethod
    def solve_configure_word_form(configure):
        b = ''
        for i in range(len(configure)):
            j = i + 1
            a = configure[i]
            b = b + a
            if j % 2 == 0:
                b = b + ' '
        return b

    def messagebox(self, message: str):
        """
        设计会话弹窗
        :param message:弹窗内容
        :return:
        """
        result = tk.messagebox.askyesno(title="请确认信息", message=message)
        logger.debug(fr"配置详细信息： {message}")
        logger.debug(f"弹窗选择结果{result}")
        self.terminal_print(msg=result, info_type="弹窗选择结果")

        if result:
            car_type = re.findall("你确认要配置.*：", message)[0][6:-1]
            self.terminal_print(msg=car_type, info_type="选择的车型")

            # 解析出来配置字
            config = re.findall("配置字为.*吗？", message)[0][4:-2]
            logger.debug(f"2e写入配置字为：{config}")
            # 处理2E写入的配置字，两个字符一分隔
            self.terminal_print(msg=self.solve_configure_word_form(configure=config.lower()), info_type="2e写入的配置字")
            # 执行写配置的任务
            # 1.写配置
            self.terminal_print(msg="即将写入数据", info_type="提示")
            response_data_2e = self.uds.write_config(data=config, did=self.did)
            logger.debug(f"写配置字返回值：{response_data_2e}")
            self.terminal_print(msg=response_data_2e, info_type="写配置字返回值")
            # 2.重启
            self.uds.reset_11()
            self.terminal_print(msg='等待30s', info_type="重启")
            sleep(30)

            # 5. 22读配置
            response_data_22_after = self.uds.read_fd_22(did=self.did)
            logger.debug(f"22读出来的配置：{response_data_22_after}")
            logger.debug(f"重启后的读结果判断{response_data_22_after.lower() == config.lower()}")
            self.terminal_print(msg=self.solve_configure_word_form(response_data_22_after.lower()), info_type="22读出来的配置")
            self.terminal_print(msg=response_data_22_after.lower() == config.lower(), info_type="重启后的读结果判断")
            if config.lower() != response_data_22_after.lower():
                logger.info(f"{car_type}配置失败，请检查")
                self.terminal_print(msg=car_type, info_type="配置失败")
            else:
                logger.info(f"{car_type}配置成功")
                self.terminal_print(msg=car_type, info_type="配置成功")
            self.terminal_print(msg="########################################本次操作完成#############################"
                                    "###########", info_type="提示")

    def car_type_config(self, configure: dict):
        """
        车型配置的功能
        :param configure:读取的configure字典数据
        :return:
        """
        column = 1
        row = 1
        for key, value in configure.items():
            button_text = key
            car_type = list(value.keys())[0]
            car_config = list(value.values())[0]
            message = f"你确认要配置{button_text}：\n, 车型为{car_type}\n, 配置字为{car_config}吗？"
            btn = tk.Button(self.fm_b, text=button_text, command=lambda x=message: self.messagebox(message=x),
                            width=BUTTON_WIDTH)

            btn.grid(row=row, column=column)
            btn.grid(row=row, column=column, sticky="E" + "W")

            # 处理button排列的行数和列数
            if column != 0 and column % BUTTON_WIDTH == 0:
                row += 1
                column = 1
            else:
                column += 1

    def function_config(self):
        # 功能配置
        pass

    def interface_design(self):
        pass

    def exit_root(self):
        self.root.destroy()
        self.uds.close_can()
