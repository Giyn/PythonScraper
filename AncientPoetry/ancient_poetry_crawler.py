"""
-------------------------------------
# -*- coding: utf-8 -*-
# @Time    : 2020/10/5 12:11:55
# @Author  : Giyn
# @Email   : giyn.jy@gmail.com
# @File    : ancient_poetry_crawler.py
# @Software: PyCharm
-------------------------------------
"""

import requests
import logging
import time
import json
from lxml import etree
from faker import Faker
from collections import OrderedDict

# log information settings
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s: %(message)s')

fake = Faker()

URL = 'https://so.gushiwen.cn/mingju/default.aspx?p={}&c=&t='


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
            res = requests.get(url, headers={'User-Agent': fake.user_agent()})
            if res.status_code == 200:
                return res
        except Exception as e:
            logging.ERROR(e)


def parse_and_save_poetry(html):
    """

    Parse web pages and extract image resources

    Args:
        html: html

    Returns:
        None

    """
    doc = etree.HTML(html)
    for i in range(1, 51):
        text = doc.xpath(
            "/html[@id='html']/body/div[@class='main3']/div[@class='left']/div[@class='sons']/div[@class='cont'][{}]/a/text()".format(
                str(i)))
        content = text[0]
        author = text[1].split("《")[0]
        from_ = "《" + text[1].split("《")[1]
        each_poetry_dict = OrderedDict()
        if author != '':
            each_poetry_dict["content"] = content
            each_poetry_dict["author"] = author
            each_poetry_dict["from"] = from_
        else:
            each_poetry_dict["content"] = content
            each_poetry_dict["from"] = from_

        poetry_dict = json.dumps(each_poetry_dict, sort_keys=False, indent=2,
                                 separators=(',', ': '), ensure_ascii=False)
        save_as_json(poetry_dict)
    logging.info('Successfully save a piece of poetry!')


def save_as_json(poetry_dict):
    """

    Save data as json

    Args:
        poetry_dict: poetry dict

    Returns:
        None

    """
    save_path = 'poetry.json'
    with open(save_path, 'a+') as file:
        file.write(str(poetry_dict) + ",\n")


def process(index):
    """

    Each process

    Args:
        index: page index

    Returns:
        None

    """
    parse_and_save_poetry(get_html(URL.format(str(index))).text)
    logging.info("Successfully complete a process!")


def main():
    """

    main entry

    Args:
        None

    Returns:
        None

    """
    for index in range(1, 21):
        process(index)


if __name__ == "__main__":
    main()
