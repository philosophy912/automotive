# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2021, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        remove_comment.py
# @Author:      lizhe
# @Created:     2022/10/23 - 19:45
# --------------------------------------------------------
import os.path
import re

from typing import List, NoReturn, Optional

from ..logger.logger import logger


def remove_comment(file: str):
    if not os.path.exists(file):
        raise RuntimeError(f"file or folder [{file}] not exist, please check it again")
    if os.path.isdir(file):
        for root, dirs, files in os.walk(file):
            for f in files:
                __handle_contents(os.path.join(root, f))
    else:
        __handle_contents(file)


def __get_indexes(sub_str: str, content: str) -> List[int]:
    """
    在字符串中查找子串的位置
    :param sub_str:
    :param content:
    :return:
    """
    if len(sub_str) != 1:
        raise RuntimeError(f"only support char but {sub_str}")
    return [substr.start() for substr in re.finditer(sub_str, content)]


def __remove_logger(content: str) -> Optional[str]:
    """
    去掉logger打印
    :param content:
    """
    # 去掉了python中的logger
    if content.strip().startswith("logger."):
        return None
    # 去掉了java的log文件的打印
    elif content.strip().startswith("log."):
        return None
    # 去掉了python代码logger的导入
    elif "import logger" in content and "loguru" not in content:
        return None
    # 去掉lombok的导入
    elif "import lombok.extern.slf4j.Slf4j;" in content:
        return None
    # 去掉Slf4j的注释
    elif content.strip().startswith("@Slf4j"):
        return None
    else:
        return content


def __handle_contents(file: str) -> NoReturn:
    logger.debug(f"now handle file[{file}]")
    with open(file, "r", encoding="utf-8", errors="ignore") as f:
        file = file.lower()
        contents = f.readlines()
        if file.endswith(".py"):
            contents = __remove_python_comment(contents)
        if file.endswith(".java") or file.endswith(".h") \
                or file.endswith(".cpp") or file.endswith(".c") or file.endswith(".hpp"):
            contents = __remove_java_comments(contents)
        if file.endswith(".xml"):
            contents = __remove_xml_comments(contents)
        if file.endswith(".sh"):
            contents = __remove_shell_comments(contents)
    with open(file, "w", encoding="utf-8", errors="ignore") as f:
        for content in contents:
            # 可能去除\n所以要加回来
            if content.endswith("\n"):
                f.write(f"{content}")
            else:
                f.write(f"{content}\n")


def __remove_python_comment(contents: List[str]) -> List[str]:
    """
    去除python的注释
    :param contents:
    :return:
    """
    python_multi_comment1 = "\"\"\""
    python_multi_comment2 = "\'\'\'"
    python_single_comment = "#"
    result = []
    multi_comment = False
    for index, content in enumerate(contents):
        line = content.strip()
        # 当前是否处于多行注释状态
        if multi_comment:
            # 此时找到了多行注释的结尾
            if line.startswith(python_multi_comment1) or line.startswith(python_multi_comment2):
                multi_comment = False
        else:
            # 此时找到了多行注释的头部
            if line.startswith(python_multi_comment1) or line.startswith(python_multi_comment2):
                multi_comment = True
            else:
                # 判断单行注释的情况
                if line.startswith(python_single_comment):
                    continue
                # 有行内注释的情况
                elif python_single_comment in line:
                    # 首先找出所有#号的位置
                    single_comment_count = content.count(python_single_comment)
                    if single_comment_count > 1:
                        # 可能有多个注释
                        indexes = __get_indexes(python_single_comment, content)
                        for sub_str_index in indexes:
                            last_str = content[sub_str_index - 1]
                            next_str = content[sub_str_index + 1]
                            condition1 = last_str == "\'" and next_str == "\'"
                            condition2 = last_str == "\"" and next_str == "\""
                            if condition1 or condition2:
                                continue
                            else:
                                # 去掉logger
                                rest_content = content[:sub_str_index]
                                rest_content = __remove_logger(rest_content)
                                if rest_content:
                                    result.append(rest_content)
                    else:
                        # 只有一个注释
                        hash_str_index = content.index(python_single_comment)
                        rest_content = content[:hash_str_index]
                        rest_content = __remove_logger(rest_content)
                        if rest_content:
                            result.append(rest_content)
                else:
                    # 不是注释，需要加入到内容中
                    content = __remove_logger(content)
                    if content:
                        result.append(content)
    return result


def __remove_java_comments(contents: List[str]) -> List[str]:
    java_multi_start = "/*"
    java_multi_end = "*/"
    java_single_comment = "//"
    result = []
    multi_comment = False
    for index, content in enumerate(contents):
        # logger.debug(f"content = [{content}]")
        line = content.strip()
        # 当前是否处于多行注释状态
        if multi_comment:
            # 此时找到了多行注释的结尾
            if java_multi_end in line:
                multi_comment = False
        else:
            # 此时找到了多行注释的头部
            if line.startswith(java_multi_start):
                multi_comment = True
            else:
                # 判断单行注释的情况
                if line.startswith(java_single_comment):
                    continue
                # 单行注释的另外 一种方法
                elif line.startswith(java_multi_start) and line.endswith(java_multi_end):
                    continue
                # 有行内注释的情况
                elif java_single_comment in line:
                    # 首先找出所有#号的位置
                    single_comment_count = content.count(java_single_comment)
                    if single_comment_count > 1:
                        # 可能有多个注释
                        indexes = __get_indexes(java_single_comment, content)
                        for sub_str_index in indexes:
                            last_str = content[sub_str_index - 1]
                            next_str = content[sub_str_index + 1]
                            condition1 = last_str == "\'" and next_str == "\'"
                            condition2 = last_str == "\"" and next_str == "\""
                            if condition1 or condition2:
                                continue
                            else:
                                # 去掉logger
                                rest_content = content[:sub_str_index]
                                rest_content = __remove_logger(rest_content)
                                if rest_content:
                                    result.append(rest_content)
                    else:
                        # 只有一个注释
                        hash_str_index = content.index(java_single_comment)
                        rest_content = content[:hash_str_index]
                        rest_content = __remove_logger(rest_content)
                        if rest_content:
                            result.append(rest_content)
                else:
                    # 不是注释，需要加入到内容中
                    content = __remove_logger(content)
                    if content:
                        result.append(content)
    return result


def __remove_xml_comments(contents: List[str]) -> List[str]:
    xml_start = "<!--"
    xml_end = "-->"
    result = []
    multi_comment = False
    for index, content in enumerate(contents):
        # logger.debug(f"content = [{content}]")
        line = content.strip()
        # 当前是否处于多行注释状态
        if multi_comment:
            # 此时找到了多行注释的结尾
            if line.endswith(xml_end):
                multi_comment = False
        else:
            # 此时找到了多行注释的头部
            if line.startswith(xml_start) and not line.endswith(xml_end):
                multi_comment = True
            else:
                # 判断单行注释的情况
                if line.startswith(xml_start) and line.endswith(xml_end):
                    continue
                else:
                    # 不是注释，需要加入到内容中
                    result.append(content)
    return result


def __remove_shell_comments(contents: List[str]) -> List[str]:
    shell_single_comment = "#"
    result = []
    for index, content in enumerate(contents):
        # logger.debug(f"content = [{content}]")
        line = content.strip()
        # 目前shell只考虑了单行注释的情况
        if line.startswith(shell_single_comment) and not line.startswith("#!"):
            continue
        else:
            # 不是注释，需要加入到内容中
            result.append(content)

    return result
