# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, China TSP, All rights reserved
# --------------------------------------------------------
# @Name:        email.py
# @Purpose:     电子邮件类，用于接收和发送电子邮件
# @Author:      lizhe
# @Created:     2020/02/13 13:38
# --------------------------------------------------------


class EmailConfig(object):
    """
    email所使用到的参数，如当前发件人/收件人的地址等
    """

    def __init__(self):
        # 当前用到的email地址,发件人/收件人使用的邮箱地址
        self.address = None
        # 设置用户名
        self.password = None
        # SMTP的地址
        self.smtp_address = None
        # SMTP端口
        self.smtp_port = 25
        # pop3的地址
        self.pop3_address = None
        # pop3的端口
        self.pop3_port = 110


class EmailObject(object):
    """
    邮件收发类，用于组织邮件对象，即邮件由那些部分组成
    """

    def __init__(self):
        # 邮件从哪里发送来
        self.email_from = None
        # 邮件要发到哪里去
        self.email_to = None
        # 邮件要抄送给谁
        self.email_cc = None
        # 邮件主题
        self.subject = None
        # 邮件正文内容
        self.content = None
        # 邮件附件
        self.attachments = []


class ElectronicMail(object):
    """
    电子邮件类，用于接收和发送电子邮件
    """

    def __init__(self, email_config: EmailConfig):
        """
        类中初始化相关设置

        :param email_config: email的相关配置内容，以类的形式组装
        """
        self.__email_config = email_config

    def send_email(self, email_object: EmailObject):
        """
        发送一封邮件

        :param email_object: 邮件对象（详见EmailObject对象说明)
        """
        pass

    def receive_latest_email(self) -> EmailObject:
        """
        接收最新的一封邮件

        :return:  邮件对象（详见EmailObject对象说明)
        """
        pass

    def receive_emails(self) -> list:
        """
        接收所收到的所有邮件

        :return: 邮件对象列表
        """
        pass
