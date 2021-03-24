"""
-------------------------------------
# -*- coding: utf-8 -*-
# @Time    : 2021/3/24 9:04:52
# @Author  : Giyn
# @Email   : giyn.jy@gmail.com
# @File    : base_recruitment_scraper.py
# @Software: PyCharm
-------------------------------------
"""

import logging

import requests
from faker import Faker
from lxml import etree

fake = Faker()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')


class BaseRecruitmentScraper:
    def __init__(self, website: str):
        self.website = website
        self.headers = {'User-Agent': fake.user_agent()}
        self.ip = []

    def get_page(self, url: str, expand_ip: bool) -> str:
        logging.info('scraping %s', url)
        if not expand_ip:
            page = requests.get(url=url, headers=self.headers, timeout=20).text  # html

        return page

    @staticmethod
    def parse_page(page: str, xpath_expression: dict) -> str:
        doc = etree.HTML(page)
        content = doc.xpath(xpath_expression)

        return content

    def __repr__(self):
        return 'Scraper of %s' % self.website


if __name__ == '__main__':
    pass
