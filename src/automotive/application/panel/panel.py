# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2021, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        gui.py.py
# @Author:      lizhe
# @Created:     2021/12/15 - 21:24
# --------------------------------------------------------
import copy
from concurrent.futures import ThreadPoolExecutor
from time import sleep
from tkinter import *
from tkinter.ttk import *
from typing import List, Dict, Any
from .reader import ConfigReader
from automotive import CANService, logger, CanBoxDeviceEnum

TEXT = "text"
ON = "on"
OFF = "off"
CHECK_BUTTONS = "check_buttons"
THREAD_BUTTONS = "thread_buttons"
COMBOXS = "comboxs"
ENTRIES = "entries"
VALUES = "values"
ACTIONS = "actions"
DEFAULT_MESSAGE = "default_message"
BUS_LOST = "bus_lost"
MESSAGE_LOST = "message_lost"


class TabFrame(Frame):

    def __init__(self, master, can_service: CANService, config: Dict[str, Any], filter_nodes: List[str],
                 thread_pool: ThreadPoolExecutor):
        super().__init__(master)
        self.can_service = can_service
        self.thread_pool = thread_pool
        self.__filter_nodes = filter_nodes
        # 单选框按钮配置
        self.__check_buttons = config[CHECK_BUTTONS] if config[CHECK_BUTTONS] else dict()
        logger.debug(f"check_buttons = {self.__check_buttons}")
        # 闪烁单选框按钮配置
        self.__thread_buttons = config[THREAD_BUTTONS] if config[THREAD_BUTTONS] else dict()
        logger.debug(f"thread_buttons = {self.__thread_buttons}")
        # 下拉框按钮配置
        self.__comboxs = config[COMBOXS] if config[COMBOXS] else dict()
        logger.debug(f"comboxs = {self.__comboxs}")
        # 输入框按钮配置
        self.__entries = config[ENTRIES] if config[ENTRIES] else dict()
        logger.debug(f"entries = {self.__entries}")
        # 每行能够容纳的数量
        self.__max_line_count = 12  # 36
        # 双行能够容纳的数量
        self.__max_double_line_count = int(self.__max_line_count / 2)
        # 输入框支持的事件列表
        self.support_event_keys = "<Return>",
        # 单选框值
        self.check_button_bool_vars = dict()
        # 闪烁单选框值
        self.thread_button_bool_vars = dict()
        # 按钮框对象字典
        self.buttons = dict()
        # 单选框对象字典
        self.check_buttons = dict()
        # 闪烁单选框对象字典
        self.thread_buttons = dict()
        # 下拉框对象字典
        self.comboxs = dict()
        # 输入框对象字典
        self.entries = dict()
        # 闪烁事件Task
        self.thread_task = dict()
        # 总线丢失按钮 =
        # 开始的行列
        self.row = 0
        self.column = 0
        # 布局显示
        self.pack()
        # 创建公共按钮
        self.create_common_widget()
        # 创建单选按钮
        self.create_check_buttons()
        # 创建下拉按钮
        self.create_comboxs()
        # 创建输入框
        self.create_entries()
        # 创建事件单选按钮
        self.create_thread_buttons()

    def create_common_widget(self):
        # ********** 创建一个发送默认消息的按钮 check_button **********
        text_name = DEFAULT_MESSAGE
        # 创建Button对象
        self.buttons[text_name] = Button(self, text="发送默认消息", command=lambda x=text_name: self.__button_event(x))
        # 布局button
        self.buttons[text_name].grid(row=self.row, column=self.column, sticky=W)
        # ********** 创建一个总线丢失的按钮 check_button **********
        text_name = BUS_LOST
        # 创建CheckButton对象并放到check_buttons中方便调用
        self.buttons[text_name] = Button(self, text="总线丢失", command=lambda x=text_name: self.__button_event(x))
        # 布局checkbutton
        self.buttons[text_name].grid(row=self.row, column=self.column + 1, sticky=W)
        # ********** 创建一个信号丢失的输入框  entry **********
        # 获取输入框的名称
        Label(self, text="要丢失信号").grid(row=self.row, column=self.column + 2, sticky=W)
        self.entries[MESSAGE_LOST] = Entry(self, bd=1, width=10)
        self.entries[MESSAGE_LOST].grid(row=self.row, column=self.column + 3, sticky=W)
        self.entries[MESSAGE_LOST].bind(self.support_event_keys[0],
                                        lambda x, y=("", MESSAGE_LOST): self.__entry_event(x, y))
        self.row += 1

    def __button_event(self, text_name: str):
        self.buttons[text_name]["state"] = DISABLED
        self.__special_actions(text_name)

    def __special_actions(self, text_name: str):
        if text_name == DEFAULT_MESSAGE:
            self.can_service.send_default_messages(filter_sender=self.__filter_nodes)
        elif text_name == BUS_LOST:
            self.can_service.stop_transmit()
        self.buttons[text_name]["state"] = NORMAL

    def create_check_buttons(self):
        # 创建下拉框
        if self.row != 0:
            self.row += 1
        # 创建单选框
        index = 0
        for key, value in self.__check_buttons.items():
            function_name = key
            text_name = value[TEXT]
            if index == 0:
                self.column = 0
            elif index % self.__max_line_count == 0:
                self.row += 1
                self.column = 0
            else:
                self.column += 1
            # 创建bool对象接收值
            self.check_button_bool_vars[function_name] = BooleanVar()
            # 创建CheckButton对象并放到check_buttons中方便调用
            button = Checkbutton(self, text=text_name,
                                 variable=self.check_button_bool_vars[function_name],
                                 onvalue=True,
                                 offvalue=False,
                                 command=lambda x=function_name: self.__check_button_event(x))
            self.check_buttons[function_name] = button
            logger.debug(f"row = {self.row}, column = {self.column}, index = {index}")
            # 布局checkbutton
            self.check_buttons[function_name].grid(row=self.row, column=self.column, sticky=W)
            index += 1

    def __check_button_event(self, function_name):
        values = self.__check_buttons[function_name]
        text_name = values[TEXT]
        on_actions = values[ON]
        off_actions = values[OFF]
        if self.check_button_bool_vars[function_name].get():
            logger.debug(f"{text_name} ON")
            self.__send_actions(on_actions)
        else:
            logger.debug(f"{text_name} OFF")
            self.__send_actions(off_actions)

    def create_comboxs(self):
        # 创建下拉框
        if self.row != 0:
            self.row += 1
        index = 0
        for key, value in self.__comboxs.items():
            function_name = key
            text_name = value[TEXT]
            if index == 0:
                self.column = 0
            elif index % self.__max_double_line_count == 0:
                self.row += 1
                self.column = 0
            else:
                self.column += 1
            # 获取下拉框的名称
            values = list(value[VALUES].keys())
            logger.debug(f"row = {self.row}, column = {self.column}, index = {index}")
            # 创建Label框
            Label(self, text=text_name).grid(row=self.row, column=self.column, sticky=W)
            # 创建下拉框
            self.comboxs[function_name] = Combobox(self, values=values, state="readonly", width=5)
            # 设置下拉框初始值为第一个值
            self.comboxs[function_name].current(0)
            logger.debug(f"row = {self.row}, column = {self.column}, index = {index}")
            # 布局下拉框
            self.comboxs[function_name].grid(row=self.row, column=self.column + 1, sticky=W)
            # 绑定下拉框事件
            self.comboxs[function_name].bind("<<ComboboxSelected>>",
                                             lambda x, y=("", function_name): self.__combox_event(x, y))
            logger.debug(f"row = {self.row}, column = {self.column}")
            self.column += 1
            index += 1

    def __combox_event(self, event, function_name):
        """
        能够找到下拉框，并根据下拉框的内容进行判断
        后续能够根据内容进行消息的发送
        """
        function_name = function_name[1]
        combox_param = self.__comboxs[function_name]
        # 字典中定义的值列表
        values = combox_param[VALUES]
        text_name = combox_param[TEXT]
        actual_values = list(values.keys())
        # 当前选中的是第几个
        combox_index = self.comboxs[function_name].current()
        select_name = actual_values[combox_index]
        actions = values[select_name]
        logger.debug(f"设置{text_name}为{select_name}")
        self.__send_actions(actions)
        logger.trace(event)

    def create_entries(self):
        # 创建输入框
        if self.row != 0:
            self.row += 1
        index = 0
        for key, value in self.__entries.items():
            function_name = key
            text_name = value[TEXT]
            if index == 0:
                self.column = 0
            elif index % self.__max_double_line_count == 0:
                self.row += 1
                self.column = 0
            else:
                self.column += 1
            logger.debug(f"row = {self.row}, column = {self.column}, index = {index}")
            # 获取输入框的名称
            Label(self, text=text_name).grid(row=self.row, column=self.column, sticky=W)
            # 创建输入框
            self.entries[function_name] = Entry(self, width=5)
            logger.debug(f"row = {self.row}, column = {self.column}, index = {index}")
            self.entries[function_name].grid(row=self.row, column=self.column + 1, sticky=W)
            # 绑定事件
            for event_key in self.support_event_keys:
                self.entries[function_name].bind(event_key,
                                                 lambda x, y=("", function_name): self.__entry_event(x, y))
            self.column += 1
            index += 1

    def __entry_event(self, event, params):
        logger.trace(event)
        function_name = params[1]
        if function_name == MESSAGE_LOST:
            value = self.entries[MESSAGE_LOST].get()
            if value != "":
                # 0x152,0x153, 0x154
                value.replace("，", ",")
                if "," in value:
                    values = value.split(",")
                else:
                    # 0x164
                    values = [value]
                for msg_id in values:
                    msg_id = msg_id.strip()
                    # 处理16进制
                    if "x" in msg_id or "X" in msg_id:
                        # 把16进制转换成10进制
                        message_id = int(msg_id, 16)
                    else:
                        message_id = int(f"0x{msg_id}", 16)
                    logger.debug(f"message_id = {message_id}")
                    self.can_service.stop_transmit(message_id)
        else:
            entry_value = self.entries[function_name].get()
            params = self.__entries[function_name]
            actions = params[ACTIONS]
            text_name = params[TEXT]
            logger.debug(f"设置{text_name}值为{entry_value}")
            new_actions = copy.deepcopy(actions)
            for action in new_actions:
                if len(action) == 2:
                    msg_id, signals = action
                    for name, value in signals.items():
                        if value is None:
                            logger.debug(f"change {name} value to {entry_value}")
                            signals[name] = float(entry_value)
            self.__send_actions(new_actions)

    def create_thread_buttons(self):
        # 创建事件单选框
        if self.row != 0:
            self.row += 1
        index = 0
        for key, value in self.__thread_buttons.items():
            function_name = key
            text_name = value[TEXT]
            if index == 0:
                self.column = 0
            elif index % self.__max_line_count == 0:
                self.row += 1
                self.column = 0
            else:
                self.column += 1

            # 创建bool对象接收值
            self.thread_button_bool_vars[text_name] = BooleanVar()
            # 创建CheckButton对象并放到thread_buttons中方便调用
            button = Checkbutton(self, text=text_name,
                                 variable=self.thread_button_bool_vars[text_name],
                                 onvalue=True,
                                 offvalue=False,
                                 command=lambda x=function_name: self.__thread_button_event(x))
            self.thread_buttons[function_name] = button
            logger.debug(f"row = {self.row}, column = {self.column}, index = {index}")
            self.thread_buttons[function_name].grid(row=self.row, column=self.column, sticky=W)
            index += 1

    def __thread_button_event(self, function_name):
        if function_name == DEFAULT_MESSAGE:
            logger.info(f"send default messages and filter nodes {self.__filter_nodes}")
            if self.thread_button_bool_vars[DEFAULT_MESSAGE].get():
                self.thread_pool.submit(self.__special_actions, 1)
        elif function_name == BUS_LOST:
            logger.info("can bus lost")
            if self.thread_button_bool_vars[BUS_LOST].get():
                self.thread_pool.submit(self.__special_actions, 2)
        else:
            param = self.__thread_buttons[function_name]
            text_name = param[TEXT]
            actions = param[ACTIONS]
            if self.thread_button_bool_vars[text_name].get():
                if function_name not in self.thread_task:
                    task = self.thread_pool.submit(self.__thread_method, text_name, actions)
                    self.thread_task[function_name] = task
            else:
                if function_name in self.thread_task:
                    self.thread_task.pop(function_name)

    def __thread_method(self, name, actions):
        logger.debug(actions)
        while self.thread_button_bool_vars[name].get():
            self.__send_actions(actions)

    def __send_actions(self, actions: List):
        for action in actions:
            if len(action) == 2:
                msg_id, signals = action
                logger.info(f"{hex(msg_id)} = {signals}")
                self.can_service.send_can_signal_message(msg_id, signals)
            elif len(action) == 1:
                logger.debug(f"{action}")
                sleep_time = float(action[0])
                sleep(sleep_time)
            else:
                raise RuntimeError(f"value[{action}] incorrect")


class Gui(object):

    def __init__(self, config_file: str, dbc: str, can_box_device: CanBoxDeviceEnum,
                 filter_nodes: List[str] = None, can_fd: bool = False):
        self.tk = Tk()
        self.tk.title = "CAN面板"
        # 初始化 CANService
        self.can_service = CANService(dbc, can_box_device=can_box_device, can_fd=can_fd)
        # 打开can盒
        self.can_service.open_can()
        # 默认消息发送要过滤的节点
        self.__filter_nodes = filter_nodes
        # 获取按钮
        reader = ConfigReader()
        config = reader.read_from_file(config_file)
        # 多线程的最大线程数
        self.max_workers = 600
        # 初始化线程池
        self.thread_pool = ThreadPoolExecutor(max_workers=self.max_workers)
        self.tab_control = Notebook(self.tk)
        # tab选项框对象字典
        self.tabs = []
        for key, value in config.items():
            logger.debug(f"handle tab {key}")
            tab = TabFrame(self.tk, can_service=self.can_service, filter_nodes=filter_nodes,
                           config=value, thread_pool=self.thread_pool)
            self.tab_control.add(tab, text=key)
            self.tabs.append(tab)
        self.tab_control.pack(expand=1, fill="both")
        # 第一个tab
        self.tab_control.select(self.tabs[0])
        self.tk.protocol('WM_DELETE_WINDOW', self.exit_root)
        self.tk.mainloop()

    def exit_root(self):
        self.can_service.close_can()
        self.tk.destroy()
