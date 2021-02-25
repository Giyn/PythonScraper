"""
-------------------------------------
# -*- coding: utf-8 -*-
# @Time    : 2021/2/23 22:47:17
# @Author  : Giyn
# @Email   : giyn.jy@gmail.com
# @File    : UsersArtworks.py
# @Software: PyCharm
-------------------------------------
"""

import os
import hashlib
import json
import logging
import time

import requests
from faker import Faker
from lxml import etree
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ChromeOptions

fake = Faker()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')

option = ChromeOptions()
option.headless = True
option.add_argument("--disable-blink-features=AutomationControlled")
option.add_experimental_option('excludeSwitches', ['enable-automation'])
option.add_experimental_option('useAutomationExtension', False)
browser = webdriver.Chrome(options=option)

URL = 'https://www.pixiv.net/ajax/user/{}/profile/all?lang=zh'
cookie = ''
proxies = {"http": "http://127.0.0.1:1080",
           "https": "https://127.0.0.1:1080"}


def scrape_page(url):
    """
    Page scraping framework

    Args:
        url: pages to be scraped
    Returns:
        None
    """
    logging.info('scraping %s', url)
    try:
        browser.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument',
                                {'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'})
        time.sleep(1)
        browser.get(url)
    except TimeoutException:
        logging.error('error occurred while scraping %s', url, exc_info=True)

    return browser.page_source


def save_img(url, ID):
    """
    Save image

    Args:
        url: URL
        ID: user ID
    Returns:
        None
    """
    browser.get(url)  # 作品页面
    doc_work = etree.HTML(browser.page_source)
    # print(browser.page_source)
    url_img = doc_work.xpath('//div[@role="presentation"]/a/@href')[0]  # 提取原图URL
    print(url_img)
    headers_img = {'User-Agent': fake.user_agent(), 'referer': 'https://www.pixiv.net/'}
    res_img = requests.get(url_img, headers=headers_img, proxies=proxies)  # 访问原图资源
    img = res_img.content  # 获取原图资源
    fmd5 = hashlib.md5(img)
    img_name = fmd5.hexdigest()

    if not os.path.exists(ID):
        os.makedirs(ID)

    with open('{}/{}.jpg'.format(ID, img_name), 'wb') as f:
        f.write(img)


if __name__ == "__main__":
    ID = '74184'
    domain = 'https://www.pixiv.net/artworks/'
    html = scrape_page(URL.format(ID))
    doc = etree.HTML(html)
    data = json.loads(doc.xpath('/html/body/pre/text()')[0])['body']['illusts']
    url_list = []
    for key, value in data.items():
        url_list.append(domain + key)
        print(domain + key)
        try:
            save_img(domain + key, ID)
        except:
            pass
