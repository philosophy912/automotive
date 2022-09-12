# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2021, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        framework.py
# @Author:      lizhe
# @Created:     2022/5/25 - 21:39
# --------------------------------------------------------
import importlib
import importlib.util
import os.path
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from tkinter import Tk, Text, BOTH, END, Button, Frame, DISABLED, NORMAL
from tkinter.ttk import Combobox
from typing import Dict, Sequence, Union

from automotive import Utils
from automotive.application.common.enums import ProjectEnum
from automotive.logger.logger import logger


class Stress(object):
    """
    GUI框架 OmoSoftQA
    根据配置文件来生成相应的应用，开发人员只需要写具体的自动化用例测试代码即可。
    使用流程
    1. 根据配置文件配置需要用到的信息, 采用yml方式编写
    actions:
        - OnOffAction: 上下电测试  # 代表实现了BaseAction方法的类
        - BatteryOnOfAction: 上下电测试 # 代表了实现BaseAction方法的类
    2. BaseActionAction 的实现类的配置文件需要查询该文件同级
    """

    def __init__(self, project: Union[ProjectEnum, str], action_path: str,
                 width: int = 550, height: int = 350, title: str = "自动化测试"):
        """
        Event就是测试的事件，支持多种事件，应该根据配置文件来进行配置
        :param project: 项目前缀，仅支持ProjectEnum配置的项目
        :param action_path: Event【测试事件】的文件夹所在路径， 代码会自动的去查找以project开头的文件
        :param width: GUI的高
        :param height: GUI的宽
        :param title: GUI显示的名字
        """
        # 线程池句柄
        self.__max_workers = 2
        self.__thread_pool = ThreadPoolExecutor(max_workers=self.__max_workers)
        # 创建队列
        self.__queue = Queue()
        self.__queue_flag = True
        # 当前进行的线程
        self.__action_future = None
        self.__queue_future = None
        self.__title = title
        self.__width = width
        self.__height = height
        # 读取配置文件并实例化对象， 其中key就是Action中的类说明，请简要说明，否则抛异常， value就是实例化后的Action类对象
        self.__classes = self.__get_config(project, action_path)
        # combobox中显示的内容
        self.__values = list(self.__classes.keys())
        # 设置高宽和标题，并居中显示
        self.__tk = Tk()
        self.__tk.title(title)
        self.__tk.geometry(f"{self.__width}x{self.__height}")
        screen_width, screen_height = self.__get_center_point()
        self.__tk.geometry(f"+{screen_width}+{screen_height}")
        # 创建Panel
        self.__create_panel()
        # 传入的测试用例集合， 选中的是当前传入的第1个
        self.__actions = list(self.__classes.values())
        self.__select_action = self.__actions[0]
        # self.__class_instance = None
        # 按键状态
        self.__button_status = True
        # 关闭
        self.__tk.protocol("WM_DELETE_WINDOW", self.__exit_root)
        self.__tk.mainloop()

    def __queue_get(self):
        logger.info("start queue get thread")
        while self.__queue_flag:
            logger.trace(f"queue_flag is {self.__queue_flag}")
            if not self.__queue.empty():
                queue_content = self.__queue.get()
                # logger.info(queue_content)
                self.__insert_contents(queue_content)
            logger.trace(f"action_future status is {self.__action_future is None}")
            if self.__action_future:
                if self.__action_future.done():
                    self.__end_thread()
        logger.debug("end queue get thread")

    def __get_center_point(self):
        screen_width = self.__tk.winfo_screenwidth() / 2 - self.__width / 2
        screen_height = self.__tk.winfo_screenheight() / 2 - self.__height / 2
        return int(screen_width), int(screen_height)

    def __create_panel(self):
        """
        创建面板
        """
        # 创建Frame
        self.__frame = Frame(self.__tk, width=self.__width, height=self.__height)
        self.__text = Text(self.__frame)
        self.__text.pack(fill=BOTH)
        self.__frame.grid(row=0, column=0, columnspan=3)
        self.__clear_button = Button(self.__tk, text="清除", width=20, command=self.__clear_event)
        self.__clear_button.grid(row=1, column=0)
        self.__start_button = Button(self.__tk, text="开始", width=20, command=self.__start)
        self.__start_button.grid(row=1, column=1)
        self.__combobox = Combobox(self.__tk, values=self.__values, state="readonly")
        self.__combobox.current(0)
        self.__combobox.bind("<<ComboboxSelected>>", lambda x="": self.__select_event)
        self.__combobox.grid(row=1, column=2)

    def __select_event(self, event):
        logger.info(event)
        current_select_index = self.__combobox.current()
        self.__select_action = self.__actions[current_select_index]

    def __insert_contents(self, contents: Union[Sequence, str, int, float]):
        if isinstance(contents, (str, int, float)):
            self.__insert_text(contents)
        else:
            for content in contents:
                self.__insert_text(content)

    def __insert_text(self, content: str, next_line: bool = True):
        """
        插入到文本框中
        :param content: 文本内容
        :param next_line: 是否换行， 默认换行
        """
        # 加上了时间的显示
        current_time = Utils.get_time_as_string("%Y-%m-%d %H:%M:%S")
        new_content = f"{content}\n" if next_line else f"{content}"
        display_content = f"{current_time}:  {new_content}"
        logger.debug(f"text content is [{content}]")
        self.__text.insert(END, display_content)
        self.__text.see(END)

    def __clear_event(self):
        """
        清除文本框
        """
        logger.debug("清除文本框")
        self.__text.delete(1.0, END)

    def __exit_root(self):
        """
        退出时候需要销毁的内容
        :return:
        """
        # 关闭can service等等 异常退出
        self.__select_action.close()
        self.__tk.destroy()

    @staticmethod
    def __get_config(project: Union[ProjectEnum, str], action_path: str) -> Dict:
        """
        根据project的value为头的去查找actions下面的的python文件
        :return:
        """
        testcases = dict()
        logger.debug(f"action_path is [{action_path}]")
        # 校验路径是否存在
        if not os.path.exists(action_path):
            raise RuntimeError(f"{action_path} 不存在，请仔细检查")
        if isinstance(project, str):
            project = ProjectEnum.from_value(project)
        project_name = project.value[0].lower()
        # 查找actions文件夹下面的文件
        actions_file = os.listdir(action_path)
        # 过滤出来python文件
        actions_file = filter(lambda x: x.endswith("py"), actions_file)
        actions_file = filter(lambda x: x.startswith(project_name), actions_file)
        actions_file = filter(lambda x: "init" not in x, actions_file)
        actions_files = list(actions_file)
        if len(actions_files) >= 1:
            for action_file in actions_files:
                # 获取action的绝对路径
                abs_action_file = os.path.join(action_path, action_file)
                # 获取action对应的xml的绝对路径
                abs_xml_file = os.path.join(action_path, action_file.replace("py", "yml"))
                if not os.path.exists(abs_xml_file):
                    raise RuntimeError(f"Action {action_file} 对应的配置文件不存在，请检查")
                module_name = action_file.split(".")[0]
                # 根据文件获取spec，然后根据spec加载module
                module_spec = importlib.util.spec_from_file_location(module_name, abs_action_file)
                module = importlib.util.module_from_spec(module_spec)
                # 模块的Loader必须要执行一次， 否则模块有问题
                module_spec.loader.exec_module(module)
                # 根据文件名获取类名
                # 类名首先需要去掉项目名开头的, 项目名是一定会存在的
                class_name = module_name[len(project_name) + 1:]
                if "_" in class_name:
                    class_names = class_name.split("_")
                    class_names = list(map(lambda x: x.capitalize(), class_names))
                    # 首字母大写，模块名匹配类名
                    class_name = "".join(class_names)
                else:
                    class_name = class_name.capitalize()
                # 获取到了类对象
                clazz = getattr(module, class_name)
                clazz_instance = clazz(abs_xml_file)
                description = clazz.__doc__
                if description is None:
                    raise RuntimeError("请填写测试用例简要说明")
                else:
                    if len(description) > 30:
                        raise RuntimeError("测试用例描述不要超过30个字")
                    else:
                        testcases[clazz.__doc__] = clazz_instance
            return testcases
        else:
            raise RuntimeError(f"{actions_files} 下面没有 {project_name}的测试用例，请检查")

    def __start(self):
        """
        选中的事件一定得在线程中执行，否则UI线程要被卡死
        所有的事件必须实现flag功能，即当flag变为False的时候，需要跳出循环，即退出程序执行。
        """
        if self.__button_status:
            self.__start_thread()
        else:
            self.__end_thread()

    def __start_thread(self):
        """
        开启子线程
        """
        self.__button_status = False
        self.__start_button["state"] = DISABLED
        self.__start_button["text"] = "停止"
        self.__clear_event()
        # 线程池句柄
        if self.__thread_pool is None:
            self.__thread_pool = ThreadPoolExecutor(max_workers=self.__max_workers)
        # 开启多线程
        # 实例化对象
        # clazz, xml_file = self.__select_action
        # self.__class_instance = clazz(xml_file)
        self.__queue_flag = True
        # 清空queue中的内容
        self.__queue.queue.clear()
        logger.debug("start child thread")
        # 创建子线程读取线程
        self.__queue_future = self.__thread_pool.submit(self.__queue_get)
        # 开始多线程执行任务
        self.__action_future = self.__thread_pool.submit(self.__select_action.run_stress, self.__queue)
        logger.debug(f"self.__action_future id is {id(self.__action_future)}")
        logger.debug("set button to normal")
        self.__start_button["state"] = NORMAL

    def __end_thread(self):
        """
        关闭子线程
        """
        self.__button_status = True
        self.__start_button["state"] = DISABLED
        logger.debug("end thread")
        self.__start_button["text"] = "开始"
        logger.debug("stop event and set queue flag false")
        self.__queue_flag = False
        # 清空queue中的内容
        logger.debug("clear queue content")
        self.__queue.queue.clear()
        self.__action_future = None
        # self.__class_instance = None
        self.__queue_future = None
        logger.debug("thread stopped")
        if self.__thread_pool:
            # 结束线程之前强制调用close方法关闭设备
            logger.debug("call BaseAction close method")
            self.__select_action.close()
            logger.debug("shutdown thread pool")
            self.__thread_pool.shutdown(wait=False)
            self.__thread_pool = None
        logger.debug("set button to normal")
        self.__start_button["state"] = NORMAL
