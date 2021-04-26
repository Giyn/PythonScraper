# -*- coding: utf-8 -*-
"""
Created on Mon Jun  8 11:05:40 2020

@author: Giyn
"""

import logging
import multiprocessing
import time

import pymongo
import requests
from fake_useragent import UserAgent
from lxml import etree

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s: %(message)s')  # 日志信息设置
ua = UserAgent()

MONGO_CONNECTION_STRING = 'mongodb://localhost:27017'  # MongoDB的连接字符串
MONGO_DB_NAME = 'movies'  # 数据库名称
MONGO_COLLECTION_NAME = 'douban_movies'  # 集合名称

client = pymongo.MongoClient(MONGO_CONNECTION_STRING)  # 创建MongoDB的连接对象
db = client[MONGO_DB_NAME]  # 指定数据库
collection = db[MONGO_COLLECTION_NAME]  # 指定集合


def get_html(url):
    """
    @功能: 爬取网页并获取其HTML代码
    @参数: 网页URL
    @返回: 网页的HTML代码
    """
    logging.info('scraping %s...', url)
    try:
        time.sleep(0.5)
        response = requests.get(url, headers={'User-Agent': ua.chrome})
        if response.status_code == 200:
            return response.text
        logging.error('get invalid status code %s while scraping %s', response.status_code, url)
    except requests.RequestException:
        logging.error('error occurred while scraping %s', url, exc_info=True)


def get_page_html(index):
    """
    @功能: 获取外部页面的HTML代码
    @参数: 页面索引
    @返回: 外部页面的HTML代码
    """
    page_url = f"https://movie.douban.com/top250?start={index}&filter="
    return get_html(page_url)


def get_movies_url(page_html):
    """
    @功能: 从外部页面获取每部电影的URL
    @参数: 每个外部页面的HTML代码
    @返回: 每个外部页面的URL
    """
    doc = etree.HTML(page_html)
    for i in range(1, 26):
        movie_url = doc.xpath("//ol/li[{}]//div[@class='hd']/a/@href".format(i))[0]  # 提取每部电影的URL
        logging.info('get movie url %s', movie_url)
        yield movie_url


def scrape_html(url):
    """
    @功能: 爬取网页并获取其HTML代码
    @参数: 网页URL
    @返回: 网页的HTML代码
    """
    return get_html(url)  # 代码复用,降低耦合度


def parse_movie(movie_html):
    """
    @功能: 解析每部电影的信息并提取
    @参数: 对应电影的HTML代码
    @返回: dict形式的电影信息
    """
    doc = etree.HTML(movie_html)  # 解析电影HTML代码
    cover = doc.xpath("//div[@id='mainpic']/a/img/@src")[0]
    name = doc.xpath("//div[@id='content']/h1/span[@property='v:itemreviewed']/text()")[0]
    rating_num = doc.xpath("//a[@class='rating_people']/span/text()")[0]
    info = ''.join(
        doc.xpath("//div[@class='indent']//span[@property='v:summary']/text()")).replace('\n',
                                                                                         '').replace(
        '\xa0', '').replace(u'\u3000', u'').replace(' ', '')
    score = doc.xpath("//div[@id='interest_sectl']//strong[@property='v:average']/text()")[0]
    score = float(score) if score else None

    return {
        'cover': cover,
        'name': name,
        'rating_num': rating_num,
        'info': info,
        'score': score
    }


def save_to_MongoDB(data):
    """
    @功能: 把电影数据存入MongoDB数据库
    @参数: dict形式的电影信息
    @返回: 无
    """
    collection.update_one({
        'name': data.get('name')
    }, {
        '$set': data
    }, upsert=True)


def main(page_index):
    """
    @功能: 每个线程
    @参数: 电影页面索引
    @返回: 无
    """
    page_html = get_page_html(page_index)
    movies_url = get_movies_url(page_html)

    for movie_url in movies_url:
        movie_html = scrape_html(movie_url)
        data = parse_movie(movie_html)

        logging.info('get data %s', data)
        logging.info('saving data to mongodb')
        save_to_MongoDB(data)
        logging.info('data saved successfully')


if __name__ == '__main__':
    pool = multiprocessing.Pool()
    page_indexs = range(0, 250, 25)
    pool.map(main, page_indexs)
    pool.close()
