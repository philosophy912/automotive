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
import os
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.header import Header
from email.mime.text import MIMEText
from enum import Enum, unique
from exchangelib import DELEGATE, Account, Credentials, Message, Mailbox, HTMLBody, FileAttachment

from automotive import logger


@unique
class EmailType(Enum):
    """
    邮箱类型
    """
    # SMTP模式
    SMTP = "smtp"
    # EXCHANGE模式
    EXCHANGE = "exchange"


class EmailUtils(object):

    def __init__(self, email_address: str, password: str, email_type: EmailType = EmailType.SMTP,
                 smtp_address: str = None, smtp_port: int = 25, pop3_address: str = None, pop3_port: str = 110,
                 is_tsl: bool = False):
        """
        初始化配置参数
        :param email_address: 邮箱地址
        :param password:  邮箱密码
        :param email_type:  邮箱类型，支持SMTP和
        :param smtp_address: SMTP的地址
        :param smtp_port: smtp端口
        :param pop3_address: pop3的地址
        :param pop3_port: pop3的端口
        :param is_tsl: 是否tsl加密
        """
        self.__type = email_type
        self.__email_address = email_address
        if email_type == EmailType.SMTP:
            if smtp_address and smtp_port:
                if smtp_port == 465:
                    self.__server = smtplib.SMTP(smtp_address, smtp_port)
                else:
                    self.__server = smtplib.SMTP(smtp_address, smtp_port)
                    if is_tsl:
                        self.__server.starttls()
                self.__server.set_debuglevel(0)
                self.__server.login(email_address, password)
            if pop3_address and pop3_port:
                self.__pop3_server = poplib.POP3(pop3_address, pop3_port)
                # 打印POP3服务器的欢迎文字，验证是否正确连接到了邮件服务器
                logger.info(self.__pop3_server.getwelcome().decode('utf8'))
                # 开始进行身份验证
                self.__pop3_server.user(email_address)
                self.__pop3_server.pass_(password)
        else:
            username = email_address.split("@")[0]
            credentials = Credentials(username=username, password=password)
            self.__account = Account(primary_smtp_address=email_address, credentials=credentials,
                                     autodiscover=True, access_type=DELEGATE)

    def send_email(self, email_to: list, subject: str, content: str, attachments=None, email_cc=None):
        """
        发送邮件
        :param email_to:  邮件要发到哪里去
        :param subject: 邮件主题
        :param content: 邮件正文内容
        :param attachments: 邮件附件
        :param email_cc:  邮件要抄送给谁
        :return:
        """
        if email_cc is None:
            email_cc = []
        if attachments is None:
            attachments = []
        if self.__type == EmailType.SMTP:
            message = MIMEMultipart()
            message.attach(MIMEText(content, "html", "utf-8"))
            message["From"] = self.__email_address
            message["To"] = ",".join(email_to)
            message["Cc"] = ",".join(email_cc)
            message["Subject"] = Header(subject, "utf-8").encode()
            to_address = ",".join(email_to + email_cc)
            for attachment in attachments:
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
            self.__server.sendmail(self.__email_address, to_address, message.as_string())
            self.__server.quit()
        else:
            to_recipients = []
            for to in email_to:
                to_recipients.append(Mailbox(email_address=to))
            cc_recipients = []
            for cc in email_cc:
                cc_recipients.append(Mailbox(email_address=cc))
            message = Message(
                account=self.__account,
                subject=subject,
                body=HTMLBody(content),
                to_recipients=to_recipients,
                cc_recipients=cc_recipients
            )
            for attachment in attachments:
                with open(attachment, "rb") as f:
                    file_name = os.path.basename(attachment)
                    attachment_file = FileAttachment(name=file_name, content=f.read())
                    message.attach(attachment_file)
            message.send()

    def receive_email(self, folder: str = None) -> list:
        """
        TODO 暂时未完成测试
        接收邮件
        :return: (subject, content, attachments)
        """
        if self.__type == EmailType.SMTP:
            # 返回邮件总数目和占用服务器的空间大小（字节数）， 通过stat()方法即可
            email_count, email_size = self.__pop3_server.stat()
            logger.info("消息的数量: {0}, 消息的总大小: {1}".format(email_count, email_size))
            # 使用list()返回所有邮件的编号，默认为字节类型的串
            rsp, msg_list, rsp_siz = self.__pop3_server.list()
            logger.info(f"服务器的响应: {rsp},\n消息列表： {msg_list},\n返回消息的大小： {rsp_siz}")
            logger.info(f'邮件总数： {len(msg_list)}')
            logger.info(f"{msg_list}")
            return []
        else:
            emails = []
            if folder:
                sub_folder = self.__account.root // '信息存储顶部' // '收件箱' // f'{folder}'
                for item in sub_folder.all().order_by('-datetime_received')[:100]:
                    email = item.subject, item.sender
            else:
                for item in self.__account.inbox.all().order_by('-datetime_received')[:100]:
                    pass
