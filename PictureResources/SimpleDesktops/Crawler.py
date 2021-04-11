# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name  : Crawler
   Description:
   Author     : Giyn
   date       : 2020/9/5 22:13:23
-------------------------------------------------
"""
__author__ = 'Giyn'

import logging
import multiprocessing
import os
import time

import requests
from faker import Faker
from lxml import etree

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s: %(message)s')  # log information settings

fake = Faker()

URL = 'http://simpledesktops.com/browse/{}/'


def get_html(url):
    """

    Get page

    Args:
        url: URL

    Returns:
        res.text: page content

    """
    failed = 1  # request failed parameters

    while True:
        try:
            if failed % 2 == 0:
                logging.info("Too many failed requests!")
            time.sleep(1)
            res = requests.get(url, headers={'User-Agent': fake.user_agent()})
            if res.status_code == 200:
                return res
        except Exception as e:
            logging.ERROR(e)
            failed += 1


def parse_html(html):
    """

    Parse web pages and extract image resources

    Args:
        html: html

    Returns:
        images_list: images list

    """
    doc = etree.HTML(html)
    raw_images_list = doc.xpath(
        "/html/body/div//div[@class='desktops column span-24 archive']/div//img/@src")
    images_list = []
    for each_pic in raw_images_list:
        images_list.append(each_pic.replace('.295x184_q100.png', ''))

    logging.info("Successfully get images list!")

    return images_list


def download_img(url_list):
    """

    Download images

    Args:
        url_list: image url list

    Returns:
        None

    """
    dir_name = 'simple_desktops'
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)

    for url in url_list:
        img = get_html(url).content  # return bytes type which is binary data
        img_name = url.split('/')[-1].split('.')[0]

        with open('{}/{}.png'.format(dir_name, img_name), 'wb') as file:
            file.write(img)

        logging.info("Successfully download an image!")


def process(index):
    """

    Each process

    Args:
        None

    Returns:
        None

    """
    url = URL.format(index)
    images_list = parse_html(get_html(url).text)
    download_img(images_list)

    logging.info("Successfully complete a process!")


if __name__ == "__main__":
    pool = multiprocessing.Pool()
    page_indexs = range(1, 52)
    pool.map(process, page_indexs)
    pool.close()
