"""
-------------------------------------
# -*- coding: utf-8 -*-
# @Time    : 2021/4/25 14:48:00
# @Author  : Giyn
# @Email   : giyn.jy@gmail.com
# @File    : scrape_douban_books.py
# @Software: PyCharm
-------------------------------------
"""

import pymysql
import asyncio
import logging
import random
import re

from fake_useragent import UserAgent
from lxml import etree
from pyppeteer import launch
from pyppeteer.errors import TimeoutError

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s: %(message)s')
ua = UserAgent()

INDEX_URL = 'https://book.douban.com/tag/{tag}?start={page}'
tags_list = ['小说', '外国文学', '文学', '经典', '中国文学', '日本文学', '散文', '名著']
browser, tab = None, None

conn = pymysql.connect(
    host="localhost",
    user="root",
    password="******",
    database="book",
    charset="utf8"
)

cursor = conn.cursor()  # 得到一个可以执行SQL语句的光标对象


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
        await asyncio.sleep(random.randint(0, 1))
        await tab.goto(url, {'timeout': 1000 * 60})
    except TimeoutError:
        logging.error('出错, 爬取网站为: %s', url, exc_info=True)


async def scrape_index(tag, page=1):
    """构造 URL 并爬取

    构造所需的 URL 并爬取

    Args:
        tag : 标签
        page: 页数

    Returns:

    """
    url = INDEX_URL.format(tag=tag, page=page)
    await scrape_page(url)


async def parse_index():
    """解析出详情 URL

    解析出每本书籍的详情 URL

    Args:

    Returns:
        每本书籍的详情 pyppeteer 对象

    """
    return await tab.xpath("//ul[@class='subject-list']/li/div[@class='info']/h2/a")


async def scrape_detail(url):
    """

    复用代码

    Args:
        url: 网页链接

    Returns:

    """
    await scrape_page(url)


async def parse_detail():
    """解析详细字段信息

    解析每本书籍的详细字段信息

    Args:

    Returns:
        json 格式的数据

    """
    detail_html = await tab.content()
    detail_doc = etree.HTML(detail_html)

    try:
        book_info = detail_doc.xpath("string(//div[@id='info'])").replace('\n', '').replace(' ', '').replace('\xa0', '')
    except:
        book_info = ''

    try:
        book_name = detail_doc.xpath("//div[@id='wrapper']/h1/span[@property='v:itemreviewed']/text()")[0]
    except:
        book_name = ''
    try:
        author = re.findall(r'作者:.+?(?=出品方|译者|原作名|出版社|副标题|出版年|页数|定价|装帧|ISBN)', book_info)[0].split(':')[1]
    except:
        author = ''
    try:
        press = re.findall(r'出版社:[\u4e00-\u9fa5]+?(?=出品方|译者|原作名|作者|副标题|出版年|页数|定价|装帧|ISBN)', book_info)[0].split(':')[1]
    except:
        press = ''
    try:
        publishing_year = re.findall(r'出版年:.+?(?=出品方|译者|原作名|作者|出版社|副标题|页数|定价|装帧|ISBN)', book_info)[0].split(':')[1].split('-')[0]
    except:
        publishing_year = ''
    try:
        score = float(detail_doc.xpath("//strong[@property='v:average']/text()")[0])
    except:
        score = ''
    try:
        rating_num = int(detail_doc.xpath("//span[@property='v:votes']/text()")[0])
    except:
        rating_num = ''
    try:
        page_num = int(re.findall(r'页数:.+?(?=出品方|译者|原作名|作者|出版社|副标题|出版年|定价|装帧|ISBN)', book_info)[0].split(':')[1])
    except:
        page_num = ''
    try:
        price = re.findall(r'定价:.+?(?=出品方|译者|原作名|作者|出版社|副标题|出版年|页数|装帧|ISBN)', book_info)[0].split(':')[1]
    except:
        price = ''
    try:
        ISBN = re.findall(r'ISBN:\d+', book_info)[0].split(':')[1]
    except:
        ISBN = ''
    try:
        content_introduction = ' '.join(detail_doc.xpath("//div[@id='link-report']//div[@class='intro']/p/text()"))
    except:
        content_introduction = ''
    try:
        cover_url = detail_doc.xpath("//div[@id='mainpic']/a/@href")[0]
    except:
        cover_url = ''
    try:
        readers = str(detail_doc.xpath("//span[@class='comment-info']/a/@href"))
    except:
        readers = ''

    return (book_name, author, press, publishing_year, score, rating_num,
            page_num, price, ISBN, content_introduction, cover_url, readers)


async def main():
    """

    主函数

    Args:

    Returns:

    """
    await init()
    try:
        for tag in tags_list[3:]:
            # 每个标签爬取50页
            for page in range(0, 1000, 20):
                try:
                    await scrape_index(tag, page)
                    url_elements = await parse_index()  # 获取详细 url
                    all_detail_url = []  # 存储详细 url
                    for url_element in url_elements:
                        # 保存详情 url
                        all_detail_url.append(
                            await (await url_element.getProperty('href')).jsonValue())

                    for each_detail_url in all_detail_url:
                        try:
                            await scrape_detail(each_detail_url)
                            detail_data = await parse_detail()
                        except:
                            logging.error('爬取 %s 时出现错误!' % each_detail_url)
                        logging.info('数据 %s', detail_data)
                        try:
                            insert_sql = "INSERT IGNORE INTO douban_book VALUES" \
                                         "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                            cursor.execute(insert_sql, detail_data)
                            conn.commit()  # 提交数据
                            logging.info('数据成功插入数据库!')
                        except Exception as e:
                            logging.error(e)
                            conn.rollback()
                except:
                    continue
    finally:
        await browser.close()
        conn.commit()  # 提交数据
        cursor.close()  # 关闭游标
        conn.close()  # 关闭数据库


if __name__ == '__main__':
    while True:
        try:
            asyncio.get_event_loop().run_until_complete(main())
        except:
            logging.error('网络错误!')
