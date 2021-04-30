"""
-------------------------------------
# -*- coding: utf-8 -*-
# @Time    : 2021/4/30 10:46:42
# @Author  : Giyn
# @Email   : giyn.jy@gmail.com
# @File    : scrape_book_covers.py
# @Software: PyCharm
-------------------------------------
"""

import asyncio
import logging
import os
import random

import aiohttp
import pymysql
from fake_useragent import UserAgent

CONCURRENT = 4  # 并发限制
semaphore = asyncio.Semaphore(CONCURRENT)
session = None
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s: %(message)s')  # log information settings
ua = UserAgent()

conn = pymysql.connect(
    host="localhost",
    user="root",
    password="******",
    database="book",
    charset="utf8"
)

cursor = conn.cursor()  # 得到一个可以执行SQL语句的光标对象

select_sql = 'SELECT book_name, cover_url FROM douban_book'

cover_url_num = cursor.execute(select_sql)
covers_url_tuple = cursor.fetchall()


async def scrape_api(cover_tuple):
    """

    爬取图片

    Args:

    Returns:

    """
    async with semaphore:
        async with aiohttp.ClientSession() as session:
            try:
                await asyncio.sleep(random.randint(1, 2))
                if not os.path.exists('book_covers'):
                    os.mkdir('book_covers')
                response = await session.get(url=cover_tuple[1],
                                             headers={'User-Agent': ua.chrome})
                img = await response.read()
                img_name = cover_tuple[0]
                with open('{}/{}.png'.format('book_covers', img_name), 'wb') as file:
                    file.write(img)
                logging.info("已成功下载一张图片 %s!" % img_name)
            except Exception as e:
                logging.error("下载失败!", e)


async def main():
    """

    主函数

    Args:

    Returns:

    """
    global session
    session = aiohttp.ClientSession()
    tasks = [asyncio.ensure_future(scrape_api(each_cover)) for each_cover in covers_url_tuple]
    await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
