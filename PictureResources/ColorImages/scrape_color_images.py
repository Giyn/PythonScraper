"""
-------------------------------------
# -*- coding: utf-8 -*-
# @Time    : 2020/12/11 16:29:45
# @Author  : Giyn
# @Email   : giyn.jy@gmail.com
# @File    : scrape_color_images.py
# @Software: PyCharm
-------------------------------------
"""
__author__ = 'Giyn'

import aiohttp
import asyncio
import hashlib
import logging

URL = 'https://setu.awsl.ee/api/setu!'
CONCURRENCY = 200  # 并发限制
NUM = 30000
semaphore = asyncio.Semaphore(CONCURRENCY)
session = None
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s: %(message)s')  # log information settings


async def scrape_api():
    async with semaphore:
        async with aiohttp.ClientSession() as session:
            try:
                response = await session.get(URL)
                img = await response.read()
                fmd5 = hashlib.md5(img)
                img_name = fmd5.hexdigest()
                with open('{}/{}.png'.format('color_images_md5', img_name), 'wb') as file:
                    file.write(img)
                logging.info("Successfully get an image!")
            except:
                pass
            await asyncio.sleep(5)


async def main():
    global session
    session = aiohttp.ClientSession()
    scrape_index_tasks = [asyncio.ensure_future(scrape_api()) for _ in range(NUM)]
    await asyncio.gather(*scrape_index_tasks)


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
