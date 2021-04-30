"""
-------------------------------------
# -*- coding: utf-8 -*-
# @Time    : 2021/4/27 23:08:06
# @Author  : Giyn
# @Email   : giyn.jy@gmail.com
# @File    : scrape_book_users.py
# @Software: PyCharm
-------------------------------------
"""

import asyncio
import logging
import random
import re

import pymysql
from fake_useragent import UserAgent
from lxml import etree
from pyppeteer import launch
from pyppeteer.errors import TimeoutError

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s: %(message)s')
ua = UserAgent()

browser, tab = None, None

conn = pymysql.connect(
    host="localhost",
    user="root",
    password="******",
    database="book",
    charset="utf8"
)

cursor = conn.cursor()  # 得到一个可以执行SQL语句的光标对象


def get_user_urls_list():
    """

    获取用户 URL 列表

    Args:

    Returns:

    """
    USERS_list = []
    with open('user_urls.txt', mode='r', encoding='utf-8') as file:
        lines = file.readlines()
        for each_line in lines:
            USERS_list.append(each_line.strip())

    USERS_list = list(set(USERS_list))
    USERS_list.remove('')

    return USERS_list


async def init():
    """初始化配置

    初始化 pyppeteer 配置

    Args:

    Returns:

    """
    global browser, tab
    browser = await launch(headless=False,
                           args=['--disable-infobars'],
                           userDataDir='./userdata_douban')
    tab = await browser.newPage()

    await tab.setViewport({'width': 1530, 'height': 800})
    await tab.setUserAgent(ua.chrome)


async def scrape_page(url):
    """

    爬取网页通用函数

    Args:
        url: 网页链接

    Returns:

    """
    logging.info('正在爬取: %s', url)
    try:
        await asyncio.sleep(random.randint(1, 2))
        await tab.goto(url, {'timeout': 1000 * 60})
    except TimeoutError:
        logging.error('出错, 爬取网站为: %s', url, exc_info=True)


async def scrape_index(user_url, index):
    """构造 URL 并爬取

    构造所需的 URL 并爬取

    Args:
        user_url: 用户主页面
        index   : URL 索引

    Returns:

    """
    url = user_url + 'start={}'.format(index)
    await scrape_page(url)


async def parse_user():
    """解析详细字段信息

    解析每位用户的详细字段信息

    Args:

    Returns:
        json 格式的数据

    """
    detail_html = await tab.content()
    detail_doc = etree.HTML(detail_html)
    try:
        nickname = re.findall(r'.+?(?=读过的书)', detail_doc.xpath("//div[@id='db-usr-profile']/div[@class='info']/h1/text()")[0])[0].strip()
    except:
        nickname = ''
    try:
        read_num = re.findall(r'\d+', detail_doc.xpath("//div[@id='db-usr-profile']/div[@class='info']/h1/text()")[0])[0]
        read_num = int(read_num)
    except:
        read_num = ''
    try:
        read_page = detail_doc.xpath("//div[@class='paginator']/a")[-1].text
    except:
        read_page = ''

    return [nickname, read_num], read_page


async def parse_detail():
    """解析详细字段信息

    解析每位用户的详细字段信息

    Args:

    Returns:
        json 格式的数据

    """
    detail_html = await tab.content()
    detail_doc = etree.HTML(detail_html)
    read_book_and_score = {}
    for i in range(1, 16):
        try:
            name = detail_doc.xpath("//li[{}]/div[@class='info']//a/@title".format(str(i)))[0]
        except:
            continue
        try:
            score = re.findall(r'\d+', detail_doc.xpath("//li[{}]/div[@class='info']/div[@class='short-note']//span[1]/@class".format(str(i)))[0])[0]
            score = int(score)
        except:
            continue
        try:
            read_book_and_score.update({name: score})
        except:
            pass

    return read_book_and_score


async def main(user_urls_list):
    """

    主函数

    Args:

    Returns:

    """
    await init()
    try:
        for user in user_urls_list:
            try:
                user_info_list = []
                user_read_score_dict = {}
                user_id = user.split('/')[-2]
                user_info_list.append(user_id)
                user_book_url = 'https://book.douban.com/people/{}/collect?'.format(user_id)
                await scrape_page(user_book_url)
                nickname_and_read_num, read_page = await parse_user()
                user_info_list.extend(nickname_and_read_num)
                for index in range(0, int(read_page) * 15, 15):
                    try:
                        await scrape_index(user_book_url, index)
                        user_read_score_dict.update(await parse_detail())
                    except:
                        continue
                user_info_list.append(str(user_read_score_dict))
            except:
                continue
            user_info_list = tuple(user_info_list)
            logging.info('数据 %s', user_info_list)
            try:
                insert_sql = "INSERT IGNORE INTO douban_book_users VALUES" \
                             "(%s, %s, %s, %s)"
                cursor.execute(insert_sql, user_info_list)
                conn.commit()  # 提交数据
                logging.info('数据成功插入数据库!')
            except Exception as e:
                logging.error(e)
                conn.rollback()
    finally:
        await browser.close()
        conn.commit()  # 提交数据
        cursor.close()  # 关闭游标
        conn.close()  # 关闭数据库


if __name__ == '__main__':
    user_urls_list = get_user_urls_list()[1500:2000]
    asyncio.get_event_loop().run_until_complete(main(user_urls_list))
