# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, China TSP, All rights reserved
# --------------------------------------------------------
# @Name:        email_utils.py
# @Purpose:     todo
# @Author:      lizhe
# @Created:     2020/11/6 - 16:11
# --------------------------------------------------------
import smtplib
import poplib
import email
import os
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.header import Header
from email.parser import Parser
from email.header import decode_header
from email.utils import parseaddr, formataddr
from email.mime.text import MIMEText
from automotive import logger


class EmailContent(object):
    def __init__(self):
        # 邮件从哪里发送来
        self.email_from = None
        # 邮件要发到哪里去
        self.email_to = []
        # 邮件要抄送给谁
        self.email_cc = []
        # 邮件主题
        self.subject = None
        # 邮件正文内容
        self.content = None
        # 邮件附件
        self.attachments = []


class EmailConfig(object):
    def __init__(self):
        # 当前用到的email地址
        self.address = None
        # 设置用户名
        self.password = None
        # SMTP的地址
        self.smtp_address = None
        # smtp端口
        self.smtp_port = 25
        # pop3的地址
        self.pop3_address = None
        # pop3的端口
        self.pop3_port = 110


class EmailUtils(object):

    def __init__(self, config: EmailConfig):
        """
            初始化配置参数
            :param config: Email的配置类（具体参考Email的配置参数)
        """
        self.__config = config
        if config.smtp_address and config.smtp_port:
            self.__server = smtplib.SMTP(config.smtp_address, config.smtp_port)
            self.__server.starttls()
            self.__server.set_debuglevel(0)
            self.__server.login(config.address, config.password)
            logger.info("login account success")
        if config.pop3_address and config.pop3_port:
            self.__pop3_server = poplib.POP3(config.pop3_address, config.pop3_port)

    @staticmethod
    def __format_address(email_address):
        """
        功能：用于规范邮箱格式
        :param email_address: 邮箱全称
        :return: 规范后的邮箱
        """
        name, address = parseaddr(email_address)
        return formataddr((Header(name, "utf-8").encode(), address))

    def send_email(self, email_content: EmailContent):
        """
        发送邮件
        :param email_content: 邮件内容
        """
        message = MIMEMultipart()
        message.attach(MIMEText(email_content.content, "html", "utf-8"))
        message["From"] = email_content.email_from
        message["To"] = ",".join(email_content.email_to)
        message["Cc"] = ",".join(email_content.email_cc)
        message["Subject"] = Header(email_content.subject, "utf-8").encode()
        to_address = ",".join(email_content.email_to + email_content.email_cc)
        for attachment in email_content.attachments:
            with open(attachment, "rb") as f:
                file_name = os.path.basename(attachment)
                # 把附件的内容读进来
                attachment_file = MIMEApplication(f.read())
                # 加上必要的头信息
                attachment_file.add_header("Content-Disposition", "attachment", filename=("gbk", "", file_name))
                attachment_file.add_header('Content-ID', '<0>')
                attachment_file.add_header('X-Attachment-Id', '0')
                # 添加到MIMEMultipart中
                message.attach(attachment_file)
        self.__server.sendmail(email_content.email_from, to_address, message.as_string())
        self.__server.quit()

    def receive_email(self) -> list:
        """
        TODO 暂时未完成测试
        接收邮件
        :return: EmailContent对象
        """
        # 打印POP3服务器的欢迎文字，验证是否正确连接到了邮件服务器
        logger.info(self.__pop3_server.getwelcome().decode('utf8'))
        # 开始进行身份验证
        self.__pop3_server.user(self.__config.address)
        self.__pop3_server.pass_(self.__config.password)
        # 返回邮件总数目和占用服务器的空间大小（字节数）， 通过stat()方法即可
        email_count, email_size = self.__pop3_server.stat()
        logger.info("消息的数量: {0}, 消息的总大小: {1}".format(email_count, email_size))
        # 使用list()返回所有邮件的编号，默认为字节类型的串
        rsp, msg_list, rsp_siz = self.__pop3_server.list()
        logger.info(f"服务器的响应: {rsp},\n消息列表： {msg_list},\n返回消息的大小： {rsp_siz}")
        logger.info(f'邮件总数： {len(msg_list)}')
        return []
