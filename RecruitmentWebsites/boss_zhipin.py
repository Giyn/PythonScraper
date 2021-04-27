"""
-------------------------------------
# -*- coding: utf-8 -*-
# @Time    : 2021/3/26 23:03:04
# @Author  : Giyn
# @Email   : giyn.jy@gmail.com
# @File    : boss_zhipin.py
# @Software: PyCharm
-------------------------------------
"""

import asyncio
import logging
import os
import random
import re

import pandas as pd
from fake_useragent import UserAgent
from lxml import etree
from pyppeteer import launch
from pyppeteer.errors import TimeoutError

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')
ua = UserAgent()

INDEX_URL = 'https://www.zhipin.com/c100010000/?query={keyword}&page={page}'
key_words_list = ['人工智能', 'AI', '深度学习', '机器学习', 'python', '机器视觉', '图像识别', '图像处理',
                  '图像算法', '自然语言处理', 'NLP', '语音识别', '数据标注', '自动驾驶', '智能驾驶']

browser, tab = None, None


async def init():
    """初始化配置

    初始化 pyppeteer 配置

    Args:

    Returns:

    """
    global browser, tab
    browser = await launch(headless=True,
                           args=['--disable-infobars'],
                           userDataDir='./userdata_bosszhipin')
    tab = await browser.newPage()
    await tab.setViewport({'width': 1530, 'height': 800})
    await tab.setUserAgent(ua.chrome)
    await tab.evaluateOnNewDocument(
        'function(){Object.defineProperty(navigator, "webdriver", {get: () => undefined})}')


async def scrape_page(url):
    """

    爬取网页通用函数

    Args:
        url: 网页链接

    Returns:

    """
    logging.info('正在爬取: %s', url)
    try:
        await asyncio.sleep(random.randint(2, 3))
        await tab.goto(url, {'timeout': 1000 * 20})
    except TimeoutError:
        logging.error('出错, 爬取网站为: %s', url, exc_info=True)


async def scrape_index(keyword, page=1):
    """构造 URL 并爬取

    构造所需的 URL 并爬取

    Args:
        keyword: 关键词
        page   : 页数

    Returns:

    """
    url = INDEX_URL.format(keyword=keyword, page=page)
    await scrape_page(url)


async def parse_index():
    """解析出详情 URL

    解析出每个职位的详情 URL

    Args:

    Returns:
        每个职位的详情 pyppeteer 对象

    """
    return await tab.xpath("//span[@class='job-name']/a")


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

    解析每个职位的详细字段信息

    Args:

    Returns:
        json 格式的数据

    """
    detail_html = await tab.content()
    detail_doc = etree.HTML(detail_html)
    try:
        job_name = detail_doc.xpath("//div[@class='name']/h1/@title")[0]
    except:
        job_name = ''
    try:
        academic_requirements = ','.join(re.findall('大专|本科|硕士|博士', ''.join(
            ''.join(detail_doc.xpath("//div[@class='info-primary']//p/text()")).split())))
    except:
        academic_requirements = ''
    try:
        salary = detail_doc.xpath("//span[@class='salary']/text()")[0]
    except:
        salary = ''
    try:
        description = ''.join(
            ''.join(detail_doc.xpath("//div[@class='job-sec']/div[@class='text']/text()")).split())
    except:
        description = ''
    try:
        company_name = detail_doc.xpath("//div[@class='job-sec']/div[@class='name']/text()")[0]
    except:
        company_name = ''
    try:
        work_place = detail_doc.xpath("//a[@class='text-city']/text()")[0]
    except:
        work_place = ''

    return {
        '数据来源': 'BOSS直聘',
        '岗位名称': job_name,
        '学历要求': academic_requirements,
        '薪资待遇': salary,
        '岗位职责/职位描述': description,
        '公司名称': company_name,
        '工作地点': work_place
    }


async def main():
    """

    主函数

    Args:

    Returns:

    """
    await init()
    try:
        for key_word in key_words_list:
            # 每个关键词爬取 10 页
            for page in range(1, 11):
                try:
                    await scrape_index(key_word, page)
                    url_elements = await parse_index()
                    all_detail_url = []  # 存储详细 url
                    data_list = []  # 存储目标数据
                    for url_element in url_elements:
                        # 保存详情 url
                        all_detail_url.append(
                            await (await url_element.getProperty('href')).jsonValue())

                    for each_detail_url in all_detail_url:
                        await scrape_detail(each_detail_url)
                        detail_data = await parse_detail()
                        data_list.append(detail_data)
                        logging.info('数据 %s', detail_data)

                    df = pd.DataFrame(data_list)

                    if os.path.exists('data.csv'):
                        df.to_csv("data.csv", encoding='utf_8_sig', mode='a+', index=False,
                                  header=False)
                        logging.info('数据已保存')
                    else:
                        df.to_csv("data.csv", encoding='utf_8_sig', index=False)
                        logging.info('数据已保存')
                except:
                    continue
    finally:
        await browser.close()


if __name__ == '__main__':
    while True:
        try:
            asyncio.get_event_loop().run_until_complete(main())
        except:
            logging.error('网络错误')
