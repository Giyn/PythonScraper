"""
-------------------------------------
# -*- coding: utf-8 -*-
# @Time    : 2020/11/9 20:56:36
# @Author  : Giyn
# @Email   : giyn.jy@gmail.com
# @File    : old_official_website.py
# @Software: PyCharm
-------------------------------------
"""

import smtplib
from email.header import Header
from email.mime.text import MIMEText

import requests
from lxml import etree


def get_html(url):
    print("正在获取页面……")
    headers = {
        'Cookie': "UM_distinctid=17101abc69635b-0e556116b0f673-f313f6d-144000-17101abc6973c8; JSESSIONID=3178C10CD6DE2F5EA6033F90566F562C; wzws_cid=7a15963ee9210949b0d09b2f2889a0907ed8418df0e1e8b8122cd34a54d6be425da4ae3433c5ca7b3146755fc4cfcc31069f2f47f9468431388ba3ddfcac6c9f875fc30f80771a437b1ce7a07185b1d9",
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    }
    try:
        r = requests.get(url, headers=headers)
        r.encoding = r.apparent_encoding
        if r.status_code == 200:
            print("获取页面成功！")
    except Exception as e:
        print("获取页面失败，原因是：%s" % e)

    return r.text


def get_url():
    headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"}
    url = "http://old.gdut.edu.cn/"
    r = requests.get(url, headers=headers)
    html = etree.HTML(r.text)

    link1 = html.xpath("/html/body/div[@class='box-c3']/div[@class='news-s']/div[@class='news-zv']/ul/li/a/@href")
    link2 = html.xpath("/html/body/div[@class='box-c']/div[@class='news-s']/div[@class='news-zv']/ul/li/a/@href")
    link3 = html.xpath("/html/body/div[@class='box-c3']/div[@class='news-g']/div[@class='news-zv2']/ul/li/a/@href")
    link4 = html.xpath("/html/body/div[@class='box-c']/div[@class='news-g']/div[@class='news-zv2']/ul/li/a/@href")
    link5 = html.xpath("/html/body/div[@class='box-c']/div[@class='news-x']/div[@class='news-zv3']/ul/li/a/@href")

    return link1, link2, link3, link4, link5


def parse_html(html):
    print("正在解析页面……")

    html = etree.HTML(html)

    gdut_news = html.xpath("/html/body/div[@class='box-c3']/div[@class='news-s']/div[@class='news-zv']/ul/li/a/@title")
    gdut_media = html.xpath("/html//div[6]/div[1]/div[2]/ul/li/a/@title")
    bwcx_fdsz = html.xpath("/html//div[5]/div[2]/div[2]/ul/li/a/@title")
    Academic_Notice = html.xpath("/html/body/div[6]/div[2]/div[2]/ul/li/a/@title")
    stu_work = html.xpath("/html/body/div[6]/div[3]/div[2]/ul/li/a/@title")

    print("解析页面成功！")

    for i in range(5):
        gdut_news[i] = gdut_news[i] + " 详情点击：" + get_url()[0][i]
        gdut_media[i] = gdut_media[i] + " 详情点击：" + get_url()[1][i]
        bwcx_fdsz[i] = bwcx_fdsz[i] + " 详情点击：" + get_url()[2][i]
        Academic_Notice[i] = Academic_Notice[i] + " 详情点击：" + get_url()[3][i]
        stu_work[i] = stu_work[i] + " 详情点击：" + get_url()[4][i]

    all_news = '\n'.join(gdut_news) + '\n' + '\n'.join(
        gdut_media) + '\n' + '\n'.join(bwcx_fdsz) + '\n' + '\n'.join(
        Academic_Notice) + '\n' + '\n'.join(stu_work)

    return all_news


def sent_email(mail_body):
    sender = '490601115@qq.com'
    receiver = 'uzukidd@gmail.com'
    smtpServer = 'smtp.qq.com'  # 简单邮件传输协议服务器（这里是QQ邮箱的）
    username = '490601115@qq.com'
    password = '****************'
    mail_title = '【广东工业大学官网通知】'
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
        print('邮件发送成功！')
        smtp.quit()
    except smtplib.SMTPException:
        print("邮件发送失败！")


if __name__ == '__main__':
    url = 'http://old.gdut.edu.cn/'
    html = get_html(url)
    sent_email(mail_body=parse_html(html))
