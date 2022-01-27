# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2021, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        gui.py.py
# @Author:      lizhe
# @Created:     2021/12/15 - 21:24
# --------------------------------------------------------
import copy
from time import sleep
from tkinter import Frame, Button, NORMAL, DISABLED, W, BooleanVar, Checkbutton, Entry, Label, Tk, messagebox, \
    HORIZONTAL, E
from tkinter.ttk import Combobox, Notebook, Separator
from typing import List, Dict, Any, Union
from automotive.logger.logger import logger
from automotive.core.can.can_service import CANService
from automotive.core.can.common.enums import CanBoxDeviceEnum
from .reader import ConfigReader
from .reader import check_buttons, thread_buttons, comboxs, entries, buttons, receive_buttons
from ..common.constants import OPEN_DEVICE, CLOSE_DEVICE, CLEAR_STACK, DEFAULT_MESSAGE, BUS_LOST, \
    MESSAGE_LOST, TEXT, ON, OFF, VALUES, ACTIONS, COMMON, CHECK_MSGS, CHECK_MESSAGE, MESSAGE_ID, SIGNAL_NAME, \
    SIGNAL_VALUE,SIGNAL_VALUES, SEARCH_COUNT, EXACT_SEARCH, YES_OR_NO, CHECK_SIGNAL
from ...utils.common.enums import ExcelEnum

class TabFrame(Frame):

    def __init__(self, master, can_service: CANService, config: Dict[str, Any], filter_nodes: List[str],
                 common_panel: bool = False, max_line_count: int = None):
        super().__init__(master)
        self.can_service = can_service
        self.thread_pool = can_service.can_bus.thread_pool
        self.__filter_nodes = filter_nodes
        # 单选框按钮配置
        self.__check_buttons = config[check_buttons] if config[check_buttons] else dict()
        logger.debug(f"check_buttons = {self.__check_buttons}")
        # 闪烁单选框按钮配置
        self.__thread_buttons = config[thread_buttons] if config[thread_buttons] else dict()
        logger.debug(f"thread_buttons = {self.__thread_buttons}")
        # 下拉框按钮配置
        self.__comboxs = config[comboxs] if config[comboxs] else dict()
        logger.debug(f"comboxs = {self.__comboxs}")
        # 输入框按钮配置
        self.__entries = config[entries] if config[entries] else dict()
        logger.debug(f"entries = {self.__entries}")
        # 按钮框配置
        self.__buttons = config[buttons] if config[buttons] else dict()
        logger.debug(f"buttons = {self.__buttons}")
        # 接收按钮框配置
        self.__receive_buttons = config[receive_buttons] if config[receive_buttons] else dict()
        logger.debug(f"receive_buttons = {self.__receive_buttons}")
        # 每行能够容纳的数量
        self.__max_line_count = max_line_count  # 36
        # 双行能够容纳的数量
        self.__max_double_line_count = int(self.__max_line_count / 2)
        # 设置标签（label）默认宽度
        self.__label_width = 25
        # 设置下拉框（comboxs）默认宽度
        self.__comboxs_width = 20
        # 设置单选按钮（checkBut）默认宽度
        self.__checkBut_width = 25
        # 设置多线程按钮框（thread_buttons）默认宽度
        self.__thread_buttons_width = 20
        # 设置按钮（button）默认宽度
        self.__buttons_width = 20
        # 设置输入框（entrie)默认宽度
        self.__entrie_width = 10
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
        if common_panel:
            self.create_common_widget()
        # 创建单选按钮
        self.create_check_buttons()
        # 创建下拉按钮
        self.create_comboxs()
        # 创建输入框
        self.create_entries()
        # 创建事件单选按钮
        self.create_thread_buttons()
        # 创建按钮框(多线程)
        self.create_buttons()
        # 创建接收检查按钮
        self.create_receive_buttons()


    def create_common_widget(self):
        """
        创建 打开设备、关闭设备、清除数据（清除接收到的数据)、发送默认消息（通过初始化的filter_node过滤消息), 总线丢失、丢失部分信号等按键
        """
        # ********** 创建打开设备按钮 check_button **********
        text_name, show_name = OPEN_DEVICE
        # 创建Button对象
        self.buttons[text_name] = Button(self, text=show_name,
                                         command=lambda x=OPEN_DEVICE: self.__special_button_event(x))
        # 布局button
        self.buttons[text_name].grid(row=self.row, column=self.column, sticky=W)
        self.buttons[text_name]["state"] = NORMAL
        self.column += 1
        # ********** 创建关闭设备按钮 **********
        text_name, show_name = CLOSE_DEVICE
        # 创建Button对象
        self.buttons[text_name] = Button(self, text=show_name,
                                         command=lambda x=CLOSE_DEVICE: self.__special_button_event(x))
        # 布局button
        self.buttons[text_name].grid(row=self.row, column=self.column, sticky=W)
        self.buttons[text_name]["state"] = DISABLED
        self.column += 1
        # ********** 创建清除接收到的CAN信号按钮 **********
        text_name, show_name = CLEAR_STACK
        # 创建Button对象
        self.buttons[text_name] = Button(self, text=show_name,
                                         command=lambda x=CLEAR_STACK: self.__special_button_event(x))
        # 布局button
        self.buttons[text_name].grid(row=self.row, column=self.column, sticky=W)
        self.column += 1
        # ********** 创建一个发送默认消息的按钮 button **********
        text_name, show_name = DEFAULT_MESSAGE
        # 创建Button对象
        self.buttons[text_name] = Button(self, text=show_name,
                                         command=lambda x=DEFAULT_MESSAGE: self.__special_button_event(x))
        # 布局button
        self.buttons[text_name].grid(row=self.row, column=self.column, sticky=W)
        self.column += 1
        # ********** 创建一个总线丢失的按钮 button **********
        text_name, show_name = BUS_LOST
        # 创建CheckButton对象并放到check_buttons中方便调用
        self.buttons[text_name] = Button(self, text=show_name,
                                         command=lambda x=BUS_LOST: self.__special_button_event(x))
        # 布局checkbutton
        self.buttons[text_name].grid(row=self.row, column=self.column, sticky=W)
        self.column += 1
        # ********** 创建一个信号丢失的输入框  entry **********
        text_name, show_name = MESSAGE_LOST
        # 获取输入框的名称
        Label(self, text=show_name).grid(row=self.row, column=self.column, sticky=W)
        self.column += 1
        self.entries[text_name] = Entry(self, width=10)
        self.entries[text_name].grid(row=self.row, column=self.column, sticky=W, columnspan=2)
        self.entries[text_name].bind(self.support_event_keys[0],
                                     lambda x, y=("", text_name): self.__entry_event(x, y))
        self.row += 1
        Separator(self, orient=HORIZONTAL).grid(row=self.row, column=0, pady=5, sticky=E + W,
                                                columnspan=self.__max_line_count)
        self.row += 1
        # ********** 创建信号检查部分 **********
        self.__create_message_check()
        # ********** 创建检测信号是否之前发送值部分 *******
        self.row += 1
        Separator(self, orient=HORIZONTAL).grid(row=self.row, column=0, pady=5, sticky=E + W,
                                                columnspan=self.__max_line_count)
        self.row += 1
        self.__create_message_signal_check()

    def __create_message_check(self):
        """
        创建信号检查部分
        帧ID， 信号名称 信号值， 出现次数 精确查找等选中，用于在主机操作后的检查
        """
        self.column = 0
        text_name, show_name = MESSAGE_ID
        Label(self, text=show_name).grid(row=self.row, column=self.column, sticky=W)
        self.column += 1
        self.entries[text_name] = Entry(self, width=8)  # 等同于 message_id = Entry
        self.entries[text_name].grid(row=self.row, column=self.column, sticky=W)
        self.column += 1
        text_name, show_name = SIGNAL_NAME
        Label(self, text=show_name).grid(row=self.row, column=self.column, sticky=W)
        self.column += 1
        self.entries[text_name] = Entry(self, width=20)  # 等同于signal_name = Entry
        self.entries[text_name].grid(row=self.row, column=self.column, sticky=W, columnspan=2)
        self.column += 2
        text_name, show_name = SIGNAL_VALUE
        Label(self, text=show_name).grid(row=self.row, column=self.column, sticky=W)
        self.column += 1
        self.entries[text_name] = Entry(self, width=8)  # 等同于signal_value = Entry
        self.entries[text_name].grid(row=self.row, column=self.column, sticky=W)
        self.column += 1
        text_name, show_name = SEARCH_COUNT
        Label(self, text=show_name).grid(row=self.row, column=self.column, sticky=W)
        self.column += 1
        self.entries[text_name] = Entry(self, width=8)
        self.entries[text_name].grid(row=self.row, column=self.column, sticky=W)
        self.column += 1
        text_name, show_name = EXACT_SEARCH
        Label(self, text=show_name).grid(row=self.row, column=self.column, sticky=W)
        self.column += 1
        # 创建下拉框
        self.comboxs[text_name] = Combobox(self, values=YES_OR_NO, state="readonly", width=5)
        # 设置下拉框初始值为第一个值
        self.comboxs[text_name].current(0)
        # 布局下拉框
        self.comboxs[text_name].grid(row=self.row, column=self.column, sticky=W)
        self.column += 1
        text_name, show_name = CHECK_MESSAGE
        # 创建Button对象
        self.buttons[text_name] = Button(self, text=show_name,
                                         command=lambda x=CHECK_MESSAGE: self.__special_button_event(x))
        # 布局button
        self.buttons[text_name].grid(row=self.row, column=self.column, sticky=W)
        self.buttons[text_name]["state"] = NORMAL

    def __create_message_signal_check(self):
        """
        创建信号之前发送过那些值检测
        帧ID，信号名称 精确查找的等选择
        :return:
        """
        self.column = 0
        text_name, show_name = MESSAGE_ID
        Label(self, text=show_name).grid(row=self.row, column=self.column, sticky=W)
        self.column += 1
        self.entries[text_name] = Entry(self, width=8)  # 等同于 message_id = Entry
        self.entries[text_name].grid(row=self.row, column=self.column, sticky=W)
        self.column += 1
        text_name, show_name = SIGNAL_NAME
        Label(self, text=show_name).grid(row=self.row, column=self.column, sticky=W)
        self.column += 1
        self.entries[text_name] = Entry(self, width=20)  # 等同于signal_name = Entry
        self.entries[text_name].grid(row=self.row, column=self.column, sticky=W, columnspan=2)
        self.column += 2
        text_name, show_name = SIGNAL_VALUES
        Label(self, text=show_name).grid(row=self.row, column=self.column, sticky=W)
        self.column += 1
        self.entries[text_name] = Entry(self, width=40, state=DISABLED)  # 等同于signal_value = Entry
        self.entries[text_name].grid(row=self.row, column=self.column, sticky=W, columnspan=5)
        self.column += 5
        text_name, show_name = CHECK_SIGNAL
        # 创建Button对象
        self.buttons[text_name] = Button(self, text=show_name,
                                         command=lambda x=CHECK_SIGNAL: self.__special_button_event(x))
        # 布局button
        self.buttons[text_name].grid(row=self.row, column=self.column, sticky=W)
        self.buttons[text_name]["state"] = NORMAL
        logger.info(f"entries are {entries}")

    def __special_button_event(self, button_type: tuple):
        text_name, show_name = button_type
        self.buttons[text_name]["state"] = DISABLED
        try:
            self.__special_actions(button_type)
        except RuntimeError as e:
            messagebox.showerror("出错了", f"【{e}】")
            logger.error(e)
            self.buttons[text_name]["state"] = NORMAL

    def __special_actions(self, button_type: tuple):
        open_text_name = OPEN_DEVICE[0]
        close_text_name = CLOSE_DEVICE[0]
        message_id_text_name = MESSAGE_ID[0]
        signal_name_text_name = SIGNAL_NAME[0]
        signal_value_text_name = SIGNAL_VALUE[0]
        signal_values_text_name = SIGNAL_VALUES[0]
        search_count_text_name = SEARCH_COUNT[0]
        exact_search_text_name = EXACT_SEARCH[0]
        text_name, show_name = button_type
        if button_type == DEFAULT_MESSAGE:
            self.can_service.send_default_messages(filter_sender=self.__filter_nodes)
            self.buttons[text_name]["state"] = NORMAL
        elif button_type == BUS_LOST:
            self.can_service.stop_transmit()
            self.buttons[text_name]["state"] = NORMAL
        elif button_type == OPEN_DEVICE:
            self.can_service.open_can()
            self.buttons[open_text_name]["state"] = DISABLED
            self.buttons[close_text_name]["state"] = NORMAL
        elif button_type == CLOSE_DEVICE:
            self.can_service.close_can()
            self.buttons[open_text_name]["state"] = NORMAL
            self.buttons[close_text_name]["state"] = DISABLED
        elif button_type == CLEAR_STACK:
            self.can_service.clear_stack_data()
            self.buttons[text_name]["state"] = NORMAL
        elif button_type == CHECK_MESSAGE:
            # 获取message id,如果未填写message_id,则设置message_id 为默认值None
            message_id = None
            if self.entries[message_id_text_name].get() != "":
                message_id = int(self.entries[message_id_text_name].get(), 16)
            # 获取signal name
            signal_name = self.entries[signal_name_text_name].get().strip()
            # 获取signal value
            signal_value_text = self.entries[signal_value_text_name].get()
            if signal_value_text != "":
                signal_value = int(signal_value_text)
                # 获取次数
                search_count_text = self.entries[search_count_text_name].get()
                if search_count_text != "":
                    search_count = int(search_count_text)
                else:
                    search_count = None
                # 获取是否精确查找
                index = self.comboxs[exact_search_text_name].current()
                # 选中第一个则表示是True
                exact_search = (index == 0)
                stack = self.can_service.get_stack()
                result = self.can_service.check_signal_value(stack, message_id, signal_name, signal_value, search_count,
                                                             exact_search)
                show_message = "成功" if result else "失败"
                exact_message = "精确" if exact_search else "不精确"
                message = f"检查信号【{signal_name}】值为【{signal_value}】收到次数" \
                          f"为【{search_count}】，匹配方式是【{exact_message}】检查结果是【{show_message}】"
                if result:
                    messagebox.showinfo(title=show_message, message=message)
                else:
                    messagebox.showerror(title=show_message, message=message)
                self.buttons[text_name]["state"] = NORMAL
            else:
                messagebox.showerror(title="失败", message="请填写需要查询的信号值")
            self.buttons[text_name]["state"] = NORMAL
        elif button_type == CHECK_SIGNAL:
            # 获取message_id 并设置默认值为None
            message_id = None
            if self.entries[message_id_text_name].get() != "":
                message_id = int(self.entries[message_id_text_name].get(), 16)
            # 获取signal name
            signal_name = self.entries[signal_name_text_name].get().strip()
            # 检测信号值是否已经发送过，并返回检测到的信号值 result
            stack = self.can_service.get_stack()
            result = self.can_service.get_receive_signal_values(stack, signal_name, message_id)
            if len(result) > 0:
                self.entries[signal_values_text_name]["state"] = NORMAL
                # 将之前的值先清空
                self.entries[signal_values_text_name].delete(0, "end")
                # 将返回的值插入到输入框中
                self.entries[signal_values_text_name].insert(0, result)
                self.entries[signal_values_text_name]["state"] = DISABLED
            else:
                messagebox.showerror(title="失败", message=f"{signal_name} is not received")

            self.buttons[text_name]["state"] = NORMAL

    def create_check_buttons(self):
        """
        创建选中框，适用于单选发送消息的情况
        """
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
                                 command=lambda x=function_name: self.__check_button_event(x),
                                 width=self.__checkBut_width,
                                 anchor="w"
                                 )
            self.check_buttons[function_name] = button
            logger.debug(f"row = {self.row}, column = {self.column}, index = {index}")
            # 布局checkbutton
            self.check_buttons[function_name].grid(row=self.row, column=self.column, sticky=W)
            index += 1
        self.row += 1
        if len(self.__check_buttons) != 0:
            Separator(self, orient=HORIZONTAL).grid(row=self.row, column=0, pady=5, sticky=E + W,
                                                    columnspan=self.__max_line_count)
            self.row += 1

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
        """
        创建下拉框，选中的时候触发事件， 适用于枚举类型的选中框
        """
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
            Label(self, text=text_name, width=self.__label_width, anchor="w").grid(row=self.row, column=self.column,
                                                                                   sticky=W)
            # 创建下拉框
            self.comboxs[function_name] = Combobox(self, values=values, state="readonly", width=self.__comboxs_width)
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
        self.row += 1
        if len(self.__comboxs) != 0:
            Separator(self, orient=HORIZONTAL).grid(row=self.row, column=0, pady=5, sticky=E + W,
                                                    columnspan=self.__max_line_count)
            self.row += 1

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
        """
        创建输入框，适用于车速类型的线性信号值
        """
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
            Label(self, text=text_name, width=self.__label_width, anchor="w").grid(row=self.row, column=self.column,
                                                                                   sticky=W)
            # 创建输入框
            self.entries[function_name] = Entry(self, width=self.__entrie_width)
            logger.debug(f"row = {self.row}, column = {self.column}, index = {index}")
            self.entries[function_name].grid(row=self.row, column=self.column + 1, sticky=W)
            # 绑定事件
            for event_key in self.support_event_keys:
                self.entries[function_name].bind(event_key,
                                                 lambda x, y=("", function_name): self.__entry_event(x, y))
            self.column += 1
            index += 1
        self.row += 1
        if len(self.__entries) != 0:
            Separator(self, orient=HORIZONTAL).grid(row=self.row, column=0, pady=5, sticky=E + W,
                                                    columnspan=self.__max_line_count)
            self.row += 1

    def __entry_event(self, event, params):
        message_lost = MESSAGE_LOST[0]
        logger.trace(event)
        function_name = params[1]
        if function_name == message_lost:
            value = self.entries[function_name].get()
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
                    try:
                        self.can_service.stop_transmit(message_id)
                    except RuntimeError as e:
                        logger.error(e)
                        messagebox.showerror("出错了", f"【{e}】")
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
        """
        创建周期交替变化或者有时间延迟的信号发送， 如双闪灯
        选中会发送，不选中则不发送
        名字上以【】区别
        """
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
            button = Checkbutton(self, text=f"【{text_name}】",
                                 variable=self.thread_button_bool_vars[text_name],
                                 onvalue=True,
                                 offvalue=False,
                                 command=lambda x=function_name: self.__thread_check_button_event(x),
                                 width=self.__thread_buttons_width,
                                 anchor="w"

                                 )
            self.thread_buttons[function_name] = button
            logger.debug(f"row = {self.row}, column = {self.column}, index = {index}")
            self.thread_buttons[function_name].grid(row=self.row, column=self.column, sticky=W)
            index += 1
        self.row += 1
        if len(self.__thread_buttons) != 0:
            Separator(self, orient=HORIZONTAL).grid(row=self.row, column=0, pady=5, sticky=E + W,
                                                    columnspan=self.__max_line_count)
            self.row += 1

    def __thread_check_button_event(self, function_name):
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
                try:
                    self.can_service.send_can_signal_message(msg_id, signals)
                except RuntimeError as e:
                    logger.error(e)
                    messagebox.showerror("出错了", f"【{e}】")
            elif len(action) == 1:
                logger.debug(f"sleep {action} seconds")
                sleep_time = float(action[0])
                sleep(sleep_time)
            else:
                raise RuntimeError(f"value[{action}] incorrect")

    def create_buttons(self):
        """
        创建事件信号按钮，主要用于有时间延迟的部分，如长按或者短按方向盘按键， press release两种状态切换需要时间等待
        """
        if self.row != 0:
            self.row += 1
        index = 0
        for key, value in self.__buttons.items():
            function_name = key
            text_name = value[TEXT]
            if index == 0:
                self.column = 0
            elif index % self.__max_line_count == 0:
                self.row += 1
                self.column = 0
            else:
                self.column += 1
            # 创建CheckButton对象并放到thread_buttons中方便调用
            self.buttons[function_name] = Button(self, text=text_name,
                                                 command=lambda x=function_name: self.__thread_button_event(x),
                                                 width=self.__buttons_width)
            logger.debug(f"row = {self.row}, column = {self.column}, index = {index}")
            self.buttons[function_name].grid(row=self.row, column=self.column, sticky=W)
            index += 1
        self.row += 1
        if len(self.__buttons) != 0:
            Separator(self, orient=HORIZONTAL).grid(row=self.row, column=0, pady=5, sticky=E + W,
                                                    columnspan=self.__max_line_count)
            self.row += 1

    def __thread_button_event(self, function_name):
        try:
            self.buttons[function_name]["state"] = DISABLED
            param = self.__buttons[function_name]
            text_name = param[TEXT]
            logger.debug(f"press {text_name} button")
            actions = param[ACTIONS]
            self.thread_pool.submit(self.__send_actions, actions)
        except RuntimeError as e:
            logger.error(e)
            messagebox.showerror("出错了", f"【{e}】")
        finally:
            self.buttons[function_name]["state"] = NORMAL

    def create_receive_buttons(self):
        """
        创建接收检查按钮， 模拟其他ECU接收
        """
        if self.row != 0:
            self.row += 1
        index = 0
        for key, value in self.__receive_buttons.items():
            function_name = key
            text_name = value[TEXT]
            if index == 0:
                self.column = 0
            elif index % self.__max_line_count == 0:
                self.row += 1
                self.column = 0
            else:
                self.column += 1
            # 创建CheckButton对象并放到thread_buttons中方便调用
            logger.debug(f"add button {function_name} in buttons")
            self.buttons[function_name] = Button(self, text=f"【{text_name}】",
                                                 command=lambda x=function_name: self.__receive_button_event(x))
            logger.debug(f"row = {self.row}, column = {self.column}, index = {index}")
            self.buttons[function_name].grid(row=self.row, column=self.column, sticky=W)
            index += 1
        self.row += 1
        if len(self.__receive_buttons) != 0:
            Separator(self, orient=HORIZONTAL).grid(row=self.row, column=0, pady=5, sticky=E + W,
                                                    columnspan=self.__max_line_count)
            self.row += 1

    def __receive_button_event(self, function_name):
        self.buttons[function_name]["state"] = DISABLED
        param = self.__receive_buttons[function_name]
        text_name = param[TEXT]
        logger.debug(f"press {text_name} button")
        check_msgs = param[CHECK_MSGS]
        msg_id, signal_name, signal_value, count, expect_value = check_msgs
        try:
            stack = self.can_service.get_stack()
            result = self.can_service.check_signal_value(stack, msg_id, signal_name, signal_value, count, expect_value)
            show_message = "成功" if result else "失败"
            exact_message = "精确" if expect_value else "不精确"
            message = f"检查【{hex(msg_id)}】中信号【{signal_name}】值为【{signal_value}】收到次数" \
                      f"为【{count}】，匹配方式为【{exact_message}】的检查结果是【{show_message}】"
            if result:
                messagebox.showinfo(title=show_message, message=message)
            else:
                messagebox.showerror(title=show_message, message=message)
        except RuntimeError as e:
            logger.error(e)
            messagebox.showerror(title="出错了", message=f"【{e}】")
        finally:
            self.buttons[function_name]["state"] = NORMAL


class Gui(object):

    def __init__(self, excel_file: str, dbc: str, can_box_device: Union[CanBoxDeviceEnum, str, None] = None,
                 filter_nodes: List[str] = None, can_fd: bool = False,
                 excel_type: ExcelEnum = ExcelEnum.OPENPYXL, max_workers: int = 500, max_line_count: int = 8):
        """

        :param excel_file: Excel文件路径 （必填项）
        :param dbc: 项目dbc文件路径 （必填项）
        :param can_box_device:（选填）
        :param filter_nodes:发送默认信号筛选器（默认值）
        :param can_fd:（选填）
        :param excel_type: （选填）
        :param max_workers:默认值就行（选填）
        :param max_line_count:面板一行中显示的最大数量，默认值为8，如果显示不全可以自己修改
        """
        self.tk = Tk()
        self.tk.title("CAN面板")
        # 初始化 CANService
        self.can_service = CANService(dbc, can_box_device=can_box_device, can_fd=can_fd, max_workers=max_workers)
        # 默认消息发送要过滤的节点
        self.__filter_nodes = filter_nodes
        # 获取按钮
        service = ConfigReader(excel_type)
        tab_configs = dict()
        tab_configs[COMMON] = {check_buttons: {}, thread_buttons: {}, comboxs: {},
                               entries: {}, buttons: {}, receive_buttons: {}}
        config = service.read_from_file(excel_file)
        tab_configs.update(config)
        self.tab_control = Notebook(self.tk)
        # tab选项框对象字典
        self.tabs = []
        for key, value in tab_configs.items():
            logger.info(f"handle tab {key}")
            if key == COMMON:
                common_panel = True
            else:
                common_panel = False
            tab = TabFrame(self.tk, can_service=self.can_service, filter_nodes=filter_nodes,
                           config=value, common_panel=common_panel, max_line_count=max_line_count)
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
