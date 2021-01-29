# -*- coding: utf-8 -*-
"""
Created on Mon Jun  8 11:05:40 2020

@author: Giyn
"""

import multiprocessing
import requests
import logging
import random
import pymongo
from lxml import etree


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s') # 日志信息设置

headers = [
              {'User-Agent': "Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10"},
              {'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36 OPR/26.0.1656.60"},
              {'User-Agent': "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; QQBrowser/7.0.3698.400)"},
              {'User-Agent': "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SV1; QQDownload 732; .NET4.0C; .NET4.0E; SE 2.X MetaSr 1.0)"},
              {'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko"},
              {'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Maxthon/4.4.3.4000 Chrome/30.0.1599.101 Safari/537.36"}
          ]

MONGO_CONNECTION_STRING = 'mongodb://localhost:27017' # MongoDB的连接字符串
MONGO_DB_NAME = 'movies' # 数据库名称
MONGO_COLLECTION_NAME = 'movies1' # 集合名称

client = pymongo.MongoClient(MONGO_CONNECTION_STRING) # 创建MongoDB的连接对象
db = client['movies'] # 指定数据库
collection = db['douban_movies'] # 指定集合


def get_html(url):
    """
    @功能: 爬取网页并获取其HTML代码
    @参数: 网页URL
    @返回: 网页的HTML代码
    """
    logging.info('scraping %s...', url)
    try:
        response = requests.get(url, headers=random.choice(headers))
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
    for i in range(1,26):
        movie_url = doc.xpath('//ol/li[{}]/div/div[2]/div[1]/a/@href'.format(i))[0] # 提取每部电影的URL
        logging.info('get movie url %s', movie_url)
        yield movie_url


def scrape_html(url):
    """
    @功能: 爬取网页并获取其HTML代码
    @参数: 网页URL
    @返回: 网页的HTML代码
    """
    return get_html(url) # 代码复用,降低耦合度


def parse_movie(movie_html):
    """
    @功能: 解析每部电影的信息并提取
    @参数: 对应电影的HTML代码
    @返回: dict形式的电影信息
    """
    doc = etree.HTML(movie_html) # 解析电影HTML代码
    cover = doc.xpath("//div[3]/div[1]/div[3]/div[1]/div[1]/div[1]/div[1]/div[1]/a/img/@src")[0]
    name = doc.xpath("//div[3]/div[1]/h1/span[1]/text()")[0]
    rating_num = doc.xpath("//div[3]/div[1]/div[3]/div[1]/div[1]/div[1]/div[2]/div[1]/div[2]/div/div[2]/a/span/text()")[0]
    info = ''.join(doc.xpath("//div[@class='related-info']/div[@id='link-report']/span/text()")).strip().replace(' ', '').replace('\n', '').replace('\xa0', '').replace(u'\u3000', u' ')
    score = doc.xpath("//div[3]/div[1]/div[3]/div[1]/div[1]/div[1]/div[2]/div[1]/div[2]/strong/text()")[0]
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