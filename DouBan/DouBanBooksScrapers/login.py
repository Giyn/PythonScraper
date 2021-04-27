"""
-------------------------------------
# -*- coding: utf-8 -*-
# @Time    : 2021/3/28 16:45:45
# @Author  : Giyn
# @Email   : giyn.jy@gmail.com
# @File    : login.py
# @Software: PyCharm
-------------------------------------
"""

import asyncio

from fake_useragent import UserAgent
from pyppeteer import launch

ua = UserAgent()

url = 'https://book.douban.com/'


async def main():
    browser = await launch({'headless': False,
                            'args': ['--disable-infobars'],
                            'userDataDir': './userdata_douban'
                            })
    page = await browser.newPage()

    await page.setViewport({'width': 1530, 'height': 800})
    await page.setUserAgent(ua.chrome)
    await page.evaluateOnNewDocument(
        'function(){Object.defineProperty(navigator, "webdriver", {get: () => undefined})}')

    await page.goto(url, options={'timeout': 10000})

    await asyncio.sleep(412)
    await browser.close()


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
