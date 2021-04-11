"""
-------------------------------------
# -*- coding: utf-8 -*-
# @Time    : 2020/10/5 12:11:55
# @Author  : Giyn
# @Email   : giyn.jy@gmail.com
# @File    : scrape_GDUT_news_and_send_Email.py
# @Software: PyCharm
-------------------------------------
"""

import logging
import smtplib
import time
from email.header import Header
from email.mime.text import MIMEText

import requests
from fake_useragent import UserAgent
from lxml import etree

# log information settings
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s: %(message)s')
ua = UserAgent()


def get_html(url):
    """

    Get page html

    Args:
        url: URL

    Returns:
        response object

    """
    while True:
        try:
            time.sleep(4.12)
            res = requests.get(url, headers={'User-Agent': ua.chrome})
            if res.status_code == 200:
                return res
        except Exception as e:
            logging.ERROR(e)


def parse_html(text):
    doc = etree.HTML(text)

    news_num = len(doc.xpath(
        '/html/body/form//div[@id="ContentPlaceHolder1_ListView1_ItemPlaceHolderContainer"]/p'))

    news_list = []

    for i in range(1, news_num + 1):
        news_title = doc.xpath('/html/body/form//div[@id="ContentPlaceHolder1_ListView1_ItemPlaceHolderContainer"]/p[{}]/a/@title'.format(str(i)))[0]
        news_url = 'http://news.gdut.edu.cn/' + doc.xpath('/html/body/form//div[@id="ContentPlaceHolder1_ListView1_ItemPlaceHolderContainer"]/p[{}]/a/@href'.format(str(i)))[0].replace('./', '')
        news_from = doc.xpath('/html/body/form//div[@id="ContentPlaceHolder1_ListView1_ItemPlaceHolderContainer"]/p[{}]/span/@title'.format(str(i)))[0]
        news_date = doc.xpath('/html/body/form//div[@id="ContentPlaceHolder1_ListView1_ItemPlaceHolderContainer"]/p[{}]/span[2]/text()'.format(str(i)))[0].strip().replace(']', '').replace(u'\xa0', u' ')

        news = str({"title": news_title, "url": news_url, "from": news_from, "date": news_date})

        news_list.append(news)

    all_news = '\n'.join(news_list)

    return all_news


def sent_email(mail_body):
    sender = '490601115@qq.com'
    receiver = 'uzukidd@gmail.com'
    smtpServer = 'smtp.qq.com'  # 简单邮件传输协议服务器（这里是QQ邮箱的）
    username = '490601115@qq.com'
    password = '****************'
    mail_title = '【广东工业大学新闻网最新通知】'
    mail_body = mail_body

    message = MIMEText(mail_body, 'plain', 'utf-8')
    message["Accept-Language"] = "zh-CN"
    message["Accept-Charset"] = "ISO-8859-1,utf-8"
    message['From'] = sender
    message['To'] = receiver
    message['Subject'] = Header(mail_title, 'utf-8')

    try:
        smtp = smtplib.SMTP()
        smtp.connect(smtpServer)
        smtp.login(username, password)
        smtp.sendmail(sender, receiver, message.as_string())
        logging.info('邮件发送成功！')
        smtp.quit()
    except smtplib.SMTPException:
        logging.info('邮件发送失败！')


if __name__ == '__main__':
    url = 'http://news.gdut.edu.cn/ArticleList.aspx?category=4'
    text = get_html(url).text
    news = parse_html(text)
    sent_email(news)
